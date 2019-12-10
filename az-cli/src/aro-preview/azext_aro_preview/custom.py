# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import uuid

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from ._client_factory import (cf_resource_groups,
                              cf_network_virtual_networks,
                              cf_network_virtual_networks_subnets,
                              cf_auth_management,
                              cf_graph_rbac_management)
from .vendored_sdks.models import (OpenShiftCluster,
                                   ServicePrincipalProfile,
                                   NetworkProfile,
                                   WorkerProfile,
                                   MasterProfile)
from azure.graphrbac.models import GetObjectsParameters

from msrestazure.azure_exceptions import CloudError

logger = get_logger(__name__)

FP_CLIENT_ID="f1dd0a37-89c6-4e07-bcd1-ffd3d43d8875"

def aro_preview_create(cmd, client, resource_group_name, resource_name,
                       client_id,
                       client_secret,
                       location,
                       pod_cidr=None,
                       service_cidr=None,
                       master_vm_size=None,
                       worker_vm_size=None,
                       worker_vm_disk_size_gb=None,
                       worker_count=None,
                       vnet_resource_group_name=None,
                       vnet_name=None,
                       vnet_worker_subnet_name=None,
                       vnet_master_subnet_name=None,
                       tags=None,
                       no_wait=False):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # if rg with cluster name does not exist
    if not _create_resourcegroup(cmd.cli_ctx, resource_group_name, subscription_id, location, 2):
        raise CLIError('Could not create resourcegroup')

    # vnet creation flow
    if vnet_resource_group_name is None:
        # try to create new VNET using az credentials
        if not _create_vnet_resourcegroup(cmd.cli_ctx,
                                          resource_name,
                                          resource_group_name + "-vnet",
                                          subscription_id,
                                          location,
                                          client_id):
            raise CLIError('Count not create VNET resource group'
                           'Are you an Owner on this subscription?')

        vnet_resource_group_name = resource_group_name + "-vnet"

    # check if provided vnet contains right subnets, if not - fail
    if vnet_name is None:
        vnet_name = "vnet"
    if vnet_worker_subnet_name is None:
        vnet_worker_subnet_name = resource_name + "-worker"
    if vnet_master_subnet_name is None:
        vnet_master_subnet_name = resource_name + "-master"


    if not _validate_vnet_subnet(cmd.cli_ctx, vnet_resource_group_name, vnet_name, vnet_master_subnet_name, subscription_id) and \
       not _validate_vnet_subnet(cmd.cli_ctx, vnet_resource_group_name, vnet_name, vnet_worker_subnet_name, subscription_id):
        raise CLIError('Provided vnet validation error')

    # set subnetID's
    vnet_master_subnet_name = "/subscriptions/{}/resourcegroups/{}/providers/Microsoft.Network/virtualNetworks/vnet/subnets/{}".format(subscription_id, vnet_resource_group_name, vnet_master_subnet_name) # pylint: disable=line-too-long
    vnet_worker_subnet_name = "/subscriptions/{}/resourcegroups/{}/providers/Microsoft.Network/virtualNetworks/vnet/subnets/{}".format(subscription_id, vnet_resource_group_name, vnet_worker_subnet_name) # pylint: disable=line-too-long

    if pod_cidr is None:
        pod_cidr = "10.128.0.0/14"
    if service_cidr is None:
        service_cidr = "172.30.0.0/16"


    # vm configuration
    if master_vm_size is None:
        master_vm_size = "Standard_D8s_v3"
    if worker_vm_size is None:
        worker_vm_size = "Standard_D2s_v3"
    if worker_vm_disk_size_gb is None:
        worker_vm_disk_size_gb = 128
    if worker_count is None:
        worker_count = 3


    # construct OpenShiftCluster object
    oc = OpenShiftCluster(
        location=location,
        tags=tags,
        service_principal_profile=ServicePrincipalProfile(
            client_id=client_id,
            client_secret=client_secret,
        ),
        network_profile=NetworkProfile(
            pod_cidr=pod_cidr,
            service_cidr=service_cidr,
        ),
        master_profile=MasterProfile(
            vm_size=master_vm_size,
            subnet_id=vnet_master_subnet_name,
        ),
        worker_profiles=[WorkerProfile(
            name="worker",
            vm_size=worker_vm_size,
            disk_size_gb=worker_vm_disk_size_gb,
            subnet_id=vnet_worker_subnet_name,
            count=worker_count,
        )]
    )
    return sdk_no_wait(no_wait, client.create,
                       resource_group_name=resource_group_name,
                       resource_name=resource_name,
                       parameters=oc)

def aro_preview_delete(client, resource_group_name, resource_name,
                       no_wait=False):
    return sdk_no_wait(no_wait, client.delete,
                       resource_group_name=resource_group_name,
                       resource_name=resource_name)

def aro_preview_list(client):
    return client.list()

def aro_preview_show(client, resource_group_name, resource_name):
    return client.get(resource_group_name, resource_name)

def aro_preview_get_credentials(client, resource_group_name, resource_name):
    return client.get_credentials(resource_group_name, resource_name)

def aro_preview_update(client, resource_group_name, resource_name,
                       worker_count=None,
                       worker_pool_name=None,
                       no_wait=False):

    if worker_pool_name is None:
        worker_pool_name = "workers"

    oc = client.get(resource_group_name, resource_name)

    for i, p in oc.WorkerProfile:
        if p.name == worker_pool_name and p.count != worker_count:
            oc.WorkerProfile[i].count = worker_count

    return sdk_no_wait(no_wait, client.create,
                       resource_group_name=resource_group_name,
                       resource_name=resource_name,
                       parameters=oc)


def _get_rg_location(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    # Just do the get, we don't need the result, it will error out if the group doesn't exist.
    rg = groups.get(resource_group_name)
    return rg.location

def _validate_vnet_subnet(cli_ctx, resource_group_name, virtual_network_name, subnet_name, subscription_id):
    subnet_client = cf_network_virtual_networks_subnets(cli_ctx, subscription_id)
    subnet_list = subnet_client.list(resource_group_name, virtual_network_name)

    for i in subnet_list:
        if i.name == subnet_name:
            return True
    return False

def _create_vnet_resourcegroup(cli_ctx, cluster_name, resource_group_name,
                               subscription_id,
                               location,
                               cluster_client_id,
                               delay=2):

    if not _create_resourcegroup(cli_ctx, resource_group_name, subscription_id, location, delay):
        return False

    if not _create_vnet(cli_ctx, resource_group_name, "vnet", "10.0.0.0/9", cluster_name,
                        subscription_id, location):
        return False

    if not _add_role_assignment(cli_ctx, "ARO v4 Development Subnet Contributor", FP_CLIENT_ID, delay,
                                "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/vnet".format(subscription_id, resource_group_name)): # pylint: disable=line-too-long
        return False

    if not _add_role_assignment(cli_ctx, "ARO v4 Development Subnet Contributor", cluster_client_id, delay,
                                "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/vnet".format(subscription_id, resource_group_name)): # pylint: disable=line-too-long
        return False

    return True


def _create_resourcegroup(cli_ctx, resource_group_name, subscription_id, location, delay=2):
    # Create RG
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for create resource group', value=0, total_val=1.0)
    logger.info('Waiting for create resource group')
    for x in range(0, 10):
        hook.add(message='Waiting for create resource group', value=0.1 * x, total_val=1.0)
        try:
            groups_client = cf_resource_groups(cli_ctx, subscription_id=subscription_id)
            groups_client.create_or_update(resource_group_name, {'location':location})
            break
        except CLIError as ex:
            raise ex
        except CloudError as ex:
            logger.info(ex)
            time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='Resource group creation done', value=1.0, total_val=1.0)
    logger.info('Resource group creation done')
    return True

def _create_vnet(cli_ctx, resource_group_name, resource_name, address_prefix,
                 subnet_prefix,
                 subscription_id,
                 location,
                 delay=2):
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for create vnet', value=0, total_val=1.0)
    logger.info('Waiting for create vnet')
    for x in range(0, 10):
        hook.add(message='Waiting for create vnet', value=0.1 * x, total_val=1.0)
        try:
            vnet_client = cf_network_virtual_networks(cli_ctx, subscription_id)
            async_vnet_creation = vnet_client.create_or_update(
                resource_group_name,
                resource_name,
                {
                    'location': location,
                    'address_space': {
                        'address_prefixes': [address_prefix]
                    }
                }
            )
            async_vnet_creation.wait()

            # Create subnets for masters and workers
            # TODO: Make these separate function and configurable
            print("vnet create")
            subnet_client = cf_network_virtual_networks_subnets(cli_ctx, subscription_id)
            async_subnet_creation = subnet_client.create_or_update(
                resource_group_name,
                resource_name,
                subnet_prefix+"-master",
                {'address_prefix': "10.0.1.0/24"}
            )
            async_subnet_creation.wait()

            async_subnet_creation = subnet_client.create_or_update(
                resource_group_name,
                resource_name,
                subnet_prefix+"-worker",
                {'address_prefix': "10.0.2.0/24"}
            )
            async_subnet_creation.wait()
            break

        except CLIError as ex:
            raise ex
        except CloudError as ex:
            logger.info(ex)
            time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='Vnet creation done', value=1.0, total_val=1.0)
    logger.info('Vnet creation done')
    return True

def _add_role_assignment(cli_ctx, role, service_principal, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to propagate', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to propagate')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to propagate', value=0.1 * x, total_val=1.0)
        try:
            create_role_assignment(cli_ctx, role, service_principal, scope=scope)
            break
        except CloudError as ex:
            if ex.message == 'The role assignment already exists.':
                break
            logger.info(ex.message)
        except:  # pylint: disable=bare-except
            pass
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='AAD role propagation done', value=1.0, total_val=1.0)
    logger.info('AAD role propagation done')
    return True



def create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None):
    return _create_role_assignment(cli_ctx, role, assignee, resource_group_name, scope)


def _create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None, resolve_assignee=True):
    from azure.cli.core.profiles import ResourceType, get_sdk
    factory = cf_auth_management(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    scope = _build_role_scope(resource_group_name, scope, assignments_client.config.subscription_id)

    role_id = _resolve_role_id(role, scope, definitions_client)
    object_id = _resolve_object_id(cli_ctx, assignee) if resolve_assignee else assignee
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=object_id)
    assignment_name = uuid.uuid4()
    custom_headers = None
    return assignments_client.create(scope, assignment_name, parameters, custom_headers=custom_headers)


def _build_role_scope(resource_group_name, scope, subscription_id):
    subscription_scope = '/subscriptions/' + subscription_id
    if scope:
        if resource_group_name:
            err = 'Resource group "{}" is redundant because scope is supplied'
            raise CLIError(err.format(resource_group_name))
    elif resource_group_name:
        scope = subscription_scope + '/resourceGroups/' + resource_group_name
    else:
        scope = subscription_scope
    return scope

def _resolve_role_id(role, scope, definitions_client):
    role_id = None
    try:
        uuid.UUID(role)
        role_id = role
    except ValueError:
        pass
    if not role_id:  # retrieve role id
        role_defs = list(definitions_client.list(scope, "roleName eq '{}'".format(role)))
        print(role_defs)
        if not role_defs:
            raise CLIError("Role '{}' doesn't exist.".format(role))
        if len(role_defs) > 1:
            ids = [r.id for r in role_defs]
            err = "More than one role matches the given name '{}'. Please pick a value from '{}'"
            raise CLIError(err.format(role, ids))
        role_id = role_defs[0].id
    return role_id

def _resolve_object_id(cli_ctx, assignee):
    client = cf_graph_rbac_management(cli_ctx)
    result = None
    if assignee.find('@') >= 0:  # looks like a user principal name
        result = list(client.users.list(filter="userPrincipalName eq '{}'".format(assignee)))
    if not result:
        result = list(client.service_principals.list(
            filter="servicePrincipalNames/any(c:c eq '{}')".format(assignee)))
    if not result:  # assume an object id, let us verify it
        result = _get_object_stubs(client, [assignee])

    # 2+ matches should never happen, so we only check 'no match' here
    if not result:
        raise CLIError("No matches in graph database for '{}'".format(assignee))

    return result[0].object_id

def _get_object_stubs(graph_client, assignees):
    params = GetObjectsParameters(include_directory_object_references=True,
                                  object_ids=assignees)
    return list(graph_client.objects.get_objects_by_object_ids(params))

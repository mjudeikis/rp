# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from ._validators import validate_create_parameters


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    resource_name_type = CLIArgumentType(options_list='--resource-name-name', help='Name of the aro-preview.', id_part='name')

    with self.argument_context('aro') as c:
        c.argument('tags', tags_type)

    with self.argument_context('aro create') as c:
        c.argument('location')
        c.argument('resource_name', resource_name_type, options_list=['--name', '-n'])
        c.argument('client_id', options_list=('--client-id'), help='Cluster service principal clientID', validator=validate_create_parameters)
        c.argument('client_secret', options_list=('--client-secret'), help='Cluster service principal clientSecret', validator=validate_create_parameters)
        c.argument('pod-cidr', options_list=('--pod-cidr'), help='Pod netowork CIDR [Default: 10.128.0.0/14]')
        c.argument('service-cidr', options_list=('--service-cidr'), help='Service network CIDR [Default: 172.30.0.0/16]')

        # VM configuration
        c.argument('master-vm-size', options_list=('--master-vm-size'), help='Master VM size [Default: Standard_D8s_v3]')
        c.argument('worker-vm-size', options_list=('--worker-vm-size'), help='Worker VM size [Default: Standard_D2s_v3]')
        c.argument('worker-vm-disk-size', options_list=('--worker-vm-disk-size'), help='Worker VM disk size in GB [Default: 128]')
        c.argument('worker-count', options_list=('--worker-count'), help='Worker VM Count [Default: 3]')


        # VNET configuration
        c.argument('vnet-resource-group-name', options_list=('--vnet-resource-group-name'), validator=validate_create_parameters,
                   help='Name of the ResourceGroup, where cluster VNET is deployed. If not provided CLI will try to provision one')
        # if vnet rg name is provided we validate if cluster-name-{worker/master} subnets exist, if not
        # we require fags bellow
        c.argument('vnet-name', options_list=('--vnet-name'),
                   help='Name of the vnet inside vnet-rg-name')
        c.argument('vnet-master-subnet-name', options_list=('--vnet-master-subnet-name'),
                   help='Vnet master subnet name')
        c.argument('vnet-worker-subnet-name', options_list=('--vnet-worker-subnet-name'),
                   help='Vnet worker subnet name')

    with self.argument_context('aro update') as c:
        c.argument('location')
        c.argument('resource_name', resource_name_type, options_list=['--name', '-n'])
        c.argument('worker-pool-name', options_list=('--worker-pool-name'), help='Worker VM Pool Name [Default: workers]')
        c.argument('worker-count', options_list=('--worker-count'), help='Worker VM Count [Default: 3]')

    with self.argument_context('aro delete') as c:
        c.argument('resource_name', resource_name_type, options_list=['--name', '-n'])


    with self.argument_context('aro get-credentials') as c:
        c.argument('resource_name', resource_name_type, options_list=['--name', '-n'])

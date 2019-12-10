# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import CLIError

def validate_create_parameters(namespace):
    # mandatory values for create
    if not namespace.resource_name:
        raise CLIError('--name has no value')
    if not namespace.client_id:
        raise CLIError('--client-id has no value')
    if not namespace.client_secret:
        raise CLIError('--client-secret has no value')

    if namespace.location is None:
          raise CLIError('--location has no value')

    if namespace.resource_name == namespace.resource_group_name:
        raise CLIError('cluster name and resource group name can\'t be the same')

    # TODO: Validate our supported limits
    if namespace.worker_count is not None:
        if namespace.worker_count < 1 or namespace.worker_count > 50:
            raise CLIError('--min-count must be in the range [1,50]')

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_aro_preview
from ._format import aro_show_table_format, aro_list_table_format



def load_command_table(self, _):

    aro_preview_sdk = CliCommandType(
        operations_tmpl='azext_aro_preview.vendored_sdks.operations#OpenShiftClustersOperations.{}',
        client_factory=cf_aro_preview)


    with self.command_group('aro', aro_preview_sdk, client_factory=cf_aro_preview) as g:
        g.custom_command('create', 'aro_preview_create', supports_no_wait=True)
        g.custom_command('delete', 'aro_preview_delete', supports_no_wait=True)
        g.custom_command('list', 'aro_preview_list', table_transformer=aro_list_table_format)
        g.custom_show_command('show', 'aro_preview_show', table_transformer=aro_show_table_format)
        g.custom_command('update', 'aro_preview_update')

        g.custom_command('get-credentials', 'aro_preview_get_credentials')

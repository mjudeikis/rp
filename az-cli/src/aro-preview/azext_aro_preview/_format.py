# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------

from collections import OrderedDict
from jmespath import compile as compile_jmes, Options

def aro_show_table_format(result):
    """Format a managed cluster as summary results for display with "-o table"."""
    return [_aro_table_format(result)]

def aro_list_table_format(results):
    """Format a cluster list for display with "-o table"."""
    return [_aro_table_format(r[0]) for r in results.values()]

def _aro_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        provisioningState: provisioningState,
        fqdn: fqdn
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))

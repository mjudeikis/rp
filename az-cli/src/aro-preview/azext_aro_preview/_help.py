# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['aro'] = """
    type: group
    short-summary:  Manage Azure Red Hat OpenShift service.
"""

helps['aro create'] = """
    type: command
    short-summary: Create a aro-preview.
"""

helps['aro list'] = """
    type: command
    short-summary: List aro-previews.
"""

helps['aro delete'] = """
    type: command
    short-summary: Delete a aro-preview.
"""

helps['aro show'] = """
    type: command
    short-summary: Show details of a aro-preview.
"""

helps['aro get-credentials'] = """
    type: command
    short-summary: Get aro-previews cluster credentials
"""

helps['aro update'] = """
    type: command
    short-summary: Update a aro-preview.
"""

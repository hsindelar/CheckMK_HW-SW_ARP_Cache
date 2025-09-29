#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# License: GNU General Public License v2
#
# Author: CheckMK Agent Mode Assistant
# Date: 2025-09-26
#
# WATO Rules for ARP Table Inventory Plugin

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    Integer,
)
from cmk.rulesets.v1.form_specs.validators import NumberInRange
from cmk.rulesets.v1.rule_specs import InventoryParameters, Topic


def _parameter_form_arp_table_inventory():
    return Dictionary(
        elements={
            'max_entries': DictElement(
                parameter_form=Integer(
                    title=Title('Maximum number of ARP entries to show'),
                    help_text=Title(
                        'Limits the number of ARP entries displayed in the inventory '
                        'to avoid performance issues with large ARP tables. '
                        'Set to 0 for unlimited entries.'
                    ),
                    custom_validate=(NumberInRange(min_value=0, max_value=10000),),
                ),
                required=True,
            ),
        },
    )


rule_spec_arp_table_inventory = InventoryParameters(
    name="arp_table_inventory",
    title=Title("ARP Table Inventory"),
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_arp_table_inventory,
    condition=None,
)
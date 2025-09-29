#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# License: GNU General Public License v2
#
# Author: CheckMK Agent Mode Assistant
# Date: 2025-09-26
#
# Web Views for ARP Table Inventory Plugin

from cmk.gui.i18n import _
from cmk.gui.views.inventory.registry import inventory_displayhints

inventory_displayhints.update({
    '.networking.arp_cache.': {
        'title': _('ARP Cache'),
        'keyorder': [
            'total_entries',
            'dynamic_entries',
            'static_entries',
            'other_entries',
            'interfaces_count',
        ],
    },
    '.networking.arp_cache.total_entries': {
        'title': _('Total Entries'),
        'short': _('Total'),
    },
    '.networking.arp_cache.dynamic_entries': {
        'title': _('Dynamic Entries'),
        'short': _('Dynamic'),
    },
    '.networking.arp_cache.static_entries': {
        'title': _('Static Entries'),
        'short': _('Static'),
    },
    '.networking.arp_cache.other_entries': {
        'title': _('Other Entries'),
        'short': _('Other'),
    },
    '.networking.arp_cache.interfaces_count': {
        'title': _('Interfaces Count'),
        'short': _('Interfaces'),
    },
    '.networking.arp_cache.entries:': {
        'title': _('ARP Table Entries'),
        'keyorder': [
            'interface',
            'ip_address',
            'mac_address',
            'entry_type',
        ],
        'icon': 'inv_networking',
    },
    '.networking.arp_cache.entries:*.interface': {
        'title': _('Interface'),
        'short': _('IF'),
    },
    '.networking.arp_cache.entries:*.ip_address': {
        'title': _('IP Address'),
        'short': _('IP'),
    },
    '.networking.arp_cache.entries:*.mac_address': {
        'title': _('MAC Address'),
        'short': _('MAC'),
    },
    '.networking.arp_cache.entries:*.entry_type': {
        'title': _('Entry Type'),
        'short': _('Type'),
    },
})

#!/usr/bin/python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# License: GNU General Public License v2
#
# Author: CheckMK Agent Mode Assistant
# Date: 2025-09-26
#
# ARP Table Inventory Plugin for CheckMK
# Shows ARP cache entries in HW/SW Inventory

from typing import Dict, List, NamedTuple, Any
from cmk.agent_based.v2 import (
    Attributes,
    InventoryPlugin,
    InventoryResult,
    SNMPSection,
    SNMPTree,
    StringByteTable,
    TableRow,
    exists,
)


class ArpEntry(NamedTuple):
    interface_index: str
    ip_address: str
    mac_address: str
    entry_type: str


class ArpTableData(NamedTuple):
    arp_entries: List[ArpEntry]


def parse_arp_table(string_table: List[StringByteTable]) -> ArpTableData:
    """Parse SNMP ARP table data from ipNetToMediaTable"""
    if not string_table or not string_table[0]:
        return ArpTableData(arp_entries=[])
    
    arp_entries = []
    
    # Process each row in the table
    for row in string_table[0]:
        if len(row) >= 4:
            interface_idx = row[0]
            mac_raw = row[1]  
            ip_addr = row[2]
            entry_type_num = row[3]
            
            # Format MAC address and entry type
            mac_addr = format_mac_address_from_snmp(mac_raw)
            entry_type = get_entry_type_name(entry_type_num)
            
            if ip_addr and mac_addr and mac_addr != "00:00:00:00:00:00" and mac_addr != "invalid-mac":
                arp_entries.append(ArpEntry(
                    interface_index=interface_idx,
                    ip_address=ip_addr,
                    mac_address=mac_addr,
                    entry_type=entry_type
                ))
    
    return ArpTableData(arp_entries=arp_entries)


def format_mac_address_from_snmp(mac_raw: str) -> str:
    """Convert MAC address from SNMP binary/string format to standard xx:xx:xx:xx:xx:xx"""
    if not mac_raw:
        return "00:00:00:00:00:00"
    
    # If it is binary data (bytes), convert to hex
    if isinstance(mac_raw, bytes):
        if len(mac_raw) == 6:  # Standard MAC length
            return ":".join(f"{b:02x}" for b in mac_raw)
    
    # Handle string format that might be corrupted by encoding issues
    if isinstance(mac_raw, str):
        # Handle space-separated hex format like "94 2A 6F 0C A9 09 "
        if " " in mac_raw.strip():
            hex_parts = mac_raw.strip().split()
            if len(hex_parts) == 6:
                try:
                    # Convert hex strings to integers and back to formatted hex
                    formatted_parts = []
                    for part in hex_parts:
                        if part:  # Skip empty parts
                            formatted_parts.append(f"{int(part, 16):02x}")
                    if len(formatted_parts) == 6:
                        return ":".join(formatted_parts).lower()
                except ValueError:
                    pass
        
        # Try to get bytes from the string and format as hex
        try:
            # Convert string to bytes and then format as hex
            mac_bytes = mac_raw.encode('latin-1')  # Use latin1 to preserve all byte values
            if len(mac_bytes) == 6:  # Standard MAC length
                return ":".join(f"{b:02x}" for b in mac_bytes)
        except:
            pass
        
        # If it looks like it is already a MAC with colons, fix it
        if ":" in mac_raw:
            parts = mac_raw.split(":")
            if len(parts) == 6:
                # Pad parts that are missing leading zeros
                formatted_parts = []
                for part in parts:
                    # Remove any non-hex characters
                    clean_part = "".join(c for c in part if c in "0123456789abcdefABCDEF")
                    if clean_part:
                        # Pad to 2 digits
                        formatted_parts.append(clean_part.zfill(2)[-2:])  # Take last 2 chars in case of overflow
                    else:
                        formatted_parts.append("00")
                
                if len(formatted_parts) == 6:
                    return ":".join(formatted_parts).lower()
        
        # Last resort: try to extract hex values from the raw string
        try:
            hex_chars = []
            for char in mac_raw:
                hex_chars.append(f"{ord(char):02x}")
            
            if len(hex_chars) == 6:
                return ":".join(hex_chars)
        except:
            pass
    
    return "invalid-mac"  # Return something readable if we cannot parse


def get_entry_type_name(type_num: str) -> str:
    """Convert numeric ARP entry type to readable name"""
    type_mapping = {
        "1": "other",
        "2": "invalid", 
        "3": "dynamic",
        "4": "static"
    }
    return type_mapping.get(type_num, "unknown")


def inventory_arp_table(params: Dict[str, Any], section: ArpTableData) -> InventoryResult:
    """Create inventory data for ARP table"""
    if not section.arp_entries:
        return
    
    # Create summary attributes
    total_entries = len(section.arp_entries)
    dynamic_count = sum(1 for entry in section.arp_entries if entry.entry_type == "dynamic")
    static_count = sum(1 for entry in section.arp_entries if entry.entry_type == "static")
    interfaces = set(entry.interface_index for entry in section.arp_entries)
    
    path = ['networking', 'arp_cache']
    yield Attributes(
        path=path,
        inventory_attributes={
            "total_entries": total_entries,
            "dynamic_entries": dynamic_count,
            "static_entries": static_count,
            "other_entries": total_entries - dynamic_count - static_count,
            "interfaces_count": len(interfaces),
        }
    )
    
    # Create table rows for each ARP entry
    path = path + ['entries']
    max_entries = params.get('max_entries', 1000)  # Limit entries to avoid performance issues
    
    for i, entry in enumerate(section.arp_entries):
        if i >= max_entries:
            break
            
        yield TableRow(
            path=path,
            key_columns={
                "interface": f"Interface {entry.interface_index}",
                "ip_address": entry.ip_address,
            },
            inventory_columns={
                "mac_address": entry.mac_address,
                "entry_type": entry.entry_type,
            }
        )


# SNMP Section Definition
snmp_section_arp_table = SNMPSection(
    name="arp_table",
    parse_function=parse_arp_table,
    detect=exists(".1.3.6.1.2.1.4.22.1.1.*"),  # Check if ipNetToMediaTable exists
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.4.22.1",  # ipNetToMedia table base
            oids=[
                "1",  # ipNetToMediaIfIndex
                "2",  # ipNetToMediaPhysAddress  
                "3",  # ipNetToMediaNetAddress
                "4",  # ipNetToMediaType
            ],
        ),
    ],
)


# Inventory Plugin Definition
inventory_plugin_arp_table = InventoryPlugin(
    name="arp_table",
    sections=["arp_table"],
    inventory_function=inventory_arp_table,
    inventory_default_parameters={
        "max_entries": 1000,  # Maximum number of ARP entries to show in inventory
    },
    inventory_ruleset_name="arp_table_inventory",
)
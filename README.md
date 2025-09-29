# CheckMK ARP Cache Inventory Plugin

A custom CheckMK plugin that displays ARP table information in the Hardware/Software Inventory for network devices.

## What This Plugin Does

Displays network device ARP tables in CheckMK's Hardware/Software Inventory, showing:
- Summary statistics (total/dynamic/static entries)  
- Detailed table with IP addresses, MAC addresses, interfaces, and entry types

## Overview

This plugin collects ARP (Address Resolution Protocol) cache data from network devices via SNMP and displays it in CheckMK's inventory system. It shows both summary statistics and detailed ARP entries with IP addresses, MAC addresses, interfaces, and entry types.

## Features

- **Automatic Detection**: Automatically detects devices with SNMP ARP table support
- **Flexible MAC Parsing**: Handles various MAC address formats
- **Summary Statistics**: Shows total, dynamic, static, and other entry counts
- **Detailed Table**: Displays individual ARP entries with full details
- **Web Interface**: Integrated with CheckMK's web inventory display
- **Configurable**: WATO rules for customizing maximum entries displayed

## Files

1. **`inv_arp_table.py`** - Main inventory plugin
   - Location: `local/lib/python3/cmk_addons/plugins/inventory/agent_based/`
   - Purpose: SNMP data collection, parsing, and inventory generation

2. **`inv_arp_table_rules.py`** - WATO configuration rules
   - Location: `local/lib/python3/cmk_addons/plugins/inventory/rulesets/`
   - Purpose: Web interface configuration options

3. **`inv_arp_table_views.py`** - Web interface display hints
   - Location: `local/share/check_mk/web/plugins/views/`
   - Purpose: Defines how data appears in the web interface

## Installation

### Manual Installation

1. Copy files to the CheckMK site directories:
   ```bash
   # Copy main plugin
   cp inv_arp_table.py /omd/sites/[SITE]/local/lib/python3/cmk_addons/plugins/inventory/agent_based/
   
   # Copy WATO rules
   cp inv_arp_table_rules.py /omd/sites/[SITE]/local/lib/python3/cmk_addons/plugins/inventory/rulesets/
   
   # Copy web views
   cp inv_arp_table_views.py /omd/sites/[SITE]/local/share/check_mk/web/plugins/views/
   ```

2. Set proper permissions:
   ```bash
   chown [SITE]:[SITE] /omd/sites/[SITE]/local/lib/python3/cmk_addons/plugins/inventory/agent_based/inv_arp_table.py
   chown [SITE]:[SITE] /omd/sites/[SITE]/local/lib/python3/cmk_addons/plugins/inventory/rulesets/inv_arp_table_rules.py
   chown [SITE]:[SITE] /omd/sites/[SITE]/local/share/check_mk/web/plugins/views/inv_arp_table_views.py
   ```

3. Restart CheckMK services:
   ```bash
   su - [SITE]
   cmk -R  # Restart core
   omd restart apache  # Restart web interface
   ```

### Kubernetes/Helm Chart Installation

```bash
# Copy files to CheckMK pod
kubectl cp inv_arp_table.py [POD_NAME]:/tmp/inv_arp_table.py -c [CONTAINER_NAME]
kubectl cp inv_arp_table_rules.py [POD_NAME]:/tmp/inv_arp_table_rules.py -c [CONTAINER_NAME]
kubectl cp inv_arp_table_views.py [POD_NAME]:/tmp/inv_arp_table_views.py -c [CONTAINER_NAME]

# Install inside pod
kubectl exec [POD_NAME] -c [CONTAINER_NAME] -- su - [SITE] -c "cp /tmp/inv_arp_table.py local/lib/python3/cmk_addons/plugins/inventory/agent_based/"
kubectl exec [POD_NAME] -c [CONTAINER_NAME] -- su - [SITE] -c "cp /tmp/inv_arp_table_rules.py local/lib/python3/cmk_addons/plugins/inventory/rulesets/"
kubectl exec [POD_NAME] -c [CONTAINER_NAME] -- su - [SITE] -c "cp /tmp/inv_arp_table_views.py local/share/check_mk/web/plugins/views/"

# Restart services
kubectl exec [POD_NAME] -c [CONTAINER_NAME] -- bash -c "su - [SITE] -c 'source .profile && cmk -R && omd restart apache'"
```

## Usage

1. **Automatic Discovery**: The plugin automatically detects devices with ARP tables
2. **Run Inventory**: Execute inventory discovery on target hosts:
   ```bash
   cmk --inventory [HOSTNAME]
   ```
3. **View Results**: Check the inventory in the web interface under:
   - Host → Hardware/Software Inventory → Networking → ARP Cache

## Configuration

Configure the plugin via WATO:
- Go to **Setup** → **Parameters** → **Inventory**
- Look for **"ARP Table Inventory"** rules
- Set **Maximum entries** to limit displayed entries (default: 1000)

## Data Structure

The plugin creates the following inventory structure:

```
networking/
└── arp_cache/
    ├── Attributes:
    │   ├── total_entries      (Total ARP entries)
    │   ├── dynamic_entries    (Dynamic entries count)
    │   ├── static_entries     (Static entries count)
    │   ├── other_entries      (Other types count)
    │   └── interfaces_count   (Number of interfaces)
    └── entries/
        └── Table with rows:
            ├── interface      (Interface name/number)
            ├── ip_address     (IP address)
            ├── mac_address    (MAC address)
            └── entry_type     (dynamic/static/other)
```

## Supported Devices

- **Tested on**: 
  - Ubiquiti UniFi devices (AP, Switch)
  - **Ruckus ICX7150-24F switches** (Production deployment)
  - **Ruckus wireless APs** (Production deployment)
- **Requirements**: SNMP-enabled devices with ipNetToMediaTable (`.1.3.6.1.2.1.4.22`)
- **Compatibility**: Most network devices supporting standard IP-MIB ARP tables

## SNMP Details

- **MIB**: IP-MIB (RFC 4293)
- **Table**: ipNetToMediaTable (`.1.3.6.1.2.1.4.22.1`)
- **OIDs Used**:
  - `.1.3.6.1.2.1.4.22.1.1` - ipNetToMediaIfIndex
  - `.1.3.6.1.2.1.4.22.1.2` - ipNetToMediaPhysAddress
  - `.1.3.6.1.2.1.4.22.1.3` - ipNetToMediaNetAddress
  - `.1.3.6.1.2.1.4.22.1.4` - ipNetToMediaType

## MAC Address Formats Supported

- Standard colon format: `aa:bb:cc:dd:ee:ff`
- Space-separated hex (UniFi): `AA BB CC DD EE FF`
- Binary/raw SNMP data
- Various other formats with automatic conversion

## Entry Types

- **Dynamic (3)**: Learned via ARP protocol
- **Static (4)**: Manually configured entries
- **Other (1)**: Other/unknown types
- **Invalid (2)**: Invalid entries (filtered out)

## Troubleshooting

### Plugin Not Working
1. Check file permissions and locations
2. Verify SNMP access to target devices
3. Test SNMP ARP data availability:
   ```bash
   cmk --snmpwalk --extraoid .1.3.6.1.2.1.4.22 [HOSTNAME]
   ```

### No Data in Inventory
1. Run inventory with debug:
   ```bash
   cmk --debug --inventory -v [HOSTNAME]
   ```
2. Check for "arp_table: ok" in output
3. Verify detection OID exists in SNMP walk

### Web Interface Issues
1. Clear browser cache
2. Restart Apache: `omd restart apache`
3. Check web interface logs for errors

## Example Output

**Summary Attributes:**
- Total Entries: 5
- Dynamic Entries: 5
- Static Entries: 0
- Other Entries: 0
- Interfaces Count: 1

**Table Entries:**
| Interface | IP Address    | MAC Address       | Type    |
|-----------|---------------|-------------------|---------|
| Interface 11 | 192.168.1.1   | 94:2a:6f:0c:a9:09 | dynamic |
| Interface 11 | 192.168.1.2   | e0:d5:5e:2c:8b:04 | dynamic |
| Interface 11 | 192.168.1.220 | ba:c6:30:55:d4:16 | dynamic |

## Development Notes

- Built for CheckMK 2.3+ using Agent API v2
- Follows CheckMK plugin development best practices
- Modular design with separate parsing, inventory, and display components
- Tested with Ubiquiti UniFi devices but should work with most SNMP-enabled network equipment

## License

GNU General Public License v2

## Author

Created using CheckMK Agent Mode Assistant - September 2025

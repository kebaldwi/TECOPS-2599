# 2.0 — Cisco Catalyst Center: Network Settings & Device Credentials Automation

> **Playbook:** `network_settings.yml`  
> **Modules:** `cisco.dnac.network_settings_workflow_manager`, `cisco.dnac.device_credential_workflow_manager`  
> **Minimum Catalyst Center version:** 2.3.7.6  
> **Minimum Ansible version:** 2.15  
> **Authors:** Igor Manassypov — Systems Engineer (imanassy@cisco.com)  
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
   - [Inventory](#inventory)
   - [Vault (Credentials)](#vault-credentials)
6. [Input Data Structure — `settings.json`](#input-data-structure--settingsjson)
   - [Top-Level Schema](#top-level-schema)
   - [The `network_settings` Block](#the-network_settings-block)
   - [The `device_credentials` Block](#the-device_credentials-block)
   - [The `assign_credentials` Block](#the-assign_credentials-block)
   - [Full Example](#full-example)
7. [Playbook Walkthrough — Step by Step](#playbook-walkthrough--step-by-step)
   - [Step 1: Load and Validate Input Data](#step-1-load-and-validate-input-data)
   - [Step 2: Derive Site Names](#step-2-derive-site-names)
   - [Step 3: Build Network Settings Payload](#step-3-build-network-settings-payload)
   - [Step 4: Build Global Credential Payload](#step-4-build-global-credential-payload)
   - [Step 5: Build Credential Assignment Payload](#step-5-build-credential-assignment-payload)
   - [Step 6: Apply Network Settings](#step-6-apply-network-settings)
   - [Step 7: Create/Update Global Device Credentials](#step-7-createupdate-global-device-credentials)
   - [Step 8: Assign Credentials to Sites](#step-8-assign-credentials-to-sites)
   - [Step 9: Summary](#step-9-summary)
8. [Data Transformation Reference](#data-transformation-reference)
9. [Running the Playbook](#running-the-playbook)
10. [Debug Mode](#debug-mode)
11. [Expected Output](#expected-output)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This playbook applies **network infrastructure settings** (DNS, DHCP, NTP, SNMP, Syslog, AAA, banner) to individual sites in Cisco Catalyst Center, and simultaneously manages **global device credentials** (CLI, SNMPv2c, NETCONF) that allow Catalyst Center to communicate with discovered network devices.

Both operations are fully idempotent. If a setting already matches the desired state in CatC, the module will not re-push it.

### What it does

| Action | Module |
|--------|--------|
| Applies DNS, DHCP, NTP, SNMP, Syslog, Banner, NetFlow, AAA per site | `network_settings_workflow_manager` |
| Creates/updates global CLI, SNMPv2c R/O, SNMPv2c R/W, NETCONF credentials | `device_credential_workflow_manager` |
| Assigns global credentials to designated sites | `device_credential_workflow_manager` |

### Playbook ordering dependency

This playbook must run **after** [1.0 — Site Hierarchy](../1.0-Cisco-Catalyst-Center-Site-Hierarchy/README.md). The site paths referenced in `settings.json` must already exist in CatC before network settings can be applied to them.

---

## Prerequisites

| Requirement | Version / Notes |
|-------------|----------------|
| Ansible | >= 2.15 |
| Python | >= 3.9 |
| `dnacentersdk` | >= 2.11.0 |
| `cisco.dnac` collection | 6.46.0 |
| Cisco Catalyst Center | >= 2.3.7.6 |
| Site hierarchy | Must exist (run 1.0 first) |

---

## Directory Structure

```
2.0-Cisco-Catalyst-Center-Settings/
├── ansible.cfg                 # Ansible defaults (inventory path)
├── inventory.yml               # CatC connection + input file path
├── network_settings.yml        # Main playbook
├── vault.yml                   # Ansible Vault encrypted credentials (git-ignored)
├── vault.yml.example           # Plain-text credential template
├── .vault_pass                 # Vault password file (git-ignored, chmod 600)
├── requirements.txt            # Python pip dependencies
└── requirements.yml            # Ansible Galaxy collection dependencies
```

The playbook reads from the shared `settings.json` in the project tree:

```
Projects/
└── BGP_EVPN/
    └── Settings/
        └── settings.json       # Network settings + credentials input data
```

---

## Installation

```bash
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
echo 'your_vault_password' > .vault_pass && chmod 600 .vault_pass
```

---

## Configuration

### Inventory

**File:** `inventory.yml`

```yaml
all:
  hosts:
    catalyst_center:
      ansible_host: localhost
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"

      dnac_host: 198.18.129.100
      dnac_port: 443
      dnac_version: 2.3.7.9
      dnac_verify: false
      dnac_debug: false
      dnac_log: true
      dnac_log_level: INFO

      settings_json_path: "../../../../Projects/BGP_EVPN/Settings/settings.json"
```

| Variable | Purpose |
|----------|---------|
| `settings_json_path` | Path to the `settings.json` input file (relative or absolute) |

### Vault (Credentials)

```bash
cp vault.yml.example vault.yml
ansible-vault encrypt vault.yml --vault-password-file .vault_pass
```

`vault.yml.example`:

```yaml
dnac_username: "admin"
dnac_password: "your_catc_password_here"
```

---

## Input Data Structure — `settings.json`

### Top-Level Schema

```json
{
  "project": [
    {
      "HierarchyArea":   "<area name>",
      "HierarchyBldg":   "<building name or null>",
      "HierarchyFloor":  "<floor name or null>",
      "HierarchyParent": "<parent path>",
      "network_settings":  { ... },
      "device_credentials": { ... },
      "assign_credentials": { ... }
    }
  ]
}
```

The playbook derives the target **site path** from the four `Hierarchy*` fields and applies the three `*_settings`/`*_credentials` blocks to that site.

### Hierarchy Field → Site Path Resolution

The deepest non-null `Hierarchy*` field determines the target site path:

| Condition | Resulting site path |
|-----------|---------------------|
| `HierarchyFloor` is set | `HierarchyParent/HierarchyArea/HierarchyBldg/HierarchyFloor` |
| `HierarchyBldg` is set | `HierarchyParent/HierarchyArea/HierarchyBldg` |
| `HierarchyArea` is set | `HierarchyParent/HierarchyArea` |
| None set | `HierarchyParent` |

**Example:**

```json
{
  "HierarchyParent": "Global/PODS",
  "HierarchyArea":   "POD 0",
  "HierarchyBldg":   "Building P0",
  "HierarchyFloor":  null
}
```

Resolves to: `Global/PODS/POD 0/Building P0`

### The `network_settings` Block

All fields use **module-native snake_case names** and are passed directly to `network_settings_workflow_manager`. Any top-level key whose value is `null` is filtered out before submission to the API.

```json
"network_settings": {
  "dhcp_server":   ["198.18.133.1"],
  "dns_server": {
    "domain_name":          "dcloud.cisco.com",
    "primary_ip_address":   "198.18.133.1",
    "secondary_ip_address": null
  },
  "ntp_server": ["198.18.133.1"],
  "timezone": "America/Toronto",
  "message_of_the_day": {
    "banner_message":       "DNAC Template Lab P0!",
    "retain_existing_banner": false
  },
  "snmp_server": {
    "configure_dnac_ip": true
  },
  "syslog_server": {
    "configure_dnac_ip": true
  },
  "network_aaa": {
    "server_type":              "ISE",
    "primary_server_address":   "198.18.133.27",
    "pan_address":              "198.18.133.27",
    "protocol":                 "RADIUS",
    "secondary_server_address": null
  },
  "client_and_endpoint_aaa": {
    "server_type":              "ISE",
    "primary_server_address":   "198.18.133.27",
    "pan_address":              "198.18.133.27",
    "protocol":                 "RADIUS",
    "shared_secret":            "C1sco12345",
    "secondary_server_address": null
  }
}
```

| Sub-key | Purpose |
|---------|---------|
| `dhcp_server` | List of DHCP server IPs applied at the site |
| `dns_server` | Domain name + primary/secondary DNS |
| `ntp_server` | List of NTP server IPs |
| `timezone` | IANA timezone string for the site |
| `message_of_the_day` | Login banner + retain-existing flag |
| `snmp_server` | SNMP trap/inform configuration (auto-configure CatC IP) |
| `syslog_server` | Syslog destination (auto-configure CatC IP) |
| `network_aaa` | AAA for network device authentication |
| `client_and_endpoint_aaa` | AAA for endpoint/802.1X |

### The `device_credentials` Block

Defines the **global credentials** created in CatC and available to all discovery and provisioning operations. This structure maps directly to the `global_credential_details` schema of `device_credential_workflow_manager`.

```json
"device_credentials": {
  "cli_credential": [
    {
      "description":     "CLI-net-admin",
      "username":        "net-admin",
      "password":        "cisco",
      "enable_password": "cisco"
    }
  ],
  "snmp_v2c_read": [
    { "description": "RO", "read_community": "RO" }
  ],
  "snmp_v2c_write": [
    { "description": "RW", "write_community": "RO" }
  ],
  "netconf_credential": [
    { "description": "NETCONF-netadmin", "netconf_port": "830" }
  ]
}
```

### The `assign_credentials` Block

Associates the global credentials created above with a specific site. Maps directly to the `assign_credentials_to_site` schema.

```json
"assign_credentials": {
  "site_name": ["Global/PODS/POD 0/Building P0"],
  "cli_credential": {
    "description": "CLI-net-admin",
    "username":    "net-admin"
  },
  "snmp_v2c_read":  { "description": "RO" },
  "snmp_v2c_write": { "description": "RW" }
}
```

### Full Example

```json
{
  "project": [
    {
      "HierarchyArea":   "POD 0",
      "HierarchyBldg":   "Building P0",
      "HierarchyFloor":  null,
      "HierarchyParent": "Global/PODS",
      "network_settings": {
        "dhcp_server": ["198.18.133.1"],
        "dns_server": {
          "domain_name":        "dcloud.cisco.com",
          "primary_ip_address": "198.18.133.1"
        },
        "ntp_server":  ["198.18.133.1"],
        "timezone":    "America/Toronto",
        "message_of_the_day": {
          "banner_message":        "BGP EVPN Lab!",
          "retain_existing_banner": false
        },
        "snmp_server":   { "configure_dnac_ip": true },
        "syslog_server": { "configure_dnac_ip": true },
        "network_aaa": {
          "server_type":             "ISE",
          "primary_server_address":  "198.18.133.27",
          "pan_address":             "198.18.133.27",
          "protocol":                "RADIUS"
        },
        "client_and_endpoint_aaa": {
          "server_type":             "ISE",
          "primary_server_address":  "198.18.133.27",
          "pan_address":             "198.18.133.27",
          "protocol":                "RADIUS",
          "shared_secret":           "C1sco12345"
        }
      },
      "device_credentials": {
        "cli_credential":    [{ "description": "CLI-net-admin", "username": "net-admin", "password": "cisco", "enable_password": "cisco" }],
        "snmp_v2c_read":     [{ "description": "RO", "read_community": "RO" }],
        "snmp_v2c_write":    [{ "description": "RW", "write_community": "RO" }],
        "netconf_credential":[{ "description": "NETCONF-netadmin", "netconf_port": "830" }]
      },
      "assign_credentials": {
        "site_name": ["Global/PODS/POD 0/Building P0"],
        "cli_credential":  { "description": "CLI-net-admin", "username": "net-admin" },
        "snmp_v2c_read":   { "description": "RO" },
        "snmp_v2c_write":  { "description": "RW" }
      }
    }
  ]
}
```

---

## Playbook Walkthrough — Step by Step

### Step 1: Load and Validate Input Data

Same pipeline as all playbooks in this suite: `slurp` → `b64decode` → `from_json` → `assert`. See [6.0 README — Step 1](../6.0-Cisco-Catalyst-Center-Network-Profile/README.md#step-1-load-and-validate-input-data) for a detailed explanation.

### Step 2: Derive Site Names

**Purpose:** Build a `site_names` list that maps each `project` entry to its target CatC site path. This list is index-aligned with `settings_data.project` so `site_names[i]` is always the path for `project[i]`.

```jinja2
{%- for entry in settings_data.project -%}
  {%- if entry.HierarchyFloor -%}
    {%- set s = entry.HierarchyParent + '/' + entry.HierarchyArea + '/' + entry.HierarchyBldg + '/' + entry.HierarchyFloor -%}
  {%- elif entry.HierarchyBldg -%}
    {%- set s = entry.HierarchyParent + '/' + entry.HierarchyArea + '/' + entry.HierarchyBldg -%}
  {%- elif entry.HierarchyArea -%}
    {%- set s = entry.HierarchyParent + '/' + entry.HierarchyArea -%}
  {%- else -%}
    {%- set s = entry.HierarchyParent -%}
  {%- endif -%}
  {%- set ns.result = ns.result + [s] -%}
{%- endfor -%}
```

**Transformation example:**

```
Input entry:
  HierarchyParent: "Global/PODS"
  HierarchyArea:   "POD 0"
  HierarchyBldg:   "Building P0"
  HierarchyFloor:  null

Output site_names[0]: "Global/PODS/POD 0/Building P0"
```

### Step 3: Build Network Settings Payload

**Purpose:** Iterate over each entry's `network_settings` block and construct the `network_management_details` payload. The key transformation is **filtering out null values** — the module rejects keys with `null` values for optional fields like `network_aaa`, so they are stripped before submission.

```jinja2
{%- set cfg = entry.network_settings | dict2items
              | selectattr('value', 'ne', None)
              | list | items2dict -%}
```

**Transformation trace:**

```
Input network_settings:
  {
    "dhcp_server": ["198.18.133.1"],
    "dns_server":  { ... },
    "network_aaa": null,          ← filtered out (null)
    "client_and_endpoint_aaa": { ... }
  }

Filter chain:
  dict2items → [{"key": "dhcp_server", "value": [...]}, {"key": "network_aaa", "value": null}, ...]
  selectattr('value', 'ne', None) → removes null entries
  items2dict → {"dhcp_server": [...], "dns_server": {...}, "client_and_endpoint_aaa": {...}}

Output payload item:
  {
    "site_name": "Global/PODS/POD 0/Building P0",
    "settings": {
      "dhcp_server": ["198.18.133.1"],
      "dns_server":  { ... },
      "client_and_endpoint_aaa": { ... }
    }
  }
```

### Step 4: Build Global Credential Payload

**Purpose:** Extract entries that have a non-null `device_credentials` block and wrap each in the `global_credential_details` envelope expected by the module.

```jinja2
{%- if entry.device_credentials -%}
  {%- set ns.result = ns.result + [{'global_credential_details': entry.device_credentials}] -%}
{%- endif -%}
```

**Output example:**

```yaml
credential_list:
  - global_credential_details:
      cli_credential:
        - description: CLI-net-admin
          username: net-admin
          password: cisco
          enable_password: cisco
      snmp_v2c_read:
        - description: RO
          read_community: RO
      snmp_v2c_write:
        - description: RW
          write_community: RO
      netconf_credential:
        - description: NETCONF-netadmin
          netconf_port: "830"
```

### Step 5: Build Credential Assignment Payload

**Purpose:** Extract entries that have a non-null `assign_credentials` block and wrap each in the `assign_credentials_to_site` envelope.

```yaml
credential_assign_list:
  - assign_credentials_to_site:
      site_name:
        - "Global/PODS/POD 0/Building P0"
      cli_credential:
        description: CLI-net-admin
        username: net-admin
      snmp_v2c_read:
        description: RO
      snmp_v2c_write:
        description: RW
```

### Step 6: Apply Network Settings

Loops over `network_settings_list` and calls `cisco.dnac.network_settings_workflow_manager` once per site with `state: merged`.

```yaml
- name: Apply network settings at site "{{ item.site_name }}"
  cisco.dnac.network_settings_workflow_manager:
    state: merged
    config:
      - network_management_details:
          - "{{ item }}"
  loop: "{{ network_settings_list }}"
```

Each iteration targets one site with its filtered settings. Using `loop` instead of batching all sites into a single `config` call gives clearer per-site error messages if one site fails.

### Step 7: Create/Update Global Device Credentials

```yaml
- name: Create/update global device credentials
  cisco.dnac.device_credential_workflow_manager:
    state: merged
    config:
      - "{{ item }}"
  loop: "{{ credential_list }}"
  when: credential_list | length > 0
```

This step is automatically skipped when no entries in the JSON have a `device_credentials` block.

### Step 8: Assign Credentials to Sites

```yaml
- name: Assign credentials to site
  cisco.dnac.device_credential_workflow_manager:
    state: merged
    config:
      - "{{ item }}"
  loop: "{{ credential_assign_list }}"
  when: credential_assign_list | length > 0
```

The `device_credential_workflow_manager` module handles both credential creation (Step 7) and assignment (Step 8) — they are distinguished by the presence of `global_credential_details` vs. `assign_credentials_to_site` in the `config` payload.

### Step 9: Summary

```yaml
- name: Settings synchronization complete
  debug:
    msg:
      - "Network settings applied successfully"
      - "Sites configured: {{ network_settings_list | map(attribute='site_name') | list | join(', ') }}"
      - "Global credential sets created: {{ credential_list | length }}"
      - "Site credential assignments: {{ credential_assign_list | length }}"
```

---

## Data Transformation Reference

```
settings.json
└── project[]
    ├── HierarchyParent/Area/Bldg/Floor fields
    │         │
    │         ▼ Step 2 — deepest non-null path resolution
    │   site_names[i] = "Global/PODS/POD 0/Building P0"
    │
    ├── network_settings (null values filtered)
    │         │
    │         ▼ Step 3 — dict2items | selectattr | items2dict
    │   network_settings_list[i] = {site_name, settings: {...}}
    │
    ├── device_credentials
    │         │
    │         ▼ Step 4 — wrap in global_credential_details
    │   credential_list[i] = {global_credential_details: {...}}
    │
    └── assign_credentials
              │
              ▼ Step 5 — wrap in assign_credentials_to_site
        credential_assign_list[i] = {assign_credentials_to_site: {...}}

              │
              ▼ Steps 6-8 — module calls
    network_settings_workflow_manager  → PUT /dna/intent/api/v1/network/{siteId}
    device_credential_workflow_manager → POST /dna/intent/api/v1/global-credential
    device_credential_workflow_manager → POST /dna/intent/api/v1/credential-to-site/{siteId}
```

---

## Running the Playbook

### Apply settings from the default path

```bash
ansible-playbook network_settings.yml --vault-password-file .vault_pass
```

### Override the input file at runtime

```bash
ansible-playbook network_settings.yml \
  --vault-password-file .vault_pass \
  -e settings_json_path=/absolute/path/to/settings.json
```

### Enable debug output

```bash
DEBUG=true ansible-playbook network_settings.yml --vault-password-file .vault_pass
```

---

## Debug Mode

Set `DEBUG=true` to enable intermediate-variable debug tasks after each build step:

| Debug Task | Shows |
|-----------|-------|
| `--DEBUG-- Site names derived from settings.json` | The `site_names` list |
| `--DEBUG-- Network settings payload list` | The full `network_settings_list` |
| `--DEBUG-- Global credential payload list` | The full `credential_list` |
| `--DEBUG-- Credential assignment payload list` | The full `credential_assign_list` |
| `--DEBUG-- Network settings results` | Raw module return from Step 6 |
| `--DEBUG-- Credential create results` | Raw module return from Step 7 |
| `--DEBUG-- Credential assignment results` | Raw module return from Step 8 |

---

## Expected Output

```
TASK [Validate that project key exists in input data] **************************
ok: [catalyst_center] => { "msg": "Input data loaded — 1 entries found." }

TASK [Validate network settings list is non-empty] *****************************
ok: [catalyst_center] => { "msg": "1 site(s) have settings to apply." }

TASK [Apply network settings at site "Global/PODS/POD 0/Building P0"] **********
changed: [catalyst_center]

TASK [Create/update global device credentials] *********************************
changed: [catalyst_center]

TASK [Assign credentials to site "Global/PODS/POD 0/Building P0"] *************
changed: [catalyst_center]

TASK [Settings synchronization complete] ***************************************
ok: [catalyst_center] => {
    "msg": [
        "Network settings applied successfully",
        "Sites configured: Global/PODS/POD 0/Building P0",
        "Global credential sets created: 1",
        "Site credential assignments: 1"
    ]
}

PLAY RECAP *********************************************************************
catalyst_center : ok=9  changed=3  unreachable=0  failed=0  skipped=2
```

`skipped=2` — credential tasks are skipped when no entries have those blocks.

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Site not found` | Site path does not exist in CatC | Run playbook 1.0 first to create the hierarchy |
| `null value for required field` | A settings sub-key has `null` where CatC expects a value | Remove the key entirely from the JSON (null filtering only removes top-level keys) |
| `Credential already exists` | Same description, different password | Module is idempotent — it will update to the new password |
| `Credential assignment failed` | Credential description not found globally | Ensure Step 7 (credential creation) succeeded before Step 8 runs |
| `AAA shared_secret missing` | `client_and_endpoint_aaa` block has no `shared_secret` | Add `shared_secret` to the `client_and_endpoint_aaa` block |
| `Timezone invalid` | Non-standard timezone string | Use an IANA string, e.g. `America/Toronto`, `UTC`, `America/Los_Angeles` |
| `dnac_version mismatch` | SDK version exceeds appliance version | Set `dnac_version: 2.3.7.9` in `inventory.yml` |
| TLS errors | Self-signed certificate | Set `dnac_verify: false` for lab environments |

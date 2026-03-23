# 3.0 — Cisco Catalyst Center: Device Discovery Automation

> **Playbook:** `device_discovery.yml`  
> **Module:** `cisco.dnac.discovery_workflow_manager`  
> **Minimum Catalyst Center version:** 2.3.7.6  
> **Minimum Ansible version:** 2.15  
> **Authors:** Igor Manassypov — Systems Engineer (imanassy@cisco.com)  
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

---

## Table of Contents

1. [Overview](#overview)
   - [Logical Flow](#logical-flow)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
   - [Inventory](#inventory)
   - [Vault (Credentials)](#vault-credentials)
6. [Input Data Structure — `devices.json`](#input-data-structure--devicesjson)
   - [Top-Level Schema](#top-level-schema)
   - [The `DeviceList` Field](#the-devicelist-field)
   - [Full Example](#full-example)
7. [Playbook Walkthrough — Step by Step](#playbook-walkthrough--step-by-step)
   - [Step 1: Load and Validate Input Data](#step-1-load-and-validate-input-data)
   - [Step 2: Build Discovery Config List](#step-2-build-discovery-config-list)
   - [Step 3: Run Device Discovery](#step-3-run-device-discovery)
   - [Step 4: Summary](#step-4-summary)
8. [Discovery Module Parameters Reference](#discovery-module-parameters-reference)
9. [Data Transformation Reference](#data-transformation-reference)
10. [Running the Playbook](#running-the-playbook)
11. [Debug Mode](#debug-mode)
12. [Expected Output](#expected-output)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This playbook automates **device discovery** in Cisco Catalyst Center. It reads a `devices.json` file, extracts every entry that has a `DeviceList` (a comma-separated list of management IP addresses), and submits one **MULTI RANGE** discovery job per entry to Catalyst Center.

Catalyst Center's discovery engine then attempts to reach each IP using SSH (preferred), Telnet, or HTTPS, validates credentials against the configured global credential set, and adds the reachable devices to the device inventory.

### What it does

| Action | Mechanism |
|--------|-----------|
| Loads and validates input JSON | `lookup('file', path) | from_json` + Jinja2 filters |
| Splits comma-separated IP strings into lists | Jinja2 `split(',')` + `map('trim')` |
| Builds one discovery job config per site entry | `set_fact` with `namespace` |
| Submits all discovery jobs | `cisco.dnac.discovery_workflow_manager` — `state: merged` |

### Logical Flow

The diagram below shows every decision point and state transition from startup to completion:

![Logical Flow](DIAGRAMS/logical-flow.png)

> Source: [`DIAGRAMS/logical-flow.mmd`](DIAGRAMS/logical-flow.mmd) — re-render with `mmdc -i DIAGRAMS/logical-flow.mmd -o DIAGRAMS/logical-flow.png --scale 3`

### Playbook ordering dependency

This playbook should run **after** [2.0 — Settings](../2.0-Cisco-Catalyst-Center-Settings/README.md). Global credentials must exist in CatC before discovery can reference them by description. Discovery does not assign devices to sites — that is handled by [4.0 — Assign To Site](../4.0-Cisco-Catalyst-Center-Assign-To-Site/README.md).

---

## Prerequisites

| Requirement | Version / Notes |
|-------------|----------------|
| Ansible | >= 2.15 |
| Python | >= 3.9 |
| `dnacentersdk` | >= 2.11.0 |
| `cisco.dnac` collection | 6.46.0 |
| Cisco Catalyst Center | >= 2.3.7.6 |
| Global credentials | Must exist in CatC (run 2.0 first) |

---

## Directory Structure

```
3.0-Cisco-Catalyst-Center-Device-Discovery/
├── ansible.cfg                 # Ansible defaults (inventory path)
├── inventory.yml               # CatC connection + input file path
├── device_discovery.yml        # Main playbook
├── vault.yml                   # Ansible Vault encrypted credentials (git-ignored)
├── vault.yml.example           # Plain-text credential template
├── .vault_pass                 # Vault password file (git-ignored, chmod 600)
├── requirements.txt            # Python pip dependencies
├── requirements.yml            # Ansible Galaxy collection dependencies
└── DIAGRAMS/
    ├── logical-flow.mmd        # Mermaid source — re-render with mmdc
    └── logical-flow.png        # Rendered flowchart (referenced by README)
```

Input data comes from the shared `devices.json`:

```
Projects/
└── BGP_EVPN/
    └── Settings/
        └── devices.json        # Site hierarchy + device list data
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

      devices_json_path: "../../../../Projects/BGP_EVPN/Settings/devices.json"
```

| Variable | Purpose |
|----------|---------|
| `devices_json_path` | Relative or absolute path to the `devices.json` input file |

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

## Input Data Structure — `devices.json`

### Top-Level Schema

```json
{
  "project": [
    {
      "HierarchyName": "<full site path>",
      "SiteType":      "<area|building|floor|null>",
      "DeviceList":    "<ip1,ip2,...> or null",
      ...
    }
  ]
}
```

This playbook only processes entries where `DeviceList` is non-null. All other fields are ignored.

### The `DeviceList` Field

`DeviceList` is a **comma-separated string** of management IP addresses (not a JSON array). The playbook splits and trims the string into an `ip_address_list` for the discovery module.

```json
"DeviceList": "198.19.1.1,198.19.1.2,198.19.1.3,198.19.1.4,198.19.1.5,198.19.1.6"
```

**After splitting:**

```yaml
ip_address_list:
  - 198.19.1.1
  - 198.19.1.2
  - 198.19.1.3
  - 198.19.1.4
  - 198.19.1.5
  - 198.19.1.6
```

> Entries where `DeviceList` is `null` (e.g., area or building nodes that have no directly managed devices) are automatically skipped.

### The `HierarchyName` Field and Discovery Job Name

The `HierarchyName` field on each entry is used as the `discovery_name` passed to the module. This name appears in the CatC **Discovery** view and in the discovery job history, making it immediately clear which site the devices were discovered into (e.g. `Global/PODS/POD 0/Building P0`). If `HierarchyName` is absent, it defaults to `"Device-Discovery"`.

### Full Example

```json
{
  "project": [
    {
      "HierarchyName": "Global",
      "SiteType":      null,
      "DeviceList":    null
    },
    {
      "HierarchyName": "Global/PODS",
      "SiteType":      "area",
      "DeviceList":    null
    },
    {
      "HierarchyName": "Global/PODS/POD 0/Building P0",
      "SiteType":      "building",
      "DeviceList":    null
    },
    {
      "HierarchyName": "Global/PODS/POD 0/Building P0/Floor 1",
      "SiteType":      "floor",
      "Project":       "Building P0",
      "DeviceList":    "198.19.1.1,198.19.1.2,198.19.1.3,198.19.1.4,198.19.1.5,198.19.1.6",
      "DayNTemplateNames": [
        {
          "TemplateName":   "BGP-EVPN-BUILD.j2",
          "TemplateTag":    "DEMO",
          "Project":        "Building P0",
          "TemplateTarget": ["198.19.1.1","198.19.1.2","198.19.1.3"],
          "DeployTemplate": true
        }
      ]
    }
  ]
}
```

Only the last entry (Floor 1) has a `DeviceList` — one discovery job will be submitted covering all six IPs.

---

## Playbook Walkthrough — Step by Step

### Step 1: Load and Validate Input Data

The path is resolved to absolute, then `lookup('file', _resolved_json_path) | from_json` reads and parses the JSON in one step. An `assert` task validates the shape before any processing begins.

### Step 2: Build Discovery Config List

**Purpose:** Iterate over `devices_data.project`, extract entries with a non-null `DeviceList`, split the IP string, and build the complete discovery module config dict for each.

```yaml
- name: Build discovery config list
  set_fact:
    discovery_list: >-
      {%- set ns = namespace(result=[]) -%}
      {%- for entry in devices_data.project -%}
        {%- if entry.DeviceList -%}
          {%- set ips = entry.DeviceList.split(',') | map('trim') | list -%}
          {%- set disc = {
            'discovery_name': entry.HierarchyName | default('Device-Discovery'),
            'discovery_type': 'MULTI RANGE',
            'ip_address_list': ips,
            'protocol_order': 'ssh',
            'retry': 5,
            'timeout': 3,
            'preferred_mgmt_ip_method': 'UseLoopBack',
            'discovery_specific_credentials': {
              'net_conf_port': '830'
            },
            'global_credentials': {
              'cli_credentials_list': [{'description': 'CLI-net-admin', 'username': 'net-admin'}],
              'snmp_v2_read_credential_list': [{'description': 'RO'}],
              'snmp_v2_write_credential_list': [{'description': 'RW'}],
              'net_conf_port_list': [{'description': 'NETCONF-net-admin'}]
            }
          } -%}
          {%- set ns.result = ns.result + [disc] -%}
        {%- endif -%}
      {%- endfor -%}
      {{ ns.result }}
```

**Transformation trace:**

```
Input entry:
  HierarchyName: "Global/PODS/POD 0/Building P0/Floor 1"
  DeviceList:    "198.19.1.1,198.19.1.2,198.19.1.3"

Processing:
  1. entry.DeviceList is truthy → enter block
  2. ips = "198.19.1.1,198.19.1.2,198.19.1.3".split(',') | map('trim')
         = ["198.19.1.1", "198.19.1.2", "198.19.1.3"]
  3. Build disc dict (see Discovery Module Parameters below)
  4. Append to ns.result

Output discovery_list[0]:
  {
    "discovery_name":           "Global/PODS/POD 0/Building P0/Floor 1",
    "discovery_type":           "MULTI RANGE",
    "ip_address_list":          ["198.19.1.1", "198.19.1.2", "198.19.1.3"],
    "protocol_order":           "ssh",
    "retry":                    5,
    "timeout":                  3,
    "preferred_mgmt_ip_method": "UseLoopBack",
    "discovery_specific_credentials": {
      "net_conf_port": "830"
    },
    "global_credentials": {
      "cli_credentials_list":           [{"description": "CLI-net-admin", "username": "net-admin"}],
      "snmp_v2_read_credential_list":  [{"description": "RO"}],
      "snmp_v2_write_credential_list": [{"description": "RW"}],
      "net_conf_port_list":            [{"description": "NETCONF-net-admin"}]
    }
  }
```

### Step 3: Run Device Discovery

**Purpose:** Loop over `discovery_list` and submit each job to CatC.

```yaml
- name: "Discover devices"
  cisco.dnac.discovery_workflow_manager:
    state: merged
    config:
      - "{{ item }}"
  loop: "{{ discovery_list }}"
  register: discovery_results
```

Each iteration submits one discovery job. CatC processes the job asynchronously — the module monitors the job status and waits for completion before returning.

#### Credential references, not secrets

The `global_credentials` block in the discovery config contains **description + username** pairs only, not passwords. CatC resolves these references to the actual secrets that were stored when the credentials were created (by playbook 2.0). This prevents credentials from being embedded in the input data file.

```json
"cli_credentials_list": [
  {
    "description": "CLI-net-admin",   ← matches the description set in 2.0
    "username":    "net-admin"        ← used to disambiguate when multiple creds share a description
  }
]
```

### Step 4: Summary

```yaml
- name: Device discovery complete
  debug:
    msg:
      - "Device discovery submitted successfully"
      - "Discovery tasks run: {{ discovery_list | length }}"
      - "Devices targeted: {{ discovery_list | map(attribute='ip_address_list') | flatten | join(', ') }}"
```

The `map(attribute='ip_address_list') | flatten` pattern extracts and flattens the nested IP lists across all discovery jobs into a single comma-separated string for the summary.

---

## Discovery Module Parameters Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| `discovery_type` | `MULTI RANGE` | Treats each IP in the list as an individual target. Use `RANGE` for contiguous subnets or `CDP`/`LLDP` for topology-based discovery. |
| `protocol_order` | `ssh` | Primary protocol for device communication. Can also be `telnet` or `ssh,telnet`. |
| `retry` | `5` | Number of connection retry attempts per device. |
| `timeout` | `3` | Seconds to wait for each connection attempt. |
| `discovery_specific_credentials.net_conf_port` | `830` | NETCONF port number passed to the discovery job. Must be placed under `discovery_specific_credentials` — the module reads it from there (top-level `netconf_port` is silently ignored). |
| `preferred_mgmt_ip_method` | `UseLoopBack` | Prefer loopback interfaces as the management IP. Use `None` to use the discovery IP as-is. |

---

## Data Transformation Reference

```
devices.json
└── project[]
    └── [n].DeviceList  (non-null entries only)
        "198.19.1.1,198.19.1.2, 198.19.1.3"
              │
              ▼ Step 2 — split(',') | map('trim') | list
        ip_address_list = ["198.19.1.1", "198.19.1.2", "198.19.1.3"]
              │
              ▼ Build disc dict
        discovery_list[n] = {
          discovery_name: "Global/PODS/POD 0/Building P0/Floor 1",
          discovery_type: "MULTI RANGE",
          ip_address_list: [...],
          global_credentials: {
            cli_credentials_list: [{"description": "CLI-net-admin", ...}],
            ...
          }
        }
              │
              ▼ Step 3 — loop + module call
        cisco.dnac.discovery_workflow_manager (state: merged)
        → POST /dna/intent/api/v1/discovery
        → GET  /dna/intent/api/v1/discovery/{id}  (poll for completion)
```

**Before — `devices.json` entry:**

```json
{
  "HierarchyName": "Global/PODS/POD 0/Building P0/Floor 1",
  "DeviceList":    "198.19.1.1,198.19.1.2,198.19.1.3,198.19.1.4,198.19.1.5, 198.19.1.6"
}
```

> `DeviceList` is a raw comma-separated string with optional whitespace around entries. The Jinja2 expression `entry.DeviceList.split(',') | map('trim') | list` strips whitespace from each token before building the list. Only entries where `DeviceList` is non-null produce a discovery item.

**After — `discovery_list[0]`** (submitted to `discovery_workflow_manager`):

```json
{
  "discovery_name":              "Global/PODS/POD 0/Building P0/Floor 1",
  "discovery_type":              "MULTI RANGE",
  "ip_address_list":             ["198.19.1.1", "198.19.1.2", "198.19.1.3", "198.19.1.4", "198.19.1.5", "198.19.1.6"],
  "protocol_order":              "ssh",
  "retry":                       5,
  "timeout":                     3,
  "preferred_mgmt_ip_method":    "UseLoopBack",
  "discovery_specific_credentials": { "net_conf_port": "830" },
  "global_credentials": {
    "cli_credentials_list":          [{ "description": "CLI-net-admin", "username": "net-admin" }],
    "snmp_v2_read_credential_list":  [{ "description": "RO" }],
    "snmp_v2_write_credential_list": [{ "description": "RW" }],
    "net_conf_port_list":            [{ "description": "NETCONF-netadmin" }]
  }
}
```

Each `discovery_list` item triggers one `POST /dna/intent/api/v1/discovery` call, after which the module polls `GET /dna/intent/api/v1/discovery/{id}` until the job reaches a terminal state and reports per-IP reachability.

---

## Running the Playbook

### Discover devices using the default input file

```bash
ansible-playbook device_discovery.yml --vault-password-file .vault_pass
```

### Override the input file at runtime

```bash
ansible-playbook device_discovery.yml \
  --vault-password-file .vault_pass \
  -e devices_json_path=/absolute/path/to/devices.json
```

### Discover only specific devices (inline override)

```bash
ansible-playbook device_discovery.yml \
  --vault-password-file .vault_pass \
  -e devices_json_path=../../../../Projects/TRADITIONAL/Settings/devices.json
```

---

## Debug Mode

```bash
DEBUG=true ansible-playbook device_discovery.yml --vault-password-file .vault_pass
```

Prints:
- `discovery_list` — the fully built config list before any API calls
- `discovery_results` — raw module return including job IDs and reachability details

---

## Expected Output

```
TASK [Validate that project key exists in input data] **************************
ok: [catalyst_center] => { "msg": "Input data loaded — 5 entries found." }

TASK [Validate discovery list is non-empty] ************************************
ok: [catalyst_center] => { "msg": "1 discovery task(s) to run." }

TASK [Discover devices] ********************************************************
changed: [catalyst_center]

TASK [Device discovery complete] ***********************************************
ok: [catalyst_center] => {
    "msg": [
        "Device discovery submitted successfully",
        "Discovery tasks run: 1",
        "Devices targeted: 198.19.1.1, 198.19.1.2, 198.19.1.3, 198.19.1.4, 198.19.1.5, 198.19.1.6"
    ]
}

PLAY RECAP *********************************************************************
catalyst_center : ok=6  changed=1  unreachable=0  failed=0  skipped=1
```

After discovery completes, devices appear in **CatC → Provision → Inventory** with status `Reachable`. They are not yet assigned to a site — proceed with [4.0 — Assign To Site](../4.0-Cisco-Catalyst-Center-Assign-To-Site/README.md).

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `No entries with DeviceList found` | All entries have `null` DeviceList | Add IP addresses to the `DeviceList` field in the JSON |
| `Global credential not found` | CLI/SNMP/NETCONF credential description not in CatC | Run playbook 2.0 first to create global credentials |
| Discovery job stuck / times out | Devices unreachable from CatC | Verify IP reachability: `ping` from the CatC appliance to the device IPs |
| Devices show `Unreachable` | Wrong credentials or SSH not enabled | Verify CLI credentials in playbook 2.0 match the device configuration |
| `NETCONF connection refused` | NETCONF not enabled on device | Configure `netconf-yang` on the device, or remove the NETCONF credential from the discovery config |
| Duplicate discovery job name | Multiple entries have the same `HierarchyName` | Each `HierarchyName` must be unique — discovery job names are derived from it |
| `dnac_version mismatch` | SDK version exceeds appliance version | Set `dnac_version: 2.3.7.9` in `inventory.yml` |
| TLS errors | Self-signed certificate | Set `dnac_verify: false` for lab environments |

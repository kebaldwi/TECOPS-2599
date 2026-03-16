# 1.0 — Cisco Catalyst Center: Site Hierarchy Automation

> **Playbook:** `site_hierarchy.yml`  
> **Module:** `cisco.dnac.site_workflow_manager`  
> **Minimum Catalyst Center version:** 2.3.7.6  
> **Minimum Ansible version:** 2.14  
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
6. [Input Data Structure — `devices.json`](#input-data-structure--devicesjson)
   - [Top-Level Schema](#top-level-schema)
   - [Field Reference](#field-reference)
   - [Type-Specific Fields](#type-specific-fields)
   - [Full Example](#full-example)
7. [Playbook Walkthrough — Step by Step](#playbook-walkthrough--step-by-step)
   - [Step 1: Load and Validate Input Data](#step-1-load-and-validate-input-data)
   - [Step 2: Build Lookup Maps](#step-2-build-lookup-maps)
   - [Step 3: Generate All Unique Paths](#step-3-generate-all-unique-paths)
   - [Step 4: Create or Delete Sites](#step-4-create-or-delete-sites)
8. [Data Transformation Reference](#data-transformation-reference)
9. [Running the Playbook](#running-the-playbook)
10. [Debug Mode](#debug-mode)
11. [Expected Output](#expected-output)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This playbook automates the creation and management of the **Site Hierarchy** in Cisco Catalyst Center (formerly DNA Center). The site hierarchy organises network locations into a tree of **Areas**, **Buildings**, and **Floors** — the fundamental grouping structure that all other automation (settings, discovery, templates, and profiles) relies upon.

The playbook is data-driven and fully **idempotent**: it reads a `devices.json` file, derives every required path (including intermediate parent nodes), sorts them from shallowest to deepest, and calls `cisco.dnac.site_workflow_manager` in order — guaranteeing that parent sites always exist before children are created. Re-running the playbook makes no changes if the hierarchy already matches.

### What it does

| Action | Mechanism |
|--------|-----------|
| Loads and validates input JSON | `ansible.builtin.slurp` + Jinja2 filters |
| Builds type/metadata lookup maps | `set_fact` with dict comprehension |
| Expands all intermediate paths | Jinja2 path-splitting loop |
| Sorts paths shallow-first | Depth-bucketing sort |
| Creates areas, buildings, floors | `state: merged` |
| Deletes in reverse order (children first) | `state: deleted` with reversed list |

---

## Prerequisites

| Requirement | Version / Notes |
|-------------|----------------|
| Ansible | >= 2.14 |
| Python | >= 3.9 |
| `dnacentersdk` | >= 2.11.0 |
| `cisco.dnac` collection | 6.46.0 |
| Cisco Catalyst Center | >= 2.3.7.6 (for `floor_number` support) |

> **Note:** `floor_number` is a mandatory field in the `site_workflow_manager` module from CatC API version 2.3.7.6 onwards. Earlier versions will reject floor creation without it.

---

## Directory Structure

```
1.0-Cisco-Catalyst-Center-Site-Hierarchy/
├── ansible.cfg                 # Ansible defaults (inventory path)
├── inventory.yml               # CatC connection + default building/floor values
├── site_hierarchy.yml          # Main playbook
├── site_input.json.example     # Example input file (devices.json format)
├── vault.yml                   # Ansible Vault encrypted credentials (git-ignored)
├── vault.yml.example           # Plain-text credential template
├── .vault_pass                 # Vault password file (git-ignored, chmod 600)
├── requirements.txt            # Python pip dependencies
└── requirements.yml            # Ansible Galaxy collection dependencies
```

The playbook references `devices.json` from the project tree by default:

```
Projects/
└── BGP_EVPN/
    └── Settings/
        └── devices.json        # Site hierarchy + device assignment input data
```

---

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ansible collections

```bash
ansible-galaxy collection install -r requirements.yml
```

### 3. Set up the vault password file

```bash
echo 'your_vault_password' > .vault_pass
chmod 600 .vault_pass
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

      # Catalyst Center connection
      dnac_host: 198.18.129.100
      dnac_port: 443
      dnac_version: 2.3.7.9
      dnac_verify: false

      # Input file path (relative or absolute)
      devices_json_path: "site_input.json"

      # Building defaults — applied when JSON entry omits these fields
      default_building_address:   "1 Cisco Way, San Jose, CA 95134"
      default_building_country:   "United States"
      default_building_latitude:  37.3382
      default_building_longitude: -121.8863

      # Floor defaults — applied when JSON entry omits these fields
      default_floor_rf_model:  "Cubes And Walled Offices"
      default_floor_width:     100
      default_floor_length:    100
      default_floor_height:    10
      default_floor_number:    1
```

| Variable | Purpose |
|----------|---------|
| `devices_json_path` | Relative or absolute path to the input JSON file |
| `default_building_*` | Fallback values for buildings with no address/coordinate data |
| `default_floor_*` | Fallback values for floors with no dimension data |

### Vault (Credentials)

```bash
cp vault.yml.example vault.yml
ansible-vault encrypt vault.yml --vault-password-file .vault_pass
```

`vault.yml.example` contains:

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
    { /* site entry — Global root */ },
    { /* site entry — area      */ },
    { /* site entry — building  */ },
    { /* site entry — floor     */ }
  ]
}
```

Every entry in the `project` array represents exactly **one node** in the site hierarchy. The playbook uses only the hierarchy-related fields; all other keys (`DeviceList`, `NetworkProfile`, template arrays) are ignored by this playbook.

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `HierarchyName` | string | **Yes** | Full `/`-delimited path from `Global` to this node, e.g. `Global/PODS/POD 0/Building P0/Floor 1` |
| `SiteType` | string or null | **Yes** | `area`, `building`, or `floor`. `null` for the root `Global` entry (skipped). |
| `address` | string | Building only | Civic address. Falls back to `default_building_address`. |
| `country` | string | Building only | Country name. Falls back to `default_building_country`. |
| `latitude` | float | Building only | GPS latitude. Falls back to `default_building_latitude`. |
| `longitude` | float | Building only | GPS longitude. Falls back to `default_building_longitude`. |
| `rf_model` | string | Floor only | RF environment model (see CatC UI for valid values). Falls back to `default_floor_rf_model`. |
| `width` | int | Floor only | Floor width in feet. Falls back to `default_floor_width`. |
| `length` | int | Floor only | Floor length in feet. Falls back to `default_floor_length`. |
| `height` | int | Floor only | Ceiling height in feet. Falls back to `default_floor_height`. |
| `floor_number` | int | Floor only | Floor number (required by CatC ≥ 2.3.7.6). Falls back to `default_floor_number`. |

> **Valid `rf_model` values:** `Cubes And Walled Offices`, `Drywall Office Only`, `Indoor High Ceiling`, `Outdoor Open Space`, `Free Space`, `Sparse`, `Very Sparse`

### Intermediate Node Requirement

Every **ancestor** in the path must have its own entry in `project`. The playbook expands leaf paths into all their sub-paths and deduplicates, but it relies on the JSON to declare the `SiteType` of each ancestor.

If you omit an intermediate node its type cannot be determined and site creation will fail.

**Correct** — all levels declared:

```json
{ "HierarchyName": "Global/PODS",                           "SiteType": "area"     },
{ "HierarchyName": "Global/PODS/POD 0",                     "SiteType": "area"     },
{ "HierarchyName": "Global/PODS/POD 0/Building P0",         "SiteType": "building" },
{ "HierarchyName": "Global/PODS/POD 0/Building P0/Floor 1", "SiteType": "floor"    }
```

**Incorrect** — `Global/PODS/POD 0` is missing, playbook cannot determine its type:

```json
{ "HierarchyName": "Global/PODS",                           "SiteType": "area"     },
{ "HierarchyName": "Global/PODS/POD 0/Building P0",         "SiteType": "building" }
```

### Full Example

```json
{
  "project": [
    {
      "HierarchyName": "Global",
      "SiteType": null,
      "DeviceList": null
    },
    {
      "HierarchyName": "Global/ONTARIO",
      "SiteType": "area",
      "DeviceList": null
    },
    {
      "HierarchyName": "Global/ONTARIO/OSHAWA",
      "SiteType": "area",
      "DeviceList": null
    },
    {
      "HierarchyName": "Global/ONTARIO/OSHAWA/HOME",
      "SiteType": "building",
      "address": "100 King St W, Oshawa, ON L1H 1B5, Canada",
      "country": "Canada",
      "latitude": 43.8971,
      "longitude": -78.8658,
      "DeviceList": null
    },
    {
      "HierarchyName": "Global/ONTARIO/OSHAWA/HOME/FLOOR 1",
      "SiteType": "floor",
      "rf_model": "Cubes And Walled Offices",
      "width": 200,
      "length": 150,
      "height": 10,
      "floor_number": 1,
      "DeviceList": "10.1.1.10"
    }
  ]
}
```

---

## Playbook Walkthrough — Step by Step

### Step 1: Load and Validate Input Data

Identical to the pattern used across all playbooks in this suite. `ansible.builtin.slurp` reads the file, `b64decode` decodes it, and `from_json` parses it into an Ansible variable. An `assert` task validates the shape before any processing begins. See [6.0 README — Step 1](../6.0-Cisco-Catalyst-Center-Network-Profile/README.md#step-1-load-and-validate-input-data) for a full explanation of this pipeline.

### Step 2: Build Lookup Maps

**Purpose:** Iterate over `project` once and build three dictionaries keyed by `HierarchyName` for O(1) lookup when constructing the per-site API payload in Step 4.

Three maps are built in a single `set_fact`:

| Map | Keys | Values |
|-----|------|--------|
| `site_type_map` | `HierarchyName` paths | `"area"` / `"building"` / `"floor"` |
| `building_info_map` | Building paths | `{address, country, latitude, longitude}` |
| `floor_info_map` | Floor paths | `{rf_model, width, length, height, floor_number}` |

**Example — input entry:**

```json
{
  "HierarchyName": "Global/PODS/POD 0/Building P0/Floor 1",
  "SiteType": "floor",
  "rf_model": "Cubes And Walled Offices",
  "width": 100,
  "length": 100,
  "height": 10,
  "floor_number": 1
}
```

**Example — resulting map entries:**

```
site_type_map["Global/PODS/POD 0/Building P0/Floor 1"] = "floor"

floor_info_map["Global/PODS/POD 0/Building P0/Floor 1"] = {
  "rf_model":     "Cubes And Walled Offices",
  "width":        100,
  "length":       100,
  "height":       10,
  "floor_number": 1
}
```

Missing optional fields fall back to inventory variable defaults (e.g., `default_floor_rf_model`, `default_floor_width`) via Jinja2's `| default(...)` filter.

### Step 3: Generate All Unique Paths

**Purpose:** Expand every `HierarchyName` leaf path into all its ancestor sub-paths, deduplicate, and sort from shallowest to deepest so the API never receives a child before its parent.

**Algorithm:**

```
For each HierarchyName in project:
  For each depth d from 2 to len(parts):
    emit parts[:d] | join('/')   → one sub-path per depth level

Deduplicate all emitted paths.
Sort by depth (bucket sort: d=2 first, then d=3, ..., d=19).
```

**Example — single leaf path expanded:**

```
Input:  "Global/PODS/POD 0/Building P0/Floor 1"

Emits:
  depth 2 → "Global/PODS"
  depth 3 → "Global/PODS/POD 0"
  depth 4 → "Global/PODS/POD 0/Building P0"
  depth 5 → "Global/PODS/POD 0/Building P0/Floor 1"
```

**Result (`all_site_paths`):**

```yaml
- Global/PODS
- Global/PODS/POD 0
- Global/PODS/POD 0/Building P0
- Global/PODS/POD 0/Building P0/Floor 1
```

Note that `Global` (depth 1) is always skipped — it is the CatC root and pre-exists by definition.

### Step 4: Create or Delete Sites

**Purpose:** Loop over `all_site_paths` (or its reverse for deletion), build the typed site config dict for each path, and call `cisco.dnac.site_workflow_manager`.

Two mutually exclusive tasks run based on the `state` variable (default: `merged`):

| `state` value | Loop order | Effect |
|---------------|------------|--------|
| `merged` | Shallow → deep (parents first) | Creates/updates sites |
| `deleted` | Deep → shallow (children first) | Deletes sites |

**Per-path config construction:**

```
path = "Global/PODS/POD 0/Building P0/Floor 1"

1. Split path → parts = ["Global", "PODS", "POD 0", "Building P0", "Floor 1"]
2. parent_name = parts[:-1] | join("/")  → "Global/PODS/POD 0/Building P0"
3. site_name   = parts[-1]               → "Floor 1"
4. site_type   = site_type_map[path]     → "floor"
5. metadata    = floor_info_map[path]    → {rf_model, width, length, height, floor_number}

6. Build config dict:
{
  "site_type": "floor",
  "site": {
    "floor": {
      "name":         "Floor 1",
      "parent_name":  "Global/PODS/POD 0/Building P0",
      "rf_model":     "Cubes And Walled Offices",
      "width":        100,
      "length":       100,
      "height":       10,
      "floor_number": 1
    }
  }
}
```

This dict is passed directly to `cisco.dnac.site_workflow_manager` as the `config` value.

---

## Data Transformation Reference

```
devices.json
└── project[]
    └── [n].HierarchyName + SiteType + metadata
              │
              ▼ Step 2 — set_fact (3 maps)
    site_type_map    = { "Global/.../.../Floor 1": "floor", ... }
    building_info_map = { "Global/.../Building":  {address, ...}, ... }
    floor_info_map   = { "Global/.../Floor 1":   {rf_model, ...}, ... }
              │
              ▼ Step 3 — path expansion + dedup + depth sort
    all_site_paths = [
      "Global/PODS",
      "Global/PODS/POD 0",
      "Global/PODS/POD 0/Building P0",
      "Global/PODS/POD 0/Building P0/Floor 1"
    ]
              │
              ▼ Step 4 — per-path config build + module call
    cisco.dnac.site_workflow_manager (state: merged)
    ├── POST /dna/intent/api/v1/site  (area)
    ├── POST /dna/intent/api/v1/site  (building)
    └── POST /dna/intent/api/v1/site  (floor)
```

---

## Running the Playbook

### Create hierarchy (default)

```bash
ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass
```

### Use the shared BGP_EVPN devices.json

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e devices_json_path=../../../../Projects/BGP_EVPN/Settings/devices.json
```

### Use an absolute or custom path

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e devices_json_path=/absolute/path/to/devices.json
```

### Override building/floor defaults at runtime

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e default_building_country=Canada \
  -e "default_building_address='100 King St W, Toronto, ON'"
```

### Delete the entire hierarchy (children first)

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e state=deleted
```

> **Warning:** Deletion will fail if devices are still assigned to any site. Run playbook 4.0 with `state=deleted` first to unassign devices, or reassign them in CatC UI.

---

## Debug Mode

```bash
DEBUG=true ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass
```

Enables additional tasks that print:
- The ordered `all_site_paths` list before any API calls
- Each per-site config dict as it is built

---

## Expected Output

```
TASK [Validate that project key exists in input data] **************************
ok: [catalyst_center] => { "msg": "Input data loaded — 5 entries found." }

TASK [Display site paths to be provisioned (4 total)] **************************
ok: [catalyst_center] => {
    "msg": [
        "Global/PODS",
        "Global/PODS/POD 0",
        "Global/PODS/POD 0/Building P0",
        "Global/PODS/POD 0/Building P0/Floor 1"
    ]
}

TASK [Create site ...] *********************************************************
changed: [catalyst_center] => (item=Global/PODS)
changed: [catalyst_center] => (item=Global/PODS/POD 0)
changed: [catalyst_center] => (item=Global/PODS/POD 0/Building P0)
changed: [catalyst_center] => (item=Global/PODS/POD 0/Building P0/Floor 1)

PLAY RECAP *********************************************************************
catalyst_center : ok=7  changed=1  unreachable=0  failed=0  skipped=0
```

On subsequent runs the module task will show `changed=0` (idempotent).

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Authentication failed` | Wrong credentials in `vault.yml` | Re-edit `vault.yml` and verify username/password |
| `name/parent_name should not be None` | `SiteType` missing from a JSON entry | Add explicit `SiteType` to every non-null entry |
| `country should not be None` | Building has no `country` field | Add `country` to the JSON entry or set `default_building_country` |
| `floor_number` validation error | CatC ≥ 2.3.7.6 requires this field | Add `floor_number` to each floor entry or set `default_floor_number` |
| `Parent site not found` | Intermediate node missing from JSON | Ensure every ancestor path has its own entry with a `SiteType` |
| `Cannot delete — site has children` | Trying to delete parent before child | Use `state=deleted` (auto-reverses order), or delete manually from deepest level up |
| `dnac_version mismatch warning` | SDK version higher than appliance | Set `dnac_version: 2.3.7.9` (highest known SDK version) |
| `Collection not found` | `cisco.dnac` not installed | Run `ansible-galaxy collection install -r requirements.yml` |
| TLS/SSL errors | Self-signed certificate | Set `dnac_verify: false` for lab; use valid cert in production |
├── site_hierarchy.yml       # Main playbook
├── site_input.json.example  # Example input file (devices.json format)
├── vault.yml.example        # Credential template
├── vault.yml                # Encrypted credentials (ansible-vault, not committed)
└── .vault_pass              # Vault password file (not committed)
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.9+ |
| Ansible | 2.14+ |
| `cisco.dnac` collection | 6.x (supports CatC 2.3.7) |

Install the required collection:

```bash
ansible-galaxy collection install cisco.dnac
```

---

## Credentials Setup

```bash
# 1. Copy the credential template
cp vault.yml.example vault.yml

# 2. Edit with your Catalyst Center credentials
#    Set: dnac_username, dnac_password

# 3. Create a vault password file
echo "your_vault_password" > .vault_pass
chmod 600 .vault_pass

# 4. Encrypt
ansible-vault encrypt vault.yml --vault-password-file .vault_pass
```

---

## Input File Format

The playbook accepts a JSON file with the same structure as `devices.json` used across the Projects folder. The key field is `HierarchyName` — a `/`-separated path from `Global` down to the target site.

### Required Fields (all entries)

| Field | Description |
|-------|-------------|
| `HierarchyName` | Full path from `Global`, e.g. `Global/ONTARIO/OSHAWA/HOME/FLOOR 1` |
| `SiteType` | `area`, `building`, or `floor` — must be declared explicitly on every entry |

### Optional Fields (per SiteType)

**For `building`:**

| Field | Default (from `inventory.yml`) |
|-------|--------------------------------|
| `address` | `default_building_address` |
| `country` | `default_building_country` |
| `latitude` | `default_building_latitude` |
| `longitude` | `default_building_longitude` |

**For `floor`:**

| Field | Default (from `inventory.yml`) |
|-------|--------------------------------|
| `rf_model` | `default_floor_rf_model` |
| `width` | `default_floor_width` |
| `length` | `default_floor_length` |
| `height` | `default_floor_height` |
| `floor_number` | `default_floor_number` (required by CatC ≥ 2.3.7.6) |

> **Note:** Field names follow the `cisco.dnac` module's snake_case convention: `rf_model` not `rfModel`, `floor_number` not `floorNumber`.

### Site Type Resolution

The playbook resolves the type for each path in this priority order:

1. **Explicit `SiteType`** in the JSON entry matching the path — this is the expected and recommended approach
2. **Name pattern inference (fallback)** — if no `SiteType` is present on a path, the site name is matched against patterns:
   - Starts with `FLOOR`, `FL `, `FL-`, `FL_`, or `F<digit>` → `floor`
   - Starts with `BUILDING` or `BLDG` → `building`
   - Anything else → `area`

> **Best practice:** Declare `SiteType` explicitly on every entry. The inference fallback exists as a safety net but buildings typed by inference will still fall back to inventory defaults for address/coordinates.

### Intermediate Nodes

All ancestor paths **must** be present in the JSON with their own `SiteType`. The playbook deduplicates paths across all entries and guarantees parents are created before children by sorting paths by depth.

For example, to create `Global/PODS/POD 0/Building P0/Floor 1`, the input must include an entry for each level:

```json
{ "HierarchyName": "Global/PODS",                          "SiteType": "area"     },
{ "HierarchyName": "Global/PODS/POD 0",                    "SiteType": "area"     },
{ "HierarchyName": "Global/PODS/POD 0/Building P0",        "SiteType": "building" },
{ "HierarchyName": "Global/PODS/POD 0/Building P0/Floor 1","SiteType": "floor"    }
```

### Example Input File

See `site_input.json.example` for a complete reference. Abbreviated form:

```json
{
    "project": [
        {
            "HierarchyName": "Global/ONTARIO",
            "SiteType": "area",
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [...],
            "DayNTemplateNames": [...]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/HOME",
            "SiteType": "building",
            "address": "100 King St W, Oshawa, ON L1H 1B5, Canada",
            "country": "Canada",
            "latitude": 43.8971,
            "longitude": -78.8658,
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [...],
            "DayNTemplateNames": [...]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/HOME/FLOOR 1",
            "SiteType": "floor",
            "rf_model": "Cubes And Walled Offices",
            "width": 200,
            "length": 150,
            "height": 10,
            "floor_number": 1,
            "DeviceList": "10.1.1.10",
            "NetworkProfile": null,
            "Day0TemplateNames": [...],
            "DayNTemplateNames": [...]
        }
    ]
}
```

---

## Running the Playbook

**Build or update site hierarchy from the default input file:**

```bash
ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass
```

**Use a custom input file:**

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e devices_json_path=/path/to/your/devices.json
```

**Use the TRADITIONAL/Settings/devices.json directly:**

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e "devices_json_path=../../../../Projects/TRADITIONAL/Settings/devices.json"
```

**Use the BGP_EVPN/Settings/devices.json directly:**

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e "devices_json_path=../../../../Projects/BGP_EVPN/Settings/devices.json"
```

**Dry run (check mode — no changes made to CatC):**

```bash
ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass --check
```

**Override building/floor defaults at runtime:**

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e "default_building_address='123 Main St, Toronto, ON'" \
  -e "default_building_country='Canada'" \
  -e "default_floor_rf_model='Drywall Office Only'"
```

**Delete the site hierarchy:**

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e "state=deleted"
```

With a specific input file:

```bash
ansible-playbook site_hierarchy.yml \
  --vault-password-file .vault_pass \
  -e "state=deleted" \
  -e "devices_json_path=../../../../Projects/BGP_EVPN/Settings/devices.json"
```

> **Important:** The playbook automatically reverses the site order when `state=deleted`, deleting children before their parents so CatC never tries to remove a site that still has children. Ensure no devices are assigned to any of the sites before running with `state=deleted`.

## How It Works

```
1. Load devices.json
        │
        ▼
2. Build lookup maps
   site_type_map / building_info_map / floor_info_map
        │
        ▼
3. Collect all unique paths across all HierarchyName entries
   Deduplicate, then sort by depth — parents first
        │
        ▼
4. Pre-compute config payload list (one dict per path)
   ├── Resolve type from site_type_map (fallback: name-pattern inference)
   ├── Merge metadata from building_info_map / floor_info_map
   │   (or fall back to inventory defaults)
   └── Build typed dict: { site_type, site: { <type>: { name, parent_name, ... } } }
        │
        ▼
5. Loop over payload list — call cisco.dnac.site_workflow_manager (state: merged)
        │
        ▼
6. Summary
```

---

## Catalyst Center Configuration

Edit `inventory.yml` to point to your CatC instance:

```yaml
dnac_host: dnac.dcloud.cisco.com   # CatC FQDN or IP
dnac_version: 2.3.7.6              # Must match your CatC version exactly
dnac_verify: false                 # Set true in production with a valid cert
```

Default values applied when the JSON entry omits optional fields:

```yaml
default_building_address:   "1 Cisco Way, San Jose, CA 95134"
default_building_country:   "United States"
default_building_latitude:  37.3382
default_building_longitude: -121.8863

default_floor_rf_model:  "Cubes And Walled Offices"
default_floor_width:     100
default_floor_length:    100
default_floor_height:    10
default_floor_number:    1
```

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Authentication failed` | Wrong credentials | Re-edit `vault.yml` and verify username/password |
| `name/parent_name should not be None` | `SiteType` missing from a JSON entry | Add explicit `SiteType` to every entry in the input file |
| `country should not be None` | Building entry has no `country` field and no default | Add `country` to the JSON entry or set `default_building_country` in `inventory.yml` |
| `floor_number` error | Required in CatC ≥ 2.3.7.6 | Add `floor_number` to the floor entry or ensure `default_floor_number` is set |
| `Parent site not found` | Out-of-order creation | Should not occur — playbook sorts by depth. Verify all intermediate paths have entries in the JSON |
| `Building type requires address` | `SiteType: building` with no address and no default | Set `address`, `latitude`, `longitude`, `country` in the JSON entry or inventory defaults |
| `Collection not found` | Missing `cisco.dnac` | Run `ansible-galaxy collection install cisco.dnac` |
| `dnac_version mismatch` | Version string wrong | Set `dnac_version: 2.3.7.6` in `inventory.yml` |

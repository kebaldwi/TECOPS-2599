# 1.0 — Cisco Catalyst Center: Site Hierarchy Automation

> **Playbook:** `site_hierarchy.yml`  
> **Modules:** `cisco.catalystcenter.areas`, `.buildings`, `.floors`, `.sites_info`  
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

This playbook automates the creation and management of the **Site Hierarchy** in Cisco Catalyst Center. The site hierarchy organises network locations into a tree of **Areas**, **Buildings**, and **Floors** — the fundamental grouping structure that all other automation (settings, discovery, templates, and profiles) relies upon.

The playbook is data-driven and reads a `devices.json` file, derives every required path (including intermediate parent nodes), sorts them from shallowest to deepest, and calls individual `cisco.catalystcenter` modules in order — guaranteeing that parent sites always exist before children are created.

> **Why individual modules instead of `site_workflow_manager`?**  
> `cisco.catalystcenter` is the current, actively maintained collection (replaces the legacy `cisco.dnac`). Individual modules expose every API call explicitly — which API endpoint fires, which UUID is required as `parentId`, and why the create/update/delete split exists. This transparency makes the playbook ideal for **lab and teaching scenarios**.

### What it does

| Action | Mechanism |
|--------|-----------|
| Loads and validates input JSON | `lookup('file', path) \| from_json` + Jinja2 filters |
| Builds type/metadata lookup maps | `set_fact` with dict comprehension |
| Expands all intermediate paths | Jinja2 path-splitting loop |
| Sorts paths shallow-first | Depth-bucketing sort |
| Resolves existing site UUIDs | `sites_info` → `site_id_map` (Phase A) |
| Creates areas, buildings, floors | `state: present` without `id:` (Phase B) |
| Updates existing sites | `state: present` with `id:` (Phase B) |
| Deletes in reverse order (children first) | `state: absent` with `id:` (Phase C) |

### Logical Flow

The diagram below shows every decision point and state transition from startup to completion:

![Logical Flow](DIAGRAMS/logical-flow.png)

> Source: [`DIAGRAMS/logical-flow.mmd`](DIAGRAMS/logical-flow.mmd) — re-render with `mmdc -i DIAGRAMS/logical-flow.mmd -o DIAGRAMS/logical-flow.png --scale 3`

---

## Prerequisites

| Requirement | Version / Notes |
|-------------|----------------|
| Ansible | >= 2.15 |
| Python | >= 3.9 |
| `catalystcentersdk` | >= 2.3.7.9 |
| `cisco.catalystcenter` collection | 2.1.3 |
| `ansible.utils` collection | >= 2.11.0 (required by action plugins) |
| Cisco Catalyst Center | >= 2.3.7.6 (for `floorNumber` support) |

> **Note:** `cisco.catalystcenter` modules do not support `check_mode`. Dry-run verification must be done by reviewing the `Display computed site payloads` debug output before committing.

---

## Directory Structure

```
1.0-Cisco-Catalyst-Center-Site-Hierarchy/
├── ansible.cfg                 # Ansible defaults (inventory path, deprecation_warnings suppressed)
├── inventory.yml               # CatC connection (catc_*) + default building/floor values
├── site_hierarchy.yml          # Main playbook
├── tasks/
│   ├── create_or_update_site.yml  # Phase B: per-site create/update logic (include_tasks)
│   └── delete_site.yml            # Phase C: per-site delete logic (include_tasks)
├── site_input.json.example     # Example input file (devices.json format)
├── vault.yml                   # Ansible Vault encrypted credentials (git-ignored)
├── vault.yml.example           # Plain-text credential template
├── .vault_pass                 # Vault password file (git-ignored, chmod 600)
├── requirements.txt            # Python pip dependencies
├── requirements.yml            # Ansible Galaxy collection dependencies
└── DIAGRAMS/
    ├── logical-flow.mmd        # Mermaid source — re-render with mmdc
    └── logical-flow.png        # Rendered flowchart (referenced by README)
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

This installs `catalystcentersdk>=2.3.7.9` — the Python SDK used by the `cisco.catalystcenter` collection.

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
      catc_host:    198.18.129.100
      catc_port:    443
      catc_version: "2.3.7.9"
      catc_verify:  false
      catc_debug:   false

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
| `catc_host` | CatC hostname or IP | 
| `catc_port` | API port (default 443) |
| `catc_version` | SDK version string — must be ≤ appliance version |
| `catc_verify` | SSL certificate verification (`false` for self-signed certs) |
| `catc_debug` | Enable verbose `catalystcentersdk` tracing |
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
catc_username: "admin"
catc_password: "your_catc_password_here"
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

The path is resolved to absolute (relative paths are expanded from `playbook_dir`), then `lookup('file', _resolved_json_path) | from_json` reads and parses the JSON in one step. An `assert` task validates the shape before any processing begins.

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

**Purpose:** Compose a typed config dict for each path and call the appropriate `cisco.catalystcenter` module — but ONLY after resolving which sites already exist.

#### Why ID resolution is mandatory

Unlike `cisco.dnac.site_workflow_manager`, the individual `cisco.catalystcenter` modules have **no built-in idempotency by name**. The action plugin's `get_object_by_name()` always returns `None` — existence checks only work if you supply the site's UUID as `id:`. Without the UUID, every run would POST a new site.

#### Phase A: Resolve all existing site UUIDs

```
GET /dna/intent/api/v1/sites   (no limit — returns all sites)
        ↓
 site_id_map = {
   "Global":                                "<uuid>",
   "Global/PODS":                           "abc123-...",
   "Global/PODS/POD 0/Building P0/Floor 1": "xyz789-...",
   ...
 }
```

#### Phase B: Create / update (state=merged)

`include_tasks: tasks/create_or_update_site.yml` is called once per entry in the depth-sorted `site_configs_list`. Using `include_tasks` rather than a plain `loop:` is **critical**: `set_fact` inside `include_tasks` takes effect immediately (before the next iteration), whereas `set_fact` inside a plain loop only takes effect after the entire loop completes. This means a parent site's UUID is added to `site_id_map` as soon as it is created, and the very next iteration can look it up as `parentId`.

Per-site logic inside `tasks/create_or_update_site.yml`:

```
path = "Global/PODS/POD 0/Building P0/Floor 1"

1. site_type = site_type_map[path]     → "floor"
2. parent    = "Global/PODS/POD 0/Building P0"
3. parent_id = site_id_map[parent]     → "def456-..."  ← must exist
4. exists?   = path in site_id_map     → False (first run)

   if NOT exists:
     POST /dna/intent/api/v1/site  { type: floor, site: { floor: { name, parentName, rfModel, ... } } }  ← cisco.dnac.site
     GET  /dna/intent/api/v1/sites?nameHierarchy=<path>   ← ID resolution
     site_id_map[path] = new UUID

   if EXISTS:
     PUT  /dna/intent/api/v2/floors/{id}  { id, name, parentId, rfModel, ... }
```

#### Phase C: Delete (state=deleted)

`include_tasks: tasks/delete_site.yml` loops the **reversed** list (deepest first). CatC rejects deletion of a site that still has children, so children-first ordering is required.

```
   DELETE /dna/intent/api/v2/floors/{id}     (floor — deepest, deleted first)
   DELETE /dna/intent/api/v2/buildings/{id}  (building)
   DELETE /dna/intent/api/v1/areas/{id}      (area — shallowest, deleted last)
```

Sites not found in `site_id_map` are silently skipped.

---

## Data Transformation Reference

```
devices.json
└── project[]
    └── [n].HierarchyName + SiteType + metadata
              │
              ▼ Step 2 — set_fact (3 maps)
    site_type_map     = { "Global/.../.../Floor 1": "floor", ... }
    building_info_map = { "Global/.../Building":    {address, ...}, ... }
    floor_info_map    = { "Global/.../Floor 1":     {rf_model, ...}, ... }
              │
              ▼ Step 3 — path expansion + dedup + depth sort
    all_site_paths = [
      "Global/PODS",
      "Global/PODS/POD 0",
      "Global/PODS/POD 0/Building P0",
      "Global/PODS/POD 0/Building P0/Floor 1"
    ]
              │
              ▼ Step 4 — pre-compute site_configs_list
    site_configs_list = [ {site_type, site: {<type>: {name, parent_name, ...}}}, ... ]
              │
              ▼ Phase A — GET /dna/intent/api/v1/sites (all sites)
    site_id_map = { "Global": "uuid-0", "Global/PODS": "uuid-1", ... }
              │
              ▼ Phase B — include_tasks (serial, depth-sorted)
    per NEW site   → POST /dna/intent/api/v1/areas        (area)
                   → POST /dna/intent/api/v2/buildings     (building)
                   → POST /dna/intent/api/v1/site          (floor — cisco.dnac.site; v2 POST returns 500 on CatC 2.3.x)
                   → GET /dna/intent/api/v1/sites?nameHierarchy=<path>  (UUID)
                   → site_id_map[path] = new UUID  ← visible to next iteration
    per EXISTING   → PUT  /dna/intent/api/v1/areas/{id}
    site           → PUT  /dna/intent/api/v2/buildings/{id}
                   → PUT  /dna/intent/api/v2/floors/{id}
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

> **Note:** `cisco.catalystcenter` modules do **not** support `--check` mode. Review the `Display computed site payloads` debug output before running to verify the payload structure.

---

## Debug Mode

```bash
ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass -e catc_debug=true
```

Setting `catc_debug=true` enables two things simultaneously:

1. **Verbose SDK HTTP tracing** — every `catalystcentersdk` API request (URL, method, headers) and response is printed to stderr alongside the normal Ansible output.
2. **Ansible debug tasks** — 16 extra `debug:` tasks gated on `catc_debug | default(false) | bool` fire throughout the play and per-site task file.

> **Note:** The `-e catc_debug=true` CLI flag passes a string; `| bool` coercion in every `when:` condition handles the type conversion correctly.

### Debug Task Reference

| File | Debug Task | Variable(s) Printed |
|------|-----------|---------------------|
| `site_hierarchy.yml` | `DEBUG \| Resolved JSON path` | `_resolved_json_path` — absolute path used to load the JSON |
| `site_hierarchy.yml` | `DEBUG \| site_data (raw JSON)` | `site_data` — full parsed JSON document |
| `site_hierarchy.yml` | `DEBUG \| site_type_map / building_info_map / floor_info_map` | All three lookup maps built in Step 2 |
| `site_hierarchy.yml` | `DEBUG \| all_site_paths (ordered)` | `all_site_paths` — depth-sorted list of paths |
| `site_hierarchy.yml` | `DEBUG \| site_configs_list (full payload)` | `site_configs_list` — typed config dict per path |
| `site_hierarchy.yml` | `DEBUG \| catc_all_sites raw response` | Raw Phase A `GET /dna/intent/api/v1/sites` response |
| `tasks/create_or_update_site.yml` | `DEBUG \| Step 1 — type/name/parent` | `_type`, `_name`, `_parent` extracted from `site_config` |
| `tasks/create_or_update_site.yml` | `DEBUG \| Step 2 — path/parent_id/exists/site_id` | `_path`, `_parent_id`, `_exists`, `_site_id` |
| `tasks/create_or_update_site.yml` | `DEBUG \| Area CREATE result` | `_area_create` (skipped unless `_type == 'area'` and new) |
| `tasks/create_or_update_site.yml` | `DEBUG \| Area UPDATE result` | `_area_update` (skipped unless `_type == 'area'` and exists) |
| `tasks/create_or_update_site.yml` | `DEBUG \| Building CREATE result` | `_building_create` (skipped unless building and new) |
| `tasks/create_or_update_site.yml` | `DEBUG \| Building UPDATE result` | `_building_update` (skipped unless building and exists) |
| `tasks/create_or_update_site.yml` | `DEBUG \| Floor CREATE result` | `_floor_create` (skipped unless floor and new) |
| `tasks/create_or_update_site.yml` | `DEBUG \| Floor UPDATE result` | `_floor_update` (skipped unless floor and exists) |
| `tasks/create_or_update_site.yml` | `DEBUG \| New site query response` | `_new_site_info` — UUID query result (only on CREATE) |
| `tasks/create_or_update_site.yml` | `DEBUG \| site_id_map after update` | Full `site_id_map` after the new UUID is added (only on CREATE) |

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

TASK [Phase A — Fetch all existing sites from Catalyst Center] ****************
ok: [catalyst_center]

TASK [Phase A — site_id_map (1 existing sites)] ******************************
ok: [catalyst_center] => { "msg": {"Global": "abc123-..."} }

TASK [Area     | CREATE | Global/PODS] ****************************************
changed: [catalyst_center]

TASK [Query ID for newly created area | Global/PODS] **************************
ok: [catalyst_center]

TASK [Area     | CREATE | Global/PODS/POD 0] **********************************
changed: [catalyst_center]

TASK [Building | CREATE | Global/PODS/POD 0/Building P0] *********************
changed: [catalyst_center]

TASK [Floor    | CREATE | Global/PODS/POD 0/Building P0/Floor 1] **************
changed: [catalyst_center]

TASK [Site hierarchy provisioning complete] ***********************************
ok: [catalyst_center] => { "msg": "Successfully provisioned 4 site(s)." }

PLAY RECAP *********************************************************************
catalyst_center : ok=N changed=4 unreachable=0 failed=0 skipped=N
```

On subsequent runs, existing sites receive `UPDATE` calls that return `result: "Object already present"` with `changed=false`.

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Authentication failed` | Wrong credentials in `vault.yml` | Re-edit `vault.yml` and verify `catc_username`/`catc_password` |
| `name/parent_name should not be None` | `SiteType` missing from a JSON entry | Add explicit `SiteType` to every non-null entry |
| `country should not be None` | Building has no `country` field | Add `country` to the JSON entry or set `default_building_country` |
| `floorNumber validation error` | CatC ≥ 2.3.7.6 requires this field | Add `floor_number` to each floor entry or set `default_floor_number` |
| `Parent site not found` / `parentId required` | Parent UUID not in `site_id_map` | Ensure all ancestor paths exist in the JSON with explicit `SiteType` |
| `Cannot delete — site has children` | Trying to delete parent before child | Use `state=deleted` (auto-reverses order), or delete manually deepest-first |
| `catalystcentersdk not installed` | Missing Python SDK | Run `pip install -r requirements.txt` |
| `Collection not found` | `cisco.catalystcenter` not installed | Run `ansible-galaxy collection install -r requirements.yml` |
| `ansible.utils` import error | Missing `ansible.utils` collection | Run `ansible-galaxy collection install ansible.utils` |
| TLS/SSL errors | Self-signed certificate | Set `catc_verify: false` in `inventory.yml` for lab |
| Version mismatch warning | `catc_version` > appliance version | Set `catc_version: "2.3.7.9"` (or lower to match appliance) |
| `retries exhausted` on ID query | CatC slow to commit new site | Increase `retries` or `delay` in `tasks/create_or_update_site.yml` |
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
| Ansible | 2.15+ |
| `cisco.catalystcenter` collection | 2.1.3 (supports CatC 2.3.7) |
| `ansible.utils` collection | >= 2.11.0 |
| `catalystcentersdk` | >= 2.3.7.9 |

Install the required collections and SDK:

```bash
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

---

## Credentials Setup

```bash
# 1. Copy the credential template
cp vault.yml.example vault.yml

# 2. Edit with your Catalyst Center credentials
#    Set: catc_username, catc_password

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

> **Note:** Field names in `site_configs_list` use snake_case (`rf_model`, `floor_number`); the `cisco.catalystcenter.floors` module requires camelCase (`rfModel`, `floorNumber`). The `tasks/create_or_update_site.yml` file handles this mapping transparently.

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

**Preview payloads before committing (no `--check` mode support):**

```bash
ansible-playbook site_hierarchy.yml --vault-password-file .vault_pass -e catc_debug=true
```

> `cisco.catalystcenter` modules do not support Ansible `--check` mode. To review the planned site payloads without making any API calls, run with `catc_debug=true` and inspect the `DEBUG | site_configs_list` and `Phase A — site_id_map` debug output.

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
Phase A — GET /dna/intent/api/v1/sites (resolve all existing UUIDs → site_id_map)
        │
        ▼
Phase B — include_tasks: create_or_update_site.yml (per site, depth-sorted)
   ├── NEW site  → POST  + GET nameHierarchy → UUID added to site_id_map
   └── EXISTING  → PUT with id: (idempotent via UUID lookup)
        │
Phase C — include_tasks: delete_site.yml (reversed list, deepest first)
   └── DELETE with id: for each site present in site_id_map
        │
        ▼
Summary
```

---

## Catalyst Center Configuration

Edit `inventory.yml` to point to your CatC instance:

```yaml
catc_host:    dnac.dcloud.cisco.com   # CatC FQDN or IP
catc_version: "2.3.7.9"              # Must match or be lower than your CatC version
catc_verify:  false                  # Set true in production with a valid cert
catc_debug:   false                  # Set true for verbose SDK HTTP tracing
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
| `Authentication failed` | Wrong credentials | Re-edit `vault.yml` and verify `catc_username`/`catc_password` |
| `name/parent_name should not be None` | `SiteType` missing from a JSON entry | Add explicit `SiteType` to every entry in the input file |
| `country should not be None` | Building entry has no `country` field and no default | Add `country` to the JSON entry or set `default_building_country` in `inventory.yml` |
| `floorNumber` validation error | Required in CatC ≥ 2.3.7.6 | Add `floor_number` to the floor entry or ensure `default_floor_number` is set |
| `Parent site not found` / `parentId required` | UUID not in `site_id_map` | Ensure all ancestor paths exist in JSON with explicit `SiteType`; re-run Phase A |
| `Building type requires address` | `SiteType: building` with no address and no default | Set `address`, `latitude`, `longitude`, `country` in the JSON entry or inventory defaults |
| `Collection not found` | `cisco.catalystcenter` not installed | Run `ansible-galaxy collection install -r requirements.yml` |
| Version mismatch warning | `catc_version` > appliance version | Set `catc_version: "2.3.7.9"` (or lower) in `inventory.yml` |
| `retries exhausted` on ID query | CatC slow to commit new site | Increase `retries` or `delay` in `tasks/create_or_update_site.yml` |

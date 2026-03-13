# CatC Site Hierarchy

Ansible playbook that reads a `devices.json`-formatted input file and builds a complete **Cisco Catalyst Center site hierarchy** (areas, buildings, floors) using the `cisco.dnac.site_workflow_manager` module.

The playbook is fully **idempotent** — re-running it will not duplicate existing sites.

---

## Directory Structure

```
Cisco-Catalyst-Center-Site-Hierarchy/
├── ansible.cfg              # Ansible defaults
├── inventory.yml            # CatC connection parameters and defaults
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

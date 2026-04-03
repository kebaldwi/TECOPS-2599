# TRADITIONAL Project — Settings Reference

> **As-Built Documentation**
> **Authors:** Keith Baldwin — Solutions Engineer — Automation HyperSpecialist (kebaldwi@cisco.com)
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

This document describes the structure and purpose of the two configuration files in this folder — [`settings.json`](settings.json) and [`devices.json`](devices.json) — which together form the declarative intent layer that drives the Traditional switching automation lifecycle across Cisco Workflows, Ansible, and Python tooling paths.

---

## Table of Contents

1. [Purpose](#purpose)
2. [Two-File Design: settings.json vs devices.json](#two-file-design-settingsjson-vs-devicesjson)
3. [settings.json — Site Configuration File](#settingsjson--site-configuration-file)
   - [Design Principle — Repeating Project Array](#design-principle--repeating-project-array)
   - [Top-Level Structure](#top-level-structure)
   - [Field Reference — Site Hierarchy Fields](#field-reference--site-hierarchy-fields)
   - [Field Reference — Network Settings](#field-reference--network-settings)
   - [Field Reference — Device Credentials](#field-reference--device-credentials)
   - [Field Reference — Device List](#field-reference--device-list)
   - [Field Reference — Network Profile](#field-reference--network-profile)
4. [devices.json — Hierarchy Node File](#devicesjson--hierarchy-node-file)
   - [Design Principle — Flat Node List](#design-principle--flat-node-list)
   - [Top-Level Structure](#top-level-structure-1)
   - [Field Reference — Node Fields](#field-reference--node-fields)
5. [How the Tooling Consumes These Files](#how-the-tooling-consumes-these-files)
6. [Traditional vs BGP\_EVPN Settings Differences](#traditional-vs-bgp_evpn-settings-differences)
7. [Adding a New Site](#adding-a-new-site)
8. [Field Null Handling](#field-null-handling)
9. [Full Examples](#full-examples)

---

## Purpose

The settings files in this folder serve as the **single source of truth** for the TRADITIONAL project's automation workflows. They define every site-specific parameter needed to:

1. **Build the site hierarchy** in Catalyst Center (Area → Building → Floor, or any multi-level path)
2. **Apply network settings** per site (DNS, DHCP, NTP, SNMP, Syslog, NetFlow, AAA, banner)
3. **Create and assign device credentials** (CLI, SNMP v2c R/W, NETCONF)
4. **Run device discovery** against a defined IP list
5. **Bind templates to sites** via a named network profile, controlling which Day-N and Day-0 PnP templates are associated with which devices at which sites

All three tooling paths — Cisco Workflows, Ansible, and Python — read these files from GitHub and use them as their sole source of configuration intent, ensuring consistency regardless of which automation path is used.

---

## Two-File Design: settings.json vs devices.json

The TRADITIONAL project provides two complementary configuration files. Each serves a distinct purpose:

| File | Design | Primary Usage |
|------|--------|--------------|
| `settings.json` | Repeating `project[]` array — one element per physical site | Configure network settings, credentials, discovery, and template binding for each site with full per-site control |
| `devices.json` | Flat `project[]` array — one element per **hierarchy node** | Describe a multi-level hierarchy as a flat ordered list; supports complex region/campus/building/floor topologies without nesting |

The two files can be used independently or together depending on the workflow being executed. `settings.json` is the primary file consumed by the full automation lifecycle. `devices.json` offers an alternative flat-list approach for operators who prefer to describe hierarchy as an explicit node sequence.

---

## settings.json — Site Configuration File

### Design Principle — Repeating Project Array

The `project` key is a **JSON array**. Each element in the array represents **one complete site definition** — a single Catalyst Center floor-level site with its own unique hierarchy location, network settings, credentials, discovery scope, and template profile.

```json
{
    "project": [
        { /* Site 1 — POD 1, Building P1, Floor 1 */ },
        { /* Site 2 — POD 2, Building P2, Floor 1 */ },
        { /* Site 3 — POD 3, Building P3, Floor 2 */ }
    ]
}
```

This design enables **finite, per-site control** over every configurable dimension:

| Dimension | Per-Site Control |
|-----------|----------------|
| Hierarchy placement | Each entry targets a unique `HierarchyArea / HierarchyBldg / HierarchyFloor` path |
| Network settings | DNS, DHCP, NTP, SNMP, Syslog, NetFlow, AAA, and banner can differ per site |
| Device credentials | Each site can use different CLI usernames, SNMP communities, or NETCONF ports |
| Discovery scope | `device_list` is scoped to the devices at that site only |
| Template binding | `network_profile` independently controls which Day-N and Day-0 PnP templates are bound to which devices at that site |

The automation tooling iterates over every element in the `project` array and applies each definition independently, in order. Adding a new site requires only appending a new object to the array — no changes to the tooling are needed.

---

### Top-Level Structure

```
settings.json
└── project[]                          # Array — one element per site
    ├── HierarchyParent                # Catalyst Center parent path
    ├── HierarchyArea                  # Area name under parent
    ├── HierarchyBldg                  # Building name under area
    ├── HierarchyFloor                 # Floor name under building
    ├── HierarchyBldgAddress           # Physical address for building geo-location
    ├── network_settings{}             # Site-level network infrastructure settings
    │   ├── dhcp_server[]              # DHCP server IP list
    │   ├── dns_server{}               # Domain name and DNS server IPs
    │   ├── ntp_server[]               # NTP server IP list
    │   ├── timezone                   # IANA timezone string
    │   ├── message_of_the_day{}       # Login banner text and retain flag
    │   ├── snmp_server{}              # SNMP trap destination IPs
    │   ├── syslog_server{}            # Syslog destination IPs
    │   ├── netflow_server{}           # NetFlow collector IP and port
    │   ├── network_aaa               # Network AAA (null = not configured)
    │   └── client_and_endpoint_aaa{} # Client/endpoint AAA (ISE/RADIUS)
    ├── device_credentials{}           # Global device credential definitions
    │   ├── cli_credential{}           # SSH/Telnet credential
    │   ├── snmp_v2c_read{}            # SNMP v2c read-only community
    │   ├── snmp_v2c_write{}           # SNMP v2c read-write community
    │   └── netconf_credential{}       # NETCONF credential and port
    ├── device_list                    # Comma-separated discovery IP string
    └── network_profile{}              # Template-to-site binding definition
        ├── profile_name               # Switching profile name in Catalyst Center
        ├── DayNTemplateNames[]        # Day-N (post-onboarding) template bindings
        └── Day0TemplateNames[]        # Day-0 (PnP onboarding) template bindings
```

---

### Field Reference — Site Hierarchy Fields

These five fields define where this site element lives in the Catalyst Center hierarchy. Together they form the full site path: `{HierarchyParent}/{HierarchyArea}/{HierarchyBldg}/{HierarchyFloor}`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `HierarchyParent` | string | Full path to the parent node in Catalyst Center. Must already exist or be created by a prior site entry. | `"Global/PODS"` |
| `HierarchyArea` | string | Area name to create or reference under the parent. | `"POD 1"` |
| `HierarchyBldg` | string | Building name to create or reference under the area. | `"Building P1"` |
| `HierarchyFloor` | string | Floor name to create or reference under the building. | `"Floor 1"` |
| `HierarchyBldgAddress` | string | Physical street address for the building. Used by Catalyst Center to set geographic location metadata. | `"400 E Tasman Dr, Bldg 12, San Jose, CA 95134"` |

The hierarchy is created in parent-before-child order. If multiple project entries share the same `HierarchyArea` or `HierarchyBldg`, the tooling is idempotent — it skips creation of objects that already exist and resolves their existing UUIDs for downstream use.

---

### Field Reference — Network Settings

The `network_settings` object defines all site-level network infrastructure services applied to the site in Catalyst Center under **Design → Network Settings**.

#### `dhcp_server`

Array of DHCP server IP addresses assigned to this site.

```json
"dhcp_server": ["198.18.133.1"]
```

Multiple servers are supported. Each IP is registered as a DHCP server for the site scope.

#### `dns_server`

Domain name and DNS resolver configuration for the site.

| Field | Type | Description |
|-------|------|-------------|
| `domain_name` | string | Default DNS domain appended to unqualified hostnames |
| `primary_ip_address` | string | Primary DNS resolver IP |
| `secondary_ip_address` | string \| null | Secondary DNS resolver IP, or `null` if not required |

#### `ntp_server`

Array of NTP server IP addresses. Catalyst Center pushes these to managed devices at the site.

```json
"ntp_server": ["198.18.133.1"]
```

#### `timezone`

IANA timezone string applied to the site. Controls time display and log timestamps in Catalyst Center for this site scope.

```json
"timezone": "America/Toronto"
```

#### `message_of_the_day`

Login banner definition applied to the site.

| Field | Type | Description |
|-------|------|-------------|
| `banner_message` | string | The banner text to display at device login |
| `retain_existing_banner` | boolean | `false` = replace any existing banner; `true` = keep existing banner if one is set |

#### `snmp_server`

SNMP trap receiver configuration.

| Field | Type | Description |
|-------|------|-------------|
| `configure_dnac_ip` | boolean | `true` = automatically include the Catalyst Center IP as a trap receiver |
| `ip_addresses` | array | Additional SNMP trap destination IPs |

#### `syslog_server`

Syslog message receiver configuration.

| Field | Type | Description |
|-------|------|-------------|
| `configure_dnac_ip` | boolean | `true` = automatically include the Catalyst Center IP as a syslog receiver |
| `ip_addresses` | array | Additional syslog destination IPs |

#### `netflow_server`

NetFlow / telemetry collector configuration for streaming telemetry and flow data.

| Field | Type | Description |
|-------|------|-------------|
| `configure_dnac_ip` | boolean | `true` = automatically include the Catalyst Center IP as a NetFlow collector |
| `ip_address` | string | Collector IP address |
| `port` | integer | UDP destination port for NetFlow exports (standard: `2055`) |

#### `network_aaa`

Network device AAA (authentication for device management access). Set to `null` when not required for this site, or provide a structured object with `server_type`, `primary_server_address`, `protocol`, and `shared_secret` fields.

```json
"network_aaa": null
```

#### `client_and_endpoint_aaa`

Client and endpoint AAA configuration (ISE/RADIUS for 802.1X and MAB). Applied to the site to configure RADIUS authentication for end-user devices.

| Field | Type | Description |
|-------|------|-------------|
| `server_type` | string | AAA server type: `"ISE"` or `"AAA"` |
| `primary_server_address` | string | IP address of the primary RADIUS/ISE PSN node |
| `pan_address` | string | IP address of the ISE Policy Administration Node (PAN). Used when `server_type` is `"ISE"`. |
| `protocol` | string | Authentication protocol: `"RADIUS"` or `"TACACS"` |
| `shared_secret` | string | RADIUS shared secret. **Treat as a credential — use Ansible Vault or a secrets manager in production.** |
| `secondary_server_address` | string \| null | IP of secondary RADIUS/ISE PSN, or `null` |

---

### Field Reference — Device Credentials

The `device_credentials` object defines the global device credentials created in Catalyst Center under **Design → Credentials** and assigned to the site. These credentials are used by Catalyst Center for SNMP polling, SSH management access, and NETCONF operations.

#### `cli_credential`

SSH/Telnet access credential.

| Field | Description |
|-------|-------------|
| `description` | Label used to identify this credential in Catalyst Center (must be unique). Used by the tooling to look up the credential UUID. |
| `username` | SSH login username |
| `password` | SSH login password. **Treat as a credential — protect in production.** |
| `enable_password` | Privileged mode enable password |

#### `snmp_v2c_read`

SNMP v2c read-only community string.

| Field | Description |
|-------|-------------|
| `description` | Label used to identify this credential in Catalyst Center |
| `read_community` | SNMPv2c read community string (e.g., `"ro"`) |

#### `snmp_v2c_write`

SNMP v2c read-write community string.

| Field | Description |
|-------|-------------|
| `description` | Label used to identify this credential in Catalyst Center |
| `write_community` | SNMPv2c write community string (e.g., `"rw"`) |

#### `netconf_credential`

NETCONF over SSH credential.

| Field | Description |
|-------|-------------|
| `description` | Label used to identify this credential in Catalyst Center |
| `netconf_port` | TCP port for NETCONF sessions (standard: `"830"`) |

> **Note on credential descriptions:** The `description` field is the key the tooling uses to look up the UUID of an already-created credential. If you change a description between runs, the tooling will create a new credential rather than updating the existing one.

---

### Field Reference — Device List

`device_list` is a comma-separated string of management IP addresses for all devices at this site. It is used by the discovery and provisioning stages of the tooling.

```json
"device_list": "198.18.130.1,198.18.10.2,198.18.20.2"
```

- **Discovery:** The tooling splits this string and builds one or more Catalyst Center discovery jobs targeting these IPs.
- **Provisioning:** The Cisco Workflow provisioning path uses this list to determine which device UUIDs to provision and deploy templates to.
- **Network profile:** The `TemplateTarget` arrays in `network_profile` should be a subset of, or equal to, this list. In the TRADITIONAL project example, the core/distribution switch (`198.18.130.1`) is included in discovery but not in `TemplateTarget` — only the access switches receive the Day-N build template.

Separate site entries with non-overlapping `device_list` values ensure each device is discovered in the context of its correct site.

---

### Field Reference — Network Profile

The `network_profile` object binds the Catalyst Center **switching network profile** to this site's template content. This is the mechanism that connects committed templates in the Template Hub to the devices at this site for provisioning and Day-N deployment.

#### `profile_name`

The name of the switching network profile in Catalyst Center. If a profile with this name already exists, the tooling updates it. If it does not exist, the tooling creates it.

```json
"profile_name": "Traditional-Switching"
```

#### `DayNTemplateNames`

Array of Day-N template binding objects. Each element defines one template that should be bound to the network profile and optionally deployed to a set of devices. In the TRADITIONAL project, `BUILD-MasterBuild.j2` is a **composite orchestration template** that calls the individual `BUILD-*.j2` sub-templates in sequence to build a complete device configuration.

| Field | Type | Description |
|-------|------|-------------|
| `TemplateName` | string | Exact name of the composite or member template in the Catalyst Center Template Hub. Must match the committed template name. |
| `TemplateTag` | string | Tag label used by the tooling to filter and identify templates. |
| `Project` | string | The Catalyst Center template project the template belongs to. Used to resolve the template UUID. |
| `TemplateTarget` | array | List of device IP addresses to deploy this template to during the provisioning workflow. Must be a subset of `device_list`. |
| `DeployTemplate` | boolean | `true` = the provisioning workflow will deploy this template to all IPs in `TemplateTarget`; `false` = profile binding only, no deployment. |

Multiple Day-N template objects can be listed in the array to bind and optionally deploy more than one template to devices at this site.

#### `Day0TemplateNames`

Array of Day-0 (PnP onboarding) template binding objects. Follows the same structure as `DayNTemplateNames`. Used to bind PnP claim templates to the network profile for zero-touch device onboarding.

Unlike the BGP\_EVPN project (which has a null Day-0 entry), the TRADITIONAL project actively uses Day-0 templates. `Titanium-L2-PnP-Jinja-Template.j2` is the Layer 2 PnP claim template used to onboard new access switches via Plug-and-Play without any manual console connection.

Available Day-0 templates in this project:

| Template | Use Case |
|----------|----------|
| `Titanium-L2-PnP-Jinja-Template.j2` | Layer 2 access switch PnP onboarding (default) |
| `Titanium-L3-PnP-Template.j2` | Layer 3 distribution/routed switch PnP onboarding |
| `Titanium-L3-EIGRP-PnP-Template.j2` | Layer 3 with EIGRP routing PnP onboarding |
| `Titanium-L3-OSPF-PnP-Template.j2` | Layer 3 with OSPF routing PnP onboarding |
| `Automation-Seed.j2` | Automation seed configuration for discovered devices |
| `Automation-Edge.j2` | Edge device automation seed configuration |
| `Titanium-L3-PnP-Automation-Seed.j2` | Combined L3 PnP + automation seed |

Set individual fields to `null` and `TemplateTarget` to `[]` when no Day-0 template is required for a site entry.

---

## devices.json — Hierarchy Node File

### Design Principle — Flat Node List

`devices.json` takes a fundamentally different approach to hierarchy definition. Rather than grouping all settings for one physical site into a single object, it represents the **entire Catalyst Center hierarchy as a flat ordered list of nodes** — one object per hierarchy level.

```json
{
    "project": [
        { "HierarchyName": "Global",                          "SiteType": null },
        { "HierarchyName": "Global/ONTARIO",                  "SiteType": "area" },
        { "HierarchyName": "Global/ONTARIO/OSHAWA",           "SiteType": "area" },
        { "HierarchyName": "Global/ONTARIO/OSHAWA/HOME",      "SiteType": "building" },
        { "HierarchyName": "Global/ONTARIO/OSHAWA/HOME/FLOOR 1", "SiteType": "floor" }
    ]
}
```

This design is particularly useful for:

- **Complex multi-region hierarchies** with many intermediate area levels that would make the `settings.json` approach verbose
- **Scripted hierarchy generation** — a script can produce the flat node list by walking a regional inventory
- **Partial hierarchy builds** — nodes with `DeviceList: null` are created but have no devices or templates assigned, making them ready containers for later population
- **Leaf-node template assignment** — template bindings are only required at floor-level nodes; all parent nodes can carry null template entries

The tooling processes the array in order (top-to-bottom), ensuring parent nodes are created before any child node references them.

---

### Top-Level Structure

```
devices.json
└── project[]                          # Array — one element per hierarchy node
    ├── HierarchyName                  # Full slash-delimited path from Global
    ├── SiteType                       # Node type: null | "area" | "building" | "floor"
    ├── DeviceList                     # Comma-separated IP string, or null
    ├── NetworkProfile                 # Profile name string, or null
    ├── Day0TemplateNames[]            # Day-0 (PnP) template bindings
    └── DayNTemplateNames[]            # Day-N template bindings
```

---

### Field Reference — Node Fields

#### `HierarchyName`

The full slash-delimited path of this node in the Catalyst Center hierarchy, starting from `Global`.

```json
"HierarchyName": "Global/ONTARIO/OSHAWA/HOME/FLOOR 1"
```

- The root entry must be `"Global"` with `SiteType: null`.
- Each subsequent entry must extend an already-defined path — the tooling processes nodes in array order, so parents must appear before children.
- Path components can contain spaces (e.g., `"FLOOR 1"`).

#### `SiteType`

The Catalyst Center type for this hierarchy node.

| Value | Meaning |
|-------|---------|
| `null` | Root node (Global) — not created; used as an anchor reference |
| `"area"` | Geographic or logical area grouping (no physical location required) |
| `"building"` | Physical building (requires an address in Catalyst Center if geo-location is enabled) |
| `"floor"` | Floor within a building; leaf node where devices are assigned |

Template bindings and device assignments are only applied at `"floor"` nodes. `"area"` and `"building"` nodes carry null template entries and serve as hierarchy containers.

#### `DeviceList`

Comma-separated string of device management IP addresses associated with this hierarchy node, or `null` for non-leaf nodes.

```json
"DeviceList": "10.1.1.10"
```

Only `"floor"` type nodes should carry non-null device lists. The tooling uses this field to associate discovered devices with this specific location in the hierarchy.

#### `NetworkProfile`

Name of the Catalyst Center switching network profile to associate with this node, or `null`.

```json
"NetworkProfile": null
```

When set, the tooling binds or creates the named profile and links it to this hierarchy node. When `null`, no profile association is made for this node.

#### `Day0TemplateNames` and `DayNTemplateNames`

Same structure as in `settings.json`. Each is an array of template binding objects:

| Field | Type | Description |
|-------|------|-------------|
| `TemplateName` | string \| null | Template name in the Catalyst Center Template Hub |
| `TemplateTag` | string \| null | Tag label for filtering |
| `Project` | string \| null | Catalyst Center template project name |
| `TemplateTarget` | array | Device IPs to deploy to (subset of `DeviceList`) |
| `DeployTemplate` | boolean \| null | `true` = deploy during run; `false`/`null` = bind only |

For non-floor nodes, set all fields to `null` and `TemplateTarget` to `[]`.

---

## How the Tooling Consumes These Files

All three automation paths read the relevant file from GitHub and iterate over every element in the `project` array:

### settings.json Consumption

| Tooling Stage | Cisco Workflow | Ansible Playbook | Python Script | Fields Used |
|---------------|---------------|-----------------|--------------|-------------|
| Build Hierarchy | `GitOps-BuildHierarchy-v3` | `site_hierarchy.yml` | `site_hierarchy.py` | `HierarchyParent/Area/Bldg/Floor`, `HierarchyBldgAddress` |
| Network Settings | `GitOps-BuildSettings-v3` | `network_settings.yml` | `network_settings.py` | `network_settings.*` |
| Device Credentials | `GitOps-BuildSettings-v3` | `credentials.yml` | `credentials.py` | `device_credentials.*` |
| Device Discovery | `GitOps-DeviceDiscovery-v3` | `device_discovery.yml` | `device_discovery.py` | `device_list`, `device_credentials.*` |
| Network Profile | `GitOps-BuildNetworkProfile-v3` | `network_profile.yml` | `network_profile.py` | `network_profile.*` |
| Provisioning | `GitOps-Provisioning-v3` | `provision_devices.yml` + `deploy_composite_template.yml` | `deploy_composite.py` | `device_list`, `network_profile.DayNTemplateNames`, `network_profile.Day0TemplateNames` |

### devices.json Consumption

| Tooling Stage | Fields Used | Notes |
|---------------|-------------|-------|
| Build Hierarchy | `HierarchyName`, `SiteType` | Creates each node in path order |
| Device Association | `DeviceList` | Associates discovered devices with floor node |
| Network Profile | `NetworkProfile` | Binds profile to node if non-null |
| PnP Onboarding | `Day0TemplateNames` | Claims new devices at floor nodes |
| Day-N Deployment | `DayNTemplateNames` | Deploys build templates to floor node devices |

---

## Traditional vs BGP\_EVPN Settings Differences

The TRADITIONAL and BGP\_EVPN projects use the same `settings.json` schema, enabling the same tooling to serve both fabric types. Key differences reflect the underlying network architecture:

| Dimension | TRADITIONAL | BGP\_EVPN |
|-----------|-------------|-----------|
| Network profile name | `Traditional-Switching` | `BGP-EVPN-Switching` |
| Day-N template | `BUILD-MasterBuild.j2` (composite orchestrator) | `BGP-EVPN-BUILD.j2` |
| Day-0 PnP template | `Titanium-L2-PnP-Jinja-Template.j2` (active) | null (no PnP in lab) |
| Device list scope | Core + access switches (distinct TemplateTarget for access only) | All fabric nodes targeted equally |
| Additional config file | `devices.json` (flat hierarchy) | Not present |
| Template architecture | Modular BUILD sub-templates orchestrated by MasterBuild | Single integrated EVPN build template |
| SNMP communities | Lowercase (`ro` / `rw`) | Uppercase (`RO` / `RO`) |

---

## Adding a New Site

### Adding to settings.json

Append a new object to the `project` array. Copy an existing entry and update all fields to reflect the new site's hierarchy placement, network addresses, credentials, discovery scope, and template profile.

```json
{
    "project": [
        { /* existing site */ },
        {
            "HierarchyArea": "POD 2",
            "HierarchyBldg": "Building P2",
            "HierarchyFloor": "Floor 1",
            "HierarchyParent": "Global/PODS",
            "HierarchyBldgAddress": "400 E Tasman Dr, Bldg 13, San Jose, CA 95134",
            "network_settings": { },
            "device_credentials": { },
            "device_list": "198.18.131.1,198.18.11.2,198.18.21.2",
            "network_profile": {
                "profile_name": "Traditional-Switching",
                "DayNTemplateNames": [
                    {
                        "TemplateName": "BUILD-MasterBuild.j2",
                        "TemplateTag": "DEMO",
                        "Project": "Building P2",
                        "TemplateTarget": ["198.18.11.2","198.18.21.2"],
                        "DeployTemplate": true
                    }
                ],
                "Day0TemplateNames": [
                    {
                        "TemplateName": "Titanium-L2-PnP-Jinja-Template.j2",
                        "TemplateTag": "DEMO",
                        "Project": "Building P2",
                        "TemplateTarget": ["198.18.11.2","198.18.21.2"],
                        "DeployTemplate": true
                    }
                ]
            }
        }
    ]
}
```

### Adding to devices.json

Append one object per new node. Every node from the first new level down to the floor must be added. Parent nodes that already exist in the array do not need to be duplicated.

```json
{
    "project": [
        { /* existing Global node */ },
        { /* existing area nodes */ },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/OFFICE",
            "SiteType": "building",
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ],
            "DayNTemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/OFFICE/FLOOR 1",
            "SiteType": "floor",
            "DeviceList": "10.2.1.10",
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": "Titanium-L2-PnP-Jinja-Template.j2", "TemplateTag": "DEMO", "Project": "Day0Templates", "TemplateTarget": ["10.2.1.10"], "DeployTemplate": true }
            ],
            "DayNTemplateNames": [
                { "TemplateName": "BUILD-MasterBuild.j2", "TemplateTag": "DEMO", "Project": "DayNTemplates", "TemplateTarget": ["10.2.1.10"], "DeployTemplate": true }
            ]
        }
    ]
}
```

---

## Field Null Handling

### settings.json Null Fields

| Field | `null` Behavior |
|-------|----------------|
| `dns_server.secondary_ip_address` | No secondary DNS server configured for this site |
| `network_aaa` | Network device AAA is not applied to this site |
| `client_and_endpoint_aaa.secondary_server_address` | No secondary RADIUS/ISE PSN for this site |
| `Day0TemplateNames[*].TemplateName` | No Day-0 template bound to the profile |
| `Day0TemplateNames[*].DeployTemplate` | No PnP deployment triggered |

### devices.json Null Fields

| Field | `null` Behavior |
|-------|----------------|
| `SiteType` | Node is the Global root — not created, used as reference anchor |
| `DeviceList` | No devices associated with this hierarchy node |
| `NetworkProfile` | No network profile bound to this node |
| `Day0TemplateNames[*].TemplateName` | No Day-0 template bound at this node |
| `DayNTemplateNames[*].TemplateName` | No Day-N template bound at this node |
| `DeployTemplate` | Template is bound to the profile but not deployed in this run |

---

## Full Examples

### settings.json — Single Site

```json
{
    "project": [
        {
            "HierarchyParent": "Global/PODS",
            "HierarchyArea":   "POD 1",
            "HierarchyBldg":   "Building P1",
            "HierarchyFloor":  "Floor 1",
            "HierarchyBldgAddress": "400 E Tasman Dr, Bldg 12, San Jose, CA 95134",

            "network_settings": {
                "dhcp_server":  ["198.18.133.1"],
                "dns_server": {
                    "domain_name":          "dcloud.cisco.com",
                    "primary_ip_address":   "198.18.133.1",
                    "secondary_ip_address": null
                },
                "ntp_server":  ["198.18.133.1"],
                "timezone":    "America/Toronto",
                "message_of_the_day": {
                    "banner_message":         "DNAC Template Lab P1!",
                    "retain_existing_banner": false
                },
                "snmp_server": {
                    "configure_dnac_ip": true,
                    "ip_addresses": ["198.18.133.27"]
                },
                "syslog_server": {
                    "configure_dnac_ip": true,
                    "ip_addresses": ["198.18.133.27"]
                },
                "netflow_server": {
                    "configure_dnac_ip": true,
                    "ip_address": "198.18.133.27",
                    "port": 2055
                },
                "network_aaa": null,
                "client_and_endpoint_aaa": {
                    "server_type":              "ISE",
                    "primary_server_address":   "198.18.133.27",
                    "pan_address":              "198.18.133.27",
                    "protocol":                 "RADIUS",
                    "shared_secret":            "C1sco12345",
                    "secondary_server_address": null
                }
            },

            "device_credentials": {
                "cli_credential": {
                    "description":     "CLI-net-admin",
                    "username":        "netadmin",
                    "password":        "C1sco12345",
                    "enable_password": "C1sco12345"
                },
                "snmp_v2c_read": {
                    "description":    "RO",
                    "read_community": "ro"
                },
                "snmp_v2c_write": {
                    "description":     "RW",
                    "write_community": "rw"
                },
                "netconf_credential": {
                    "description":  "NETCONF-netadmin",
                    "netconf_port": "830"
                }
            },

            "device_list": "198.18.130.1,198.18.10.2,198.18.20.2",

            "network_profile": {
                "profile_name": "Traditional-Switching",
                "DayNTemplateNames": [
                    {
                        "TemplateName":   "BUILD-MasterBuild.j2",
                        "TemplateTag":    "DEMO",
                        "Project":        "Building P1",
                        "TemplateTarget": ["198.18.10.2","198.18.20.2"],
                        "DeployTemplate": true
                    }
                ],
                "Day0TemplateNames": [
                    {
                        "TemplateName":   "Titanium-L2-PnP-Jinja-Template.j2",
                        "TemplateTag":    "DEMO",
                        "Project":        "Building P1",
                        "TemplateTarget": ["198.18.10.2","198.18.20.2"],
                        "DeployTemplate": true
                    }
                ]
            }
        }
    ]
}
```

### devices.json — Multi-Level Hierarchy

```json
{
    "project": [
        {
            "HierarchyName": "Global",
            "SiteType": null,
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ],
            "DayNTemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ]
        },
        {
            "HierarchyName": "Global/ONTARIO",
            "SiteType": "area",
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ],
            "DayNTemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA",
            "SiteType": "area",
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ],
            "DayNTemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/HOME",
            "SiteType": "building",
            "DeviceList": null,
            "NetworkProfile": null,
            "Day0TemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ],
            "DayNTemplateNames": [
                { "TemplateName": null, "TemplateTag": null, "Project": null, "TemplateTarget": [], "DeployTemplate": null }
            ]
        },
        {
            "HierarchyName": "Global/ONTARIO/OSHAWA/HOME/FLOOR 1",
            "SiteType": "floor",
            "DeviceList": "10.1.1.10",
            "NetworkProfile": null,
            "Day0TemplateNames": [
                {
                    "TemplateName":   "Titanium-PnP-Jinja-Template.j2",
                    "TemplateTag":    "DEMO",
                    "Project":        "Day0Templates",
                    "TemplateTarget": ["10.1.1.10"],
                    "DeployTemplate": true
                }
            ],
            "DayNTemplateNames": [
                {
                    "TemplateName":   "BUILD-MasterBuild.j2",
                    "TemplateTag":    "DEMO",
                    "Project":        "DayNTemplates",
                    "TemplateTarget": ["10.1.1.10"],
                    "DeployTemplate": true
                }
            ]
        }
    ]
}
```

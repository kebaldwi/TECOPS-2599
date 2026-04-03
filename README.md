# TECOPS-2599 — Cisco Catalyst Center Network Orchestration

> **As-Built Documentation**
> **Authors:** Keith Baldwin — Solutions Engineer — Automation HyperSpecialist (kebaldwi@cisco.com), Igor Manassypov — Systems Engineer (imanassy@cisco.com)
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

This repository contains the complete network orchestration suite for project **TECOPS-2599**, presented at **Cisco Live 2026**. It delivers a fully automated, GitOps-driven lifecycle for Cisco Catalyst Center — from initial site commissioning through Day-N template deployment — across three parallel tooling paths: Cisco Workflows, Ansible, and Python.

---

## Table of Contents

1. [Business Overview](#business-overview)
2. [Repository Structure](#repository-structure)
3. [Projects](#projects)
   - [BGP\_EVPN](#bgp_evpn)
   - [TRADITIONAL](#traditional)
4. [Support](#support)
   - [Labs](#labs)
   - [Resources](#resources)
5. [Quick Start](#quick-start)
6. [Tooling Paths](#tooling-paths)
7. [Lab Environment](#lab-environment)

---

## Business Overview

Enterprise and public-sector network teams are under sustained pressure to commission new sites faster, reduce configuration drift, satisfy audit requirements, and scale operations without growing headcount proportionally. Manual Catalyst Center GUI workflows cannot meet these demands at scale.

TECOPS-2599 addresses this by treating **GitHub as the single source of truth** for all network configuration intent — site topology, network settings, device credentials, Jinja2 templates, and composite template definitions — and automating the full provisioning lifecycle through Catalyst Center REST APIs.

The repository provides three parallel tooling paths that all produce the same outcome in Catalyst Center:

| Path | Tooling | Best For |
|------|---------|----------|
| [Cisco Workflows](Support/Resources/Cisco%20Workflows/) | Cisco SecureX / XDR Workflow Manager | Platform-native, GUI-auditable operations |
| [Ansible](Support/Resources/Ansible/) | Ansible + cisco.catalystcenter collection | CI/CD pipeline integration, fleet operations |
| [Python](Support/Resources/Python/) | Pure Python REST | API learning, debugging, custom integrations |

Teams choose the path that matches their operational model and skill set. All three paths reference the same `settings.json` and template source in GitHub, maintaining a single source of truth regardless of tooling choice.

---

## Repository Structure

```
TECOPS-2599/
├── Projects/
│   ├── BGP_EVPN/                  # BGP EVPN fabric project
│   │   ├── Configs/               # Generated device configurations
│   │   ├── Day0Templates/         # PnP onboarding Jinja2 templates
│   │   ├── DayNTBD/               # Day-N templates under development
│   │   ├── DayNTemplates/         # Production Day-N Jinja2 templates
│   │   └── Settings/              # settings.json for this project
│   └── TRADITIONAL/               # Traditional (non-EVPN) fabric project
│       ├── Configs/               # Generated device configurations
│       ├── Day0Templates/         # PnP onboarding Jinja2 templates
│       ├── DayNTemplates/         # Production Day-N Jinja2 templates
│       └── Settings/              # settings.json and devices.json
└── Support/
    ├── Labs/                      # Guided lab exercises
    │   ├── Lab - Ansible/         # Step-by-step Ansible lab
    │   └── Lab - Cisco Workflows/ # Step-by-step Cisco Workflows lab
    └── Resources/                 # Automation tooling and reference content
        ├── Ansible/               # Ansible playbook suite (9 playbooks)
        ├── Cisco Workflows/       # Cisco Workflow JSON suite (7 workflows)
        ├── Python/                # Python REST reference scripts (11 scripts)
        ├── CML/                   # Cisco Modeling Labs topology and configs
        ├── Docs/                  # Reference documentation
        └── images/                # Supporting diagrams
```

---

## Projects

The `Projects/` folder contains the network configuration intent for each fabric deployment model supported by this suite. Each project is a self-contained GitOps source of truth consumed by the automation tooling in `Support/Resources/`.

### BGP\_EVPN

**Path:** [Projects/BGP\_EVPN/](Projects/BGP_EVPN/)

The BGP EVPN project provides configuration templates and settings for a BGP EVPN campus fabric deployment on Cisco Catalyst 9000 series switches.

| Subfolder | Purpose |
|-----------|---------|
| [Configs/](Projects/BGP_EVPN/Configs/) | Generated device configurations produced after provisioning runs |
| [Day0Templates/](Projects/BGP_EVPN/Day0Templates/) | PnP onboarding Jinja2 templates for zero-touch device commissioning |
| [DayNTBD/](Projects/BGP_EVPN/DayNTBD/) | Day-N templates under active development (not yet production) |
| [DayNTemplates/](Projects/BGP_EVPN/DayNTemplates/) | Production Day-N Jinja2 templates for post-onboarding configuration |
| [Settings/](Projects/BGP_EVPN/Settings/) | `settings.json` — site hierarchy, network settings, discovery, and credential intent |

**Day0 templates** cover L2/L3 PnP onboarding for Catalyst switches with EIGRP, OSPF, and seed automation variants.

**DayN templates** implement the full BGP EVPN fabric model using a layered Jinja2 architecture:

| Template Prefix | Role |
|----------------|------|
| `DEFN-*` | Data definition templates (VRF, loopbacks, overlay, multicast, ports, NAC, roles, VNI offsets) |
| `FUNC-*` | Reusable function templates (VRF lookup, client port logic) |
| `FABRIC-*` | Top-level fabric build templates that include DEFN and FUNC layers |
| `BGP-EVPN-BUILD.yml` | Composite template YAML definition ordering all FABRIC templates |

The composite YAML definition is consumed by the `GitOps-BuildCompositeTemplate-v3` Cisco Workflow and the `create_composite_template.py` Python script to assemble the ordered composite template in Catalyst Center.

### TRADITIONAL

**Path:** [Projects/TRADITIONAL/](Projects/TRADITIONAL/)

The TRADITIONAL project provides configuration templates and settings for conventional (non-EVPN) campus fabric deployments.

| Subfolder | Purpose |
|-----------|---------|
| [Configs/](Projects/TRADITIONAL/Configs/) | Generated device configurations produced after provisioning runs |
| [Day0Templates/](Projects/TRADITIONAL/Day0Templates/) | PnP onboarding Jinja2 templates for zero-touch device commissioning |
| [DayNTemplates/](Projects/TRADITIONAL/DayNTemplates/) | Production Day-N Jinja2 templates for modular post-onboarding configuration |
| [Settings/](Projects/TRADITIONAL/Settings/) | `settings.json` and `devices.json` — site and device intent for this project |

**Day0 templates** mirror the BGP\_EVPN set, covering L2/L3 PnP onboarding with EIGRP, OSPF, and seed variants.

**DayN templates** implement a modular Day-N build model:

| Template Prefix | Role |
|----------------|------|
| `DEFN-*` | Data definition templates (VLAN, port, ACL, sensitive info) |
| `BUILD-*` | Modular configuration build templates (AAA, access, ACL, app hosting, auto-description, autoconf, IBNS, interface macros, master build, security, stacking, system, VLAN) |

The `BUILD-MasterBuild.j2` template is the top-level composite entry point that includes all relevant BUILD modules for a device class.

---

## Support

The `Support/` folder contains two parallel structures: guided **Labs** for hands-on learning and step-by-step exercises, and **Resources** providing the full automation tooling implementations.

### Labs

**Path:** [Support/Labs/](Support/Labs/)

The Labs folder provides structured, guided exercises that walk through the full Catalyst Center automation lifecycle using both tooling approaches. Labs are aligned with DCLOUD sandbox environments for safe, reproducible practice.

> **Important:** Lab content in this repository is aligned with specific DCLOUD demonstrations that must be set up by a **Cisco Employee** or **Cisco Partner**. Contact your **Local Cisco Account Team** to schedule a DCLOUD session before starting a lab.

#### Lab — Cisco Workflows

**Path:** [Support/Labs/Lab - Cisco Workflows/](Support/Labs/Lab%20-%20Cisco%20Workflows/)

A structured, step-by-step lab that guides engineers through setting up and executing the Cisco Workflows automation suite against a DCLOUD or CML lab environment.

| Module | Topic |
|--------|-------|
| Orientation | Catalyst Center orientation, UI navigation, and API access setup |
| Hierarchy | Building site hierarchy via the Cisco Workflow |
| Settings | Assigning network settings and credentials via the Cisco Workflow |
| Discovery | Running device discovery via the Cisco Workflow |
| Templates | Synchronizing templates from GitHub via the Cisco Workflow |
| Archive | Configuration archiving and inventory review |
| Inventory | Retrieving and verifying network inventory |
| Command Run | Executing show commands against managed devices |

**Outcome:** Engineers can operate the full seven-workflow GitOps suite end-to-end against a live or simulated environment.

#### Lab — Ansible

**Path:** [Support/Labs/Lab - Ansible/](Support/Labs/Lab%20-%20Ansible/)

A structured, step-by-step lab that guides engineers through executing the Ansible playbook suite against a DCLOUD or CML lab environment.

| Module | Topic |
|--------|-------|
| Orientation | Ansible control node setup, inventory, and Catalyst Center connectivity |
| Hierarchy | Running `site_hierarchy.yml` to build site structure |
| Settings | Running `network_settings.yml` to apply site network settings |
| Discovery | Running `device_discovery.yml` to discover and import devices |
| Templates | Running `ansible-git-catc.yml` to synchronize GitHub templates |
| Archive | Configuration archiving and state review |
| Inventory | Querying and verifying managed device inventory |
| Command Run | Executing ad-hoc commands via Ansible against managed devices |

**Outcome:** Engineers can execute the full nine-playbook Ansible suite end-to-end and understand how each step interacts with the Catalyst Center API.

#### DCLOUD Lab Environment

Both labs are tested against the Cisco Enterprise Networks Hardware Sandbox in DCLOUD:

- [Cisco Enterprise Networks Hardware Sandbox — West DC (SJC)](https://dcloud2-sjc.cisco.com/content/catalogue?search=Enterprise%20Networks%20Hardware%20Sandbox&screenCommand=openFilterScreen)
- [Cisco Enterprise Networks Hardware Sandbox — East DC (RTP)](https://dcloud2-rtp.cisco.com/content/catalogue?search=Enterprise%20Networks%20Hardware%20Sandbox&screenCommand=openFilterScreen)

**DCLOUD session components:**

| Component | Specification |
|-----------|--------------|
| Catalyst Center | 2.3.7.10 or later |
| Identity Services Engine (ISE) | 3.4 Patch 3 or later |
| Script Server | Ubuntu 20.04 or later |
| Windows Jump Host | Windows 10 |
| Windows Server | 2019 (DNS, DHCP, AD) |
| Catalyst Switch | 9300 — IOS-XE 17.06.01 with EWC |
| Router | ISR 4451 — IOS-XE 17.06.01a |

### Resources

**Path:** [Support/Resources/](Support/Resources/)

The Resources folder is the complete automation implementation suite. It contains three parallel tooling paths, a shared CML lab environment, reference documentation, and supporting imagery.

**Full documentation:** [Support/Resources/README.md](Support/Resources/README.md)

| Folder | Tooling | Contents |
|--------|---------|---------|
| [Ansible/](Support/Resources/Ansible/) | Ansible playbooks | 9 ordered playbooks covering the full provisioning lifecycle |
| [Cisco Workflows/](Support/Resources/Cisco%20Workflows/) | Cisco Workflow JSON | 7 GitOps workflows importable into Catalyst Center Workflow Manager |
| [Python/](Support/Resources/Python/) | Python REST scripts | 11 numbered scripts mirroring the Ansible operations with raw API calls |
| [CML/](Support/Resources/CML/) | CML topology and configs | EVPN campus topology files, startup configs, and normalization script |
| [Docs/](Support/Resources/Docs/) | Reference documentation | Session reference materials |
| [images/](Support/Resources/images/) | Diagrams | CML topology and workflow diagrams |

---

## Quick Start

### Prerequisites

- Access to a Cisco Catalyst Center instance (2.3.7.10 or later) or a DCLOUD / CML lab environment
- A GitHub account with access to this repository (for GitOps workflows)
- One of the following installed on your control machine:
  - Ansible with the `cisco.catalystcenter` and `cisco.dnac` collections (for the Ansible path)
  - Python 3.9 or later (for the Python path)
  - Access to Cisco Catalyst Center Workflow Manager (for the Cisco Workflows path)

### Choosing a Tooling Path

| If you... | Use... |
|-----------|--------|
| Already use Ansible and want CI/CD integration | [Ansible suite](Support/Resources/Ansible/README.md) |
| Prefer GUI-driven, platform-native automation | [Cisco Workflows](Support/Resources/Cisco%20Workflows/README.md) |
| Want to learn the raw API or debug issues | [Python scripts](Support/Resources/Python/README.md) |
| Are new to the project and want a learning path | [CML lab](Support/Resources/CML/README.md) → Python → Ansible → Workflows |

### Selecting a Project

| If your fabric uses... | Use project... |
|------------------------|---------------|
| BGP EVPN with VXLAN underlay | [Projects/BGP\_EVPN/](Projects/BGP_EVPN/) |
| Traditional routed access (EIGRP/OSPF) | [Projects/TRADITIONAL/](Projects/TRADITIONAL/) |

Update `Settings/settings.json` in your chosen project with your site topology and connectivity parameters before running any tooling path.

---

## Tooling Paths

All three tooling paths execute the same logical sequence against Catalyst Center:

```
1. Build Site Hierarchy       (Areas → Buildings → Floors)
2. Apply Network Settings     (DNS, NTP, DHCP, SNMP, Syslog, AAA, banner)
3. Configure Credentials      (CLI, SNMP v2c R/W, NETCONF)
4. Run Device Discovery       (IP-range discovery, credential binding)
5. Assign Devices to Sites    (Site UUID assignment)
6. Synchronize Templates      (GitHub → Catalyst Center Template Hub)
7. Build Network Profile      (Switching profile with template bindings)
8. Provision Devices          (SDA provision, Day-N template deployment)
```

Each tooling path implements this sequence using its own execution model. See the Resources README for a full side-by-side comparison: [Support/Resources/README.md](Support/Resources/README.md).

---

## Lab Environment

For teams without a production Catalyst Center instance, the [CML resources](Support/Resources/CML/) provide a complete virtualized EVPN campus fabric for safe automation practice.

The CML lab provides:

- Pre-built EVPN campus topology (spine, leaf, border, core, firewall, DHCP, DMZ)
- Startup configurations with pre-staged IP addressing (`198.18.128.0/18`)
- Multiple topology versions for CML 2.9.1 and earlier releases
- A topology normalization script for backward compatibility

**Import and start the lab:** See [Support/Resources/CML/README.md](Support/Resources/CML/README.md) for full import and startup instructions.

**Recommended execution sequence for lab use:**

1. Import CML topology and start all nodes
2. Run Python scripts `1.0` through `8.0` to learn the raw API surface
3. Run Ansible playbooks `1.0` through `9.0` to experience the abstraction layer
4. Import and run the seven Cisco Workflow JSON files in Workflow Manager
5. Adapt `settings.json` and project templates to your production environment

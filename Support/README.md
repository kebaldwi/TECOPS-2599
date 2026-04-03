# Support — TECOPS-2599 Automation Suite

> **As-Built Documentation**
> **Authors:** Keith Baldwin — Solutions Engineer — Automation HyperSpecialist (kebaldwi@cisco.com), Igor Manassypov — Systems Engineer (imanassy@cisco.com)
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

This directory provides all guided learning, reference implementations, and production-ready automation resources that support project **TECOPS-2599** — Catalyst Center network orchestration via Cisco Workflows, Ansible, and Python. It is organized into two complementary sections: a structured **Labs** environment for hands-on learning and a **Resources** library for production tooling, reference implementations, and lab infrastructure.

---

## Table of Contents

1. [Business Overview](#business-overview)
2. [Support Structure](#support-structure)
3. [Labs](#labs)
   - [What It Solves](#what-it-solves)
   - [Lab Environment](#lab-environment)
   - [Lab Paths](#lab-paths)
   - [When to Use](#when-to-use-labs)
4. [Resources](#resources)
   - [What It Solves](#what-it-solves-1)
   - [Resource Summary](#resource-summary)
   - [When to Use](#when-to-use-resources)
5. [Labs vs Resources — Choosing the Right Starting Point](#labs-vs-resources--choosing-the-right-starting-point)
6. [Recommended Learning Path](#recommended-learning-path)

---

## Business Overview

TECOPS-2599 addresses a common enterprise and public-sector challenge: deploying and managing a Catalyst Center–managed network fabric at scale, consistently and repeatably, without manual GUI interaction.

Organisations face several operational pressures that this support suite is designed to resolve:

- **Speed to service** — new sites and devices must be commissioned faster than manual processes allow
- **Configuration consistency** — every device must reflect the same intent, regardless of who executed the change or when
- **Auditability** — every change must be traceable, repeatable, and reviewable by operations, security, and compliance teams
- **Risk reduction** — deployments must be idempotent so re-running automation does not cause outages or duplicate objects
- **Skill portability** — teams proficient in Ansible, Python, REST API, or Cisco-native workflows must each find a familiar entry point to the same automation objectives
- **Accelerated adoption** — engineers new to Catalyst Center automation need guided, structured learning before they can operate production tooling confidently

The support suite resolves all six pressures by pairing structured guided labs (for learning and skill building) with production-ready reference implementations (for deployment and operations) — all backed by a shared Cisco Modeling Labs (CML) virtual lab environment.

---

## Support Structure

```
Support/
├── Labs/                          # Guided step-by-step lab exercises
│   ├── Lab - Ansible/             # 8-module Ansible automation lab path
│   ├── Lab - Cisco Workflows/     # 8-module Cisco Workflows automation lab path
│   ├── DCLOUD.md                  # DCLOUD lab environment setup guide
│   └── README.md                  # Labs index and DCLOUD environment reference
└── Resources/                     # Production-ready automation implementations
    ├── Ansible/                   # 9 Ansible playbooks — full provisioning lifecycle
    ├── Cisco Workflows/           # 7 Cisco Workflow JSON files — GitOps provisioning
    ├── Python/                    # 12 Python REST API scripts — raw API reference
    ├── CML/                       # Cisco Modeling Labs topology and startup configs
    ├── Docs/                      # Reference documentation
    ├── images/                    # Supporting diagrams
    └── README.md                  # Resources index and tooling comparison
```

---

## Labs

### What It Solves

The Labs section provides structured, step-by-step guided exercises that take engineers from foundational Catalyst Center orientation through fully automated site provisioning and template deployment. Labs are designed to build confidence and operational competency before engineers work with production automation tooling.

Each lab path follows the same 8-module story arc — from orientation through hierarchy, settings, discovery, templates, archive, inventory, and command execution — mirroring the real provisioning sequence a production automation run would follow. This deliberate alignment means that skills built in the lab directly transfer to operating the tooling in `Resources/`.

**Business outcomes enabled:**

- Rapid Catalyst Center automation skill development without risk to production infrastructure
- Consistent, structured onboarding experience for new team members across the project
- Live practice environment for demonstrating Catalyst Center automation capabilities to stakeholders
- Validation of operator understanding before granting access to production automation tooling
- Cross-tooling fluency — engineers experience both the Ansible and Cisco Workflows paths covering the same use cases

---

### Lab Environment

All labs are designed for use with the **Cisco DCLOUD** enterprise network sandbox environment. DCLOUD provides an on-demand, pre-staged virtual lab with all required components available without hardware shipping, licensing overhead, or production impact.

> **Important:** Lab content in this repository is aligned with specific DCLOUD demonstrations that must be set up by a **Cisco Employee** or **Cisco Partner**. Contact your local Cisco Account Team to schedule and access the DCLOUD session.

**DCLOUD session components:**

| Component | Specification |
|-----------|--------------|
| Catalyst Center | 2.3.7.10 or later |
| Identity Services Engine (ISE) | 3.4 Patch 3 or later |
| Script Server | Ubuntu 20.04 or later |
| Windows Jump Host | Windows 10 |
| Windows Server | 2019 (identity, DHCP, DNS) |
| Virtual Router | Catalyst 8000v — IOS-XE 17.06.01a |
| Virtual Switch | Catalyst 9300v — IOS-XE 17.12.01 |

**DCLOUD sandbox locations:**

- [Cisco Enterprise Networks Hardware Sandbox — West DC (San Jose)](https://DCLOUD2-sjc.cisco.com/content/catalogue?search=Enterprise%20Networks%20Hardware%20Sandbox&screenCommand=openFilterScreen)
- [Cisco Enterprise Networks Hardware Sandbox — East DC (RTP)](https://DCLOUD2-rtp.cisco.com/content/catalogue?search=Enterprise%20Networks%20Hardware%20Sandbox&screenCommand=openFilterScreen)

For full DCLOUD environment preparation steps see [DCLOUD.md](Labs/DCLOUD.md).

---

### Lab Paths

The Labs section contains two parallel lab paths. Both cover identical use cases and follow the same 8-module structure — engineers choose the path that matches their tooling preference or follow both to build cross-tooling fluency.

#### Lab — Ansible

**Location:** [Labs/Lab - Ansible/](Labs/Lab%20-%20Ansible/)
**Full documentation:** [Labs/Lab - Ansible/README.md](Labs/Lab%20-%20Ansible/README.md)

An 8-module guided lab that teaches Catalyst Center automation using Ansible REST API collections. Engineers build a complete site from scratch using structured playbook-driven use cases mirroring the production Ansible suite in `Resources/Ansible/`.

| Module | Topic | What Engineers Learn |
|--------|-------|---------------------|
| 0 | Orientation | Ansible environment setup, API authentication, Catalyst Center connectivity |
| 1 | Building Hierarchy | Creating areas, buildings, and floors via Ansible collection modules |
| 2 | Settings and Credentials | Applying network settings and global credentials per site |
| 3 | Device Discovery | Running discovery jobs and adding devices to inventory |
| 4 | Template Deployment | Pushing Jinja2 templates and composite builds to managed devices |
| 5 | Configuration Archive | Archiving device running configurations via Catalyst Center |
| 6 | Network Inventory | Retrieving and interpreting live device inventory from Catalyst Center |
| 7 | Command Runner | Executing show commands across managed devices from Catalyst Center |

#### Lab — Cisco Workflows

**Location:** [Labs/Lab - Cisco Workflows/](Labs/Lab%20-%20Cisco%20Workflows/)
**Full documentation:** [Labs/Lab - Cisco Workflows/README.md](Labs/Lab%20-%20Cisco%20Workflows/README.md)

An 8-module guided lab that teaches the same Catalyst Center automation use cases using Cisco Workflow Manager (SecureX / XDR) REST API collections. Engineers follow the same story arc as the Ansible lab, experiencing the platform-native GUI-driven workflow execution path that mirrors the production Cisco Workflows suite in `Resources/Cisco Workflows/`.

| Module | Topic | What Engineers Learn |
|--------|-------|---------------------|
| 0 | Orientation | Workflow Manager setup, GitHub integration, API authentication |
| 1 | Building Hierarchy | Hierarchy creation driven by GitHub-sourced settings |
| 2 | Settings and Credentials | Site settings and credential application via workflow steps |
| 3 | Device Discovery | Discovery job submission and device assignment |
| 4 | Template Deployment | Template sync from GitHub and composite template deployment |
| 5 | Configuration Archive | Archiving configurations with workflow-driven task verification |
| 6 | Network Inventory | Inventory retrieval and display via workflow output |
| 7 | Command Runner | Show command execution across devices from workflow steps |

---

### When to Use Labs

- **Onboarding new engineers** to the TECOPS-2599 project — work through the full 8-module path before operating production tooling
- **Demonstrating automation capabilities** to customers or stakeholders in a safe, resettable environment
- **Cross-training** Ansible operators on the Cisco Workflows path or vice versa
- **Troubleshooting skill gaps** — use the lab to isolate and reproduce API or template behavior without touching production
- **Instructor-led training** — both lab paths are designed for DevNet Test Drive and Cisco Live session delivery formats

---

## Resources

### What It Solves

The Resources section contains production-ready reference implementations of the complete Catalyst Center automation lifecycle across three parallel tooling paths — Ansible, Cisco Workflows, and Python — backed by a Cisco Modeling Labs (CML) virtual environment and reference documentation. All three paths produce identical outcomes in Catalyst Center, enabling teams to choose based on existing skill sets and operational models.

Each tooling path is a complete, self-contained implementation that:

- Reads configuration intent from a shared `settings.json` source of truth in GitHub
- Executes the full 7–9 step provisioning sequence (hierarchy → settings → credentials → discovery → templates → profile → provisioning)
- Is idempotent — safe to re-run without creating duplicate objects or causing outages
- Targets both the **BGP\_EVPN** and **TRADITIONAL** project configurations interchangeably

**Business outcomes enabled:**

- Commissioning a new site end-to-end in a single automated run — no GUI interaction required
- Enforcing configuration baseline on existing sites by re-running idempotent automation
- Detecting and correcting configuration drift without manual audit
- GitOps-driven template management — Jinja2 templates in GitHub are automatically synchronized to Catalyst Center
- Three-path flexibility — Ansible for pipeline teams, Cisco Workflows for platform-native operators, Python for developers and API troubleshooters

---

### Resource Summary

**Full documentation:** [Resources/README.md](Resources/README.md)

| Folder | Tooling | Primary Audience | Deployment Method |
|--------|---------|-----------------|-------------------|
| [Ansible/](Resources/Ansible/) | Ansible + cisco.catalystcenter collection | Network DevOps, CI/CD pipeline teams | `ansible-playbook` CLI or AWX/AAP |
| [Cisco Workflows/](Resources/Cisco%20Workflows/) | Cisco SecureX / XDR Workflow Manager | Cisco platform operators, NOC teams | Catalyst Center Workflow Manager |
| [Python/](Resources/Python/) | Pure Python + REST | Developers, troubleshooters, API learners | Direct Python execution |
| [CML/](Resources/CML/) | Cisco Modeling Labs | Lab engineers, training leads | CML server import |
| [Docs/](Resources/Docs/) | Reference documentation | All personas | Reference only |

#### Ansible — 9 Playbooks

| # | Playbook | Catalyst Center Outcome |
|---|----------|------------------------|
| 1.0 | `site_hierarchy.yml` | Areas, Buildings, and Floors created in correct parent-before-child order |
| 2.0 | `network_settings.yml` | DNS, NTP, Syslog, SNMP, AAA, and banner applied per site |
| 3.0 | `credentials.yml` | CLI, SNMP v2c R/W, and NETCONF global credentials created and assigned |
| 4.0 | `device_discovery.yml` | Devices discovered and added to inventory |
| 5.0 | `assign_to_site.yml` | Devices placed under their designated site in the hierarchy |
| 6.0 | `ansible-git-catc.yml` | Jinja2 and composite templates synced from GitHub into the Template Hub |
| 7.0 | `network_profile.yml` | Switching Network Profile created and bound to sites with Day-N templates |
| 8.0 | `provision_devices.yml` | Devices provisioned to site; idempotent skip for already-provisioned devices |
| 9.0 | `deploy_composite_template.yml` | Composite Day-N templates deployed with async task verification |

#### Cisco Workflows — 7 GitOps Workflows

| # | Workflow | JSON File | Catalyst Center Outcome |
|---|----------|-----------|------------------------|
| 1.0 | Build Hierarchy | `GitOps-BuildHierarchy-v3.json` | Areas, Buildings, and Floors created from GitHub settings |
| 2.0 | Build Settings | `GitOps-BuildSettings-v3.json` | Network settings and credentials applied per site |
| 3.0 | Device Discovery | `GitOps-DeviceDiscovery-v3.json` | Discovery jobs executed and devices assigned to sites |
| 4.0 | Build Templates | `GitOps-BuildTemplates-v3.json` | Day-N Jinja2 templates synchronized from GitHub into Template Hub |
| 5.0 | Composite Templates | `GitOps-BuildCompositeTemplate-v3.json` | Composite template built, assembled, and committed |
| 6.0 | Network Profile | `GitOps-BuildNetworkProfile-v3.json` | Switching profile created and bound to sites with template IDs |
| 7.0 | Provisioning | `GitOps-Provisioning-v3.json` | Devices provisioned via SDA and composite template deployed |

#### Python — 12 REST API Scripts

| # | Script | Purpose |
|---|--------|---------|
| 1.0 | `site_hierarchy.py` | Create Area, Building, and Floor site paths from settings data |
| 2.0 | `network_settings.py` | Build and apply per-site network settings payloads |
| 3.0 | `credentials.py` | Create missing CLI, SNMP, and NETCONF global credentials |
| 4.0 | `device_discovery.py` | Submit discovery jobs from device list entries |
| 5.0 | `assign_to_site.py` | Group devices by hierarchy path and assign to site UUIDs |
| 6.1 | `authenticate.py` | Obtain JWT token for subsequent API calls |
| 6.2 | `create_project.py` | Idempotent template-project lookup and creation |
| 6.3 | `create_member_template.py` | Create and commit a Jinja2 member template |
| 6.4 | `create_composite_template.py` | Create and commit a composite template from member list |
| 7.0 | `network_profile.py` | Build switching network profile payloads |
| 8.0 | `deploy_composite.py` | Deploy composite template to managed devices |
| — | `common/helpers.py` | Shared HTTP, auth, config-loading, and task-polling helpers |

---

### When to Use Resources

- **Ansible** — your team uses Ansible for infrastructure automation or operates AWX / Ansible Automation Platform pipelines
- **Cisco Workflows** — your team works within the Cisco platform and prefers native GUI-driven workflow orchestration with visual execution tracking
- **Python** — you need to diagnose API errors, prototype new automation behavior, or onboard developers to the Catalyst Center REST API surface
- **CML** — you need a safe, resettable virtual lab to validate automation changes before a production change window
- **Docs** — you need standalone reference materials for a specific component or capability

---

## Labs vs Resources — Choosing the Right Starting Point

| Situation | Start Here |
|-----------|-----------|
| New to Catalyst Center automation — need guided learning | [Labs/](Labs/) |
| Familiar with Ansible — ready to deploy | [Resources/Ansible/](Resources/Ansible/) |
| Cisco platform operator — want GUI-driven workflow execution | [Resources/Cisco Workflows/](Resources/Cisco%20Workflows/) |
| Developer or troubleshooter — need raw API examples | [Resources/Python/](Resources/Python/) |
| Need a safe lab environment to test against | [Resources/CML/](Resources/CML/) |
| Evaluating which tooling path to use | [Resources/README.md — Tooling Comparison](Resources/README.md#tooling-comparison) |

---

## Recommended Learning Path

For teams new to this project the following sequence builds understanding progressively:

1. **Set up the lab environment** — Book a DCLOUD session, follow [DCLOUD.md](Labs/DCLOUD.md) to prepare the environment, and confirm connectivity to Catalyst Center.

2. **Complete the guided lab** — Work through either [Lab - Ansible](Labs/Lab%20-%20Ansible/) or [Lab - Cisco Workflows](Labs/Lab%20-%20Cisco%20Workflows/) end-to-end. Both cover the same 8 use cases — choose the path that matches your tooling background.

3. **Stand up the CML environment** — Import the CML topology from [Resources/CML/](Resources/CML/), start all nodes, and confirm reachability using the startup configurations.

4. **Explore the Python examples** — Run the Python scripts in order against the CML environment to understand the raw API operations behind each automation step. See [Resources/Python/README.md](Resources/Python/README.md).

5. **Run the production tooling** — Execute your chosen tooling path (Ansible playbooks or Cisco Workflows) against the CML environment end-to-end. See [Resources/README.md](Resources/README.md) for the full tooling comparison and when-to-use guidance.

6. **Adapt to your environment** — Update `settings.json` with your production topology and credential references in the relevant project folder ([BGP\_EVPN](../Projects/BGP_EVPN/Settings/) or [TRADITIONAL](../Projects/TRADITIONAL/Settings/)), then run the tooling path that matches your operational model.
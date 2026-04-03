# Resources — TECOPS-2599 Automation Suite

> **As-Built Documentation**
> **Authors:** Keith Baldwin — Solutions Engineer — Automation HyperSpecialist (kebaldwi@cisco.com), Igor Manassypov — Systems Engineer (imanassy@cisco.com)
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

This directory is the root of all automation resources, reference implementations, lab infrastructure, and supporting documentation for project **TECOPS-2599**. It is structured to serve multiple operational personas — network engineers, DevOps practitioners, and automation architects — with purpose-built content for each tooling layer used in the project.

---

## Table of Contents

1. [Business Overview](#business-overview)
2. [Resource Summary](#resource-summary)
3. [Ansible](#ansible)
   - [What It Solves](#what-it-solves)
   - [Contents](#ansible-contents)
   - [When to Use](#when-to-use-ansible)
4. [Cisco Workflows](#cisco-workflows)
   - [What It Solves](#what-it-solves-1)
   - [Contents](#cisco-workflows-contents)
   - [When to Use](#when-to-use-cisco-workflows)
5. [Python](#python)
   - [What It Solves](#what-it-solves-2)
   - [Contents](#python-contents)
   - [When to Use](#when-to-use-python)
6. [CML](#cml)
   - [What It Solves](#what-it-solves-3)
   - [Contents](#cml-contents)
   - [When to Use](#when-to-use-cml)
7. [Docs](#docs)
8. [Tooling Comparison](#tooling-comparison)
9. [Recommended Learning Path](#recommended-learning-path)

---

## Business Overview

TECOPS-2599 addresses a common enterprise and public-sector challenge: deploying and managing a Catalyst Center–managed network fabric at scale, consistently and repeatably, without manual GUI interaction.

Organisations face several operational pressures:

- **Speed to service** — new sites and devices must be commissioned faster than manual processes allow
- **Configuration consistency** — every device must reflect the same intent, regardless of who executed the change or when
- **Auditability** — every change must be traceable, repeatable, and reviewable by operations, security, and compliance teams
- **Risk reduction** — deployments must be idempotent so re-running automation does not cause outages or duplicate objects
- **Skill portability** — teams already proficient in Ansible, Python, or Cisco-native workflows must each find a familiar entry point to the same automation objectives

This resource suite addresses all five pressures through three parallel tooling paths — Ansible, Cisco Workflows, and Python — backed by a shared Cisco Modeling Labs (CML) lab environment and a supporting documentation layer. All three tooling paths produce the same outcome in Catalyst Center, enabling teams to choose the approach that best fits their operational model and existing skill set.

---

## Resource Summary

| Folder | Tooling | Primary Audience | Deployment Method |
|--------|---------|-----------------|-------------------|
| [Ansible/](Ansible/) | Ansible + cisco.catalystcenter collection | Network DevOps, CI/CD pipeline teams | `ansible-playbook` CLI or AWX/AAP |
| [Cisco Workflows/](Cisco%20Workflows/) | Cisco SecureX / XDR Workflow Manager | Cisco platform operators, NOC teams | Catalyst Center Workflow Manager |
| [Python/](Python/) | Pure Python + REST | Developers, troubleshooters, API learners | Direct Python execution |
| [CML/](CML/) | Cisco Modeling Labs | Lab engineers, training leads | CML server import |
| [Docs/](Docs/) | Reference documentation | All personas | Reference only |
| [images/](images/) | Supporting diagrams | Documentation support | Reference only |

---

## Ansible

### What It Solves

The Ansible suite provides a fully declarative, idempotent automation path for the complete Catalyst Center device onboarding lifecycle. It is designed for teams that operate infrastructure-as-code pipelines using Ansible playbooks and want to integrate Catalyst Center provisioning into existing CI/CD workflows (AWX, Ansible Automation Platform, GitHub Actions).

Each playbook targets one well-scoped Catalyst Center capability. Playbooks can be run individually for scoped changes or chained in sequence for full-site commissioning. All playbooks reference a shared `settings.json` and `devices.json` source-of-truth, ensuring consistent intent across runs.

**Business outcomes enabled:**

- Commissioning a new site — hierarchy, settings, credentials, discovery, provisioning — in a single pipeline execution
- Enforcing configuration baseline on existing sites without manual GUI interaction
- Detecting and correcting configuration drift by re-running idempotent playbooks
- Integrating network provisioning into broader infrastructure-as-code pipelines alongside compute and cloud resources

### Ansible Contents

**Full documentation:** [Ansible/README.md](Ansible/README.md)

| # | Playbook | File | Catalyst Center Outcome |
|---|----------|------|------------------------|
| 1.0 | Site Hierarchy | `site_hierarchy.yml` | Areas, Buildings, and Floors created in correct parent-before-child order |
| 2.0 | Network Settings | `network_settings.yml` | DNS, NTP, Syslog, SNMP, AAA, and banner applied per site |
| 3.0 | Device Credentials | `credentials.yml` | CLI, SNMP v2c R/W, and NETCONF global credentials created and assigned |
| 4.0 | Device Discovery | `device_discovery.yml` | Devices discovered and added to inventory |
| 5.0 | Assign to Site | `assign_to_site.yml` | Devices placed under their designated site in the hierarchy |
| 6.0 | Template GitOps | `ansible-git-catc.yml` | Jinja2 and composite templates synced from GitHub into a CatC template project |
| 7.0 | Network Profile | `network_profile.yml` | Switching Network Profile created and assigned to sites with Day-N templates |
| 8.0 | Provision Devices | `provision_devices.yml` | Devices provisioned to site via SDA; idempotent skip for already-provisioned devices |
| 9.0 | Composite Deployment | `deploy_composite_template.yml` | Composite Day-N templates deployed to managed devices with async task verification |

The suite uses the `cisco.catalystcenter` and `cisco.dnac` Ansible collections. Folder `6.0` additionally integrates with a GitHub repository as a template source, enabling GitOps-driven template synchronization.

### When to Use Ansible

- Your team already uses Ansible for infrastructure automation
- You need to integrate Catalyst Center provisioning into an AWX or Ansible Automation Platform pipeline
- You require role-based access control and Ansible Vault for credential management
- You want native Ansible state management (`present`, `absent`, `merged`, `deleted`) for idempotent operations
- You are building CI/CD-triggered provisioning triggered from code commits or pipeline events

---

## Cisco Workflows

### What It Solves

The Cisco Workflows suite provides a GitOps-native automation path for the same Catalyst Center provisioning lifecycle, using Cisco SecureX / XDR Workflow Manager as the execution engine. This path is designed for teams working within the Cisco platform ecosystem who prefer a GUI-driven, low-code workflow approach with visual execution tracking, native Catalyst Center task integration, and built-in retry and error handling.

Workflows read all configuration intent directly from a GitHub repository, making GitHub the single source of truth for site topology, network settings, Jinja2 templates, and composite template definitions. Every run reflects the current state of the repository, enabling GitOps-driven drift detection and correction.

**Business outcomes enabled:**

- Platform-native provisioning without external tooling dependencies (no Ansible control node required)
- Real-time visual execution status per workflow step in the Cisco workflow platform
- GitOps-driven template management — templates in GitHub are automatically synchronized to Catalyst Center on each workflow run
- Composite template lifecycle management — YAML-defined composite structures are built and committed automatically
- Deterministic site profile and provisioning automation from a single shared settings file

### Cisco Workflows Contents

**Full documentation:** [Cisco Workflows/README.md](Cisco%20Workflows/README.md)

| # | Workflow | JSON File | Catalyst Center Outcome |
|---|----------|-----------|------------------------|
| 1.0 | Build Hierarchy | `GitOps-BuildHierarchy-v3.json` | Areas, Buildings, and Floors created from GitHub settings |
| 2.0 | Build Settings | `GitOps-BuildSettings-v3.json` | Network settings and credentials applied per site |
| 3.0 | Device Discovery | `GitOps-DeviceDiscovery-v3.json` | Discovery jobs executed and devices assigned to sites |
| 4.0 | Build Templates | `GitOps-BuildTemplates-v3.json` | Day-N Jinja2 templates synchronized from GitHub into Template Hub |
| 5.0 | Composite Templates | `GitOps-BuildCompositeTemplate-v3.json` | Composite template built, assembled, and committed |
| 6.0 | Network Profile | `GitOps-BuildNetworkProfile-v3.json` | Switching profile created and bound to sites with template IDs |
| 7.0 | Provisioning | `GitOps-Provisioning-v3.json` | Devices provisioned via SDA and composite template deployed |

Each workflow bundles its own subworkflows and GitHub utility functions inline in the JSON definition. Workflows are imported into Catalyst Center Workflow Manager directly from the JSON files.

### When to Use Cisco Workflows

- Your team operates primarily within the Cisco platform and prefers native GUI-driven workflow orchestration
- You want visual step-by-step execution status without writing or running scripts
- Your GitHub repository is already the source of truth for network configuration and template content
- You need built-in Catalyst Center task polling and error branching without writing retry logic
- Your organization's change management requires an auditable, platform-native execution record

---

## Python

### What It Solves

The Python suite provides direct REST API reference implementations that expose the raw Catalyst Center HTTP operations behind every Ansible playbook and Cisco Workflow step. This path is designed for developers, automation engineers, and troubleshooters who need to understand, debug, or extend the underlying API behavior outside of any abstraction layer.

Each Python script corresponds to a numbered Ansible operation. Running a script directly against a Catalyst Center instance produces the same outcome as the corresponding Ansible playbook or Cisco Workflow step, making the scripts useful for:

- Understanding exactly which API calls each automation step makes
- Diagnosing issues when Ansible collection modules or workflow actions produce unexpected results
- Prototyping new automation behavior before encoding it in a playbook or workflow
- Building lightweight custom automation tools that call Catalyst Center REST APIs directly

**Business outcomes enabled:**

- Faster root-cause analysis when abstraction layers obscure API errors
- Rapid prototyping of new provisioning capabilities without full playbook development cycle
- Developer onboarding to the Catalyst Center API surface without reading full API documentation
- Reusable helper library (`common/helpers.py`) for authentication, task polling, and HTTP session management

### Python Contents

**Full documentation:** [Python/README.md](Python/README.md)

| # | Script | Purpose |
|---|--------|---------|
| 1.0 | `site_hierarchy.py` | Create Area, Building, and Floor site paths from settings data |
| 2.0 | `network_settings.py` | Build and apply per-site network settings payloads |
| 3.0 | `credentials.py` | Create missing CLI, SNMP, and NETCONF global credentials |
| 4.0 | `device_discovery.py` | Submit discovery jobs from device list entries |
| 5.0 | `assign_to_site.py` | Group devices by hierarchy path and assign to site UUIDs |
| 6.1 | `authenticate.py` | Obtain JWT token (`X-Auth-Token`) for subsequent API calls |
| 6.2 | `create_project.py` | Idempotent template-project lookup and creation |
| 6.3 | `create_member_template.py` | Create and commit a Jinja2 member template |
| 6.4 | `create_composite_template.py` | Create and commit a composite template from member list |
| 7.0 | `network_profile.py` | Build switching network profile payloads |
| 8.0 | `deploy_composite.py` | Deploy composite template to managed devices |
| — | `common/helpers.py` | Shared HTTP, auth, config-loading, and task-polling helpers |

All scripts are driven by the same environment variables (`CATC_HOST`, `CATC_USERNAME`, `CATC_PASSWORD`) and reference the same `settings.json` used by the Ansible and Cisco Workflow suites.

### When to Use Python

- You need to diagnose an API error not surfaced clearly by Ansible or a Cisco Workflow
- You are onboarding developers to the Catalyst Center REST API and need clear, annotated examples
- You want to prototype a new provisioning capability before committing it to a playbook or workflow
- You are building a custom integration that calls Catalyst Center APIs directly from application code

---

## CML

### What It Solves

The Cisco Modeling Labs (CML) resources provide a fully virtualized lab environment that replicates the target network topology used throughout the project. The lab enables safe testing of automation against simulated devices before production deployment.

The CML folder contains everything needed to stand up a representative EVPN campus fabric — topology definitions, startup configurations for all nodes, a topology normalization script for older CML versions, and a visualization diagram.

**Business outcomes enabled:**

- Zero-risk validation of all Ansible playbooks, Cisco Workflows, and Python scripts before touching production infrastructure
- Consistent lab baseline across the team — every engineer imports the same topology and starts from the same known state
- Rapid iteration on automation logic — topology can be reset and re-commissioned in minutes
- Training and demonstration capability — the same lab used for development doubles as a Cisco Live session environment

### CML Contents

**Full documentation:** [CML/README.md](CML/README.md)

| Resource | Path | Description |
|----------|------|-------------|
| EVPN Campus Topology v2 | `Topology/EVPN_Campus_v2.yaml` | Recommended topology for CML 2.9.1 and later |
| EVPN Campus Topology v2 Normalized | `Topology/EVPN_Campus_v2_normalized.yaml` | Pre-normalized topology for CML earlier than 2.9.1 |
| Enterprise Sandbox Topology v1 | `Topology/EN-Sandbox-Lab-v1.yaml` | Alternative enterprise network sandbox layout |
| Startup Configurations | `Startup Configs/` | Pre-staged IOS-XE startup configs for all nodes |
| Normalization Script | `Scripts/cml_normalize.py` | Python utility to normalize topology files for older CML versions |
| Topology Diagram | `../images/cml_v2_topology.png` | Visual diagram of the v2 EVPN campus topology |

The startup configurations provide the IP addressing baseline (`198.18.128.0/18` addressing range) and initial routing state so that automation targets are reachable from the control plane immediately on lab start without additional manual configuration.

### When to Use CML

- Validating automation changes in a safe environment before a production change window
- Recreating a consistent known-good state after a failed automation run for debugging
- Demonstrating the full provisioning lifecycle during training or Cisco Live sessions
- Onboarding new team members to the project topology and automation flows

---

## Docs

The `Docs/` folder contains reference documentation for the TECOPS-2599 session.

**Full documentation:** [Docs/README.md](Docs/README.md)

This folder is intended for standalone reference materials that support the automation suite but do not belong in any single tooling subfolder.

---

## Tooling Comparison

The three automation paths — Ansible, Cisco Workflows, and Python — all produce the same outcome in Catalyst Center. The table below summarizes the key operational differences to guide tooling selection.

| Dimension | Ansible | Cisco Workflows | Python |
|-----------|---------|----------------|--------|
| Execution model | CLI / AWX / AAP pipeline | Catalyst Center Workflow Manager GUI | Direct script execution |
| Primary audience | DevOps, pipeline engineers | Cisco platform operators, NOC | Developers, troubleshooters |
| Abstraction level | Collection modules (high) | Workflow steps with subworkflows (high) | Raw REST API (low) |
| Idempotency | Native via Ansible state model | Enforced via FORCE Update flag and ID checks | Manual, per-script logic |
| Source of truth | `settings.json` + `devices.json` files | GitHub repository (GitOps) | Environment variables + `settings.json` |
| CI/CD integration | Native (AWX, AAP, GitHub Actions) | GitHub trigger via webhook possible | Custom pipeline scripting required |
| Credential management | Ansible Vault, AWX credentials | SecureX / XDR credential store | Environment variables |
| Execution visibility | Ansible output / AWX job logs | Workflow Manager step-by-step visual | Console stdout |
| Best for | Pipeline-driven, repeatable fleet ops | Platform-native, GUI-auditable ops | API debugging, prototyping, learning |

---

## Recommended Learning Path

For teams new to this project the following sequence builds understanding progressively:

1. **Stand up the lab** — Import the CML topology, start all nodes, and confirm reachability using the startup configurations in [CML/](CML/).

2. **Explore the Python examples** — Run the Python scripts in order (`1.0` through `8.0`) against the CML environment to understand the raw API calls and the data structures each step requires. See [Python/README.md](Python/README.md).

3. **Run the Ansible suite** — Execute the Ansible playbooks in order (`1.0` through `9.0`) against the same CML environment. Observe how the collection modules abstract the same API behavior seen in step 2. See [Ansible/README.md](Ansible/README.md).

4. **Import and run the Cisco Workflows** — Import the seven workflow JSON files into Catalyst Center Workflow Manager and execute them in order against the CML environment. Observe the GitOps pull and task-level execution status. See [Cisco Workflows/README.md](Cisco%20Workflows/README.md).

5. **Adapt to your environment** — Update `settings.json` (and `devices.json` for Ansible) with your production topology and credential references, then run the tooling path that matches your operational model.

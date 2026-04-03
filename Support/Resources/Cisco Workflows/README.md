# Cisco Catalyst Center - GitOps Workflow Suite

> As-Built Documentation
> Authors: Keith Baldwin - Solutions Engineer - Automation HyperSpecialist (kebaldwi@cisco.com)
> Copyright (c) 2024-2026 Cisco Systems, Inc. All rights reserved.

This document describes the complete Cisco Catalyst Center GitOps workflow suite under this folder. The suite consists of seven ordered workflows that automate site foundation, settings and credentials, discovery and assignment, template synchronization, composite template construction, profile binding, and final composite deployment.

---

## Table of Contents

1. [Suite Overview](#suite-overview)
2. [Business Drivers](#business-drivers)
3. [Provisioning Workflow](#provisioning-workflow)
4. [Workflow Reference](#workflow-reference)
   - [1.0 - Site Hierarchy](#10---site-hierarchy)
   - [2.0 - Settings and Credentials](#20---settings-and-credentials)
   - [3.0 - Device Discovery and Assign](#30---device-discovery-and-assign)
   - [4.0 - Templates GitHub Integration](#40---templates-github-integration)
   - [5.0 - Templates Composite](#50---templates-composite)
   - [6.0 - Network Profile](#60---network-profile)
   - [7.0 - Provision Composite](#70---provision-composite)
5. [Input Data Sources](#input-data-sources)
6. [Installation Options](#installation-options)
7. [Meraki Free Account Setup (Optional Lab On-Ramp)](#meraki-free-account-setup-optional-lab-on-ramp)
8. [Ordering and Dependencies](#ordering-and-dependencies)

---

## Suite Overview

| # | Workflow | File | Outcome in Catalyst Center |
|---|----------|------|----------------------------|
| 1.0 | [Site Hierarchy](1.0-Cisco-Catalyst-Center-Site-Hierarchy/) | `GitOps-BuildHierarchy-v3.json` | Areas, buildings, and floors created in deterministic order |
| 2.0 | [Settings and Credentials](2.0-Cisco-Catalyst-Center-Settings-and-Credentials/) | `GitOps-BuildSettings-v3.json` | Site network settings and credential objects applied and assigned |
| 3.0 | [Device Discovery and Assign](3.0-Cisco-Catalyst-Center-Device-Discovery-and-Assign/) | `GitOps-DeviceDiscovery-v3.json` | Discovery jobs execute and discovered devices are assigned to target sites |
| 4.0 | [Templates GitHub Integration](4.0-Cisco-Catalyst-Center-Templates-Github-integration/) | `GitOps-BuildTemplates-v3.json` | DayN member templates synchronized from GitHub into CatC project |
| 5.0 | [Templates Composite](5.0-Cisco-Catalyst-Center-Templates-Composite/) | `GitOps-BuildCompositeTemplate-v3.json` | Composite template graph created/updated and committed |
| 6.0 | [Network Profile](6.0-Cisco-Catalyst-Center-Network-Profile/) | `GitOps-BuildNetworkProfile-v3.json` | Switching network profile bound to site with Day0 and DayN template IDs |
| 7.0 | [Provision Composite](7.0-Cisco-Catalyst-Center-Provision-Composite/) | `GitOps-Provisioning-v3.json` | Devices provisioned (or re-provisioned) and composite template deployed |

---

## Business Drivers

This workflow suite is designed to support enterprise and public-sector operational goals:

1. Speed to service
- Compresses multi-team manual provisioning steps into an ordered, repeatable workflow chain.
- Reduces deployment lead time for new sites and pods.

2. Operational consistency
- Enforces a single source of truth from version-controlled project settings and template artifacts.
- Reduces configuration drift across locations by reusing deterministic automation paths.

3. Risk reduction
- Uses idempotent, API-driven operations with explicit dependency ordering and task polling.
- Lowers change-failure rates caused by skipped prerequisites or inconsistent execution order.

4. Governance and auditability
- Every change to topology intent and template content can be traced to Git history and workflow execution logs.
- Supports CAB and compliance reporting with reproducible run outcomes.

5. Scale enablement
- Supports multi-device and multi-site growth without proportional growth in manual effort.
- Standardizes onboarding and DayN rollout patterns across pods and regions.

---

## Provisioning Workflow

The diagram below shows the complete end-to-end flow across workflows 1.0 through 7.0, the resources each stage produces, and the hard dependencies that gate the final deployment stage.

![Provisioning Workflow](DIAGRAMS/provisioning-workflow.png)

Source: [DIAGRAMS/provisioning-workflow.mmd](DIAGRAMS/provisioning-workflow.mmd)

Color coding:

| Color | Meaning |
|-------|---------|
| Blue | Workflow stages, input source, and intermediate Catalyst Center resources |
| Green | Final deployed state |
| Red dashed | Dependency and ordering constraints |

---

## Workflow Reference

### 1.0 - Site Hierarchy

Workflow folder: [1.0-Cisco-Catalyst-Center-Site-Hierarchy](1.0-Cisco-Catalyst-Center-Site-Hierarchy/)

Function:
- Creates and updates site hierarchy entities from project settings.
- Produces the structural dependency required by all downstream workflows.

Primary outcome:
- Valid site path objects exist and can be resolved to site IDs by later workflows.

Utilization statement:
- Use this workflow when onboarding a new region, pod, or building structure, or whenever hierarchy drift must be corrected before any site-scoped operation.

### 2.0 - Settings and Credentials

Workflow folder: [2.0-Cisco-Catalyst-Center-Settings-and-Credentials](2.0-Cisco-Catalyst-Center-Settings-and-Credentials/)

Function:
- Applies DNS, DHCP, NTP, SNMP, syslog, banner, AAA, and credential definitions per site entry.

Primary outcome:
- Site-level settings baseline and credential assignment are in place for discovery and operations.

Utilization statement:
- Use this workflow to enforce day-0 operational standards (management services and access credentials) before discovery and provisioning at scale.

### 3.0 - Device Discovery and Assign

Workflow folder: [3.0-Cisco-Catalyst-Center-Device-Discovery-and-Assign](3.0-Cisco-Catalyst-Center-Device-Discovery-and-Assign/)

Function:
- Resolves credential UUIDs, executes discovery jobs, polls task status, and assigns discovered devices to the site hierarchy.

Primary outcome:
- Devices are managed and site-assigned, enabling profile and deployment stages.

Utilization statement:
- Use this workflow when adding new switches or refreshing inventory to ensure all targets are discoverable, trusted, and mapped to the correct site scope.

### 4.0 - Templates GitHub Integration

Workflow folder: [4.0-Cisco-Catalyst-Center-Templates-Github-integration](4.0-Cisco-Catalyst-Center-Templates-Github-integration/)

Function:
- Pulls DayN template artifacts from GitHub, dependency-sorts them, and creates or updates templates in CatC.

Primary outcome:
- Member templates exist in the CatC project and are commit-ready for composite assembly.

Utilization statement:
- Use this workflow after any GitHub template change to keep Catalyst Center template content synchronized with source control.

### 5.0 - Templates Composite

Workflow folder: [5.0-Cisco-Catalyst-Center-Templates-Composite](5.0-Cisco-Catalyst-Center-Templates-Composite/)

Function:
- Builds or updates composite templates from YAML definitions and commits resulting template versions.

Primary outcome:
- Composite template and member relationships are available for profile and deployment workflows.

Utilization statement:
- Use this workflow whenever composite definitions or member bindings change so deployment payloads reference current committed template graphs.

### 6.0 - Network Profile

Workflow folder: [6.0-Cisco-Catalyst-Center-Network-Profile](6.0-Cisco-Catalyst-Center-Network-Profile/)

Function:
- Resolves Day0/DayN template IDs and binds them to site-level switching network profiles.

Primary outcome:
- Site profile exists with correct template associations for deployment context.

Utilization statement:
- Use this workflow to bind template intent to operational site context, enabling deterministic template deployment behavior per site.

### 7.0 - Provision Composite

Workflow folder: [7.0-Cisco-Catalyst-Center-Provision-Composite](7.0-Cisco-Catalyst-Center-Provision-Composite/)

Function:
- Resolves site and template version IDs, checks SDA provisioning state, provisions/re-provisions devices, and deploys the composite template per device.

Primary outcome:
- DayN configuration is rendered and applied to managed target devices.

Utilization statement:
- Use this workflow for controlled production rollout, post-change re-provisioning, and repeatable remediation of target devices in a site.

---

## Input Data Sources

The workflow suite uses shared GitOps input artifacts:

1. Project settings JSON
- `Projects/<project>/Settings/settings.json`
- Consumed across hierarchy, settings, discovery, profile, and provisioning logic.

2. GitHub template source
- Referenced by workflows 4.0 and 5.0 for member and composite template synchronization.

---

## Installation Options

This workflow suite supports two installation paths in Catalyst Center Workflow Manager.

### Option A - Install from included JSON files (local import)

Use this path when you want explicit version control of the exact workflow artifacts in this repository.

1. Open Catalyst Center and go to Platform, then Workflow Manager.
2. Select Import.
3. Import each workflow JSON from the matching folder in this repository:
- 1.0 folder JSON
- 2.0 folder JSON
- 3.0 folder JSON
- 4.0 folder JSON
- 5.0 folder JSON
- 6.0 folder JSON
- 7.0 folder JSON
4. Verify each workflow appears with expected name and version.
5. Run in the documented order in this README.

Recommended when:
- You need deterministic promotion across dev, test, and production.
- You maintain workflow changes in Git and want exact parity with repository content.

### Option B - Install from Workflow Exchange (in-product)

Use this path when you want rapid onboarding from published workflow content directly inside Catalyst Center.

1. Open Catalyst Center and go to Platform, then Select Automation.
2. Select Exchange and browse the Catalog.
3. Search for the matching GitOps workflow titles.
4. Install each required workflow package and follow any installation instructions provided.
5. Validate input variables and API permissions before first run.
6. Execute in the same dependency order defined in this README.

Recommended when:
- You want faster first-time setup without manual file import.
- Your team prefers catalog-driven lifecycle operations.

Post-install validation for either option:

1. Confirm all seven workflows are visible and enabled.
2. Confirm runtime target, credentials, and required permissions are set.
3. Execute a non-production test run using a limited target scope.
4. Confirm task polling and terminal status behavior before production rollout.

---

## Meraki Free Account Setup (Optional Lab On-Ramp)

If you are new to Cisco workflow automation, a free Meraki Dashboard environment can be useful to practice API auth, inventory modeling, and network object workflows before production Catalyst Center changes.

Important:
- Meraki Dashboard workflows are not to be confused with Catalyst Center workflows. They are not the same and do not interact.
- This step is optional in the event you already have a Meraki account and is required to run workflows 1.0 through 7.0 in this folder.

### Create a free Meraki Dashboard account

1. Go to the Meraki Dashboard signup page and create an account.
2. Verify email and complete organization setup.
3. Start a trial organization if prompted.

### Create a test network

1. In Dashboard, create a new network (for example: combined network).
2. Add at least one product type in the network profile.
3. If hardware is not available, keep the network as a logical lab network for API experimentation.

### Enable API access

1. Go to Organization settings and enable Dashboard API access.
2. Generate an API key from your user profile.
3. Store the key securely (password manager or secrets vault).

### Suggested lab exercises before CatC production use

1. Perform authenticated GET requests for organizations, networks, and devices.
2. Build a small script that reads network metadata and validates expected fields.
3. Practice idempotent update logic and rollback behavior on non-production objects.

This optional prep helps teams build API discipline and change-control habits that transfer directly to Catalyst Center workflow operations.

---

## Ordering and Dependencies

The workflows are designed to run in strict order.

```text
1.0 Site Hierarchy
  -> foundation for all site-scoped operations

2.0 Settings and Credentials
  -> requires hierarchy from 1.0

3.0 Device Discovery and Assign
  -> requires settings/credentials and valid hierarchy

4.0 Templates GitHub Integration
  -> can run once GitHub content is available

5.0 Templates Composite
  -> requires member templates from 4.0

6.0 Network Profile
  -> requires hierarchy (1.0) and template artifacts (4.0/5.0)

7.0 Provision Composite
  -> requires managed site-assigned devices (3.0), composite templates (5.0), and profile binding (6.0)
```

Recommended rollback/deletion order is reverse execution order to preserve dependency integrity.

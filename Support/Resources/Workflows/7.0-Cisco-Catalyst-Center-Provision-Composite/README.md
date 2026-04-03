# 7.0 — Cisco Catalyst Center: Provision Composite Template

> **Workflow:** `GitOps-Provisioning-v3.json`
> **Type:** Cisco Catalyst Center Generic Workflow (Intent API)
> **Subworkflows:** `Get-GitHub-File-v2`, `Get-Task-ID`, `Wait-For-Catalyst-Center-Task`
> **API Endpoints:**
> &nbsp;&nbsp;`GET  /repos/{owner}/{repo}/contents/{path}/{file}` — retrieve settings.json from GitHub
> &nbsp;&nbsp;`GET  /dna/intent/api/v1/sites` — resolve site hierarchy to siteId
> &nbsp;&nbsp;`GET  /dna/intent/api/v2/template-programmer/project` — resolve composite template ID
> &nbsp;&nbsp;`GET  /dna/intent/api/v1/network-device` — resolve management IPs to device UUIDs
> &nbsp;&nbsp;`GET  /dna/intent/api/v2/template-programmer/template` — get composite and member template details
> &nbsp;&nbsp;`GET  /dna/intent/api/v1/templates/{templateId}/versions` — resolve latest committed version UUID
> &nbsp;&nbsp;`GET  /dna/intent/api/v1/sda/provisionDevices` — check current provisioning state per device
> &nbsp;&nbsp;`POST /dna/intent/api/v1/sda/provisionDevices` — provision unprovisioned device
> &nbsp;&nbsp;`PUT  /dna/intent/api/v1/sda/provisionDevices` — re-provision already-provisioned device
> &nbsp;&nbsp;`POST /dna/intent/api/v2/template-programmer/template/deploy` — deploy composite template
> &nbsp;&nbsp;`GET  /dna/intent/api/v1/task/{taskId}` — poll async task until endTime or isError
> **Minimum Catalyst Center version:** 2.3.7.9
> **Authors:** Keith Baldwin — Solutions Engineer - Automation HyperSpecialist (kebaldwi@cisco.com)
> **Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.**

---

## Table of Contents

1. [Overview](#overview)
   - [What it does](#what-it-does)
   - [What makes this workflow different](#what-makes-this-workflow-different)
   - [Logical Flow](#logical-flow)
2. [Prerequisites](#prerequisites)
3. [Directory Structure](#directory-structure)
4. [Workflow Input Parameters](#workflow-input-parameters)
5. [Input Data Structure — `settings.json`](#input-data-structure--settingsjson)
6. [How It Works](#how-it-works)
   - [Step 1 — Retrieve settings.json from GitHub](#step-1--retrieve-settingsjson-from-github)
   - [Step 2 — Resolve Site, Template, and Device IDs](#step-2--resolve-site-template-and-device-ids)
   - [Step 3 — Build the Versioned Composite Deployment Payload](#step-3--build-the-versioned-composite-deployment-payload)
   - [Step 4 — Check Provisioning State at Site](#step-4--check-provisioning-state-at-site)
   - [Step 5 — Provision and Deploy Per Device](#step-5--provision-and-deploy-per-device)
7. [Composite Deploy Payload Reference](#composite-deploy-payload-reference)
8. [How CatC Template Version IDs Work](#how-catc-template-version-ids-work)
9. [Running the Workflow](#running-the-workflow)
10. [Expected Output](#expected-output)
11. [Workflow Ordering Dependency](#workflow-ordering-dependency)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This Cisco Catalyst Center workflow deploys **composite Day-N templates** to managed devices using a GitOps model. Configuration intent is stored in a `settings.json` file in a GitHub repository. At runtime the workflow fetches that file, resolves all required UUIDs from Catalyst Center, handles the SDA provisioning lifecycle, and deploys the composite template to every target device in a loop.

A composite template is a single deployable unit that bundles multiple child (member) templates, allowing a full device configuration stack — VRF definitions, loopbacks, overlay, NVE, multicast, and more — to be pushed atomically in one operation.

### What it does

| Action | Mechanism |
|--------|-----------|
| Retrieves configuration intent from GitHub | `Get-GitHub-File-v2` subworkflow — `GET /repos/{owner}/{repo}/contents/{path}/{file}` |
| Extracts site hierarchy and template targets | JSONPath query on the retrieved `settings.json` |
| Resolves siteId, templateId, and deviceIdArray in parallel | Three concurrent CatC API calls |
| Fetches composite template details and iterates member templates | `GET /template-programmer/template?id=` — builds `memberTemplateDeploymentInfo` |
| Resolves the latest committed template version UUID | `GET /templates/{templateId}/versions` |
| Checks per-device provisioning state at the target site | `GET /sda/provisionDevices?siteId=` |
| Provisions unprovisioned devices (SDA fabric) | `POST /sda/provisionDevices` + task poll |
| Re-provisions already-provisioned devices | `PUT /sda/provisionDevices` + task poll |
| Deploys composite template per device | `POST /template-programmer/template/deploy` + task poll |

### What makes this workflow different

Unlike a regular (non-composite) template deployment — where a single template and a flat set of parameters are pushed — a composite deployment requires that each **member template** inside the composite carry its own `targetInfo` and parameter set. This is reflected in the `memberTemplateDeploymentInfo` structure of the v2 deploy API payload.

Additionally, this workflow handles the **SDA provisioning lifecycle**: before deploying a Day-N template, each target device must be in the SDA-provisioned state. The workflow automatically determines whether each device needs initial provisioning or re-provisioning, calls the correct API, waits for task completion, then proceeds to template deployment.

Catalyst Center resolves the composite template's member list at deploy time, so the workflow must:
1. Know the composite template's committed `templateId` (version UUID) and its `mainTemplateId` (root UUID).
2. Know each member template's committed `templateId` and `mainTemplateId`.
3. Provide per-member `targetInfo` entries with device UUIDs (not IPs).

This workflow automates all three lookups. The operator only needs to specify human-readable names and IP addresses in `settings.json` in GitHub.

### Logical Flow

The diagram below shows every decision point and state transition from startup to completion:

![Logical Flow](DIAGRAMS/logical-flow.png)

> Source: [`DIAGRAMS/logical-flow.mmd`](DIAGRAMS/logical-flow.mmd) — re-render with:
> ```bash
> npx -y @mermaid-js/mermaid-cli -i DIAGRAMS/logical-flow.mmd -o DIAGRAMS/logical-flow.png -w 885 -b white
> ```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Cisco Catalyst Center | >= 2.3.7.9 |
| Composite template | Must already exist in CatC with member templates attached (run workflow 6.0 first) |
| Network profile | Must be assigned to the target site with the composite template bound (run workflow 6.0 first) |
| Target devices | Must be discovered and managed in CatC (run workflow 4.0 first) |
| Devices assigned to site | Target devices must be assigned to the target site (run workflow 5.0 first) |
| GitHub repository | `settings.json` must be accessible at the configured path |
| GitHub API access | CatC must be able to reach `api.github.com` (or configured GitHub Enterprise host) |

---

## Directory Structure

```
7.0 Cisco Catalyst Center: Provision Composite Template/
├── GitOps-Provisioning-v3.json        # Catalyst Center workflow definition (import via CatC UI)
├── DIAGRAMS/
│   ├── logical-flow.mmd               # Mermaid diagram source — re-render with mmdc
│   └── logical-flow.png               # Rendered flowchart (referenced by this README)
└── README.md                          # This document
```

Configuration intent is stored in the shared `settings.json` in the GitHub repository:

```
Projects/
└── BGP_EVPN/
    └── Settings/
        └── settings.json        # Site hierarchy + device targets + template deploy settings
```

---

## Workflow Input Parameters

These parameters are entered when the workflow is launched from the Catalyst Center UI or triggered via the Workflow API.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `GITHUB_USER` | string | `kebaldwi` | GitHub account or organisation that owns the repository |
| `GITHUB_REPO` | string | `TECOPS-2599` | Repository name containing `settings.json` |
| `GITHUB_PATH` | string | `Projects/BGP_EVPN/Settings` | Path within the repository to the folder containing `settings.json` |
| `GITHUB_FILE` | string | `settings.json` | Filename to retrieve from the GitHub path |
| `Project Name` | string | `BGP_EVPN` | Catalyst Center project name that owns the composite template |
| `HierarchyParent` | string | `Global/PODS` | Root path of the site hierarchy |
| `HierarchyArea` | string | `POD 0` | Area name under `HierarchyParent` |
| `HierarchyBldg` | string | `Building P0` | Building name under `HierarchyArea` |
| `HierarchyFloor` | string | `Floor 1` | Floor name under `HierarchyBldg` |

> The full site path used for API queries is assembled from: `{HierarchyParent}/{HierarchyArea}/{HierarchyBldg}/{HierarchyFloor}`

---

## Input Data Structure — `settings.json`

The workflow reads a single `settings.json` file from GitHub. This file is shared across all GitOps workflows in the suite.

### Top-Level Schema

```json
{
  "templateName": "<composite template name in CatC>",
  "templateTarget": ["<ip1>", "<ip2>", "..."]
}
```

The JSONPath query extracts the following keys from `settings.json`:

| Key | Description |
|-----|-------------|
| `HierarchyParent` | Root path prefix for the site (may override the workflow parameter) |
| `HierarchyArea` | Area name |
| `HierarchyBldg` | Building name |
| `HierarchyFloor` | Floor name |
| `templateTarget` | Comma-separated or array of management IP addresses of target devices |
| `templateName` | Exact name of the composite template in CatC Template Editor |

### Full Example

```json
{
  "HierarchyParent": "Global/PODS",
  "HierarchyArea":   "POD 0",
  "HierarchyBldg":   "Building P0",
  "HierarchyFloor":  "Floor 1",
  "templateName":    "BGP-EVPN-BUILD",
  "templateTarget":  ["198.19.1.1", "198.19.1.2", "198.19.1.3",
                      "198.19.1.4", "198.19.1.5", "198.19.1.6"]
}
```

In this example, the composite template `BGP-EVPN-BUILD` from the CatC project configured at workflow launch time is deployed to all six devices at `Global/PODS/POD 0/Building P0/Floor 1`.

---

## How It Works

### Step 1 — Retrieve settings.json from GitHub

The `Get-GitHub-File-v2` subworkflow calls the GitHub Contents API:

```
GET https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_PATH}/{GITHUB_FILE}
```

The response body is base64-decoded and parsed as JSON. A JSONPath query then extracts the site hierarchy fields and template targets into workflow variables:

| Variable | Source key in `settings.json` |
|----------|-------------------------------|
| `HierarchyParent` | `HierarchyParent` |
| `HierarchyArea` | `HierarchyArea` |
| `HierarchyBldg` | `HierarchyBldg` |
| `HierarchyFloor` | `HierarchyFloor` |
| `templateName` | `templateName` |
| `templateTarget` | `templateTarget` |

---

### Step 2 — Resolve Site, Template, and Device IDs

Three API calls execute in **parallel** to minimise latency:

#### Branch 1 — Get Site ID

```
GET /dna/intent/api/v1/sites?name={HierarchyFloor}&nameHierarchy={fullSitePath}
```

Extracts `siteId` — the UUID needed for provisioning state checks and SDA provisioning API calls.

#### Branch 2 — Get Template Project

```
GET /dna/intent/api/v2/template-programmer/project?name={Project Name}
```

Extracts the composite `templateId` (root UUID) that matches `templateName` within the project.

#### Branch 3 — Get Device List

```
GET /dna/intent/api/v1/network-device?managementIpAddress={ip}
```

Called once per IP address in `templateTarget`. Maps each management IP to its CatC device UUID, building `deviceIdArray`. The workflow iterates the `templateTarget` array and performs a separate lookup per IP.

---

### Step 3 — Build the Versioned Composite Deployment Payload

#### Get Composite Template Details

```
GET /dna/intent/api/v2/template-programmer/template?id={templateId}
```

Returns the full composite template object. Key fields extracted:

| Field | Description |
|-------|-------------|
| `containingTemplateIds` | List of root UUIDs for each member template attached to the composite |
| `mainTemplateId` | Root UUID of the composite template itself — used in the deploy payload |
| `isComposite` | Confirms this is a composite template |

The list of member template IDs is stored in `containingTemplateArray`.

#### For Each Member Template

For every ID in `containingTemplateArray`, the workflow calls:

```
GET /dna/intent/api/v2/template-programmer/template?id={memberTemplateId}
```

This returns the member template's body, parameter names, and default values. The workflow builds one entry in `memberTemplateDeploymentInfo` per member, combining:
- The member template's version UUID and root UUID
- The template's parameter name/value pairs (using defaults unless overridden)

#### Get Latest Template Version

```
GET /dna/intent/api/v1/templates/{templateId}/versions
```

Returns all committed versions of the composite template. The entry with the highest `versionTime` is selected as the latest committed version UUID. This version UUID is required by the v2 deploy API — using the root UUID causes CatC to silently deploy an arbitrary snapshot.

The final deployment payload is assembled at this point, embedding:
- `templateId` — latest composite version UUID
- `mainTemplateId` — composite root UUID
- `isComposite: true`
- `forcePushTemplate: true`
- `copyingConfig: true` (critical — see [Payload Reference](#composite-deploy-payload-reference))
- `memberTemplateDeploymentInfo` — one entry per member template, with per-device `targetInfo`

---

### Step 4 — Check Provisioning State at Site

```
GET /dna/intent/api/v1/sda/provisionDevices?siteId={siteId}
```

Returns the list of devices currently provisioned at the target site. The result is stored as `provisionedDeviceList` and used in Step 5 to determine the correct provisioning API call per device.

---

### Step 5 — Provision and Deploy Per Device

For each device UUID in `deviceIdArray`, the workflow:

1. **Looks up the device hostname** from the device list retrieved in Step 2.
2. **Checks provisioning state** — compares the device ID against `provisionedDeviceList`.

#### If the device is NOT provisioned

```
POST /dna/intent/api/v1/sda/provisionDevices
```

The `Wait-For-Catalyst-Center-Task` subworkflow polls:
```
GET /dna/intent/api/v1/task/{taskId}
```
until `endTime` is set or `isError` is true.

#### If the device IS already provisioned

```
PUT /dna/intent/api/v1/sda/provisionDevices
```

Same task polling as above.

#### Deploy Composite Template

Once the device is confirmed provisioned:

```
POST /dna/intent/api/v2/template-programmer/template/deploy
```

The `Get-Task-ID` subworkflow extracts the `taskId` from the response. The `Wait-For-Catalyst-Center-Task` subworkflow then polls until the task reaches a terminal state.

**Terminal states:**

| Condition | Outcome |
|-----------|---------|
| `endTime` set, `isError = false` | Template deployed successfully |
| `isError = true` | Workflow fails with the `failureReason` from the task `progress` field |

The loop then advances to the next device in `deviceIdArray` and repeats.

---

## Composite Deploy Payload Reference

Submitted to `POST /dna/intent/api/v2/template-programmer/template/deploy`.

```json
{
  "templateId":        "<composite_version_uuid>",
  "mainTemplateId":    "<composite_root_uuid>",
  "isComposite":       true,
  "forcePushTemplate": true,
  "copyingConfig":     true,
  "targetInfo": [
    {
      "id":       "<device_uuid>",
      "hostName": "<device_hostname>",
      "type":     "MANAGED_DEVICE_UUID",
      "params":   { "__device": null },
      "resourceParams": [
        { "type": "MANAGED_DEVICE_UUID",     "value": "<device_uuid>" },
        { "type": "MANAGED_DEVICE_IP",       "value": "<device_mgmt_ip>" },   // optional — enables IP-based targeting
        { "type": "MANAGED_DEVICE_HOSTNAME", "value": "<device_hostname>" }   // optional — enables hostname-based targeting
      ]
    }
  ],
  "memberTemplateDeploymentInfo": [
    {
      "templateId":        "<member1_version_uuid>",
      "mainTemplateId":    "<member1_root_uuid>",
      "forcePushTemplate": true,
      "isComposite":       false,
      "copyingConfig":     true,
      "targetInfo": [
        {
          "id":       "<device_uuid>",
          "hostName": "<device_hostname>",
          "type":     "MANAGED_DEVICE_UUID",
          "params":   { "<param_name>": "<default_value>" },
          "resourceParams": [
            { "type": "MANAGED_DEVICE_UUID",     "value": "<device_uuid>" },
            { "type": "MANAGED_DEVICE_IP",       "value": "<device_mgmt_ip>" },   // optional — enables IP-based targeting
            { "type": "MANAGED_DEVICE_HOSTNAME", "value": "<device_hostname>" }   // optional — enables hostname-based targeting
          ]
        }
      ]
    }
  ]
}
```

**Key field notes:**

| Field | Value | Notes |
|-------|-------|-------|
| `templateId` | Composite version UUID | From `GET .../versions` — **not** the root UUID. Using root UUID deploys an arbitrary snapshot. |
| `mainTemplateId` | Composite root UUID | Permanent ID assigned at template creation. Never changes. |
| `isComposite` | `true` | Required for composite deploys. |
| `copyingConfig` | `true` | **Critical — must appear at both top level and per member.** Tells CatC to push rendered config to the device. Without this, the deploy is recorded as intent only — no configuration is sent. |
| `forcePushTemplate` | `true` | Bypasses CatC in-sync check. Set to `false` to skip devices already in sync. |
| `targetInfo[].type` | `"MANAGED_DEVICE_UUID"` | Must be exactly this string. Primary device identity is carried by `id` (UUID) and `hostName`. |
| `targetInfo[].params` | `{ "__device": null }` (top-level) or template param dict (per member) | Top-level `targetInfo` uses `{"__device": null}`. Each member's `targetInfo` carries the template's own parameter name/value pairs extracted from CatC. |
| `resourceParams` | Array — one required entry, two optional | `MANAGED_DEVICE_UUID` (required — device UUID value) is sufficient for targeting. `MANAGED_DEVICE_IP` and `MANAGED_DEVICE_HOSTNAME` are **optional** additional entries that enable CatC to resolve or reference the device by IP address or hostname respectively, useful when alternative targeting methods or template variable binding is needed. This workflow uses UUID-only targeting; include the optional entries to support broader CatC resolution scenarios. |
| `memberTemplateDeploymentInfo[].templateId` | Member version UUID | Resolved from `GET .../template?id={memberRootId}` combined with version lookup. |

---

## How CatC Template Version IDs Work

Every template in Catalyst Center has two distinct UUID types:

| ID type | Description |
|---------|-------------|
| **Root UUID** (`mainTemplateId`) | Assigned when the template is first created. Permanent — never changes across edits or commits. Visible in the Template Editor URL and in the project/template API as `templateId`. |
| **Version UUID** (`templateId` in the deploy payload) | Assigned each time a new version is committed. The v2 deploy API requires this UUID — not the root UUID. Retrieved from `GET /templates/{rootId}/versions`; select the entry with the highest `versionTime`. |

> **Important:** The `versionsInfo` array returned by CatC is **not guaranteed to be in chronological order**. The workflow selects the version with the highest `versionTime` value, not `versionsInfo[0]`. Using the first entry would risk deploying a stale snapshot.

---

## Running the Workflow

### Import the Workflow

1. In Catalyst Center, navigate to **Platform → Workflow Manager**.
2. Click **Import** and upload `GitOps-Provisioning-v3.json`.
3. The workflow appears as **GitOps-Provisioning-v3** in the workflow list.

### Execute the Workflow

1. Click **Run** on the imported workflow.
2. Fill in the input parameters (see [Workflow Input Parameters](#workflow-input-parameters)).
3. Click **Execute**.
4. Monitor progress in the **Workflow Executions** view.

### Trigger via API

```bash
POST /dna/intent/api/v1/workflow-manager/workflows/{workflowId}/run
{
  "inputParameters": {
    "GITHUB_USER":    "kebaldwi",
    "GITHUB_REPO":    "TECOPS-2599",
    "GITHUB_PATH":    "Projects/BGP_EVPN/Settings",
    "GITHUB_FILE":    "settings.json",
    "Project Name":   "BGP_EVPN",
    "HierarchyParent":"Global/PODS",
    "HierarchyArea":  "POD 0",
    "HierarchyBldg":  "Building P0",
    "HierarchyFloor": "Floor 1"
  }
}
```

---

## Expected Output

A successful run produces the following per-device result sequence in the workflow execution log:

```
Step 1       Settings retrieved from GitHub: Projects/BGP_EVPN/Settings/settings.json
Step 2       siteId resolved: <uuid>
             templateId resolved: <uuid>
             deviceIdArray: [<uuid>, <uuid>, ...]
Step 3       Composite template details fetched — 6 member templates
             Latest version UUID resolved
             memberTemplateDeploymentInfo assembled
Step 4       provisionedDeviceList: [<uuid>, <uuid>, ...]
Step 5 [1/6] Device 198.19.1.1 — already provisioned → Re-Provision (PUT) → Task complete
             Deploy composite template → Task complete → SUCCESS
Step 5 [2/6] Device 198.19.1.2 — already provisioned → Re-Provision (PUT) → Task complete
             Deploy composite template → Task complete → SUCCESS
...
Step 5 [6/6] Device 198.19.1.6 — already provisioned → Re-Provision (PUT) → Task complete
             Deploy composite template → Task complete → SUCCESS
```

---

## Workflow Ordering Dependency

This workflow is the final step in the GitOps provisioning suite. All prior workflows must have completed successfully before running this one:

| Workflow | Purpose | Must run before 7.0? |
|----------|---------|----------------------|
| 1.0 — Site Hierarchy | Creates Area / Building / Floor | Yes |
| 2.0 — Network Settings | Applies DHCP, DNS, NTP, AAA to site | Yes |
| 3.0 — Credentials | Creates CLI/SNMP credentials in CatC | Yes |
| 4.0 — Device Discovery | Discovers devices and adds to inventory | Yes |
| 5.0 — Assign to Site | Moves devices from Global to target site | Yes |
| 6.0 — Template GitOps | Syncs composite and member templates from GitHub to CatC | Yes |
| 6.0 — Network Profile | Creates switching profile, binds templates, assigns to site | Yes |
| **7.0 — This workflow** | Provisions devices (SDA) + deploys composite template | — |

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Fail: template not found` | Template name in `settings.json` does not match any template in the configured CatC project | Verify `templateName` in `settings.json` exactly matches the template name in CatC Template Editor. Check `Project Name` workflow parameter. |
| SDA Provision task `isError = true` | Device not yet assigned to site, or SDA fabric not enabled at site | Run workflow 5.0 to assign devices to site first. Confirm SDA fabric is enabled at the target site in CatC. |
| Deploy task `isError = true` + `failureReason` | Template Jinja2 render error, device unreachable during push, or missing parameter values | Check member template parameter defaults. Verify device is reachable from CatC. Review template syntax in Template Editor. |
| GitHub file retrieval fails | Repository is private, wrong path, or CatC cannot reach `api.github.com` | Verify `GITHUB_USER`, `GITHUB_REPO`, `GITHUB_PATH`, `GITHUB_FILE` parameters. Check CatC outbound internet connectivity. |
| `NCTP10028` error from deploy API | Empty or malformed `resourceParams` in the deploy payload | Ensure the composite template and all member templates have been committed at least once in CatC (workflow 6.0). |
| Re-provision succeeds but deploy fails | Template version UUID mismatch — member template not yet committed | Recommit all member templates in CatC Template Editor, then re-run workflow 6.0 to sync. Re-run this workflow. |
| Devices remain unprovisioned after run | `forcePushTemplate` not set and devices appear in-sync | The workflow sets `forcePushTemplate: true` by default. If overridden, devices that CatC considers already in-sync are skipped — this is expected behaviour. |

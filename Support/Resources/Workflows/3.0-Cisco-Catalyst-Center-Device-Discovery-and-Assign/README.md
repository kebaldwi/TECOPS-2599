# 3.0 - Cisco Catalyst Center: Device Discovery and Assign

> **Workflow:** `GitOps-DeviceDiscovery-v3.json`
> **Type:** Cisco Catalyst Center Generic Workflow (Intent API)
> **Subworkflows:** `Get-GitHub-Directory-v2`, `Get-GitHub-File-v2`, `CATC-DeviceDiscovery-v3`
> **Minimum Catalyst Center version:** 2.3.7.9

---

## Overview

This workflow discovers network devices for each site hierarchy entry defined in GitHub and assigns discovered devices to the matching Catalyst Center site.

It follows a GitOps model:
- read source data from `settings.json` in GitHub,
- run deterministic discovery logic per hierarchy row,
- assign discovered devices to the intended site path.

## Logical Flow

![Logical Flow](DIAGRAMS/logical-flow.png)

Source: `DIAGRAMS/logical-flow.mmd`

Re-render command:

```bash
npx -y @mermaid-js/mermaid-cli -i DIAGRAMS/logical-flow.mmd -o DIAGRAMS/logical-flow.png -w 885 -b white
```

---

## Directory Structure

```text
3.0-Cisco-Catalyst-Center-Device-Discovery-and-Assign/
|- GitOps-DeviceDiscovery-v3.json
|- DIAGRAMS/
|  |- logical-flow.mmd
|  |- logical-flow.png
|- README.md
```

---

## Workflow Input Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `GITHUB-OWNER` | string | `kebaldwi` | GitHub owner/org containing the repo |
| `GITHUB-REPO` | string | `TECOPS-2599` | Repository name |
| `GITHUB-PATH` | string | `Projects/BGP_EVPN/Settings` | Folder that contains `settings.json` |
| `GITHUB-FILE` | string | `settings.json` | File to process |
| `FORCE Update` | string | `false` | Recreate existing discovery by name when true |
| `TemplateHubProjectName` | string | `BGP_EVPN` | Passed through for related template lookups |

---

## Input Data Requirements

The workflow reads hierarchy and discovery definitions from `settings.json`.

Expected fields used by this workflow include:
- hierarchy path: `HierarchyParent`, `HierarchyArea`, `HierarchyBldg`, `HierarchyFloor`
- discovery scope: seed IP/range, protocol order, timeout/retry, and optional tags
- credential selectors: references used to resolve CLI/SNMP/NETCONF global credential UUIDs

Minimal conceptual example:

```json
[
  {
    "HierarchyParent": "Global",
    "HierarchyArea": "NA",
    "HierarchyBldg": "HQ",
    "HierarchyFloor": "Floor1",
    "device_discovery": {
      "name": "HQ-Floor1-Discovery",
      "seed_ips": ["10.10.10.0/24"],
      "protocol_order": "ssh,telnet,snmp"
    }
  }
]
```

---

## How It Works

### Step 1 - Read GitHub Directory

`Get-GitHub-Directory-v2` calls:
- `GET api.github.com/repos/{owner}/{repo}/contents/{path}`

The workflow extracts file names and loops each file.

### Step 2 - Match Target File

Condition checks for `GITHUB-FILE` (typically `settings.json`).
Only matching files continue.

### Step 3 - Read Raw Settings

`Get-GitHub-File-v2` calls:
- `GET api.github.com/repos/{owner}/{repo}/contents/{path}/{file}`
- Header: `Accept: application/vnd.github.raw+json`

### Step 4 - Parse Hierarchy Rows

The workflow parses table rows from JSON and iterates each row.

### Step 5 - Discovery Subprocess (Detailed)

The diagram splits this into two embedded subflows.

#### Step 5b - Discovery Preparation

Per row, workflow resolves:
- global credential UUIDs from `GET /dna/intent/api/v2/global-credential`
- Catalyst Center release info from `GET /dna/intent/api/v1/dnac-release`
- final discovery payload: discovery name, IP ranges, protocol order, credentials

#### Step 5c - Execute Discovery and Assign Site

`CATC-DeviceDiscovery-v3` follows this sequence:
1. `GET /api/v1/discovery/1/100` to check existing discovery by name.
2. Branch:
   - create path: `POST /dna/intent/api/v1/discovery`
   - recreate path: `DELETE /dna/intent/api/v1/discovery/{id}` then `POST /dna/intent/api/v1/discovery`
3. Poll async task completion via `GET /dna/intent/api/v1/task/{taskId}`.
4. Retrieve discovered devices via `GET /dna/intent/api/v1/discovery/{discoveryId}/network-device`.
5. Resolve target site ID with `GET /dna/intent/api/v2/site?groupNameHierarchy=...`.
6. Assign devices to site using `POST /dna/intent/api/v1/networkDevices/assignToSite/apply`.

### Step 6 - Stabilization Delay

Workflow sleeps for 30 seconds before completion.

---

## Expected Output

When successful:
- discovery jobs are created (or recreated) for each hierarchy row,
- discovered device UUIDs are returned,
- devices are assigned to the target Catalyst Center site hierarchy.

Common failure points:
- missing/invalid credential selectors,
- non-resolvable site path,
- unreachable seed ranges,
- async task timeout or error in discovery execution.

---

## Workflow Dependency Order

Recommended execution sequence:
1. 1.0 Site Hierarchy Build
2. 2.0 Settings and Credentials
3. 3.0 Device Discovery and Assign (this workflow)
4. 4.0 Templates GitHub Integration
5. 5.0 Templates Composite
6. 6.0 Network Profile
7. 7.0 Provision Composite

---

## Troubleshooting

- Verify `settings.json` hierarchy values match actual CatC hierarchy names exactly.
- Confirm global credentials exist and can authenticate device access methods.
- Check discovery task status detail in CatC task history when polling fails.
- Validate that `FORCE Update` behavior is expected for discovery recreation.

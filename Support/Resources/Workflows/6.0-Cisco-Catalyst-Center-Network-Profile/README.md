# 6.0 - Cisco Catalyst Center: Network Profile

> **Workflow:** `GitOps-BuildNetworkProfile-v3.json`
> **Type:** Cisco Catalyst Center Generic Workflow (Intent API)
> **Subworkflows:** `Get-GitHub-File-v2`, `CATC-GetTemplates-v2`, `CATC-CreateSiteProfile-v3`
> **Minimum Catalyst Center version:** 2.3.7.9

---

## Overview

This workflow builds and assigns a switching network profile to a target site hierarchy using Day0 and DayN template IDs resolved from Template Hub.

It consumes one GitHub settings file, resolves site and template IDs, then creates or updates the site profile association.

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
6.0-Cisco-Catalyst-Center-Network-Profile/
|- GitOps-BuildNetworkProfile-v3.json
|- DIAGRAMS/
|  |- logical-flow.mmd
|  |- logical-flow.png
|- README.md
```

---

## Workflow Input Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `GITHUB-OWNER` | string | `kebaldwi` | GitHub owner/org |
| `GITHUB-REPO` | string | `TECOPS-2599` | Repository name |
| `GITHUB-PATH` | string | `Projects/BGP_EVPN/Settings` | Path to settings file |
| `GITHUB-FILE` | string | `settings.json` | Source settings file |
| `TemplateHubProjectName` | string | `BGP_EVPN` | Template project used for Day0/DayN lookup |
| `FORCE Update` | string | `false` | Reapply profile assignment when true |

---

## Input Data Requirements

Expected fields in `settings.json` used by this workflow:
- hierarchy fields: `HierarchyParent`, `HierarchyArea`, `HierarchyBldg`, `HierarchyFloor`
- profile identity: `profile_name`
- template name arrays: `Day0TemplateNames`, `DayNTemplateNames`

Conceptual example:

```json
{
  "HierarchyParent": "Global",
  "HierarchyArea": "NA",
  "HierarchyBldg": "HQ",
  "HierarchyFloor": "Floor1",
  "profile_name": "BGP_EVPN_Switching_Profile",
  "Day0TemplateNames": ["Titanium-L3-PnP-Template"],
  "DayNTemplateNames": ["BGP-EVPN-BUILD"]
}
```

---

## How It Works

### Step 1 - Read Settings JSON

`Get-GitHub-File-v2` downloads raw file content from GitHub.

### Step 2 - Extract Profile Inputs

JSONPath queries extract:
- hierarchy path components,
- profile name,
- Day0 and DayN template name lists.

Workflow then joins or splits values to support single or multiple template references.

### Step 3 - Resolve Site ID

The workflow queries Catalyst Center site API:
- `GET /dna/intent/api/v2/site?groupNameHierarchy=...`

It captures the target `siteId` for profile assignment.

### Step 4 - Resolve Day0 and DayN Template IDs (Step 5 subflow)

For each Day0/DayN template name:
- call `CATC-GetTemplates-v2`
- `GET /dna/intent/api/v2/template-programmer/project?name=...`
- extract matching template ID

Both branches produce final Day0/DayN template ID collections.

### Step 5 - Create Site Profile

`CATC-CreateSiteProfile-v3` builds and submits site profile payload:
- profile type: switching
- hierarchy site ID
- Day0 template IDs
- DayN template IDs

Success branch ends after 30-second delay.

---

## Expected Output

When successful:
- target site has the intended switching network profile,
- Day0 and DayN template bindings are attached by template ID,
- profile is available for downstream provisioning operations.

Common failure points:
- unresolved template names,
- site hierarchy mismatch,
- insufficient permissions for profile assignment,
- malformed template list input.

---

## Workflow Dependency Order

Recommended execution sequence:
1. 1.0 Site Hierarchy Build
2. 2.0 Settings and Credentials
3. 3.0 Device Discovery and Assign
4. 4.0 Templates GitHub Integration
5. 5.0 Templates Composite
6. 6.0 Network Profile (this workflow)
7. 7.0 Provision Composite

---

## Troubleshooting

- Verify Day0/DayN names exactly match committed Template Hub templates.
- Confirm `TemplateHubProjectName` is correct for lookup scope.
- Validate resolved site path exists and is uniquely mapped.
- Inspect task and workflow execution logs for profile API response detail.

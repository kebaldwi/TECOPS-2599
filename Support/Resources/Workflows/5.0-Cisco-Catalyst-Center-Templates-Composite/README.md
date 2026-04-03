# 5.0 - Cisco Catalyst Center: Templates Composite

> **Workflow:** `GitOps-BuildCompositeTemplate-v3.json`
> **Type:** Cisco Catalyst Center Generic Workflow (Intent API)
> **Subworkflows:** `Get-GitHub-Directory-v2`, `Get-GitHub-File-v2`, `CATC-CreateCompositeTemplate-v3`, `CATC-CommitTemplate-v2`
> **Minimum Catalyst Center version:** 2.3.7.9

---

## Overview

This workflow builds or updates composite templates in Catalyst Center based on YAML definitions stored in GitHub.

It resolves member templates, product-family metadata, and then commits the composite template version for deployment use.

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
5.0-Cisco-Catalyst-Center-Templates-Composite/
|- GitOps-BuildCompositeTemplate-v3.json
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
| `GITHUB-PATH` | string | `Projects/BGP_EVPN/DayNTemplates` | Folder containing composite YAML definitions |
| `TemplateHubProjectName` | string | `BGP_EVPN` | Target Template Hub project |
| `FORCE Update` | string | `false` | Replace existing composite definitions when true |

---

## Source File Requirements

This workflow processes YAML files (`.yml`) that define composite templates and their members.

Typical semantics:
- filename maps to target template identity,
- referenced members must already exist in Template Hub,
- product family bindings are resolved before composite update.

---

## How It Works

### Step 1 - Read GitHub Directory

`GET api.github.com/repos/{owner}/{repo}/contents/{path}`

Workflow loops all files and keeps `.yml` entries.

### Step 2 - Read YAML and Normalize Name

For each `.yml` file:
- download raw definition from GitHub,
- convert filename semantics used internally (`.yml` to `.j2` mapping).

### Step 3 - Composite Create/Update (Step 5 subflow)

`CATC-CreateCompositeTemplate-v3` sequence:
1. `GET /dna/intent/api/v2/template-programmer/project?name=...`
2. if project missing, create it with `POST /dna/intent/api/v1/template-programmer/project`
3. create composite shell with `POST /dna/intent/api/v1/template-programmer/project/{projectId}/template`
4. resolve member template IDs + product family mappings
5. update composite definition with `PUT /api/v1/template-programmer/template`
6. poll async task completion.

### Step 4 - Commit Composite Template

After loop completion and delay:
- call `CATC-CommitTemplate-v2`
- API: `POST /api/v1/template-programmer/template/version`
- poll task completion.

---

## Expected Output

When successful:
- each composite YAML has a corresponding Template Hub composite,
- member template relationships are applied,
- composite template version is committed and ready for downstream provisioning.

Common failure points:
- missing member templates,
- invalid product family mapping,
- project permission issues,
- commit task failures.

---

## Workflow Dependency Order

Recommended execution sequence:
1. 1.0 Site Hierarchy Build
2. 2.0 Settings and Credentials
3. 3.0 Device Discovery and Assign
4. 4.0 Templates GitHub Integration
5. 5.0 Templates Composite (this workflow)
6. 6.0 Network Profile
7. 7.0 Provision Composite

---

## Troubleshooting

- Ensure member DayN templates are already imported and committed (Workflow 4.0).
- Validate YAML references for exact template names.
- Confirm project scope and token replacement expectations.
- Use task polling detail to isolate create/update vs commit failures.

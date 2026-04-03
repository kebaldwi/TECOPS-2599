# 4.0 - Cisco Catalyst Center: Templates GitHub Integration

> **Workflow:** `GitOps-BuildTemplates-v3.json`
> **Type:** Cisco Catalyst Center Generic Workflow (Intent API)
> **Subworkflows:** `Get-GitHub-Directory-v2`, `Get-GitHub-File-v2`, `CATC-DependencyMapping-v1`, `CATC-CreateTemplate-v3`, `CATC-CommitTemplate-v2`
> **Minimum Catalyst Center version:** 2.3.7.9

---

## Overview

This workflow imports DayN templates from GitHub into Catalyst Center Template Hub, honoring inter-template include dependencies before create or update.

Core behavior:
- enumerate candidate template files from GitHub,
- build a dependency-aware sorted order,
- create or update each template in that order,
- commit resulting template versions.

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
4.0-Cisco-Catalyst-Center-Templates-Github-integration/
|- GitOps-BuildTemplates-v3.json
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
| `GITHUB-PATH` | string | `Projects/BGP_EVPN/DayNTemplates` | DayN template folder |
| `TemplateHubProjectName` | string | `BGP_EVPN` | Target Catalyst Center template project |
| `FORCE Update` | string | `false` | Overwrite existing template definitions when true |

---

## Supported Source File Types

The workflow scans and processes template files ending in:
- `.j2`
- `.vm`
- `.json`

Files outside these extensions are ignored.

---

## How It Works

### Step 1 - Read GitHub Directory

`GET api.github.com/repos/{owner}/{repo}/contents/{path}`

Extract file names and file count.

### Step 2 - Resolve Project Name

Project name is either:
- explicit `TemplateHubProjectName`, or
- derived from the GitHub path by workflow Python logic.

### Step 3 - Build Dependency Order (Step 5 subflow)

`CATC-DependencyMapping-v1`:
1. reads candidate file contents,
2. extracts include references,
3. builds dependency table,
4. performs topological sort to produce `SortedFileList`.

This prevents child templates from being created before parent include dependencies.

### Step 4 - Create or Update Templates (Step 7 subflow)

For each file in `SortedFileList`:
1. download raw template from GitHub,
2. replace placeholder tokens with resolved project name,
3. call `CATC-CreateTemplate-v3`.

`CATC-CreateTemplate-v3` API sequence:
- `GET /dna/intent/api/v2/template-programmer/project?name=...`
- if project missing: `POST /dna/intent/api/v1/template-programmer/project`
- create template: `POST /dna/intent/api/v1/template-programmer/project/{projectId}/template`
- or update existing: `PUT /dna/intent/api/v1/template-programmer/template/`
- poll async task completion.

### Step 5 - Commit Template Versions

After create/update loop and delay:
1. get template IDs from project,
2. loop each ID through `CATC-CommitTemplate-v2`,
3. poll task completion for each commit operation.

---

## Expected Output

When successful:
- all dependency-ordered templates exist in target project,
- updated templates are version-committed,
- Template Hub state aligns with GitHub source.

Common failure points:
- unresolved include dependency,
- invalid project token substitution,
- permission errors for project/template write,
- commit task failures.

---

## Workflow Dependency Order

Recommended execution sequence:
1. 1.0 Site Hierarchy Build
2. 2.0 Settings and Credentials
3. 3.0 Device Discovery and Assign
4. 4.0 Templates GitHub Integration (this workflow)
5. 5.0 Templates Composite
6. 6.0 Network Profile
7. 7.0 Provision Composite

---

## Troubleshooting

- Confirm template include statements reference valid in-project paths.
- Validate dependency mapping output order when one template fails early.
- Verify `TemplateHubProjectName` points to intended project scope.
- Check task polling details for failed create/update/commit operations.

# Run the Template GitHub Sync Playbook

## Overview Video

[![Import Templates](https://img.youtube.com/vi/WcByI5TBV2Q/0.jpg)](https://www.youtube.com/watch?v=WcByI5TBV2Q)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

> All commands run on the Script Server using the regular DCLOUD account used during staging, with the `~/tecops-venv` activated.

## Step 1 — Inspect the Playbook Directory

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
ls
```

```text
campus-evpn/playbooks/06_sync_templates.yml
campus-evpn/roles/template_gitops/tasks/process_template.yml
campus-evpn/roles/template_gitops/tasks/process_composite.yml
campus-evpn/inventories/lab/hosts.yml
```

The `template_gitops` role includes two task files:

* `process-template.yml` — runs once per simple `.j2` template (sync to CatC).
* `process-composite.yml` — runs once per `.yml` composite definition (resolve members, sync as one composite template).

## Step 2 — Confirm Inventory Variables

```bash
grep -E '^(github|template)_' campus-evpn/inventories/lab/hosts.yml
```

For this lab the values should be:

```yaml
github_owner: kebaldwi
github_repo:  TECOPS-2599
github_branch: main
github_path:   Support/Resources/Data-Models/campus-evpn/BGP_EVPN/DayNTemplates
template_project_name: TECOPS-2599
```

## Step 3 — Optional GitHub Token

The Catalyst Center credentials are read from the shared vault. The public
`kebaldwi/TECOPS-2599` repository does not need a GitHub token. For a private
repository or higher API rate limits, create the optional local token vault:

```bash
cp campus-evpn/vaults/github.yml.example campus-evpn/vaults/github.yml
# Set git_token in the file, then encrypt with the shared Vault password.
ansible-vault encrypt campus-evpn/vaults/github.yml --ask-vault-pass
```

## Step 4 — Run the Playbook

```bash
ansible-playbook campus-evpn/playbooks/06_sync_templates.yml \
    --ask-vault-pass
```

Expect roughly the following stages in the console:

| Stage | Console hint |
|-------|--------------|
| GitHub repo / branch validation | `Validate repository access` / `Validate branch` |
| Tree listing | `Fetch repository tree` |
| Per-template fetch | `Fetch raw template ...` (one task per `.j2`) |
| Per-composite fetch | `Read composite definition ...` (one task per `.yml`) |
| Topological ordering | `Build template processing order` |
| CatC sync — flat templates | `process-template.yml` include — one *changed* per new/updated template |
| CatC sync — composites | `process-composite.yml` include — one *changed* per composite |

A successful first run produces `changed > 0` (every template is being created). Re-running with no source changes returns `changed=0`.

## Step 5 — Verify in Catalyst Center

1. Open Catalyst Center → **&#8801; Menu → Tools → Template Editor**.

   ![Template Editor](../../images/ansible/templates/templates.png?raw=true)

2. Expand the project named `TECOPS-2599` (or whatever you configured in `campus-evpn/inventories/lab/hosts.yml`). You should see:

    - One entry per `.j2` file under `Support/Resources/Data-Models/campus-evpn/BGP_EVPN/DayNTemplates` in the repo.
    - One **composite** template per `.yml` file (notably `BGP-EVPN-BUILD`).

3. Open one of the templates (e.g. `FABRIC-VRF`). The body should match the `.j2` source, and the description field should contain the latest commit message and author.

4. Open the composite template (`BGP-EVPN-BUILD`). The **Properties** tab lists the member templates in the same order as the `.yml` definition.

## Summary

You have a fully populated Catalyst Center Template Project that mirrors a GitHub folder. Editing a `.j2` file in GitHub and re-running the playbook updates the corresponding template in CatC; adding a new file syncs it; removing a file leaves it in CatC (the playbook is `state: merged`-only — it does not delete templates).

> [**Next Module**](../catc-catcenter-5-networkprofiles/01-intro.md)

> [**Return to LAB Menu**](../README.md)

# Run the Site Hierarchy Playbook

## Overview Video

[![Build Site Hierarchy](https://img.youtube.com/vi/e7lGFKs2i1w/0.jpg)](https://www.youtube.com/watch?v=e7lGFKs2i1w)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

In this section we use the shared vault created during script-server staging,
run `01_site_hierarchy.yml`, and verify the resulting hierarchy in Catalyst Center.

> All commands run on the **Script Server** using the regular DCLOUD account used during staging, inside the activated `~/tecops-venv` from the orientation module.

## Step 1 — Inspect the Playbook

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
ls
```

```text
ansible.cfg
campus-evpn/inventories/lab/hosts.yml
campus-evpn/playbooks/01_site_hierarchy.yml
campus-evpn/roles/site_hierarchy/tasks/
```

The `site_hierarchy` role contains its entrypoint and per-site task files:

* `main.yml` — selects create/update or delete based on `state`.
* `create_or_update_site.yml` — runs once per path to create or update an Area/Building/Floor.
* `delete_site.yml` — runs once per path (in deepest-first order) when `state: deleted`.

Open the common lab inventory to confirm the data path:

```bash
grep settings_json_path campus-evpn/inventories/lab/hosts.yml
# Expect: settings_json_path resolves to Support/Resources/Data-Models/campus-evpn/settings.json
```

This relative path resolves to `~/TECOPS-2599/Support/Resources/Data-Models/campus-evpn/settings.json` — the shared source-of-truth file.

## Step 2 — Confirm the Shared Vault

```bash
head -1 campus-evpn/group_vars/all/vault.yml
# Expect: $ANSIBLE_VAULT;1.1;AES256
```

The staging script prompts for and encrypts the CatC admin password. Stage 1.0 does not need a local `vault.yml`.

## Step 3 — Dry Run (Optional)

Confirm the playbook can read its inputs and authenticate to Catalyst Center without making any changes:

```bash
ansible-playbook campus-evpn/playbooks/01_site_hierarchy.yml \
    --ask-vault-pass \
    --check -v
```

If `--check` produces a `PLAY RECAP` with `failed=0`, the connection, vault, and JSON parsing are all wired up correctly.

## Step 4 — Apply the Hierarchy

```bash
ansible-playbook campus-evpn/playbooks/01_site_hierarchy.yml \
    --ask-vault-pass
```

A successful run looks like:

```text
PLAY [Build Catalyst Center Site Hierarchy] *********************************

TASK [Read settings.json] ***************************************************
ok: [catalyst_center]

TASK [Build sorted hierarchy path list] *************************************
ok: [catalyst_center]

TASK [Fetch existing site map] **********************************************
ok: [catalyst_center]

TASK [include_tasks : create_or_update_site.yml] ****************************
included: 01_create_or_update_site.yml for catalyst_center => (item=Global/NA)
included: 01_create_or_update_site.yml for catalyst_center => (item=Global/NA/HQ San Jose)
included: 01_create_or_update_site.yml for catalyst_center => (item=Global/NA/HQ San Jose/Floor 1)
...

PLAY RECAP ******************************************************************
catalyst_center  : ok=27   changed=8    unreachable=0    failed=0    skipped=3
```

> [!TIP]
> Re-run the same command immediately. The second run should report `changed=0` — that is idempotency.

## Step 5 — Verify the Hierarchy in Catalyst Center

1. In Chrome, navigate to [**Catalyst Center**](https://198.18.129.100). If an SSL warning is displayed, click **Proceed to `https://198.18.129.100` (unsafe)**.

   ![SSL Error](../../images/common/platform/catc-SSLERROR.png?raw=true)

2. Log in:
   * **username:** `admin`
   * **password:** `C1sco12345`

   ![Login](../../images/common/platform/catc-Login.png?raw=true)

3. Click the **&#8801;** icon to open the menu.

   ![Hamburger](../../images/common/platform/catc-Menu.png?raw=true)

4. Select **Design → Network Hierarchy**.

   ![Menu](../../images/common/platform/catc-Menu-Hierarchy.png?raw=true)

5. Expand the hierarchy on the left and confirm that the Area / Building / Floor entries from `settings.json` are present.

   ![Verify](../../images/ansible/hierarchy/catc-Hierarchy-Student-Verify.png?raw=true)

## Summary

You have used a single declarative file (`settings.json`) and one Ansible playbook to build the foundational Catalyst Center site hierarchy. No clicking through Design pages, no UI screenshots to follow, and the same playbook can be re-run any time `settings.json` changes — only the deltas will be applied.

> [**Next Module**](../catc-catcenter-2-settings/01-intro.md)

> [**Return to LAB Menu**](../README.md)

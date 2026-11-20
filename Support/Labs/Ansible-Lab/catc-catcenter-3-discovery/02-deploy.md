# Run the Discovery and Assign-to-Site Playbooks

## Overview Video

[![Device Discovery](https://img.youtube.com/vi/x6ELVGKPJe8/0.jpg)](https://www.youtube.com/watch?v=x6ELVGKPJe8)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

> All commands run on the Script Server using the regular DCLOUD account used during staging, with the `~/tecops-venv` activated.

## Part A — Device Discovery (4.0)

### Step 1 — Confirm the Shared Vault

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
head -1 campus-evpn/group_vars/all/vault.yml
```

### Step 2 — Run the Playbook

```bash
ansible-playbook campus-evpn/playbooks/04_device_discovery.yml \
    --ask-vault-pass
```

Discovery jobs are submitted asynchronously to Catalyst Center. The Workflow Manager module polls each job to completion before returning, so a successful `PLAY RECAP` means every IP in `device_list` has been processed (reachable + authenticated, or marked unreachable with a reason).

> [!TIP]
> If devices land in *Partial Collection Failure* or *Unreachable* state, the cause is almost always credential mismatch. Re-check that the CLI / SNMP credentials assigned to the site in Module 2 match the real device credentials (`netadmin / C1sco12345` for the DCLOUD pods).

### Step 3 — Verify in Catalyst Center

1. **Tools → Discovery** — the most recent job should show as *Complete*.

   ![Discovery Job](../../images/ansible/discovery/discovery.png?raw=true)

2. **Provision → Inventory** — every IP from `device_list` should appear with *Reachability: Reachable* and *Manageability: Managed*.

   ![Inventory](../../images/ansible/discovery/inventory.png?raw=true)

   At this point all devices are sitting under `Global` — that is correct; Part B places them.

## Part B — Assign To Site (5.0)

### Step 4 — Confirm the Shared Vault

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
head -1 campus-evpn/group_vars/all/vault.yml
```

### Step 5 — Run the Playbook

```bash
ansible-playbook campus-evpn/playbooks/05_assign_to_site.yml \
    --ask-vault-pass
```

The recap shows one *changed* result per site that needed devices moved into it. Re-running produces `changed=0`.

### Step 6 — Verify in Catalyst Center

Return to **Provision → Inventory** and look at the **Site** column for each device — it should now reflect the path from `settings.json` (e.g. `Global/NA/Pod-1`) instead of `Global`.

## Summary

The pod devices are in inventory and parked at the correct site. From here Catalyst Center can apply settings, push templates, and provision Day-N config — the next three modules cover those steps.

> [**Next Module**](../catc-catcenter-4-templates/01-intro.md)

> [**Return to LAB Menu**](../README.md)

# Run the Provision and Composite Deploy Playbooks

## Overview Video

[![Device Provisioning pt 1](https://img.youtube.com/vi/S7bYW1pY90A/0.jpg)](https://www.youtube.com/watch?v=S7bYW1pY90A)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

[![Device Provisioning pt 2](https://img.youtube.com/vi/l3niI5GUvTs/0.jpg)](https://www.youtube.com/watch?v=l3niI5GUvTs)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

> All commands run on the Script Server using the regular DCLOUD account used during staging, with the `~/tecops-venv` activated.

## Part A — Provision Devices (8.0)

### Step 1 — Confirm the Shared Vault

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
head -1 campus-evpn/group_vars/all/vault.yml
```

### Step 2 — Run the Playbook

```bash
ansible-playbook campus-evpn/playbooks/08_provision_devices.yml \
    --ask-vault-pass
```

The playbook authenticates once, then loops through each site that has a `device_list`, batching all of that site's devices into a single `POST /v1/sda/provisionDevices` call. Each call is async — the playbook polls `GET /v1/task/<taskId>` until completion before moving on.

> [!TIP]
> A site that already has every device provisioned will report `changed=false` for that batch. The playbook computes a set-difference between the requested IPs and the already-provisioned IPs before submitting; an empty difference skips the call entirely.

### Step 3 — Verify in Catalyst Center

1. Open Catalyst Center → **&#8801; Menu → Provision → Inventory**.

   ![Provision Inventory](../../images/ansible/provisioning/provision.png?raw=true)

2. Confirm each device's **Provisioning Status** column is green / *Success*.

   ![Provision Detail](../../images/ansible/provisioning/provision-detail.png?raw=true)

## Part B — Composite Template Deploy (9.0)

### Step 4 — Confirm the Shared Vault

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
head -1 campus-evpn/group_vars/all/vault.yml
```

### Step 5 — Run the Playbook

```bash
ansible-playbook campus-evpn/playbooks/09_deploy_composite_template.yml \
    --ask-vault-pass
```

For each `DayNTemplateNames` entry with `DeployTemplate: true`, the playbook:

1. Resolves the latest version UUID of the composite template.
2. Resolves the UUID of every target device IP.
3. Builds the `memberTemplateDeploymentInfo` payload (parameters per child template).
4. Submits the deploy via `POST /v2/template-programmer/template/deploy`.
5. Polls the task and surfaces `progress.failureReason` if any member fails to push.

A successful run reports `changed=true` per deploy entry. Re-running redeploys (template deploy has no built-in idempotency in CatC — repeat applies the same intent again, which is safe but is *not* a no-op).

### Step 6 — Verify on the Device

SSH directly to one of the target switches and inspect the running-config (or use the CatC UI's **Command Runner** if you prefer):

```bash
ssh netadmin@198.18.10.2
# C1sco12345
show running-config | section vrf
show running-config | section bgp
show running-config | section nve
```

You should see the BGP EVPN VRF, BGP, and NVE blocks rendered from the composite. The Catalyst Center UI also records the deploy in **Tools → Template Editor → Deployments** with one row per device target.

   ![Composite Deploy](../../images/ansible/composite/composite.png?raw=true)

   ![Provision Show](../../images/ansible/provisioning/provision-show.png?raw=true)

## Summary

You have walked the entire lifecycle of a Catalyst Center managed network through Ansible:

* **Hierarchy** built from `settings.json`.
* **Settings & credentials** applied per site.
* **Devices** discovered, authenticated, and placed at their sites.
* **Templates** synced from GitHub into a CatC Template Project.
* **Network Profile** built and bound to the sites.
* **Devices** provisioned and the composite Day-N template deployed.

Every step is repeatable, idempotent, and captured in version control. Re-running the seven modules against an empty Catalyst Center reproduces the entire fabric state from `settings.json` alone.

> [**Return to LAB Menu**](../README.md)

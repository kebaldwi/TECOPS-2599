# Lab Setup — Inventory, Vault, and Running a Playbook

This section explains the **execution pattern** that every later module follows. Run Ansible from the shared Ansible root so every playbook uses one `ansible.cfg`, inventory, and roles path.

## Overview Video

[![Preparing Ansible](https://img.youtube.com/vi/SP1f1ISY76Y/0.jpg)](https://www.youtube.com/watch?v=SP1f1ISY76Y)
> 💡 Tip: Ctrl/Cmd + Click the thumbnail to open the video in a new tab.

## The Repeating Pattern

The Catalyst Center pipeline is under
[`Support/Resources/Ansible/campus-evpn`](../../../Resources/Ansible/campus-evpn/README.md).
It uses one shared Catalyst Center vault; only stages with additional secrets
need a local vault:

```text
Support/Resources/Ansible/
├── ansible.cfg
├── requirements.txt
├── requirements.yml
├── roles/
├── 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/
└── campus-evpn/
    ├── inventories/lab/hosts.yml
    ├── playbooks/           # flat stage playbooks
    ├── roles/               # project-specific Ansible roles
    ├── vaults/              # encrypted stage-specific secrets
    └── group_vars/all/      # shared Catalyst Center vault
```

The server staging script creates
`campus-evpn/group_vars/all/vault.yml` after prompting for the CatC admin and
Vault passwords. Stages 2.0 and 3.0 require local vaults for network AAA and
device credential secrets. Stage 6.0's local vault is optional and is only
needed for a GitHub token. Use the same Vault password for all these files.

## The Source of Truth — `settings.json`

The intent that drives every playbook in this suite lives in a single file:

```text
~/TECOPS-2599/Support/Resources/Data-Models/campus-evpn/settings.json
```

This is the same file consumed by the Cisco Workflows track. Each playbook reads it (the path is set in `campus-evpn/inventories/lab/hosts.yml` as `settings_json_path`) and acts on the relevant block:

| Block in `settings.json` | Consumed by |
|--------------------------|-------------|
| `HierarchyParent / Area / Bldg / Floor / BldgAddress` | 1.0 Hierarchy |
| `network_settings` | 2.0 Settings |
| `device_credentials` / `assign_credentials` | 3.0 Credentials |
| `device_list` | 4.0 Discovery, 5.0 Assign-to-Site, 8.0 Provision |
| `network_profile` | 7.0 Network Profile |
| `DayNTemplateNames` | 9.0 Composite Deploy |

Edit this single file and every downstream playbook will pick up the change on its next run.

## The Vault

Catalyst Center API credentials come from the shared encrypted vault created during script-server staging. Stage-local vaults are required only for additional secrets: network AAA in 2.0, device CLI/SNMP credentials in 3.0, and an optional GitHub token in 6.0. Use the same Vault password for all files.

### Encrypt Stage-Specific Secrets

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
cp campus-evpn/vaults/network_settings.yml.example campus-evpn/vaults/network_settings.yml
cp campus-evpn/vaults/device_credentials.yml.example campus-evpn/vaults/device_credentials.yml
# Edit each file to supply the lab AAA and device secrets, then encrypt them.
ansible-vault encrypt campus-evpn/vaults/network_settings.yml --ask-vault-pass
ansible-vault encrypt campus-evpn/vaults/device_credentials.yml --ask-vault-pass
```

Generated `vault.yml` files are git-ignored; never commit them in plaintext.

## Running a Playbook — The One-Liner

Run a playbook with the same Vault password:

```bash
ansible-playbook campus-evpn/playbooks/<playbook>.yml --ask-vault-pass
```

The shared configuration selects the campus inventory by default.

Useful flags:

| Flag | Purpose |
|------|---------|
| `--check` | Dry-run — show what *would* change without calling CatC |
| `-v` / `-vv` / `-vvv` | Increase verbosity (the third `-v` shows raw HTTP traffic) |
| `--tags <tag>` | Run only tasks with the given tag (rarely needed in this lab) |
| `--limit <host>` | Restrict to a subset of inventory hosts |

### Reading a `PLAY RECAP`

Every successful run finishes with a recap line per host. For Catalyst Center playbooks the only "host" is `catalyst_center` and you want:

```text
PLAY RECAP *********************************************************************
catalyst_center            : ok=12   changed=4    unreachable=0    failed=0    skipped=2
```

* **`ok`** — task ran and target is in desired state (no API change required).
* **`changed`** — task ran and changed state in CatC (e.g. created a site, updated a setting).
* **`unreachable`** — Catalyst Center could not be contacted (VPN down? wrong IP?).
* **`failed`** — module returned an error (look immediately above for the failing task and its `msg:`).

Re-running a successful playbook should always produce `changed=0` — that is *idempotency* in action and is the property that makes Ansible safe to run on a schedule.

## What's Next

You are fully set up. From here, every module follows the same drumbeat:

1. Stay in `Support/Resources/Ansible` and select the stage playbook under
   `campus-evpn/playbooks/`.
2. Create and encrypt a local vault only for stages 2.0, 3.0, or optionally 6.0.
3. Run the playbook with the shared Vault password.
4. Verify the result in the Catalyst Center UI.

> [**Next Module**](../catc-catcenter-1-hierarchy/01-intro.md)

> [**Return to LAB Menu**](../README.md)

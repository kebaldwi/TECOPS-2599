# Ansible Automation

The Ansible automation is organized by EVPN deployment domain:

| Project | Purpose |
|---|---|
| [campus-evpn/](campus-evpn/README.md) | Catalyst Center automation for the Cat9kv campus EVPN lab |
| [dc-evpn/](dc-evpn/README.md) | Nexus Dashboard automation for the NX-OSv data-center VXLAN EVPN fabric and its IP Core handoff |

Shared project data models live in [Data-Models/](../../../Projects/Data-Models/).

## Shared Ansible Environment

The common `ansible.cfg`, Python requirements, Galaxy collection requirements,
and shared roles are at this directory's root. Project-specific roles live in
each project's `roles/` directory; the common configuration searches both the
shared and campus role paths. The script-server bootstrap is shared by both
EVPN projects and must be run first. It stores the Ansible Vault password in
`~/.ansible/vault_pass` with owner-only permissions and configures the
script-server virtual environment to export its path.

```bash
cd Support/Resources/Ansible
./0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/stage-script-server.sh
```

Run Ansible commands from this directory so Ansible discovers the common
configuration. The VS Code Ansible extension is also pointed at this shared
configuration so editor diagnostics resolve the same inventory and roles. The
default inventory targets the campus Catalyst Center lab. After activating the
script-server virtual environment, Ansible uses its Vault password file
automatically, so `--ask-vault-pass` is not required.

The data-center pipeline has its own `dc-evpn/ansible.cfg` (inventory plus a
pipeline-local pre-release `cisco.nd` collection), so run it from
`dc-evpn/`; see the [dc-evpn README](dc-evpn/README.md).

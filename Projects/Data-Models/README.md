# Data Models

Intent and data models for every project in this repository. The automation
paths read them from here: Ansible, Cisco Workflows (through the GitHub
repository path) and Python.

| Folder | Model | Used by |
|---|---|---|
| [campus-evpn/](campus-evpn/README.md) | `settings.json` and the `BGP_EVPN/` templates for the Catalyst Center campus EVPN fabric | [Ansible campus-evpn](../../Support/Resources/Ansible/campus-evpn/README.md), [Cisco Workflows](../../Support/Resources/Cisco%20Workflows/README.md), [Python](../../Support/Resources/Python/README.md) |
| [dc-evpn/](dc-evpn/README.md) | Nexus as Code `host_vars` for the `TECOPS-DC1` VXLAN EVPN fabric | [Ansible dc-evpn](../../Support/Resources/Ansible/dc-evpn/README.md) |
| [catalyst-center/](catalyst-center/README.md) | `settings.json` for the Traditional (non-EVPN) project; its templates stay in [TRADITIONAL/](../TRADITIONAL/) | Cisco Workflows, Ansible and Python |

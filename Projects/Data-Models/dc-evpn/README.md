# Data-Center EVPN Data Models

Nexus as Code (`cisco.nac_dc_vxlan`) data model for the `TECOPS-DC1` VXLAN
EVPN fabric, used by the [dc-evpn pipeline](../../../Support/Resources/Ansible/dc-evpn/README.md).

| File | Holds |
|---|---|
| `host_vars/TECOPS-DC1/global.nac.yaml` | Fabric name and type, iBGP AS 65005, route reflectors, VNI ranges |
| `host_vars/TECOPS-DC1/underlay.nac.yaml` | /31 underlay links |
| `host_vars/TECOPS-DC1/topology_switches.nac.yaml.example` | Switches, roles, management IPs and vPC port-channels |
| `host_vars/TECOPS-DC1/topology_vpc.nac.yaml` | dc-leaf1/dc-leaf2 vPC pair |
| `host_vars/TECOPS-DC1/vrfs.nac.yaml` | VRFs `red`, `green`, `blue` and their attach group |
| `host_vars/TECOPS-DC1/networks.nac.yaml` | One network per VRF and its vPC attachments |

Nexus as Code reads the model from the playbook directory, so
`Support/Resources/Ansible/dc-evpn/playbooks/host_vars` is a relative link to `host_vars/` here.
Stage 01 writes `topology_switches.nac.yaml` (with the lab's serial numbers)
next to the `.example` file. That file is generated and git-ignored.

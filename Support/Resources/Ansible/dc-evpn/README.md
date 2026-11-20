# Data-Center EVPN — Nexus Dashboard Ansible Automation

This pipeline builds the VXLAN EVPN data-center fabric `TECOPS-DC1` on Cisco
Nexus Dashboard 4.3.1 from a declarative YAML model. It also hands the DC
`red`, `green` and `blue` VRFs to the IP Core (`core1`/`core2`), where they are
fused into the global routing table.

It is a port of the CiscoOne Experience Lab data-center track to the CML
topology in [EVPN_Campus_v15.yaml](../../CML/Topology/EVPN_Campus_v15.yaml).

## What it builds

| Object | Values |
|---|---|
| Fabric | `TECOPS-DC1`, VXLAN EVPN, iBGP AS `65005`, two spine route reflectors, /31 underlay |
| Switches | dc-spine1 `198.18.1.115`, dc-spine2 `.116` (spine), dc-border1 `.117` (border), dc-leaf1 `.118`, dc-leaf2 `.119` (leaf) |
| vPC | dc-leaf1/dc-leaf2, peer-link Ethernet1/3-4 (auto-detected), Port-channel5/6/7 as vPC 5/6/7 |
| VRFs | `red` 50000, `green` 50001, `blue` 50002 (VLAN 2000-2002) |
| Networks | RedNetwork1 `10.200.10.1/24`, GreenNetwork1 `10.200.20.1/24`, BlueNetwork1 `10.200.30.1/24` |
| Hosts (CML v15) | dc-red01 `10.200.10.10`, dc-green01 `10.200.20.10`, dc-blue01 `10.200.30.10`, LACP-bonded to both leaves |
| External fabric | `TECOPS-External`, AS `65002`, Monitor Mode, with `core1` `198.18.1.108` and `core2` `198.18.1.109` |
| Handoffs | Six L3Outs: each VRF on dc-border1 Ethernet1/3 → core1 Ethernet1/7 and Ethernet1/4 → core2 Ethernet1/7 |

### VRF-Lite handoff and core fusion

| L3Out | VRF | Border leaf | Core | dot1q | Border address | Core address |
|---|---|---|---|---:|---|---|
| red-core1 | red | Ethernet1/3.2 | core1 Ethernet1/7.2 | 2 | 198.19.4.1/30 | 198.19.4.2 |
| green-core1 | green | Ethernet1/3.3 | core1 Ethernet1/7.3 | 3 | 198.19.4.5/30 | 198.19.4.6 |
| blue-core1 | blue | Ethernet1/3.4 | core1 Ethernet1/7.4 | 4 | 198.19.4.9/30 | 198.19.4.10 |
| red-core2 | red | Ethernet1/4.2 | core2 Ethernet1/7.2 | 2 | 198.19.4.13/30 | 198.19.4.14 |
| green-core2 | green | Ethernet1/4.3 | core2 Ethernet1/7.3 | 3 | 198.19.4.17/30 | 198.19.4.18 |
| blue-core2 | blue | Ethernet1/4.4 | core2 Ethernet1/7.4 | 4 | 198.19.4.21/30 | 198.19.4.22 |

The IP Core side is not part of the pipeline. Apply it by hand from the
incremental CLI snippets
[core01-dc-vrf-fusion.cfg](<../../CML/Startup Configs/core01-dc-vrf-fusion.cfg>) and
[core02-dc-vrf-fusion.cfg](<../../CML/Startup Configs/core02-dc-vrf-fusion.cfg>),
then bake them into the core startup configs. Each snippet creates the three
VRFs, the sub-interfaces and one eBGP neighbor per VRF (AS 65002 ↔ 65005), and
fuses the VRFs into the global table:

- `export vrf default map DC-FUSION-EXPORT` leaks the DC network subnets
  (prefix-list `DC-FUSION-SEGMENTS`) from each VRF into the core's global
  table.
- `import vrf default map DC-FUSION-IMPORT` leaks the global table into each
  VRF, including the default route and the campus prefixes. The DC subnets
  themselves are denied, so the DC VRFs stay separate from each other.
- The DC therefore learns its default route from the cores, and the fabric
  does not advertise one (`dc_vrf_lite_advertise_default_route: false`).

The snippets repeat values the pipeline owns: the addresses and dot1q tags in
`dc_vrf_lite.yml` and the subnets in `networks.nac.yaml`. Keep both in step
when either changes. Advertising the DC subnets onward to the campus fabric is
a follow-up item; see [Open items](#open-items).

## How it works

```text
Projects/Data-Models/dc-evpn/host_vars/TECOPS-DC1/*.nac.yaml   declarative model
  -> cisco.nac_dc_vxlan.validate / dtc.create / dtc.deploy   (stages 02, 06)
  -> cisco.dcnm modules -> Nexus Dashboard 198.18.133.101 -> DC switches
dc-evpn/inventory/group_vars/all/*.yml                settings NaC cannot express
  -> cisco.nd nd_manage_* modules                     (stages 03, 04, 05, 07)
```

Nexus as Code reads the model from `playbooks/host_vars/<fabric>/`.
[playbooks/host_vars](playbooks/host_vars) is a relative link to
[Projects/Data-Models/dc-evpn/host_vars](../../../../Projects/Data-Models/dc-evpn/host_vars), so the
model lives with the other project data models.

## Prerequisites

1. Stage the script server once. This is the shared bootstrap from
   [0.0](../0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/README.md). It
   installs the pinned collections, installs the pre-release `cisco.nd` into
   `dc-evpn/collections/`, and creates the encrypted
   `dc-evpn/inventory/group_vars/all/vault.yml`.
2. Load [EVPN_Campus_v15.yaml](../../CML/Topology/EVPN_Campus_v15.yaml) in CML.
   v15 adds the vPC peer-link and the three dual-homed DC hosts to the v14
   topology.
3. Apply the IP Core snippets to core1 and core2 (see
   [VRF-Lite handoff and core fusion](#vrf-lite-handoff-and-core-fusion)).
4. Make sure the script server can reach Nexus Dashboard (`198.18.133.101`) and
   the switch management network `198.18.1.0/24`.

On a server staged before dc-evpn existed, pull the repository and rerun the
bootstrap. To install `cisco.nd` by hand instead:

```bash
cd Support/Resources/Ansible/dc-evpn
ansible-galaxy collection install -r collections/requirements-cisco-nd.yml -p collections --no-deps --force
```

## Run the pipeline

dc-evpn has its own `ansible.cfg` (its own inventory, plus the local
`cisco.nd` collection), so run it from this directory:

```bash
source ~/tecops-venv/bin/activate
cd Support/Resources/Ansible/dc-evpn
ansible-playbook playbooks/00_dc_deploy.yml
```

The orchestrator runs each stage as its own `ansible-playbook` process and
stops at the first failure. Each stage's full output is saved under
`evidence/dc-deploy-<run>/`.

| # | Playbook | Collection | Outcome |
|---|---|---|---|
| 01 | `01_discover_serials.yml` | `cisco.nxos` | Reads chassis serials from the 5 DC switches and both cores over SSH, then generates `topology_switches.nac.yaml` and `inventory/group_vars/all/dc_device_serials.yml` (both git-ignored) |
| 02 | `02_create_dc_fabric.yml` | `cisco.nac_dc_vxlan` | Validates the model, then creates the fabric, imports the switches, and adds the vPC pair, port-channels, VRFs, networks and attachments |
| 03 | `03_fabric_advanced_settings.yml` | `cisco.nd` | VRF-Lite manual mode, telemetry off, location |
| 04 | `04_external_fabric.yml` | `cisco.nd` | `TECOPS-External` fabric in Monitor Mode, adds core1/core2, and builds one `ebgpVrfLite` link per core |
| 05 | `05_l3out.yml` | `cisco.nd` | Creates and attaches the six L3Outs |
| 06 | `06_recalculate_and_deploy.yml` | `cisco.nac_dc_vxlan` / `cisco.dcnm` | Recalculate and Deploy. Changes the DC switches' running configuration |
| 07 | `07_cleanup.yml` | `cisco.nd` / `cisco.nxos` | Destructive teardown, not run by the orchestrator. Needs `-e dc_cleanup_confirm=CLEANUP_OK` |

Every stage can also be run on its own in the order above.

## Intent and configuration

| File | Holds |
|---|---|
| `Projects/Data-Models/dc-evpn/host_vars/TECOPS-DC1/global.nac.yaml` | Fabric name, type, ASN, route reflectors, VNI ranges |
| `.../underlay.nac.yaml` | /31 underlay links |
| `.../topology_switches.nac.yaml.example` | Switches, roles, management IPs, vPC port-channels. Stage 01 copies it and fills in the serials |
| `.../topology_vpc.nac.yaml` | dc-leaf1/dc-leaf2 vPC pair |
| `.../vrfs.nac.yaml`, `.../networks.nac.yaml` | VRFs, networks, anycast gateways and attach groups |
| `inventory/group_vars/all/dc_switches.yml` | Switch names, management IPs and roles (single source for stage 01) |
| `inventory/group_vars/all/dc_external_settings.yml` | External fabric settings and the IP Core devices |
| `inventory/group_vars/all/dc_vrf_lite.yml` | VRF-Lite fabric mode, links, and L3Out rows. Read by stages 03-05 and 07 |
| `inventory/group_vars/all/dc_advanced_settings.yml` | Fabric options with no Nexus as Code key |
| `inventory/group_vars/all/vault.yml` | Encrypted Nexus Dashboard and NX-OS credentials ([example](inventory/group_vars/all/vault.yml.example)) |

The model is the source of truth. To change the fabric, edit the model and
rerun the pipeline. Rerunning converges the controller onto the YAML.

## Important behavior

- Stage 02 imports the five DC switches with `preserve_config: false`, which
  erases their running configuration without prompting.
- Stage 02 can stay silent for several minutes while Nexus Dashboard discovers
  the switches. The 1000 s httpapi timeouts are deliberate.
- Stages 02-05 only write intent to Nexus Dashboard. Stage 06 is the only stage
  that changes the DC switches. Nothing in the pipeline changes the cores.
- The External fabric is in Monitor Mode, so Nexus Dashboard never writes to
  the cores.
- `07_cleanup.yml` removes the L3Outs, overlays, links, switches and both
  fabrics, then strips the VRF-Lite sub-interfaces and defaults Ethernet1/3-4
  on dc-border1. It does not touch the cores; their hand-applied fusion config
  stays in place.

## Maintainer notes

Carried over from the reference pipeline, where they were validated on Nexus
Dashboard 4.2.1:

- **Separate processes.** ansible-core keys persistent connections on address,
  port, user and connection type, not on `ansible_network_os`. A `cisco.nd`
  stage could therefore reuse the `cisco.dcnm` httpapi connection that a
  previous stage left open. The orchestrator avoids this by running each stage
  in its own process.
- **Chassis serial.** Use the chassis serial from `show inventory | json`. On
  Nexus 9000v, `show version` reports the supervisor board ID instead. The
  `name` field arrives with literal quotes, so it is matched by substring.
- **`cisco.nd` pre-release.** `cisco.nd` is pinned to commit `671e596` of
  `CiscoDevNet/ansible-nd` develop; the released 1.5.0 has no `nd_manage_*`
  modules. When `cisco.nd` 2.0.0 ships, move it to `requirements.yml`.
- **Stage 03 sends only declared keys.** `nd_manage_fabric_ibgp_vxlan
  state: merged` sends only the declared keys. A `gathered` read runs first,
  because `merged` against a missing fabric tries to create it.
- **Stage 04 safety and links.**
  - `nd_manage_switches` saves and deploys by default, so stage 04 turns both
    off, and Monitor Mode is a second guard.
  - `nd_manage_l3out` does not create links, so `nd_manage_links` builds them.
    Always set `link_mtu`; omitted template inputs fall back to policy
    defaults such as 9216.
- **Stage 05 L3Out quirks.**
  - `interface_name` must be the sub-interface (`Ethernet1/3.2`).
  - Updating an L3Out resets `attach`, so stage 05 re-attaches. The module
    reports `changed` on every attach, and attach failures arrive as
    warnings, so `failed_when` checks for them.
  - `tasks/l3out_config.yml` must build its list with a single-expression
    `set_fact` loop.
- **Stage 06 needs two calls.** `config-save` recalculates, but switches only
  read Out-of-Sync after `config-preview`, which is what the NaC deploy role
  selects on.
- **Stage 07 order.** The order is L3Outs → overlays → links → switches →
  fabrics → border-leaf sub-interfaces. Switch removal uses `force=true`
  because an unforced border-leaf removal fails.
- **Data model rules.**
  - Port-channel descriptions must be plain ASCII; an em dash causes HTTP 500.
  - A vPC pair cannot be edited in place.
  - Always set `vlan_id` on VRFs and networks.

## Open items

- **Campus side of the fusion.** The cores' `TO_CAMPUS` route-map still sends
  only the default route to the campus borders, and `BGP-TO-OSPF` does not
  redistribute the DC subnets. Campus hosts still reach the DC via the core
  default route.
- **Fabric verification stage.** The reference track's verify report
  is intentionally not ported, so pyATS/Genie is not required.
- **First run on Nexus Dashboard 4.3.1.** The reference was validated on ND
  4.2.1.10. Confirm these on the first v15 run:
  - NX-OS core discovery over SNMPv3 into the External fabric.
  - vPC on NX-OSv 10.6.
  - LACP bonding on the CML Alpine hosts.

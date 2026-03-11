# Cisco Modeling Labs (CML) Resources

CML topology files, startup configurations, and utility scripts for project **TECOPS-2599 — Cisco Live 2026**.

---

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Available Topologies](#available-topologies)
3. [Topology Diagram](#topology-diagram)
4. [CML Version Compatibility](#cml-version-compatibility)
5. [Importing a Topology](#importing-a-topology)
6. [Starting the Lab](#starting-the-lab)
7. [Accessing Node Consoles](#accessing-node-consoles)
8. [References](#references)

---

## Directory Structure

```
CML/
├── Topology/
│   ├── EN-Sandbox-Lab-v1.yaml          # Enterprise Network Sandbox — Version 1
│   ├── EVPN_Campus_v1.yaml             # EVPN Campus topology — Version 1
│   ├── EVPN_Campus_v2.yaml             # EVPN Campus topology — Version 2 (recommended)
│   └── EVPN_Campus_v2_normalized.yaml  # Version 2 normalized for CML < 2.9.1
├── Startup Configs/
│   ├── README.md                       # IP addressing schema (198.18.128.0/18)
│   ├── spine01_startup.cfg
│   ├── spine02_startup.cfg
│   ├── leaf01_startup.cfg
│   ├── leaf02_startup.cfg
│   ├── border01_startup.cfg
│   ├── border02_startup.cfg
│   ├── core01.cfg
│   ├── core02.cfg
│   ├── fw.cfg
│   ├── dhcp.cfg
│   └── dmz01_startup.cfg
└── Scripts/
    └── cml_normalize.py                # Normalizes topology files for CML < 2.9.1
```

---

## Available Topologies

| File | Description |
|------|-------------|
| `Topology/EN-Sandbox-Lab-v1.yaml` | Enterprise Network Sandbox — Version 1 |
| `Topology/EVPN_Campus_v1.yaml` | EVPN Campus topology — Version 1 |
| `Topology/EVPN_Campus_v2.yaml` | EVPN Campus topology — Version 2 (current) |
| `Topology/EVPN_Campus_v2_normalized.yaml` | Version 2 pre-normalized for CML < 2.9.1 |

**Recommended:** Use `EVPN_Campus_v2.yaml` on CML 2.9.1 or later. Use `EVPN_Campus_v2_normalized.yaml` on earlier versions.

---

## Topology Diagram

![CML v2 Topology](../images/cml_v2_topology.png)

---

## CML Version Compatibility

> **Important:** The topology files in this repository were generated with **Cisco CML 2.9.1**. Importing them into an earlier version may fail or produce unexpected results due to schema differences between releases.

### Importing into CML < 2.9.1

A pre-normalized file (`EVPN_Campus_v2_normalized.yaml`) is already included. If you need to normalize a different topology file, use the provided Python script:

```bash
cd Scripts
python cml_normalize.py ../Topology/EVPN_Campus_v2.yaml
```

The script applies the following changes to produce a backward-compatible file:

| Field | Original | Normalized |
|-------|----------|------------|
| Lab version | `0.3.0` | `0.0.1` |
| `mac_address` | `null` | removed |
| `smart_annotations` | `[]` | removed |

The normalized file is written to the same directory as the input file with a `_normalized` suffix.

---

## Importing a Topology

### Prerequisites

- Access to a running Cisco CML server (version 2.x or later)
- A valid CML topology file (`.yaml`) from the `Topology/` directory
- A user account with **Lab Manager** or **Admin** privileges

### Steps

1. Open a browser and navigate to your CML server:
   ```
   https://<CML-SERVER-IP-OR-HOSTNAME>
   ```
2. Log in with your credentials and confirm you are on the **Dashboard → Labs** view.
3. Click **Import** (top-right), then **Choose File** or drag and drop the desired `.yaml` file.
4. Click **Import** to confirm.

> **Note:** CML validates the topology during import. If node images referenced in the file are not available on your server, you will receive a warning. Ensure all required node definitions and images are installed before starting the lab.

---

## Starting the Lab

1. Click the imported lab name in the Dashboard to open the **Topology Editor**.
2. Review nodes and links, then click the **Start Lab** button (▶) in the toolbar.
3. Monitor node status indicators until all required nodes reach **Green (Running)**:

   | Colour | Status |
   |--------|--------|
   | Gray | Not started |
   | Yellow | Booting |
   | Green | Running |

4. Proceed with configuration only after all nodes are in the **Running** state.

---

## Accessing Node Consoles

- Click any node in the Topology Editor to open the **Node Details** panel, then click **Open Console** for an in-browser terminal session.
- If External Connectors are configured, nodes are also reachable via SSH from the management network (`198.18.128.0/24`). See `Startup Configs/README.md` for the full IP addressing schema.

---

## References

- [Cisco CML Documentation](https://developer.cisco.com/docs/modeling-labs/)
- [CML REST API Reference](https://developer.cisco.com/docs/modeling-labs/#!rest-api-reference)
- [Cisco DevNet — Modeling Labs](https://developer.cisco.com/modeling-labs/)

---

## Author

**Igor Manassypov**  
Systems Engineer, Cisco Systems  
[imanassy@cisco.com](mailto:imanassy@cisco.com)  
Copyright © 2024–2026 Cisco Systems, Inc. All rights reserved.

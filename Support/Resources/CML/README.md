# CML

CML for Project **TECOPS-2599**

## Available Topologies

| File | Description |
|------|-------------|
| `EN-Sandbox-Lab-v1.yaml` | Enterprise Network Sandbox Lab - Version 1 |
| `EVPN_Campus_v1.yaml` | EVPN Campus Topology - Version 1 |
| `EVPN_Campus_v2.yaml` | EVPN Campus Topology - Version 2 |

---

## Topology Diagram

![CML v2 Topology](../images/cml_v2_topology.png)

---

## CML Compatibility

> **Important:** The topology files in this repository were generated using **Cisco CML 2.9.1**. Importing them into an earlier version of CML may fail or produce unexpected results due to schema differences between versions.

### Importing into an Earlier CML Version

If you need to import a topology into a CML version older than 2.9.1, use the included Python script to normalize the file first:

```bash
python cml_normalize.py <topo.yml>
```

This will produce a normalized version of the topology compatible with earlier CML releases. Replace `<topo.yml>` with the actual topology filename, for example:

```bash
python cml_normalize.py EVPN_Campus_v2.yaml
```

---

## Importing a CML Topology into Cisco CML

Follow these Cisco Validated steps to import a topology file (`.yaml`) into your Cisco CML instance.

### Prerequisites

- Access to a running Cisco CML server (version 2.x or later)
- A valid CML topology file (`.yaml`) from this directory
- A user account with **Lab Manager** or **Admin** privileges on the CML server

---

### Step 1 — Log In to Cisco CML

1. Open a web browser and navigate to your CML server URL:
   ```
   https://<CML-SERVER-IP-OR-HOSTNAME>
   ```
2. Enter your **username** and **password**.
3. Click **Login**.

---

### Step 2 — Navigate to the Dashboard

1. After logging in, you will land on the **Dashboard**.
2. Confirm you are in the **Labs** view (top navigation menu).

---

### Step 3 — Import the Topology File

1. Click the **Import** button (top-right area of the Dashboard).
2. In the dialog that appears, click **Choose File** (or drag and drop).
3. Browse to the location where you saved the topology `.yaml` file from this repository.
4. Select the desired file (e.g., `EVPN_Campus_v2.yaml`) and click **Open**.
5. Click **Import** to confirm.

> **Note:** CML will validate the topology file during import. If any node images referenced in the topology are not available on your CML server, you will receive a warning. Ensure the required node definitions and images are installed before starting the lab.

---

### Step 4 — Open the Imported Lab

1. The imported lab will appear in your **Labs** list on the Dashboard.
2. Click the lab name to open it in the **Topology Editor**.

---

### Step 5 — Start the Lab

1. In the Topology Editor, review the topology to confirm all nodes and links are correct.
2. Click the **Start Lab** button (▶) in the toolbar.
3. CML will begin booting all nodes. Monitor the node status indicators:
   - **Gray** — Not started
   - **Yellow** — Booting
   - **Green** — Running
4. Wait until all required nodes reach **Green** (Running) state before proceeding with configuration.

---

### Step 6 — Access Node Consoles

1. Click on any node in the topology to open the **Node Details** panel.
2. Click **Open Console** to launch an in-browser terminal session to the device.
3. Alternatively, use the **External Connectors** (if configured) to access nodes via SSH.

---

### Additional References

- [Cisco CML Documentation](https://developer.cisco.com/docs/modeling-labs/)
- [CML REST API](https://developer.cisco.com/docs/modeling-labs/#!rest-api-reference)
- [Cisco DevNet CML](https://developer.cisco.com/modeling-labs/)

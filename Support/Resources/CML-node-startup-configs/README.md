# CML Lab – IP Addressing Schema
## TECOPS-2599 | Cisco Live 2026

> **dCloud Allocated Block:** `198.18.128.0/18`

---

## Table of Contents

- [Address Block Allocation](#address-block-allocation)
- [Management Network](#management-network)
- [Loopback Addresses](#loopback-addresses)
- [Fabric Point-to-Point Links](#fabric-point-to-point-links)
- [Per-Device Summary](#per-device-summary)
- [Routing Protocol Reference](#routing-protocol-reference)
- [Special Addresses](#special-addresses)

---

## Address Block Allocation

| Subnet             | Purpose                  | Notes                          |
|--------------------|--------------------------|--------------------------------|
| `198.18.128.0/24`  | Out-of-Band Management   | VRF `Mgmt-vrf` / `management` |
| `198.18.129.0/24`  | Loopback Addresses       | /32 host routes                |
| `198.18.130.0/24`  | Fabric P2P Links         | /30 subnets (`.0` – `.75` used, `.76`–`.255` reserved) |
| `198.18.131.0/24`  | _Reserved_               |                                |
| `198.18.128.0/18`  | **Total dCloud Block**   | `198.18.128.0 – 198.18.191.255` |

> **Fabric P2P links** use `/30` subnets from `198.18.130.0/24`, keeping all lab addresses within the dCloud-allocated block.

---

## Management Network

**Subnet:** `198.18.128.0/24`  
**Default Gateway:** `198.18.128.1`  
**VRF (IOS-XE):** `Mgmt-vrf`  
**VRF (NX-OS):** `management`  
**Interface (IOS-XE):** `GigabitEthernet0/0`  
**Interface (NX-OS):** `mgmt0`

| Hostname   | Platform    | Mgmt Interface   | IP Address          |
|------------|-------------|------------------|---------------------|
| Spine-01   | IOS-XE      | GigabitEthernet0/0 | `198.18.128.101/24` |
| Spine-02   | IOS-XE      | GigabitEthernet0/0 | `198.18.128.102/24` |
| Leaf-01    | IOS-XE      | GigabitEthernet0/0 | `198.18.128.103/24` |
| Leaf-02    | IOS-XE      | GigabitEthernet0/0 | `198.18.128.104/24` |
| Border-01  | IOS-XE      | GigabitEthernet0/0 | `198.18.128.105/24` |
| Border-02  | IOS-XE      | GigabitEthernet0/0 | `198.18.128.106/24` |
| dmz1       | IOS-XE      | GigabitEthernet0/0 | `198.18.128.107/24` |
| core1      | NX-OS       | mgmt0              | `198.18.128.108/24` |
| core2      | NX-OS       | mgmt0              | `198.18.128.109/24` |

---

## Loopback Addresses

**Subnet:** `198.18.129.0/24` (host /32 assignments)  
**Interface:** `Loopback0` (IOS-XE) / `loopback0` (NX-OS)  
**Purpose:** OSPF Router-ID, BGP Router-ID, BGP update-source

> **Address assignment convention:** Last octet preserved from original internal scheme for easy cross-referencing.

| Hostname   | Platform | Loopback0 Address    | OSPF RID          | BGP RID           |
|------------|----------|----------------------|-------------------|-------------------|
| Spine-01   | IOS-XE   | `198.18.129.1/32`    | `198.18.129.1`    | `198.18.129.1`    |
| Spine-02   | IOS-XE   | `198.18.129.2/32`    | `198.18.129.2`    | `198.18.129.2`    |
| Leaf-01    | IOS-XE   | `198.18.129.3/32`    | `198.18.129.3`    | `198.18.129.3`    |
| Leaf-02    | IOS-XE   | `198.18.129.4/32`    | `198.18.129.4`    | `198.18.129.4`    |
| Border-01  | IOS-XE   | `198.18.129.5/32`    | `198.18.129.5`    | `198.18.129.5`    |
| Border-02  | IOS-XE   | `198.18.129.6/32`    | `198.18.129.6`    | `198.18.129.6`    |
| core1      | NX-OS    | `198.18.129.8/32`    | `198.18.129.8`    | `198.18.129.8`    |
| core2      | NX-OS    | `198.18.129.9/32`    | `198.18.129.9`    | `198.18.129.9`    |
| dmz1       | IOS-XE   | `198.18.129.200/32`  | `198.18.129.200`  | `198.18.129.200`  |

### Anycast RP (PIM)

| Interface            | Address              | Description                         |
|----------------------|----------------------|-------------------------------------|
| core1 `loopback1`    | `198.18.129.254/32`  | PIM Anycast RP (shared with core2)  |
| core2 `loopback1`    | `198.18.129.254/32`  | PIM Anycast RP (shared with core1)  |

---

## Fabric Point-to-Point Links

> All P2P links use `/30` subnets from `198.18.130.0/24`.

### Spine-01 (IOS-XE) — `198.18.129.1`

| Interface        | Peer        | Peer Interface   | Spine-01 IP          | Peer IP              | Subnet                |
|------------------|-------------|------------------|----------------------|----------------------|-----------------------|
| Gi1/0/1          | Leaf-01     | Gi1/0/1          | `198.18.130.1`       | `198.18.130.2`       | `198.18.130.0/30`     |
| Gi1/0/2          | Leaf-02     | Gi1/0/1          | `198.18.130.5`       | `198.18.130.6`       | `198.18.130.4/30`     |
| Gi1/0/3          | Border-01   | Gi1/0/1          | `198.18.130.9`       | `198.18.130.10`      | `198.18.130.8/30`     |
| Gi1/0/4          | Border-02   | Gi1/0/1          | `198.18.130.13`      | `198.18.130.14`      | `198.18.130.12/30`    |
| Gi1/0/5          | core1       | Eth1/1           | `198.18.130.33`      | `198.18.130.34`      | `198.18.130.32/30`    |
| Gi1/0/6          | core2       | Eth1/1           | `198.18.130.37`      | `198.18.130.38`      | `198.18.130.36/30`    |

### Spine-02 (IOS-XE) — `198.18.129.2`

| Interface        | Peer        | Peer Interface   | Spine-02 IP          | Peer IP              | Subnet                |
|------------------|-------------|------------------|----------------------|----------------------|-----------------------|
| Gi1/0/1          | Leaf-01     | Gi1/0/2          | `198.18.130.17`      | `198.18.130.18`      | `198.18.130.16/30`    |
| Gi1/0/2          | Leaf-02     | Gi1/0/2          | `198.18.130.21`      | `198.18.130.22`      | `198.18.130.20/30`    |
| Gi1/0/3          | Border-01   | Gi1/0/2          | `198.18.130.25`      | `198.18.130.26`      | `198.18.130.24/30`    |
| Gi1/0/4          | Border-02   | Gi1/0/2          | `198.18.130.29`      | `198.18.130.30`      | `198.18.130.28/30`    |
| Gi1/0/5          | core1       | Eth1/2           | `198.18.130.41`      | `198.18.130.42`      | `198.18.130.40/30`    |
| Gi1/0/6          | core2       | Eth1/2           | `198.18.130.45`      | `198.18.130.46`      | `198.18.130.44/30`    |

### core1 / core2 (NX-OS) — DMZ Links

| Interface        | Peer        | Peer Interface   | Core IP              | Peer IP              | Subnet                |
|------------------|-------------|------------------|----------------------|----------------------|-----------------------|
| core1 Eth1/3     | dmz1        | Gi1/0/1          | `198.18.130.65`      | `198.18.130.66`      | `198.18.130.64/30`    |
| core2 Eth1/3     | dmz1        | Gi1/0/2          | `198.18.130.69`      | `198.18.130.70`      | `198.18.130.68/30`    |
| dmz1 Gi1/0/3     | FW          | Gi1              | `198.18.130.73`      | `198.18.130.74`      | `198.18.130.72/30`    |

### core1 / core2 — PIM Sub-interfaces (dot1q tag 2, same physical cables as Spine links)

| Interface        | IP Address           | Subnet               |
|------------------|----------------------|----------------------|
| core1 Eth1/1.2   | `198.18.130.49/30`   | `198.18.130.48/30`   |
| core2 Eth1/1.2   | `198.18.130.53/30`   | `198.18.130.52/30`   |
| core1 Eth1/2.2   | `198.18.130.57/30`   | `198.18.130.56/30`   |
| core2 Eth1/2.2   | `198.18.130.61/30`   | `198.18.130.60/30`   |

---

## Per-Device Summary

### Spine-01

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.101/24`      |
| Loopback0     | Loopback0          | `198.18.129.1/32`        |
| To Leaf-01    | Gi1/0/1            | `198.18.130.1/30`        |
| To Leaf-02    | Gi1/0/2            | `198.18.130.5/30`        |
| To Border-01  | Gi1/0/3            | `198.18.130.9/30`        |
| To Border-02  | Gi1/0/4            | `198.18.130.13/30`       |
| To core1      | Gi1/0/5            | `198.18.130.33/30`       |
| To core2      | Gi1/0/6            | `198.18.130.37/30`       |

### Spine-02

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.102/24`      |
| Loopback0     | Loopback0          | `198.18.129.2/32`        |
| To Leaf-01    | Gi1/0/1            | `198.18.130.17/30`       |
| To Leaf-02    | Gi1/0/2            | `198.18.130.21/30`       |
| To Border-01  | Gi1/0/3            | `198.18.130.25/30`       |
| To Border-02  | Gi1/0/4            | `198.18.130.29/30`       |
| To core1      | Gi1/0/5            | `198.18.130.41/30`       |
| To core2      | Gi1/0/6            | `198.18.130.45/30`       |

### Leaf-01

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.103/24`      |
| Loopback0     | Loopback0          | `198.18.129.3/32`        |
| To Spine-01   | Gi1/0/1            | `198.18.130.2/30`        |
| To Spine-02   | Gi1/0/2            | `198.18.130.18/30`       |

### Leaf-02

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.104/24`      |
| Loopback0     | Loopback0          | `198.18.129.4/32`        |
| To Spine-01   | Gi1/0/1            | `198.18.130.6/30`        |
| To Spine-02   | Gi1/0/2            | `198.18.130.22/30`       |

### Border-01

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.105/24`      |
| Loopback0     | Loopback0          | `198.18.129.5/32`        |
| To Spine-01   | Gi1/0/1            | `198.18.130.10/30`       |
| To Spine-02   | Gi1/0/2            | `198.18.130.26/30`       |

### Border-02

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.106/24`      |
| Loopback0     | Loopback0          | `198.18.129.6/32`        |
| To Spine-01   | Gi1/0/1            | `198.18.130.14/30`       |
| To Spine-02   | Gi1/0/2            | `198.18.130.30/30`       |

### dmz1

| Address Type  | Interface          | Address                  |
|---------------|--------------------|--------------------------|
| Management    | GigabitEthernet0/0 | `198.18.128.107/24`      |
| Loopback0     | Loopback0          | `198.18.129.200/32`      |
| To core1      | Gi1/0/1            | `198.18.130.66/30`       |
| To core2      | Gi1/0/2            | `198.18.130.70/30`       |
| To FW         | Gi1/0/3            | `198.18.130.73/30`       |

### core1 (NX-OS)

| Address Type     | Interface    | Address                  |
|------------------|--------------|---------------------------|
| Management       | mgmt0        | `198.18.128.108/24`       |
| Loopback0        | loopback0    | `198.18.129.8/32`         |
| Anycast RP       | loopback1    | `198.18.129.254/32`       |
| To Spine-01      | Eth1/1       | `198.18.130.34/30`        |
| To Spine-02      | Eth1/2       | `198.18.130.42/30`        |
| To dmz1          | Eth1/3       | `198.18.130.65/30`        |
| PIM (Spine-01)   | Eth1/1.2     | `198.18.130.49/30`        |
| PIM (Spine-02)   | Eth1/2.2     | `198.18.130.57/30`        |

### core2 (NX-OS)

| Address Type     | Interface    | Address                  |
|------------------|--------------|---------------------------|
| Management       | mgmt0        | `198.18.128.109/24`       |
| Loopback0        | loopback0    | `198.18.129.9/32`         |
| Anycast RP       | loopback1    | `198.18.129.254/32`       |
| To Spine-01      | Eth1/1       | `198.18.130.38/30`        |
| To Spine-02      | Eth1/2       | `198.18.130.46/30`        |
| To dmz1          | Eth1/3       | `198.18.130.69/30`        |
| PIM (Spine-01)   | Eth1/1.2     | `198.18.130.53/30`        |
| PIM (Spine-02)   | Eth1/2.2     | `198.18.130.61/30`        |

---

## Routing Protocol Reference

### BGP Autonomous Systems

| AS Number | Devices                              | Role                  |
|-----------|--------------------------------------|-----------------------|
| `65001`   | Spine-01, Spine-02, Leaf-01, Leaf-02, Border-01, Border-02 | Campus Fabric (IOS-XE) |
| `65002`   | core1, core2                         | Core / WAN (NX-OS)    |
| `65003`   | dmz1                                 | DMZ                   |

### BGP Peering Summary

| Session              | Local Device | Local IP (update-src)  | Peer IP                | Remote AS |
|----------------------|--------------|------------------------|------------------------|-----------|
| Spine-01 ↔ core1     | Spine-01     | `198.18.130.33`        | `198.18.130.34`        | 65002     |
| Spine-01 ↔ core2     | Spine-01     | `198.18.130.37`        | `198.18.130.38`        | 65002     |
| Spine-02 ↔ core1     | Spine-02     | `198.18.130.41`        | `198.18.130.42`        | 65002     |
| Spine-02 ↔ core2     | Spine-02     | `198.18.130.45`        | `198.18.130.46`        | 65002     |
| core1 ↔ dmz1         | core1        | `loopback0`            | `198.18.129.200`       | 65003     |
| core2 ↔ dmz1         | core2        | `loopback0`            | `198.18.129.200`       | 65003     |
| dmz1 ↔ core1         | dmz1         | `Loopback0`            | `198.18.129.8`         | 65002     |
| dmz1 ↔ core2         | dmz1         | `Loopback0`            | `198.18.129.9`         | 65002     |

### OSPF

| Area    | Devices                                     | Purpose                     |
|---------|---------------------------------------------|-----------------------------|
| `0.0.0.0` (Area 0) | Spine-01, Spine-02, Leaf-01, Leaf-02, Border-01, Border-02, core1, core2, dmz1 | Single-area backbone |

### PIM / Multicast

| Parameter            | Value                       |
|----------------------|-----------------------------|
| RP Address           | `198.18.129.254` (Anycast)  |
| Anycast RP Members   | `198.18.129.8` (core1), `198.18.129.9` (core2) |
| Multicast Group      | `224.0.0.0/4`               |
| SSM Range            | `232.0.0.0/8`               |

---

## Special Addresses

| Address               | Description                                    |
|-----------------------|------------------------------------------------|
| `198.18.128.1`        | Management network default gateway             |
| `198.18.129.254/32`   | PIM Anycast RP (shared loopback on core1/core2)|
| `198.18.129.0/24`     | BGP network statement + `Null0` summary (spines)|
| `198.18.129.200/32`   | dmz1 Loopback0 — BGP update-source for AS65003 sessions |
| `10.10.120.0/24`      | DHCP Server subnet (redistributed into OSPF via spine route-map) |

---

## Underlay Topology Diagram

All fabric point-to-point links use `/30` subnets from `198.18.130.0/24`, within the dCloud-allocated block.

```mermaid
graph TD
    subgraph CAMPUS_FABRIC["Campus Fabric (AS 65001)"]
        S1["Spine-01\n198.18.129.1"]
        S2["Spine-02\n198.18.129.2"]
        L1["Leaf-01\n198.18.129.3"]
        L2["Leaf-02\n198.18.129.4"]
        B1["Border-01\n198.18.129.5"]
        B2["Border-02\n198.18.129.6"]
    end

    subgraph CORE["Core / WAN (AS 65002)"]
        C1["core1\n198.18.129.8"]
        C2["core2\n198.18.129.9"]
    end

    subgraph DMZ_GROUP["DMZ (AS 65003)"]
        DMZ1["dmz1\n198.18.129.200"]
    end

    S1 -- "198.18.130.0/30\n.1 ↔ .2" --- L1
    S1 -- "198.18.130.4/30\n.5 ↔ .6" --- L2
    S1 -- "198.18.130.8/30\n.9 ↔ .10" --- B1
    S1 -- "198.18.130.12/30\n.13 ↔ .14" --- B2

    S2 -- "198.18.130.16/30\n.17 ↔ .18" --- L1
    S2 -- "198.18.130.20/30\n.21 ↔ .22" --- L2
    S2 -- "198.18.130.24/30\n.25 ↔ .26" --- B1
    S2 -- "198.18.130.28/30\n.29 ↔ .30" --- B2

    S1 -- "198.18.130.32/30\nphy .33 ↔ .34\npim .49 ↔ .50" --- C1
    S1 -- "198.18.130.36/30\nphy .37 ↔ .38\npim .53 ↔ .54" --- C2
    S2 -- "198.18.130.40/30\nphy .41 ↔ .42\npim .57 ↔ .58" --- C1
    S2 -- "198.18.130.44/30\nphy .45 ↔ .46\npim .61 ↔ .62" --- C2

    C1 -- "198.18.130.64/30\n.65 ↔ .66" --- DMZ1
    C2 -- "198.18.130.68/30\n.69 ↔ .70" --- DMZ1
    DMZ1 -- "198.18.130.72/30\n.73 ↔ .74" --- FW["FW"]
```

### P2P Subnet Allocation Table

| Subnet | Link | Local IP | Peer IP | Local Interface | Peer Interface |
|--------|------|----------|---------|-----------------|----------------|
| `198.18.130.0/30`  | Spine-01 ↔ Leaf-01   | `198.18.130.1`  | `198.18.130.2`  | Gi1/0/1 | Gi1/0/1 |
| `198.18.130.4/30`  | Spine-01 ↔ Leaf-02   | `198.18.130.5`  | `198.18.130.6`  | Gi1/0/2 | Gi1/0/1 |
| `198.18.130.8/30`  | Spine-01 ↔ Border-01 | `198.18.130.9`  | `198.18.130.10` | Gi1/0/3 | Gi1/0/1 |
| `198.18.130.12/30` | Spine-01 ↔ Border-02 | `198.18.130.13` | `198.18.130.14` | Gi1/0/4 | Gi1/0/1 |
| `198.18.130.16/30` | Spine-02 ↔ Leaf-01   | `198.18.130.17` | `198.18.130.18` | Gi1/0/1 | Gi1/0/2 |
| `198.18.130.20/30` | Spine-02 ↔ Leaf-02   | `198.18.130.21` | `198.18.130.22` | Gi1/0/2 | Gi1/0/2 |
| `198.18.130.24/30` | Spine-02 ↔ Border-01 | `198.18.130.25` | `198.18.130.26` | Gi1/0/3 | Gi1/0/2 |
| `198.18.130.28/30` | Spine-02 ↔ Border-02 | `198.18.130.29` | `198.18.130.30` | Gi1/0/4 | Gi1/0/2 |
| `198.18.130.32/30` | Spine-01 ↔ core1 (phy) | `198.18.130.33` | `198.18.130.34` | Gi1/0/5 | Eth1/1 |
| `198.18.130.36/30` | Spine-01 ↔ core2 (phy) | `198.18.130.37` | `198.18.130.38` | Gi1/0/6 | Eth1/1 |
| `198.18.130.40/30` | Spine-02 ↔ core1 (phy) | `198.18.130.41` | `198.18.130.42` | Gi1/0/5 | Eth1/2 |
| `198.18.130.44/30` | Spine-02 ↔ core2 (phy) | `198.18.130.45` | `198.18.130.46` | Gi1/0/6 | Eth1/2 |
| `198.18.130.48/30` | core1 ↔ Spine-01 (PIM) | `198.18.130.49` | `198.18.130.50` | Eth1/1.2 | — |
| `198.18.130.52/30` | core2 ↔ Spine-01 (PIM) | `198.18.130.53` | `198.18.130.54` | Eth1/1.2 | — |
| `198.18.130.56/30` | core1 ↔ Spine-02 (PIM) | `198.18.130.57` | `198.18.130.58` | Eth1/2.2 | — |
| `198.18.130.60/30` | core2 ↔ Spine-02 (PIM) | `198.18.130.61` | `198.18.130.62` | Eth1/2.2 | — |
| `198.18.130.64/30` | core1 ↔ dmz1 | `198.18.130.65` | `198.18.130.66` | Eth1/3 | Gi1/0/1 |
| `198.18.130.68/30` | core2 ↔ dmz1 | `198.18.130.69` | `198.18.130.70` | Eth1/3 | Gi1/0/2 |
| `198.18.130.72/30` | dmz1 ↔ FW    | `198.18.130.73` | `198.18.130.74` | Gi1/0/3 | Gi1 |

> Subnets `198.18.130.76/30` through `198.18.130.252/30` remain available for future expansion.

---

*Last updated: 2026-03-09*  
*Cisco Live 2026 — TECOPS-2599*

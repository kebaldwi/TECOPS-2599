# DCLOUD LAB Preparation

## Overview

Welcome to the Catalyst Center + ISE Lab for Automation & Orchestration in DCLOUD! This lab is designed to provide hands-on experience with Ansible and Cisco Workflows, a powerful tool for automating and orchestrating network operations through Catalyst Center.

In this lab, we will use a complete set of Cisco Workflows which use REST API requests to automate and orchestrate network devices through Catalyst Center. This lab will focus on Catalyst Center orchestrations to build intent and templates to drive configuration.

> [!IMPORTANT] 
> Please note that LAB content in this Repository is aligned with specific DCLOUD Demonstrations that have to be set up by either a **Cisco Employee** or a **Cisco Partner**. If you are having trouble accessing the DCLOUD content please get in touch with your **Local Cisco Account Team**.

## The DCLOUD Environment

Use this environment: [**Catalyst Center + ISE lab for Automation & Orchestration**](https://dcloud2.cisco.com/demo/catalyst-center-ise-lab-for-automation-orchestration)

The DCLOUD session includes the following equipment.

* Virtual Machines:
  * Catalyst Center 2.3.7.10 or better
  * Identity Services Engine (ISE) 3.4 Patch 3 or better (deployed)
  * Script Server - Ubuntu 20.04  or better
  * Windows 10 Jump Host 
  * Windows Server 2019 - Can be configured to provide identity, DHCP, DNS, etc.
  * vSphere 8.0 - For hosting Workflows Remote AO
  * ESXi Host - For hosting Workflows Remote AO

* Virtual Networking Devices:
  * Catalyst 8000v Router - 17.16.01a IOS-XE Code
  * Catalyst 9000v Switch - 17.15.03 IOS-XE Code 
  * Cisco Nexus 9000v Switch - 10.5.3 Code

The following diagram shows the DCLOUD topology.

![DCLOUD LAB TOPOLOGY](./images/common/DCLOUD_Topology_A.png?raw=true)

### Access and Credentials:

| Platform:       | IP Address:    | Username      | Password    | 
|-----------------|----------------|---------------|-------------|
| Catalyst Center | 198.18.129.100 | admin         | C1sco12345  |
| ISE             | 198.18.133.27  | admin         | C1sco12345  |
| Windows AD      | 198.18.133.1   | admin         | C1sco12345  |
| Script Server   | 198.18.133.28  | root          | C1sco12345  |
| vSphere Server  | 198.18.134.80  | Administrator | C1sco12345! |
| CML Server      | 198.18.128.11  | Guest         | C1sco12345  |

#### Large Branch Topology

The following diagram shows one of the CML pods topology.

![DCLOUD CML LARGE CAMPUS TOPOLOGY](./images/common/DCLOUD_Topology_B.png?raw=true)

| Platform:  | OOB Mgmt:      | Loopback 0: | Username  | Password   |
|------------|----------------|-------------|-----------|------------|
| Spine-01   | 198.18.128.101 | 198.19.1.1  | net-admin | C1sco12345 |
| Spine-02   | 198.18.128.102 | 198.19.1.2  | net-admin | C1sco12345 |
| Border-01  | 198.18.128.103 | 198.19.1.3  | netadmin  | C1sco12345 |
| Border-02  | 198.18.128.104 | 198.19.1.4  | netadmin  | C1sco12345 |
| Leaf-01    | 198.18.128.105 | 198.19.1.5  | netadmin  | C1sco12345 |
| Leaf-02    | 198.18.128.106 | 198.19.1.6  | netadmin  | C1sco12345 |

#### Small Branch Topology

The following diagram shows one of the CML pods topology.

![DCLOUD CML SMALL BRANCH TOPOLOGY](./images/common/DCLOUD_Topology_C.png?raw=true)

| Platform:       | IP Address:    | Username | Password   | 
|-----------------|----------------|----------|------------|
| Router          | 198.18.140.1   | netadmin | C1sco12345 |
| Switch 1        | 198.18.10.2    | netadmin | C1sco12345 |
| Switch 2        | 198.18.20.2    | netadmin | C1sco12345 |

### DCLOUD VPN Connection

Use AnyConnect VPN to connect to DCLOUD. When connecting, look at the session details and copy the credentials from the session booked into the client to connect.

![DCLOUD VPN CONNECTION](./images/common/VPN-to-DCLOUD.png?raw=true)

### Tools Required

Please utilize the following tools to run the lab effectively and ensure they are installed on your workstation/laptop before attempting the lab.

1. Cisco AnyConnect VPN Client
2. Google Chrome

<details closed>
<summary> Expand section for Tools Required </summary>

#### Cisco AnyConnect VPN Client

This software is required to connect your workstation to Cisco dCloud. For an explanation of AnyConnect and how to use it with dCloud, please visit the following URL: 

- <a href="https://dcloud-cms.cisco.com/help/android_anyconnect" target="_blank">dCloud AnyConnect Documentation</a>

If you do not have the AnyConnect client, please visit. 

- <a href="https://dcloud-rtp-anyconnect.cisco.com" target="_blank">⬇︎AnyConnect Download Site⬇︎</a>

#### Google Chrome

Google Chrome is the optimal browser of choice when working in the Catalyst Center UI. 

To download Google Chrome, please visit. 

- <a href="https://www.google.com/chrome/downloads/" target="_blank">⬇︎Chrome Download⬇︎</a>

</details>

## Summary

This lab is intended for educational purposes only. Use of any material outside of a lab environment should be done at the operator's risk. Cisco assumes no liability for incorrect usage.

This lab is intended to help drive the adoption of REST API and will be added to over time with various use cases. The Public Workspace will also mirror the changes and be kept up to date. We hope this set of labs helps explain how the REST API may be used and goes a little further in helping define and document them.

## Summary

At this point the lab should be operational. You may now proceed with the lab of your choice. 

If you have any issues please reach out and create a Support Ticket in DCLOUD and remember to include your session information from DCLOUD.

> [!IMPORTANT]
> **Feedback:** If you found this set of **labs** or **content** helpful, please fill in comments on this feedback form [give feedback](https://github.com/kebaldwi/DNAC-TEMPLATES/discussions/new?category=feedback-and-ideas).</br></br>
**Content Problems and Issues:** If you found an **issue** on the **lab** or **content** please fill in an [issue](https://github.com/kebaldwi/DNAC-TEMPLATES/issues/new) include what file, along with the issue you ran into. 

> [**Return to Lab Menu**](./README.md)
# Lab Config Backup

Ansible playbook that collects `show running-config` from all lab devices and saves each output as a flat `.cfg` file under `config-backups/`. Supports both **IOS-XE** and **NX-OS** device types.

---

## Directory Structure

```
Lab-Config-Backup/
├── ansible.cfg              # Ansible defaults (inventory, SSH settings)
├── backup_config.yml        # Main playbook
├── inventory.yml            # Device inventory with management IPs
├── vault.yml                # Encrypted device credentials (ansible-vault)
├── vault.yml.example        # Template for creating vault.yml
├── .vault_pass              # Vault password file (not committed to source control)
└── config-backups/          # Output directory — one .cfg per device
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.9+ |
| Ansible | 2.14+ |
| `cisco.ios` collection | Latest |
| `cisco.nxos` collection | Latest |

Install the required collections:

```bash
ansible-galaxy collection install cisco.ios cisco.nxos
```

---

## Credentials Setup

Device credentials are stored in an **ansible-vault** encrypted file and are never stored in plaintext.

**First-time setup:**

```bash
# 1. Copy the example template
cp vault.yml.example vault.yml

# 2. Edit vault.yml with the actual credentials
#    vault_device_username, vault_device_password, vault_device_enable_password

# 3. Create a vault password file
echo "your_vault_password" > .vault_pass
chmod 600 .vault_pass

# 4. Encrypt the vault file
ansible-vault encrypt vault.yml --vault-password-file .vault_pass
```

> `.vault_pass` should never be committed to source control. It is already listed in `.gitignore`.

To edit credentials after encryption:

```bash
ansible-vault edit vault.yml --vault-password-file .vault_pass
```

---

## Inventory

All devices are managed via their out-of-band management addresses on `198.18.128.0/24` (VRF `Mgmt-vrf` on IOS-XE, VRF `management` on NX-OS).

| Hostname | Platform | Management IP |
|----------|----------|---------------|
| Spine01 | IOS-XE | `198.18.128.101` |
| Spine02 | IOS-XE | `198.18.128.102` |
| Leaf01 | IOS-XE | `198.18.128.103` |
| Leaf02 | IOS-XE | `198.18.128.104` |
| Border01 | IOS-XE | `198.18.128.105` |
| Border02 | IOS-XE | `198.18.128.106` |
| dmz1 | IOS-XE | `198.18.128.107` |
| dhcp-server | IOS-XE | `198.18.128.110` |
| Core-01 | NX-OS | `198.18.128.108` |
| Core-02 | NX-OS | `198.18.128.109` |

---

## Running the Playbook

**Back up all devices:**

```bash
ansible-playbook backup_config.yml --vault-password-file .vault_pass
```

**Back up a specific group only:**

```bash
# IOS-XE devices only
ansible-playbook backup_config.yml --vault-password-file .vault_pass --limit iosxe

# NX-OS devices only
ansible-playbook backup_config.yml --vault-password-file .vault_pass --limit nxos
```

**Back up a single device:**

```bash
ansible-playbook backup_config.yml --vault-password-file .vault_pass --limit Spine01
```

**Dry run (check mode):**

```bash
ansible-playbook backup_config.yml --vault-password-file .vault_pass --check
```

---

## Output

Configurations are saved to `config-backups/` with the inventory hostname as the filename:

```
config-backups/
├── Spine01.cfg
├── Spine02.cfg
├── Leaf01.cfg
├── Leaf02.cfg
├── Border01.cfg
├── Border02.cfg
├── dmz1.cfg
├── dhcp-server.cfg
├── Core-01.cfg
└── Core-02.cfg
```

Each file contains the full `show running-config` output captured at the time the playbook was run.

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `Permission denied (publickey)` | Wrong credentials in vault | Re-edit vault.yml and verify username/password |
| `Connection timed out` | Device unreachable on mgmt network | Confirm device is up and reachable at `198.18.128.x` |
| `Decryption failed` | Wrong vault password | Verify `.vault_pass` content matches the password used during encryption |
| `Collection not found` | Missing Ansible collections | Run `ansible-galaxy collection install cisco.ios cisco.nxos` |
| Empty backup files | `show run` returned no output | Check SSH access manually: `ssh net-admin@198.18.128.101` |

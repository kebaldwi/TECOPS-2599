# 0.0 — Cisco Catalyst Center Script-Server Bootstrap

Prepares an Ubuntu 22.04 or 24.04 server to run the Ansible playbooks in this
repository. It uses an isolated virtual environment at `~/tecops-venv` and
installs the Python dependencies and Galaxy collections pinned at the Ansible
repository root.
The collection and SDK pins target Catalyst Center 3.1.6, using API profile
`3.1.6.0`.

This adapts the script-server bootstrap from the CiscoOne Experience Lab
project:

1. `stage-script-server.sh` installs the minimum Ubuntu packages, creates the
   virtual environment, installs the pinned Python dependencies, and runs
   `create-catc-vault.py`.
2. `playbooks/00_preflight.yml` verifies the host, checkout, virtual
   environment, and sudo access.
3. `playbooks/01_bootstrap_script_server.yml` installs the pinned collections
   and verifies Ansible.

During staging, enter and confirm an Ansible Vault password (skipped when
`ANSIBLE_VAULT_PASSWORD_FILE` is set or `~/.ansible/vault_pass` already exists),
then, if the shared vault does not exist yet, the lab Catalyst Center admin
password. The prompts use bracketed labels to
identify the credential; they do not contain or prefill password values. The
helper creates the encrypted shared
`Support/Resources/Ansible/campus-evpn/group_vars/all/vault.yml` containing
`catc_username: admin` and `catc_password`. It does not write the credentials
to the repository in plaintext. It stores the Vault password in
`~/.ansible/vault_pass`, outside the repository, with the directory set to mode
`0700` and the file to mode `0600`. Staging configures the script-server
virtual environment to export this password-file path when activated, so
playbooks do not require `--ask-vault-pass`. If the shared vault already exists,
staging validates it and stores the password file without replacing the vault.

The helper also creates the encrypted stage vaults
`campus-evpn/vaults/network_settings.yml` (ISE RADIUS shared secrets) and
`campus-evpn/vaults/device_credentials.yml` (device CLI/enable passwords and
SNMP communities) with the lab defaults, using the same Vault password. Existing
vaults are validated and never overwritten, so rerunning the helper is safe:

```bash
~/tecops-venv/bin/python 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/create-catc-vault.py \
  ~/tecops-venv/bin/ansible-vault
```

The bootstrap does not configure lab-specific DNS, prompt for a pod number,
install wireless components, or host IOS-XE images. Stage 6.0's local vault is
optional and only needed for a GitHub token.

## Run

Run on the Ubuntu script server as a regular user with sudo privileges:

```bash
cd Support/Resources/Ansible
./0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/stage-script-server.sh
~/tecops-venv/bin/ansible-playbook -i localhost, 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/playbooks/00_preflight.yml
~/tecops-venv/bin/ansible-playbook -i localhost, 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/playbooks/01_bootstrap_script_server.yml
```

Open a new shell after bootstrap, or activate the environment in the current
shell:

```bash
source ~/tecops-venv/bin/activate
```


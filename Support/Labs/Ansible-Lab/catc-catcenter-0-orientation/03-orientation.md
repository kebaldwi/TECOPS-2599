# Orientation — Stage Ansible and the Shared Vault

In this section we clone the lab repository, stage Ansible on the Script
Server, and create the shared encrypted Catalyst Center credential vault.

> [!IMPORTANT]
> All commands run inside the SSH session you opened in [the previous section](./02-preparation.md), using the regular DCLOUD account with sudo access.

## Step 1 — Clone the Repository

```bash
cd ~
git clone https://github.com/kebaldwi/TECOPS-2599.git
cd TECOPS-2599/Support/Resources/Ansible
ls
```

The Ansible root contains the shared configuration, requirements, roles, and
the bootstrap directory.

## Step 2 — Run the Bootstrap Script

The script installs the pinned Python dependencies in `~/tecops-venv` and
prompts for the Catalyst Center admin password and Vault password. It creates
the shared encrypted CatC vault in the campus pipeline.
Run it as your regular DCLOUD account, not as root.

```bash
./0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/stage-script-server.sh
~/tecops-venv/bin/ansible-playbook -i localhost, 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/playbooks/00_preflight.yml
~/tecops-venv/bin/ansible-playbook -i localhost, 0.0-Cisco-Catalyst-Center-Script-Server-Bootstrap/playbooks/01_bootstrap_script_server.yml
```

The playbooks verify the host and install the pinned Ansible collections.
Open a new shell after bootstrap so the `~/tecops-venv/bin` PATH update is
loaded.

## Step 3 — Activate the venv

After the script completes, activate the venv in your **current** shell:

```bash
source ~/tecops-venv/bin/activate
```

Alternatively, call the executables directly from `~/tecops-venv/bin`.

Verify the toolchain:

```bash
ansible --version
# Expect: ansible [core 2.17.14]

ansible-galaxy collection list
```

## Step 4 — Prepare Vault Credentials

The staging script prompts for the Catalyst Center admin password and an
Ansible Vault password, then creates the shared encrypted
`Support/Resources/Ansible/campus-evpn/group_vars/all/vault.yml`. The same Vault password is entered interactively with `--ask-vault-pass` when
you run playbooks that load encrypted variables. Use it for any additional
stage-specific vaults.

## Step 5 — Verify a Playbook Loads

Quick smoke test — without running it, ask Ansible to syntax-check the first playbook in the suite:

```bash
cd ~/TECOPS-2599/Support/Resources/Ansible
ansible-playbook --syntax-check campus-evpn/playbooks/01_site_hierarchy.yml --ask-vault-pass
# Expect: playbook: campus-evpn/playbooks/01_site_hierarchy.yml
```

If syntax check passes, the venv, collections, and inventory paths are all wired up correctly. The shared CatC vault was prepared during staging; only stages 2.0 and 3.0 need additional local vaults for network AAA and device credential secrets.

## Recap

What you have now on the Script Server:

* `~/TECOPS-2599/` — the lab repository checked out fresh from GitHub
* `~/tecops-venv/` — isolated venv with pinned dependencies and Ansible core 2.17.14
* `Support/Resources/Ansible/campus-evpn/group_vars/all/vault.yml` — shared encrypted Catalyst Center credentials
* `~/.profile` and `~/.bashrc` — add the venv's `bin` directory to `PATH`

> [**Next Section**](./04-labsetup.md)

> [**Return to LAB Menu**](../README.md)

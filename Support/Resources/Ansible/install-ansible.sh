#!/bin/bash
# =============================================================================
#  TECOPS-2599 — Ansible Environment Setup
#  Installs all prerequisites for playbooks 1.0 – 10.0
#
#  Tested on: Ubuntu 22.04 / 24.04
#  Run as a regular user with sudo privileges
#
#  All Python packages are installed inside an isolated virtual environment
#  at ~/tecops-venv to avoid conflicts with system Python packages.
# =============================================================================
set -e

VENV_DIR="$HOME/tecops-venv"

echo "============================================================"
echo "  TECOPS-2599 — Ansible Environment Setup"
echo "============================================================"

# ── 0. Preflight: restore system python3 for apt compatibility ────────────────
# On Ubuntu 20.04 (focal), apt_pkg and add-apt-repository are compiled for
# python3.8. If a previous script run used update-alternatives to point
# /usr/bin/python3 at python3.9, every subsequent apt command breaks with
# "No module named 'apt_pkg'". Restore it here before touching apt.
echo ""
echo "[ 0/8 ] Preflight: ensuring system python3 points to python3.8..."
if [ -f /usr/bin/python3.8 ]; then
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 10 2>/dev/null || true
    sudo update-alternatives --set python3 /usr/bin/python3.8 2>/dev/null || true
    echo "  /usr/bin/python3 → $(python3 --version 2>&1) (apt compatibility restored)"
else
    echo "  python3.8 not found — skipping (not Ubuntu 20.04 focal)"
fi

# ── 1. System update ──────────────────────────────────────────────────────────
echo ""
echo "[ 1/9 ] Updating apt package lists..."
# || true prevents set -e from aborting on pre-existing GPG/repo warnings
# (e.g. expired Grafana/Jenkins keys common on shared lab jumpboxes)
sudo apt-get update || true

# ── 2. Python 3.9 ─────────────────────────────────────────────────────────────
echo ""
echo "[ 2/9 ] Installing Python 3.9..."
# deadsnakes PPA guarantees Python 3.9 is available on all Ubuntu LTS versions
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update || true
sudo apt-get install -y python3.9 python3.9-venv python3.9-distutils curl

# Verify the python3.9 binary is available — do NOT change the system default
# (update-alternatives would break apt_pkg which is compiled for system Python)
python3.9 --version

# ── 3. Virtual environment ────────────────────────────────────────────────────
echo ""
echo "[ 3/9 ] Creating virtual environment at $VENV_DIR..."
# Use python3.9 explicitly — system python3 may still point to 3.8 on focal
python3.9 -m venv "$VENV_DIR"

# Activate the venv for the remainder of this script
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "  Virtual environment active: $(which python3) ($(python3 --version))"

# Upgrade pip inside the venv
python3 -m pip install --upgrade pip

# Persist venv activation for all future shell sessions
ACTIVATE_LINE="source \"$VENV_DIR/bin/activate\""
if ! grep -qF "$ACTIVATE_LINE" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# TECOPS-2599 — activate Ansible virtual environment" >> ~/.bashrc
    echo "$ACTIVATE_LINE" >> ~/.bashrc
    echo "  Added venv activation to ~/.bashrc"
else
    echo "  ~/.bashrc already contains venv activation — skipping"
fi

# ── 4. Ansible ────────────────────────────────────────────────────────────────
echo ""
echo "[ 4/9 ] Installing Ansible into venv..."
# ansible 8.x ships ansible-core 2.15 — minimum version required by all
# playbooks in this lab series (cisco.catalystcenter and cisco.dnac both need
# ansible-core >= 2.15 for their workflow manager modules)
pip install 'ansible>=8.0.0,<9.0.0'
ansible --version

# ── 5. Python SDK dependencies ────────────────────────────────────────────────
echo ""
echo "[ 5/9 ] Installing Python SDK dependencies into venv..."

# catalystcentersdk — required by cisco.catalystcenter collection
#   Used by: playbooks 1.0 (Site Hierarchy) and 2.0 (Settings)
pip install 'catalystcentersdk>=2.3.7.9,<3.0.0'

# dnacentersdk — required by cisco.dnac collection
#   Used by: playbooks 3.0 (Credentials) through 9.0 (Provision Composite)
pip install 'dnacentersdk>=2.11.0'

# github-clone — used by playbook 6.0 (Templates GitHub integration)
pip install github-clone

# ── 6. Ansible Galaxy collections ─────────────────────────────────────────────
echo ""
echo "[ 6/9 ] Installing Ansible Galaxy collections..."
# Collections are installed to ~/.ansible/collections (user scope) so they
# persist independently of the venv and are available to all playbooks.

# cisco.catalystcenter — new collection namespace
#   Used by: playbooks 1.0 (Site Hierarchy), 2.0 (Settings)
ansible-galaxy collection install 'cisco.catalystcenter:==2.1.3' --force

# cisco.dnac — legacy collection namespace
#   Used by: playbooks 3.0 (Credentials) through 9.0 (Provision Composite)
ansible-galaxy collection install 'cisco.dnac:==6.46.0' --force

# ansible.utils — utility filters/plugins required by both cisco collections
#   Used by: playbooks 1.0, 2.0, 3.0
ansible-galaxy collection install 'ansible.utils:>=2.11.0' --force

# community.general — general-purpose modules (git_config, uri extras, etc.)
#   Used by: playbook 6.0 (Templates GitHub integration)
ansible-galaxy collection install community.general --force

# cisco.ios — SSH-based IOS device management
#   Used by: playbook 10.0 (Backup My Configs)
ansible-galaxy collection install 'cisco.ios:>=4.0.0' --force

# cisco.nxos — SSH-based NX-OS device management
#   Used by: playbook 10.0 (Backup My Configs)
ansible-galaxy collection install 'cisco.nxos:>=5.0.0' --force

# ── 7. Vault password file ────────────────────────────────────────────────────
echo ""
echo "[ 7/9 ] Checking vault password file..."
if [ ! -f "$HOME/.vault_pass" ]; then
    echo "  WARNING: ~/.vault_pass not found."
    echo "  Create it before running any playbook:"
    echo "    echo 'YourVaultPassword' > ~/.vault_pass && chmod 600 ~/.vault_pass"
else
    chmod 600 "$HOME/.vault_pass"
    echo "  ~/.vault_pass exists — permissions set to 600."
fi

# ── 8. Verify ─────────────────────────────────────────────────────────────────
echo ""
echo "[ 8/9 ] Verifying installation..."

echo ""
echo "--- Virtual environment ---"
echo "  Path:   $VIRTUAL_ENV"
echo "  Python: $(python3 --version)"

echo ""
echo "--- Ansible version ---"
ansible --version

echo ""
echo "--- Installed Python packages ---"
pip show catalystcentersdk dnacentersdk ansible | grep -E '^(Name|Version)'

echo ""
echo "--- Installed Ansible collections ---"
ansible-galaxy collection list | grep -E 'cisco\.|ansible\.utils|community\.general'

echo ""
echo "============================================================"
echo "  Setup complete!"
echo ""
echo "  The virtual environment is at: $VENV_DIR"
echo "  It will activate automatically in new shell sessions via ~/.bashrc."
echo "  To activate it now in your current shell, run:"
echo "    source \"$VENV_DIR/bin/activate\""
echo ""
echo "  Next steps:"
echo "  1. Activate the venv in your current shell (see above)"
echo "  2. Create the vault password file (if not done already):"
echo "     echo 'YourVaultPassword' > ~/.vault_pass && chmod 600 ~/.vault_pass"
echo "  3. Update vault.yml in the root of each playbook directory"
echo "     with your Catalyst Center credentials, then encrypt it:"
echo "     ansible-vault encrypt vault.yml --vault-password-file ~/.vault_pass"
echo "============================================================"

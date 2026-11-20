#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_ROOT="$(dirname "${BOOTSTRAP_DIR}")"
VENV="${TECOPS_ANSIBLE_VENV:-${HOME}/tecops-venv}"
PYTHON="${PYTHON:-python3}"

die() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[[ "$(uname -s)" == "Linux" ]] || die "Run this script on the Ubuntu script server, not on your workstation."
[[ "${EUID}" -ne 0 ]] || die "Run as a regular user with sudo privileges."
[[ -f /etc/os-release ]] || die "Cannot identify the operating system."

# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || die "Ubuntu is required (detected: ${PRETTY_NAME:-unknown})."
[[ "${VERSION_ID:-}" == "22.04" || "${VERSION_ID:-}" == "24.04" ]] \
  || die "Supported Ubuntu releases are 22.04 and 24.04 (detected: ${VERSION_ID:-unknown})."

REQUIREMENTS="${ANSIBLE_ROOT}/requirements.txt"
[[ -f "${REQUIREMENTS}" ]] || die "Missing requirements file: ${REQUIREMENTS}"

printf 'Staging Ansible on %s (%s)\n' "$(hostname)" "${PRETTY_NAME}"
sudo -p 'dcloud sudo password [DCLOUD account password]: ' -v
sudo env DEBIAN_FRONTEND=noninteractive apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  git python3 python3-pip python3-venv

"${PYTHON}" -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -r "${REQUIREMENTS}"
"${VENV}/bin/python" "${BOOTSTRAP_DIR}/create-catc-vault.py" \
  "${VENV}/bin/ansible-vault"

printf '\nAnsible environment staged at %s\n' "${VENV}"
"${VENV}/bin/ansible-playbook" --version
printf '\nFrom %s, run:\n' "${ANSIBLE_ROOT}"
printf '  cd "%s"\n' "${ANSIBLE_ROOT}"
printf '  %s/ansible-playbook -i localhost, "%s/playbooks/00_preflight.yml"\n' "${VENV}" "${BOOTSTRAP_DIR}"
printf '  %s/ansible-playbook -i localhost, "%s/playbooks/01_bootstrap_script_server.yml"\n' "${VENV}" "${BOOTSTRAP_DIR}"
printf 'Open a new shell after bootstrap so the updated PATH is loaded.\n'

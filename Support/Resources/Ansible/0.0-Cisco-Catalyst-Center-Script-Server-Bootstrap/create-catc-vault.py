#!/usr/bin/env python3
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def vault_env() -> dict[str, str]:
    # Avoid a second default vault ID when the activated virtualenv exports one.
    env = os.environ.copy()
    env.pop("ANSIBLE_VAULT_PASSWORD_FILE", None)
    return env


def read_password_file(password_file: Path) -> str:
    if os.access(password_file, os.X_OK):
        result = subprocess.run(
            [str(password_file)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if result.returncode != 0:
            raise SystemExit("The configured Vault password program failed.")
        password = result.stdout.rstrip("\r\n")
    else:
        try:
            password = password_file.read_text(encoding="utf-8").rstrip("\r\n")
        except OSError as error:
            raise SystemExit(f"Cannot read Vault password file: {password_file}") from error

    if not password or "\n" in password:
        raise SystemExit("The Vault password file must contain one non-empty line.")
    return password


def prompt_vault_password() -> str:
    password = getpass.getpass("Ansible Vault password [lab Vault password]: ")
    if not password:
        raise SystemExit("The Ansible Vault password cannot be empty.")

    confirmation = getpass.getpass(
        "Confirm Ansible Vault password [same value as above]: "
    )
    if password != confirmation:
        raise SystemExit("Ansible Vault password entries do not match.")
    return password


def create_temp_password_file(password: str) -> Path:
    password_fd, password_name = tempfile.mkstemp(
        prefix="tecops-vault-password-",
        dir="/dev/shm",
        text=True,
    )
    password_file = Path(password_name)
    with os.fdopen(password_fd, "w", encoding="utf-8") as password_handle:
        password_handle.write(f"{password}\n")
    return password_file


def store_password_file(password_file: Path, password: str) -> None:
    password_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(password_file.parent, 0o700)

    password_fd, password_name = tempfile.mkstemp(
        prefix=".vault_pass-",
        dir=password_file.parent,
        text=True,
    )
    temporary_file = Path(password_name)
    try:
        os.fchmod(password_fd, 0o600)
        with os.fdopen(password_fd, "w", encoding="utf-8") as password_handle:
            password_handle.write(f"{password}\n")
        os.replace(temporary_file, password_file)
        os.chmod(password_file, 0o600)
    finally:
        temporary_file.unlink(missing_ok=True)


def configure_virtualenv(ansible_vault: Path) -> Path:
    activate_file = ansible_vault.resolve().parent / "activate"
    if not activate_file.is_file():
        raise SystemExit(
            "Run this helper with the script-server virtualenv's ansible-vault binary."
        )

    activation = activate_file.read_text(encoding="utf-8")
    if "ANSIBLE_VAULT_PASSWORD_FILE" not in activation:
        with activate_file.open("a", encoding="utf-8") as activation_handle:
            activation_handle.write(
                '\nif [ -z "${ANSIBLE_VAULT_PASSWORD_FILE:-}" ]; then\n'
                '  export ANSIBLE_VAULT_PASSWORD_FILE="${HOME}/.ansible/vault_pass"\n'
                "fi\n"
            )
    return activate_file


def vault_password_source(password_file: Path) -> Path | None:
    source = os.environ.get("ANSIBLE_VAULT_PASSWORD_FILE")
    if source:
        return Path(source).expanduser()
    if password_file.exists():
        return password_file
    return None


def vault_accepts_password(
    ansible_vault: Path, vault_file: Path, password_file: Path
) -> bool:
    result = subprocess.run(
        [
            str(ansible_vault),
            "view",
            "--vault-password-file",
            str(password_file),
            str(vault_file),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=vault_env(),
    )
    return result.returncode == 0


LAB_SECRET = "C1sco12345"

# Lab-wide stage secrets; the public dCloud lab uses one shared password.
STAGE_VAULTS = {
    "network_settings.yml": (
        f"catc_network_aaa_shared_secret: {json.dumps(LAB_SECRET)}\n"
        f"catc_client_and_endpoint_aaa_shared_secret: {json.dumps(LAB_SECRET)}\n"
    ),
    "device_credentials.yml": (
        "catc_device_credential_secrets:\n"
        "  cli_credential:\n"
        f"    password: {json.dumps(LAB_SECRET)}\n"
        f"    enable_password: {json.dumps(LAB_SECRET)}\n"
        "  snmp_v2c_read:\n"
        '    read_community: "RO"\n'
        "  snmp_v2c_write:\n"
        '    write_community: "RW"\n'
    ),
}


def encrypt_new_vault(
    ansible_vault: Path, target: Path, plaintext: str, password_file: Path
) -> bool:
    if target.exists():
        return False

    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    plaintext_file = None
    encrypted_dir = None
    encrypted_file = None
    try:
        plaintext_fd, plaintext_name = tempfile.mkstemp(
            prefix="tecops-vault-plain-", dir="/dev/shm", text=True
        )
        plaintext_file = Path(plaintext_name)
        with os.fdopen(plaintext_fd, "w", encoding="utf-8") as plaintext_handle:
            plaintext_handle.write(plaintext)

        encrypted_dir = Path(tempfile.mkdtemp(prefix=".vault-", dir=target.parent))
        encrypted_file = encrypted_dir / target.name
        subprocess.run(
            [
                str(ansible_vault),
                "encrypt",
                "--output",
                str(encrypted_file),
                "--vault-password-file",
                str(password_file),
                str(plaintext_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            env=vault_env(),
        )
        os.chmod(encrypted_file, 0o600)
        try:
            os.link(encrypted_file, target)
        except FileExistsError:
            return False
        return True
    finally:
        if plaintext_file is not None:
            plaintext_file.unlink(missing_ok=True)
        if encrypted_file is not None:
            encrypted_file.unlink(missing_ok=True)
        if encrypted_dir is not None:
            encrypted_dir.rmdir()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: create-catc-vault.py /path/to/ansible-vault")

    bootstrap_dir = Path(__file__).resolve().parent
    campus_root = bootstrap_dir.parent / "campus-evpn"
    shared_vault = campus_root / "group_vars" / "all" / "vault.yml"
    stage_vault_dir = campus_root / "vaults"
    ansible_vault = Path(sys.argv[1])
    persistent_password_file = Path.home() / ".ansible" / "vault_pass"

    password_source = vault_password_source(persistent_password_file)
    if password_source is None:
        vault_password = prompt_vault_password()
    else:
        vault_password = read_password_file(password_source)

    catc_password = None
    if not shared_vault.exists():
        catc_password = getpass.getpass(
            "Catalyst Center admin password [lab Catalyst Center password]: "
        )
        if not catc_password:
            raise SystemExit("The Catalyst Center password cannot be empty.")
        confirmation = getpass.getpass(
            "Confirm Catalyst Center admin password [same value as above]: "
        )
        if catc_password != confirmation:
            raise SystemExit("Catalyst Center password entries do not match.")

    temporary_password_file = create_temp_password_file(vault_password)
    try:
        if catc_password is not None:
            shared_vault.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.chmod(shared_vault.parent, 0o700)
            created = encrypt_new_vault(
                ansible_vault,
                shared_vault,
                'catc_username: "admin"\n'
                f"catc_password: {json.dumps(catc_password)}\n",
                temporary_password_file,
            )
            if created:
                print(f"Created shared encrypted credentials at {shared_vault}")

        if not vault_accepts_password(
            ansible_vault, shared_vault, temporary_password_file
        ):
            raise SystemExit(
                "The supplied Vault password does not unlock the existing shared vault."
            )

        for name, plaintext in STAGE_VAULTS.items():
            target = stage_vault_dir / name
            if encrypt_new_vault(
                ansible_vault, target, plaintext, temporary_password_file
            ):
                print(f"Created encrypted stage vault at {target}")
            elif not vault_accepts_password(
                ansible_vault, target, temporary_password_file
            ):
                raise SystemExit(
                    f"The Vault password does not unlock existing stage vault {target}."
                )

        store_password_file(persistent_password_file, vault_password)
        activate_file = configure_virtualenv(ansible_vault)
    finally:
        temporary_password_file.unlink(missing_ok=True)

    print(f"Ansible Vault password is available at {persistent_password_file}.")
    print(f"Virtualenv activation configured: {activate_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

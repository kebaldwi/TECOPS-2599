#!/usr/bin/env python3
# =============================================================================
# Script:   cml_normalize.py
# Author:   Igor Manassypov, imanassy@cisco.com
# Date:     2026-03-05
# Version:  1.0
#
# Description:
#   Normalize a Cisco CML topology file for compatibility with earlier
#   versions of CML (< 2.9.1).
#
# Usage:
#   python cml_normalize.py <topo.yml>
#
# Copyright (c) 2026 Cisco and/or its affiliates.
# All rights reserved.
# =============================================================================
"""
cml_normalize.py - Normalize a Cisco CML topology file for compatibility
with earlier versions of CML (< 2.9.1).

Usage:
    python cml_normalize.py <topo.yml>

Changes applied:
    - Lab version: 0.3.0 -> 0.0.1
    - mac_address: null  -> removed
    - smart_annotations: [] -> removed
"""

import sys
import os
import re


def normalize(input_path: str) -> None:
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r") as f:
        content = f.read()

    original = content

    # 1. Lab version: 0.3.0 -> 0.0.1
    content = re.sub(
        r"(^\s*version:\s*)0\.3\.0",
        r"\g<1>0.0.1",
        content,
        flags=re.MULTILINE,
    )

    # 2. mac_address: null -> remove the line entirely
    content = re.sub(
        r"^\s*mac_address:\s*null\s*\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    # 3. smart_annotations block -> remove key and all child list items
    # Handles both inline empty form (smart_annotations: []) and block list form:
    #   smart_annotations:
    #     - tag: ...
    content = re.sub(
        r"^smart_annotations:[ \t]*(?:\[\s*\])?\n(?:[ \t]+.*\n)*",
        "",
        content,
        flags=re.MULTILINE,
    )

    if content == original:
        print("[INFO] No changes were necessary. File is already normalized.")
        return

    # Write output to a new file: <basename>_normalized.<ext>
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_normalized{ext}"

    with open(output_path, "w") as f:
        f.write(content)

    print(f"[OK] Normalized topology written to: {output_path}")


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    normalize(sys.argv[1])


if __name__ == "__main__":
    main()

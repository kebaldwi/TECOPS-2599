#!/usr/bin/env python3
# ============================================================================
# Authors
# ============================================================================
# | Name            | Role                              | Contact              |
# |-----------------|-----------------------------------|----------------------|
# | Igor Manassypov | Systems Engineer                  | imanassy@cisco.com   |
# Copyright © 2024-2026 Cisco Systems, Inc. All rights reserved.
# ============================================================================
"""Fetch all .j2 and .yml files from the BGP EVPN GitHub folder and write to local DayNTemplates."""
import json
import urllib.request
import os
import sys

REPO = "imanassypov/CatalystCenter-BGP-EVPN-VXLAN"
BRANCH = "main"
SUBFOLDER = "BGP EVPN"
LOCAL_DIR = "/Users/imanassy/Documents/Cisco Live 2026/TECOPS-2599/TECOPS-2599/Projects/BGP_EVPN/DayNTemplates"

api_url = f"https://api.github.com/repos/{REPO}/contents/{SUBFOLDER.replace(' ', '%20')}?ref={BRANCH}"

with urllib.request.urlopen(api_url) as r:
    entries = json.load(r)

files = [e for e in entries if e["type"] == "file"]
updated, created, skipped = [], [], []

for entry in files:
    name = entry["name"]
    download_url = entry["download_url"]
    local_path = os.path.join(LOCAL_DIR, name)

    with urllib.request.urlopen(download_url) as r:
        content = r.read()

    existed = os.path.exists(local_path)
    with open(local_path, "wb") as f:
        f.write(content)

    if existed:
        updated.append(name)
    else:
        created.append(name)

print(f"\nUpdated ({len(updated)}):")
for n in sorted(updated):
    print(f"  ~ {n}")

print(f"\nCreated ({len(created)}):")
for n in sorted(created):
    print(f"  + {n}")

print(f"\nDone. {len(updated)} updated, {len(created)} created.")

# DEMO 1 — Build Site Hierarchy with Ansible 1.0
### Recording guide · Read on second monitor · Drive recording on primary

> **Target length:** 3:15 – 4:00 (full) · 2:30 – 3:00 (conference cut)
> **Editing labels:** Source Data · Before State · Execute Playbook · Parent-First Creation · Result in CatC · Idempotency Proof

---

## SHOT 1 — Title Card
**⏱ 0:00 – 0:08**

▶ **DO:** Show title card or opening frame with text:
> "Demo 1: Build Site Hierarchy with Ansible 1.0"

🎙 **SAY:**
> "In this demo, I'm building the Catalyst Center site hierarchy directly from structured data."

---

## SHOT 2 — Source Data (settings.json)
**⏱ 0:08 – 0:20**

▶ **DO:** Open `settings.json` in the editor. Scroll to the hierarchy fields and pause. Keep only these fields visible — scroll away from or blur credentials below.

✓ **ON SCREEN — hierarchy fields:**
```
HierarchyParent: Global/PODS
HierarchyArea:   POD 0
HierarchyBldg:   Building P0
HierarchyFloor:  Floor 1
```

🎙 **SAY:**
> "This single project entry defines the full hierarchy path I want to create. One source of truth — no manual clicks in the UI."

---

## SHOT 3 — Expected Output Path
**⏱ 0:20 – 0:30**

▶ **DO:** Stay on `settings.json`. Pause or slowly scroll. The audience should mentally map the fields to the path below.

✓ **ON SCREEN — path the playbook will build:**
```
Global/PODS
Global/PODS/POD 0
Global/PODS/POD 0/Building P0
Global/PODS/POD 0/Building P0/Floor 1
```

🎙 **SAY:**
> "From that one definition, the playbook will expand and build the full parent-to-child path — area, building, and floor — in a single run."

---

## SHOT 4 — Before State in Catalyst Center
**⏱ 0:30 – 0:42**

▶ **DO:** Switch to the Catalyst Center browser tab. Navigate to Design → Network Hierarchy. Show that POD 0, Building P0, and Floor 1 do not exist. Hold still for several seconds.

✓ **CHECK:** Audience can see the hierarchy is incomplete / missing.

🎙 **SAY:**
> "Here is the before-state in Catalyst Center. The path does not exist yet. Everything you are about to see is created by the playbook."

---

## SHOT 5 — Playbook Glance (site_hierarchy.yml)
**⏱ 0:42 – 0:52**

▶ **DO:** Switch to editor. Open `site_hierarchy.yml`. Slowly scroll from top — show it reads `settings.json` and builds hierarchy paths. This is a brief credibility shot, not a code walkthrough. 5–8 seconds is enough.

🎙 **SAY:**
> "The playbook reads the hierarchy definition, expands every intermediate path, and prepares ordered API payloads — one per site object."

---

## SHOT 6 — Run the Playbook
**⏱ 0:52 – 1:00**

▶ **DO:** Switch to the terminal. Navigate to the 1.0 directory and run:

```bash
cd "Support/Resources/Ansible/1.0-Cisco-Catalyst-Center-Site-Hierarchy" && ansible-playbook -i inventory.yml site_hierarchy.yml --vault-password-file .vault_pass
```

▶ **DO:** Hit Enter. Let it start. Keep the terminal visible.

🎙 **SAY:**
> "Now I'll run the site hierarchy playbook."

---

## SHOT 7 — Input Load & Path Computation
**⏱ 1:00 – 1:18**

▶ **DO:** Let the terminal output scroll. Pause / slow down when these lines appear.

✓ **WATCH FOR these lines:**
```
settings data loaded
site paths to be provisioned
computed site payloads
```

🎙 **SAY:**
> "The playbook reads the JSON, computes the full hierarchy, and prepares the ordered site list. No hardcoded values — it derives everything from that one source file."

---

## SHOT 8 — Parent-First Creation Sequence
**⏱ 1:18 – 1:40**

▶ **DO:** Let output continue scrolling. Pause when you see the CREATE sequence.

✓ **WATCH FOR these lines in order:**
```
Area     CREATE  →  Global/PODS
Area     CREATE  →  Global/PODS/POD 0
Building CREATE  →  Global/PODS/POD 0/Building P0
Floor    CREATE  →  Global/PODS/POD 0/Building P0/Floor 1
```

🎙 **SAY:**
> "This is the critical behavior — parent objects are created first, then children. Each object has a valid parent context before the next one is submitted. You cannot do this reliably with a flat loop."

---

## SHOT 9 — UUID Lookup After Each Create
**⏱ 1:40 – 1:52**

▶ **DO:** Continue watching terminal output. Pause when UUID resolution lines appear.

✓ **WATCH FOR:**
```
query new site id
add path to site_id_map
```

🎙 **SAY:**
> "After each create, the playbook immediately queries CatC for the new object's UUID and stores it in its site map. That is how it can reference a freshly created parent when building the child — all in the same run."

---

## SHOT 10 — Result in Catalyst Center
**⏱ 1:52 – 2:10**

▶ **DO:** Switch to the Catalyst Center browser tab. Refresh the hierarchy page. Slowly expand the tree in this order — pause after each level:

```
PODS  →  expand
  POD 0  →  expand
    Building P0  →  expand
      Floor 1
```

▶ **DO:** Hold on the fully expanded tree for 3–4 seconds.

🎙 **SAY:**
> "Back in Catalyst Center — the full hierarchy now exists exactly as defined in the source file. Area, building, floor — all created in one playbook run."

---

## SHOT 11 — Run Again (Idempotency)
**⏱ 2:10 – 2:18**

▶ **DO:** Switch back to the terminal. Press the Up arrow to recall the same command and hit Enter.

🎙 **SAY:**
> "Now I'll run the exact same playbook again — without changing anything — to prove it is safe to re-run."

---

## SHOT 12 — Second Run Shows UPDATE Not CREATE
**⏱ 2:18 – 2:42**

▶ **DO:** Let terminal output scroll. Watch for UPDATE lines — NOT CREATE.

✓ **WATCH FOR:**
```
existing site map built
Area     UPDATE  →  Global/PODS
Area     UPDATE  →  Global/PODS/POD 0
Building UPDATE  →  Global/PODS/POD 0/Building P0
Floor    UPDATE  →  Global/PODS/POD 0/Building P0/Floor 1
```

🎙 **SAY:**
> "On the second run, the playbook detects what already exists and converges to the desired state — no duplicates, no errors. This is idempotency: you can run this as many times as you need."

---

## SHOT 13 — Final State in Catalyst Center
**⏱ 2:42 – 2:55**

▶ **DO:** Switch back to Catalyst Center. Show the hierarchy is still exactly the same — unchanged.

🎙 **SAY:**
> "The structure is identical. Nothing was duplicated, nothing was broken. That is exactly the behavior you need from automation you plan to run repeatedly."

---

## SHOT 14 — Closing Frame
**⏱ 2:55 – 3:05**

▶ **DO:** Show closing title card with the three takeaways:

```
✓  Data-driven hierarchy
✓  Parent-before-child ordering
✓  Safe to re-run
```

🎙 **SAY:**
> "This gives us a clean, repeatable site foundation for every later workflow in the automation chain."

---

## EDITING NOTES (post-production only — not needed during recording)

| Cut | What to trim |
|---|---|
| Long waits | Any pause with no output moving |
| Debug noise | Verbose task output that does not show CREATE/UPDATE/UUID lines |
| Credentials | Blur or crop any visible passwords in settings.json |
| Setup steps | cd commands, venv activation, anything before Shot 6 |

**Lower-third labels to add in Camtasia:**
- Shot 2–3: `Source Data`
- Shot 4: `Before State`
- Shot 6–9: `Execute Playbook`
- Shot 8: `Parent-First Creation`
- Shot 10: `Result in Catalyst Center`
- Shot 11–13: `Idempotency Proof`

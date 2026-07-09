---
name: testing-ushift-platform
description: Test the UShift Hospital Intelligence Platform end-to-end. Use when verifying hospital map, filters, outreach workflow, regional dashboard, or export changes.
---

# Testing the UShift Hospital Intelligence Platform

## Prerequisites

- Python 3 installed (for local HTTP server)
- Chrome browser available
- No authentication required — app is fully client-side with localStorage

## Local Server Setup

```bash
cd /home/ubuntu/repos/project/hospital-map
python3 -m http.server 8080 &
```

Verify with: `curl -s http://localhost:8080 | head -5`

Open `http://localhost:8080` in Chrome (include the `http://` scheme or the browser may search instead of navigate).

## Key Data Points

- **Total CMS hospitals:** 5,195
- **Default filtered count:** ~1,962 (with default filter settings)
- **Default filters:** Independent + 1-5 + 6-10 + 11-20 system size; Inpatient; 51-100 + 101-250 + 251-500 beds; Nonprofit + For-Profit
- **Test hospital:** DEKALB REGIONAL MEDICAL CENTER (CCN 010012, Fort Payne, AL, Southeast region)

## Core Test Flow (7 Tests)

### Test 1: Default Filters
Load the app. Verify overlay shows "Showing 1,962 of 5,195 CMS hospitals" and default filter checkboxes match spec.

### Test 2: Filter + Reset
Select Region = "Southeast". Count should drop. Click "Reset All". Count returns to 1,962.

### Test 3: Search
Type "Mayo" in search. Results should narrow to <50 Mayo-related hospitals.

### Test 4: Detail Panel & Outreach Workflow
Click a hospital in the list. Verify detail panel shows all CMS fields (name, CCN, address, county, phone, region, type, care type, ownership, beds, health system). Change Call Status, set software vendors, add a call note with contact/phone/text/software/next steps.

**CSS Bug Fix Verification:** When setting status to "Follow-Up Needed", verify the badge has a yellow/amber background. The CSS class `.status-follow-up-needed` must match (not `.status-follow-up`).

### Test 5: localStorage Persistence
Refresh the page (F5). Reopen the same hospital. All user data (status, software, notes) should persist.

### Test 6: Regional Dashboard
Click "Regions" tab. Verify 6 region cards: Northeast, Southeast, Midwest, Southwest, West, Mid-Atlantic. Each shows Total/Target/Researched/Called/Qualified/Remaining. Verify counts reflect any status changes from Test 4.

**Remaining Count Bug Fix:** The "Remaining" count should equal Target minus hospitals called *within the target set only* (not all called hospitals in the region).

### Test 7: Export
Click "Export". Verify modal with CSV/Excel/CRM formats. Check optional fields (Notes, Software Stack, Call History). Click Download. Verify file downloads with data.

## Data Regeneration

If `build_data.py` is modified, regenerate the data:

```bash
cd /home/ubuntu/repos/project/hospital-map
python3 build_data.py
```

This reads `Hospital_General_Information.csv` and `hospitals-3-geojson.geojson` to produce `hospitals_cms.json` (5,195 records).

**County/Phone Fallback Bug:** `csv.DictReader` always includes every header as a key with empty string for blanks, so `.get(key, fallback)` never triggers. The fix uses `(value.strip() or fallback)` instead.

## Deployed Site

The app might be deployed at `https://hospital-map-ejcdbibb.devinapps.com`. Redeploy via:

```bash
# Use Devin's deploy tool with command="frontend" and dir pointing to hospital-map/
```

## Tips

- Always use `http://localhost:8080` with scheme when typing in the address bar
- Maximize browser window before recording: `sudo apt-get install -y wmctrl 2>/dev/null; wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz`
- localStorage stores all user data — clear it to reset: `localStorage.clear()` in browser console
- The hospital list shows max 200 entries with a "use filters to narrow" message
- Status badge CSS classes are generated via `status.toLowerCase().replace(/\s+/g,'-')` — class names like `status-follow-up-needed` and `status-qualified-lead` must match CSS definitions exactly

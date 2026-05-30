---
name: testing-hospital-map
description: Test the UShift Hospital Intelligence Platform end-to-end. Use when verifying hospital map UI, data expansion, filter behavior, or outreach workflow changes.
---

# Testing the UShift Hospital Intelligence Platform

## Setup

1. Start the local server:
   ```bash
   cd /home/ubuntu/repos/project/hospital-map
   python3 -m http.server 8080 &
   ```
2. Open http://localhost:8080 in the browser
3. The app loads `hospitals_all.json` (~4.6 MB) on startup — wait for the map markers to render

## Key Test Areas

### Hospital Count Verification
- Header subtitle shows total count and CMS breakdown (e.g. "8,038 hospitals (5,195 CMS-verified)")
- The counter overlay on the map shows "Showing X of Y hospitals" where Y matches the header total

### CMS vs GeoJSON-Only Hospital Distinction
- **CMS hospitals** have a blue "CMS" badge in list items and a blue "CMS Verified" badge in the detail panel
- **GeoJSON-only hospitals** have NO badge in list items and an amber "GeoJSON Only" badge in the detail panel
- CMS hospitals show "CMS CCN: XXXXXX" row and "CMS Classification" header
- GeoJSON-only hospitals show "Data Source: GeoJSON (non-CMS)" and "Classification" header (no "CMS" prefix)
- Test hospital (non-CMS): search "DECATUR MORGAN" → geo_8263
- Test hospital (CMS): search "SOUTHEAST HEALTH" → CCN 010085

### Filter Behavior
- Default filters are UShift-tuned (not "show all") — they pre-select specific Health System Size, Care Type, Bed Count, and Ownership values
- "Reset All" button restores these defaults, NOT "show all"
- To show all hospitals, you must manually uncheck every active toggle button (they're styled labels, not HTML checkboxes — `document.querySelectorAll('.filter-group input[type="checkbox"]')` might not work; click each highlighted button via UI instead)
- When no toggles are active in a filter group, it means "show all" for that group
- Verify the counter matches after filter changes

### localStorage Persistence
- All outreach data (call status, notes, software stack) is keyed by `h.id`
- CMS hospitals use CCN as ID (e.g. "010085")
- GeoJSON-only hospitals use `geo_{OBJECTID}` as ID (e.g. "geo_8263")
- To test: change call status, add a note with all fields (contact, phone, text, software, next steps), reload page (Ctrl+R), re-search and verify data persists
- localStorage can be inspected via browser console: `JSON.parse(localStorage.getItem('hospitalUserData'))`

### Region Dashboard
- Click "Regions" tab to see 6 region cards (Northeast, Mid-Atlantic, Southeast, Midwest, Southwest, West)
- Each card shows hospital count, average prospect score, and remaining count
- After data expansion, region counts should be higher than CMS-only counts

### Export
- Click "Export" button to download CSV
- Verify file contains hospital data with all columns

## Common Issues

- Filter toggle buttons look like checkboxes but are styled `<label>` elements wrapping hidden `<input type="checkbox">`. The console-based approach to uncheck them might not trigger the UI's event handlers. Always use native click interactions via the UI.
- The detail panel scrolls independently. If testing elements in the detail panel, you may need to scroll down within the panel to see Software Stack, Research Source, and Call History sections.
- After searching, the search term persists. Clear it before testing filters to avoid false negatives on hospital count.

## Devin Secrets Needed

No secrets required — the app runs entirely client-side with static JSON data and localStorage.

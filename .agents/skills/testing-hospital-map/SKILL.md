---
name: testing-hospital-map
description: Test the U.S. Hospital Map webapp end-to-end. Use when verifying hospital map UI, filtering, or data display changes.
---

# Testing the Hospital Map Webapp

## Overview

The hospital map is a static single-page webapp at `hospital-map/index.html` that renders 8,340 U.S. hospitals on a Leaflet.js map with marker clustering, filtering, and popup details.

## Deployment

- Deploy using `deploy frontend` with `dir` pointing to `hospital-map/`
- The deployed URL will be something like `https://hospital-map-<hash>.devinapps.com`
- After code changes, you must redeploy to see updates on the live site

## Key Test Data Points

These counts come from the embedded data and can be used as exact assertions:

| Filter | Expected Count |
|--------|---------------|
| No filter (all) | 8,340 |
| State: TX | 876 |
| State: CA | 666 |
| Type: CHILDREN | 168 |
| Search: "Mayo" | ~24 |
| CA + PSYCHIATRIC | ~158 |

## Sentinel Values to Watch

The dataset uses sentinel values for missing data. These are common sources of bugs:

- **Beds:** `-999` means unavailable. Must filter with `h.beds && h.beds > 0` (not just `if (h.beds)` since -999 is truthy)
- **Website:** `"NOT AVAILABLE"` means no website. Must filter with `h.website && h.website !== 'NOT AVAILABLE'` (the string is truthy)
- **Rating:** `"Not Available"` (different casing from website). Filter with `h.rating !== 'Not Available'`
- **Trauma:** `"NOT AVAILABLE"` for missing trauma level

## Testing Procedure

1. **Load test:** Navigate to the deployed URL. Verify header shows "8,340 hospitals" and counter shows "Showing 8,340 of 8,340"
2. **State filter:** Select a state (e.g., TX). Verify counter updates and markers concentrate in the correct geographic region
3. **Type filter:** Select a hospital type (e.g., CHILDREN). Verify counter and marker colors match the legend
4. **Search:** Type a hospital name (e.g., "Mayo"). Verify count drops and markers appear in expected locations
5. **Popup verification:** Click an individual marker. Verify popup shows name, address, phone, type, ownership, beds, and other fields. Check that sentinel values are NOT displayed
6. **Reset:** Click "Reset Filters". Verify all inputs clear and count returns to 8,340
7. **Combined filters:** Apply multiple filters simultaneously. Verify count is less than either individual filter

## Tips

- Use browser console to set filter values programmatically when native select dropdowns are hard to interact with:
  ```js
  document.getElementById('stateFilter').value = 'TX';
  document.getElementById('stateFilter').dispatchEvent(new Event('change'));
  ```
- The map stays zoomed to the last position after filtering — this is expected behavior. Markers outside the viewport are still counted.
- To verify sentinel value fixes, find a hospital known to have missing data (e.g., MAYO CLINIC HEALTH SYS MANKATO has website = "NOT AVAILABLE")
- Marker clustering means you might need to click on cluster numbers to zoom in before individual markers become clickable

## Devin Secrets Needed

No secrets required — the app is a static frontend with no authentication.

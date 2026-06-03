---
name: testing-hospital-app
description: Test the Hospital Intelligence web app end-to-end. Use when verifying Google Sheets integration, software matrix fields, export, or data persistence.
---

# Testing Hospital Intelligence App

## Quick Start

1. Start local server:
   ```bash
   cd hospital-map && python3 -m http.server 8080
   ```
2. Open http://localhost:8080 in Chrome
3. Search for a hospital (e.g. "MERCY HOSPITAL") and click one from the list or map

## Google Sheets Payload Testing

The app sends data to a configurable Google Sheets URL. For testing, use `https://httpbin.org/post` as the endpoint (set via the Google Sheets Configuration dropdown in the left sidebar).

To capture the exact payload without it actually being sent:

```javascript
// Install fetch interceptor in browser console
const _fetch = window.fetch;
window._capturedPayload = null;
window.fetch = function(url, opts) {
  if (opts && opts.method === 'POST') window._capturedPayload = JSON.parse(opts.body);
  return _fetch.apply(this, arguments);
};
```

After clicking "Save & Send to Google Sheets", inspect `window._capturedPayload` in console to verify all keys and values.

## Key Test Areas

### Software Matrix (current: 5 roles × functions = 29 fields)
- Verify role headers render: ED Phys, ED Nurses, IP Nurses, Hospitalist, Anesthesia
- IP Nurses has fewer functions than others (no Call Scheduling) — verify this
- Each field is a text input with placeholder "Software..."
- Payload keys use pipe separator format: `"Role │ Function"` (e.g. `"ED Phys │ Scheduling"`)

### Payload Structure
- Total column count should match spec (currently 41: 12 base + 29 matrix)
- Key order matters — verify with `Object.keys(window._capturedPayload)`
- Base fields: Hospital Name, State, City / Location, Address, Beds, Health System, Ownership, Care Type, Outreach Status, Phone, Date, Notes

### Export Feature
- Click "Export" button in left sidebar
- Modal should show "Include Software Matrix" checkbox
- Download CSV and verify it's non-empty, no console errors

### Data Persistence (localStorage)
- Fill some fields, close the detail panel (× button)
- Reopen the same hospital — fields should still be populated
- Data is stored per hospital using localStorage

### Status Button Regression
- Status buttons (Called, Call Later, Not Responding) should NOT trigger Google Sheets submission
- Only "Save & Send to Google Sheets" should send data
- Test by installing fetch counter and verifying count stays 0 after status click:
  ```javascript
  window._fetchCount = 0;
  const _origFetch = window.fetch;
  window.fetch = function(url, opts) {
    if (opts && opts.method === 'POST') { window._fetchCount++; console.log('FETCH: ' + window._fetchCount); }
    return _origFetch.apply(this, arguments);
  };
  ```

## Common Pitfalls

- **Browser cache**: If testing after code changes, hard-refresh (Ctrl+Shift+R) to avoid stale JS
- **Map markers**: Multiple hospitals may overlap on the map. Use the Hospitals list tab to click a specific hospital by name instead of clicking map markers
- **CDP evaluation**: Setting field values via `document.getElementById().value = '...'` might fail via CDP. Use UI click+type interactions instead for reliability
- **Scrolling**: The detail panel is long with all matrix fields. Scroll down to see all roles and the Save button

## Devin Secrets Needed

No secrets required for local testing. The Google Sheets URL can be set to httpbin.org/post for payload inspection.

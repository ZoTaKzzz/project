---
name: testing-hospital-app
description: Test the YouShift Hospital Intelligence app end-to-end. Use when verifying Google Sheets integration, hospital detail panel UI, or outreach tracking features.
---

# Testing YouShift Hospital Intelligence

## Local Setup

1. Serve the app locally:
   ```bash
   cd hospital-map && python3 -m http.server 8080
   ```
2. Open `http://localhost:8080` in Chrome.
3. Configure a fake Google Sheets URL for testing:
   - Click **Filters** tab in the sidebar
   - Expand **Google Sheets Configuration** at the bottom
   - Paste `https://httpbin.org/post` and click **Save URL**
   - This avoids sending real data while allowing payload inspection

## Intercepting Google Sheets Payloads

The app uses `mode: 'no-cors'` for fetch requests, so the Network tab won't show response bodies. Instead, install a fetch interceptor in the browser console before clicking Save:

```javascript
const originalFetch = window.fetch;
window._lastPayload = null;
window.fetch = function(...args) {
  if (args[1] && args[1].body) {
    try {
      window._lastPayload = JSON.parse(args[1].body);
      console.log('CAPTURED PAYLOAD:', JSON.stringify(window._lastPayload, null, 2));
    } catch(e) {}
  }
  return originalFetch.apply(this, args);
};
```

After clicking "Save & Send to Google Sheets", read the captured payload:
```javascript
console.log(JSON.stringify(window._lastPayload, null, 2));
```

## Key Testing Areas

### Software Categories (Checkboxes)
- 6 categories: HR, Payroll, Credentialing, EHR, Workforce Scheduling, No Software
- **Mutual exclusivity**: "No Software" deselects all others; selecting any other deselects "No Software"
- Visual state: checked items get blue background via `.checked` class

### Physician Software Fields
- 5 text fields: Hospital, Emergency Dept, Nurses, Hospitalist, Anesthetist
- These are often blank — test that empty fields send as `""` in payload

### Status Buttons vs Save Button
- Status buttons (Called, Call Later, Not Responding) should NOT send to Google Sheets
- Status buttons should NOT re-render the detail panel (which would wipe form data)
- Only "Save & Send to Google Sheets" should trigger the fetch POST

### History Section
- After saving, the History section at the bottom of the detail panel shows past submissions
- Each entry displays: timestamp, status badge (colored), category list (blue text), note text

## Common Issues

- **Browser cache**: After merging PRs, users may still see old behavior due to cached JS. Always hard-refresh (`Ctrl+Shift+R`) when testing after code changes.
- **Single-file app**: All code is in `hospital-map/index.html` — HTML, CSS, and JS are in one file.
- **localStorage persistence**: Hospital data persists in localStorage. To reset test state, run `localStorage.clear()` in the console and refresh.

## Expected Payload Structure

The Google Sheets payload should contain these fields (22 total):
- Hospital info: `hospitalName`, `stateCity`, `address`, `beds`, `healthSystem`, `ownership`, `careType`
- Status: `callStatus`
- Software categories (boolean columns): `softwareHR`, `softwarePayroll`, `softwareCredentialing`, `softwareEHR`, `softwareWorkforceScheduling`, `noSoftware` — values are `"Yes"` or `""`
- Physician fields: `physicianHospital`, `physicianEmergencyDept`, `physicianNurses`, `physicianHospitalist`, `physicianAnesthetist`
- Free text: `note`
- Auto-generated: `date` (ISO format `YYYY-MM-DD HH:MM:SS`)

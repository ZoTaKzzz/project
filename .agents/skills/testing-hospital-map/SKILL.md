---
name: testing-hospital-map
description: Test the YouShift Hospital Intelligence hospital map app end-to-end. Use when verifying Google Sheets integration, status buttons, or findings submission.
---

# Testing the Hospital Map App

## Setup

1. Serve the app locally:
   ```bash
   cd hospital-map
   python -m http.server 8080
   ```
2. Open `http://localhost:8080` in Chrome.
3. Configure a fake Google Sheets URL for testing:
   - Scroll down in the left sidebar to **Google Sheets Configuration**
   - Enter `https://httpbin.org/post` (or any endpoint that accepts POST)
   - Click **Save URL** — a green "Google Sheets URL saved!" toast confirms it

## Key Architecture Notes

- **Single-file app**: All HTML, CSS, and JS are in `hospital-map/index.html`
- **Data persistence**: Uses `localStorage` (key: `userData`) for hospital statuses, findings, and notes
- **Google Sheets integration**: `sendToGoogleSheets()` sends a `fetch` POST in `no-cors` mode to the configured URL
- **Toast notifications**: `showToast()` displays green (success) or red (error) toasts at bottom-right; toasts auto-dismiss after 3 seconds
- **Two code paths**:
  - `selectStatus()` — Called/Call Later/Not Responding buttons (should only update local state)
  - `submitFindings()` — "Save & Send to Google Sheets" button (should send data)

## Testing Google Sheets Integration

### Verifying status buttons do NOT send
1. Click a hospital marker on the map to open the detail panel
2. Click a status button (Called, Call Later, or Not Responding)
3. **Expected**: Button highlights, NO toast appears, no network request
4. **Bug indicator**: A green "Sent to Google Sheets!" toast appears — means `sendToGoogleSheets` is being called from `selectStatus()`

### Verifying Save button DOES send
1. With a hospital selected and a status active, type findings in the Software textarea
2. Click "Save & Send to Google Sheets"
3. **Expected**: Green "Sent to Google Sheets!" toast appears, note entry added to Findings history

### Counting fetch requests (duplicate detection)
To definitively prove no duplicate sends, instrument fetch in the browser console:
```javascript
window._sheetsSendCount = 0;
const origFetch = window.fetch;
window.fetch = function(...args) {
  if (args[0] && args[0].includes('httpbin')) {
    window._sheetsSendCount++;
    console.log('SHEETS SEND #' + window._sheetsSendCount);
  }
  return origFetch.apply(this, args);
};
```
Then perform the full flow (click status → type findings → click Save) and check `window._sheetsSendCount` — it should be exactly 1.

## Tips

- The fake URL `https://httpbin.org/post` will return a successful response, triggering the green toast. If you need to test error handling, use a URL that returns an error (e.g., `https://httpbin.org/status/500`).
- Hospital markers are clustered at low zoom levels. Zoom in or click a cluster to expand individual markers.
- localStorage can be cleared via DevTools > Application > Local Storage to reset all hospital data.
- The app description text under Google Sheets Configuration might still mention sending on status button click if it hasn't been updated — this is a UI text issue, not a functional one.

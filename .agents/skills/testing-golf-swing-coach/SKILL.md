---
name: testing-golf-swing-coach
description: Test the Golf Swing Coach SPA end-to-end. Use when verifying pose detection, video playback, frame capture, or AI feedback features.
---

# Testing the Golf Swing Coach App

## Local Dev Setup

```bash
cd golf-swing-coach
python3 -m http.server 8080
```

The app is a static SPA — no build step required. Open http://localhost:8080.

## Test Video Generation

The app requires two video files (user swing + pro swing). For automated testing without real golf videos, generate synthetic test videos:

```bash
# User swing (testsrc2 pattern, 3 seconds)
ffmpeg -f lavfi -i testsrc2=size=640x480:rate=30:duration=3 -c:v libx264 -pix_fmt yuv420p /tmp/swing_user.mp4

# Pro swing (SMPTE bars, 4 seconds)
ffmpeg -f lavfi -i smptebars=size=640x480:rate=30:duration=4 -c:v libx264 -pix_fmt yuv420p /tmp/swing_pro.mp4
```

**Important:** Copy videos into the served directory for the browser to fetch them:
```bash
cp /tmp/swing_user.mp4 /tmp/swing_pro.mp4 golf-swing-coach/
```

Clean up after testing (don't commit these):
```bash
rm -f golf-swing-coach/swing_user.mp4 golf-swing-coach/swing_pro.mp4
```

## Programmatic File Upload

The file inputs are hidden. Upload via browser console using DataTransfer API:

```javascript
async function uploadFile(inputId, filePath) {
  const response = await fetch(filePath);
  const blob = await response.blob();
  const file = new File([blob], filePath.split('/').pop(), { type: 'video/mp4' });
  const input = document.querySelector('#' + inputId);
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

// Upload both videos
await uploadFile('user-file-input', 'swing_user.mp4');
await uploadFile('pro-file-input', 'swing_pro.mp4');
```

## Key Test Assertions

### Upload Flow
- `#next-to-settings` button starts disabled
- Becomes enabled only after BOTH `S.userFile` and `S.proFile` are set

### Settings → Analysis
- `goTo(3)` triggers `setupAnalysis()` which loads videos
- Pro label (`#pro-label-name`) should show selected pro name
- Videos should reach `readyState >= 2` within a few seconds

### Seek While Paused (Bug Fix)
- `onSeek()` calls `runSingleFrame()` which passes `allowPaused=true`
- Verify: seek bar input event changes `userVid.currentTime` while `userVid.paused === true`
- Without the fix, `processVideoPose` returns early at the `vid.paused` guard

### Frame Capture
- Click `#capture-btn` → new `.keyframe-card` in `#keyframes-grid`
- Card contains `<img>` with `data:image/jpeg;base64` source
- Phase labels cycle: Address → Takeaway → Top → Impact → Finish

### AI Feedback Guard
- Click `#get-feedback-btn` without API key → alert with "API key" message
- Override `window.alert` to intercept and verify the message text

## Notes

- MediaPipe Pose Landmarker loads from CDN (~10s on first load, cached after)
- Synthetic videos have no human figure → MediaPipe finds 0 landmarks (expected)
- To test actual skeleton rendering, use real golf swing videos
- API key is runtime-only (password field in Settings step) — never committed
- The app uses ES module imports from CDN, so it needs HTTP (not file://)

## Devin Secrets Needed

- `ANTHROPIC_API_KEY` (optional) — only needed to test the AI coaching feedback feature end-to-end. The app works without it; the guard test verifies the missing-key alert path.

// ============================================================================
// SwingAI Coach – Main Application
// ============================================================================
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils
} from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/+esm';

// ---------------------------------------------------------------------------
// Landmark indices (MediaPipe Pose – 33 landmarks)
// ---------------------------------------------------------------------------
const LM = {
  NOSE: 0,
  LEFT_SHOULDER: 11, RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,    RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,    RIGHT_WRIST: 16,
  LEFT_PINKY: 17,    RIGHT_PINKY: 18,
  LEFT_INDEX: 19,    RIGHT_INDEX: 20,
  LEFT_THUMB: 21,    RIGHT_THUMB: 22,
  LEFT_HIP: 23,      RIGHT_HIP: 24,
  LEFT_KNEE: 25,     RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,    RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,     RIGHT_HEEL: 30,
  LEFT_FOOT: 31,     RIGHT_FOOT: 32
};

const BODY_CONNECTIONS = [
  // Torso
  [LM.LEFT_SHOULDER, LM.RIGHT_SHOULDER],
  [LM.LEFT_HIP, LM.RIGHT_HIP],
  [LM.LEFT_SHOULDER, LM.LEFT_HIP],
  [LM.RIGHT_SHOULDER, LM.RIGHT_HIP],
  // Left arm
  [LM.LEFT_SHOULDER, LM.LEFT_ELBOW],
  [LM.LEFT_ELBOW, LM.LEFT_WRIST],
  [LM.LEFT_WRIST, LM.LEFT_INDEX],
  [LM.LEFT_WRIST, LM.LEFT_PINKY],
  // Right arm
  [LM.RIGHT_SHOULDER, LM.RIGHT_ELBOW],
  [LM.RIGHT_ELBOW, LM.RIGHT_WRIST],
  [LM.RIGHT_WRIST, LM.RIGHT_INDEX],
  [LM.RIGHT_WRIST, LM.RIGHT_PINKY],
  // Left leg
  [LM.LEFT_HIP, LM.LEFT_KNEE],
  [LM.LEFT_KNEE, LM.LEFT_ANKLE],
  [LM.LEFT_ANKLE, LM.LEFT_HEEL],
  [LM.LEFT_ANKLE, LM.LEFT_FOOT],
  // Right leg
  [LM.RIGHT_HIP, LM.RIGHT_KNEE],
  [LM.RIGHT_KNEE, LM.RIGHT_ANKLE],
  [LM.RIGHT_ANKLE, LM.RIGHT_HEEL],
  [LM.RIGHT_ANKLE, LM.RIGHT_FOOT],
];

const KEY_LANDMARKS = [
  LM.NOSE,
  LM.LEFT_SHOULDER, LM.RIGHT_SHOULDER,
  LM.LEFT_ELBOW, LM.RIGHT_ELBOW,
  LM.LEFT_WRIST, LM.RIGHT_WRIST,
  LM.LEFT_HIP, LM.RIGHT_HIP,
  LM.LEFT_KNEE, LM.RIGHT_KNEE,
  LM.LEFT_ANKLE, LM.RIGHT_ANKLE,
];

const LANDMARK_LABELS = {
  [LM.NOSE]: 'Head',
  [LM.LEFT_SHOULDER]: 'L.Shoulder', [LM.RIGHT_SHOULDER]: 'R.Shoulder',
  [LM.LEFT_ELBOW]: 'L.Elbow',      [LM.RIGHT_ELBOW]: 'R.Elbow',
  [LM.LEFT_WRIST]: 'L.Wrist',      [LM.RIGHT_WRIST]: 'R.Wrist',
  [LM.LEFT_HIP]: 'L.Hip',          [LM.RIGHT_HIP]: 'R.Hip',
  [LM.LEFT_KNEE]: 'L.Knee',        [LM.RIGHT_KNEE]: 'R.Knee',
  [LM.LEFT_ANKLE]: 'L.Ankle',      [LM.RIGHT_ANKLE]: 'R.Ankle',
};

const SWING_PHASES = [
  'Address', 'Takeaway', 'Top of Backswing',
  'Mid-Downswing', 'Impact', 'Follow-Through', 'Finish'
];

const USER_CLR  = '#00e5ff';
const PRO_CLR   = '#ffd740';
const SPINE_CLR = '#ff9800';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const S = {
  step: 1,
  userFile: null,
  proFile: null,
  club: '',
  proName: '',
  angle: 'side',   // 'side' | 'front'
  apiKey: '',
  playing: false,
  showSkeleton: true,
  showAngles: true,
  showLabels: true,
  poseLandmarker: null,
  animId: null,
  userMetrics: null,
  proMetrics: null,
  metricsHistory: { user: [], pro: [] },
  frames: [],
  lastUserT: -1,
  lastProT: -1,
  seekingByUser: false,
};

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------
async function init() {
  wireEvents();
  showLoading('Loading pose detection model (may take a few seconds)...');
  try {
    const vision = await FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'
    );
    S.poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task',
        delegate: 'GPU',
      },
      runningMode: 'VIDEO',
      numPoses: 1,
    });
    hideLoading();
  } catch (e) {
    console.error('MediaPipe init failed:', e);
    hideLoading();
    alert('Could not initialise pose detection. Please reload or try a different browser.');
  }
}

// ---------------------------------------------------------------------------
// Wire all UI events
// ---------------------------------------------------------------------------
function wireEvents() {
  // Upload
  setupUploadZone('user');
  setupUploadZone('pro');

  // Remove video buttons
  $('#user-remove').addEventListener('click', (e) => { e.stopPropagation(); removeVideo('user'); });
  $('#pro-remove').addEventListener('click',  (e) => { e.stopPropagation(); removeVideo('pro');  });

  // Step navigation buttons
  $('#next-to-settings').addEventListener('click', () => goTo(2));
  $('#back-to-upload').addEventListener('click',   () => goTo(1));
  $('#start-analysis').addEventListener('click',   () => goTo(3));
  $('#back-to-settings').addEventListener('click', () => goTo(2));
  $('#reset-analysis').addEventListener('click', resetAll);

  // Step nav header
  $$('.step-btn').forEach(b =>
    b.addEventListener('click', () => {
      const s = +b.dataset.step;
      if (s <= S.step || (s === 2 && S.userFile && S.proFile)) goTo(s);
    })
  );

  // Settings
  $('#club-select').addEventListener('change', (e) => { S.club = e.target.value; });
  $('#pro-select').addEventListener('change',  (e) => { S.proName = e.target.value; });
  $$('.toggle-btn[data-angle]').forEach(b => {
    b.addEventListener('click', () => {
      $$('.toggle-btn[data-angle]').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      S.angle = b.dataset.angle;
    });
  });

  // API key
  $('#api-key-input').addEventListener('input', (e) => { S.apiKey = e.target.value; });
  $('#toggle-key-vis').addEventListener('click', () => {
    const inp = $('#api-key-input');
    inp.type = inp.type === 'password' ? 'text' : 'password';
  });

  // Playback controls
  $('#play-pause-btn').addEventListener('click', togglePlay);
  $('#seek-bar').addEventListener('input', onSeek);
  $('#seek-bar').addEventListener('mousedown', () => { S.seekingByUser = true; });
  $('#seek-bar').addEventListener('mouseup',   () => { S.seekingByUser = false; });
  $('#speed-select').addEventListener('change', onSpeedChange);
  $('#capture-btn').addEventListener('click', captureFrame);

  // Overlay toggles
  $('#show-skeleton').addEventListener('change', (e) => { S.showSkeleton = e.target.checked; });
  $('#show-angles').addEventListener('change',   (e) => { S.showAngles = e.target.checked; });
  $('#show-labels').addEventListener('change',   (e) => { S.showLabels = e.target.checked; });

  // AI Feedback
  $('#get-feedback-btn').addEventListener('click', getAIFeedback);

  // AI Phase Play
  $('#smart-play-btn').addEventListener('click', startSmartPlayback);
}

// ---------------------------------------------------------------------------
// Upload handling
// ---------------------------------------------------------------------------
function setupUploadZone(type) {
  const zone  = $(`#${type}-upload-zone`);
  const input = $(`#${type}-file-input`);

  input.addEventListener('change', (e) => {
    if (e.target.files[0]) loadVideo(type, e.target.files[0]);
  });

  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) loadVideo(type, file);
  });
}

function loadVideo(type, file) {
  const url     = URL.createObjectURL(file);
  const preview = $(`#${type}-preview`);
  const placeholder = $(`#${type}-placeholder`);
  const container   = $(`#${type}-preview-container`);
  const zone        = $(`#${type}-upload-zone`);

  preview.src = url;
  placeholder.classList.add('hidden');
  container.classList.remove('hidden');
  zone.classList.add('has-video');

  if (type === 'user') S.userFile = file; else S.proFile = file;
  checkUploadsReady();
}

function removeVideo(type) {
  const preview     = $(`#${type}-preview`);
  const placeholder = $(`#${type}-placeholder`);
  const container   = $(`#${type}-preview-container`);
  const zone        = $(`#${type}-upload-zone`);

  if (preview.src) URL.revokeObjectURL(preview.src);
  preview.src = '';
  placeholder.classList.remove('hidden');
  container.classList.add('hidden');
  zone.classList.remove('has-video');

  if (type === 'user') S.userFile = null; else S.proFile = null;
  checkUploadsReady();
}

function checkUploadsReady() {
  $('#next-to-settings').disabled = !(S.userFile && S.proFile);
}

// ---------------------------------------------------------------------------
// Step navigation
// ---------------------------------------------------------------------------
function goTo(step) {
  if (step === 3 && (!S.userFile || !S.proFile)) return;

  // Stop playback when leaving analysis
  if (S.playing) stopPlay();

  $$('.step-content').forEach(el => el.classList.remove('active'));
  $(`#step-${step}`).classList.add('active');

  $$('.step-btn').forEach(b => {
    const s = +b.dataset.step;
    b.classList.remove('active', 'completed');
    if (s < step)  b.classList.add('completed');
    if (s === step) b.classList.add('active');
  });

  S.step = step;

  if (step === 3) setupAnalysis();
}

// ---------------------------------------------------------------------------
// Analysis setup
// ---------------------------------------------------------------------------
function setupAnalysis() {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  const proLabelEl = $('#pro-label-name');
  if (S.proName) proLabelEl.textContent = S.proName;

  // Load videos
  uVid.src = URL.createObjectURL(S.userFile);
  pVid.src = URL.createObjectURL(S.proFile);

  Promise.all([
    new Promise(r => { uVid.onloadeddata = r; }),
    new Promise(r => { pVid.onloadeddata = r; }),
  ]).then(() => {
    sizeCanvas('user');
    sizeCanvas('pro');
    // Reset seek
    $('#seek-bar').value = 0;
    updateTimeDisplay();
  });
}

function sizeCanvas(type) {
  const vid    = $(`#${type}-video`);
  const canvas = $(`#${type}-canvas`);
  canvas.width  = vid.videoWidth;
  canvas.height = vid.videoHeight;
}

// ---------------------------------------------------------------------------
// Playback controls
// ---------------------------------------------------------------------------
function togglePlay() {
  S.playing ? stopPlay() : startPlay();
}

function startPlay() {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  uVid.play();
  pVid.play();
  S.playing = true;
  S.lastUserT = -1;
  S.lastProT  = -1;
  $('#play-icon').classList.add('hidden');
  $('#pause-icon').classList.remove('hidden');
  detectLoop();

  // Sync end
  uVid.onended = () => stopPlay();
  pVid.onended = () => stopPlay();
}

function stopPlay() {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  uVid.pause();
  pVid.pause();
  S.playing = false;
  if (S.animId) cancelAnimationFrame(S.animId);
  S.animId = null;
  $('#play-icon').classList.remove('hidden');
  $('#pause-icon').classList.add('hidden');
}

function onSeek() {
  const pct = +$('#seek-bar').value / 1000;
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  if (uVid.duration) uVid.currentTime = uVid.duration * pct;
  if (pVid.duration) pVid.currentTime = pVid.duration * pct;
  updateTimeDisplay();

  // Run a single frame detection at this position
  runSingleFrame();
}

function onSpeedChange() {
  const speed = +$('#speed-select').value;
  $('#user-video').playbackRate = speed;
  $('#pro-video').playbackRate = speed;
}

function updateTimeDisplay() {
  const uVid = $('#user-video');
  const cur = fmt(uVid.currentTime || 0);
  const dur = fmt(uVid.duration || 0);
  $('#time-display').textContent = `${cur} / ${dur}`;
}
function fmt(s) {
  if (!isFinite(s)) return '0:00';
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60).toString().padStart(2, '0');
  return `${m}:${sec}`;
}

// ---------------------------------------------------------------------------
// Pose detection loop
// ---------------------------------------------------------------------------
function detectLoop() {
  if (!S.playing) return;

  processVideoPose('user', USER_CLR);
  processVideoPose('pro', PRO_CLR);

  // Update seek bar
  const uVid = $('#user-video');
  if (!S.seekingByUser && uVid.duration) {
    $('#seek-bar').value = (uVid.currentTime / uVid.duration) * 1000;
  }
  updateTimeDisplay();

  // Update metrics display
  if (S.userMetrics && S.proMetrics) {
    renderMetrics(S.userMetrics, S.proMetrics);
  }

  S.animId = requestAnimationFrame(detectLoop);
}

function processVideoPose(type, color, allowPaused = false) {
  const vid    = $(`#${type}-video`);
  const canvas = $(`#${type}-canvas`);

  if (vid.readyState < 2) return;
  if (!allowPaused && (vid.paused || vid.ended)) return;

  const now = performance.now();
  const lastKey = type === 'user' ? 'lastUserT' : 'lastProT';
  if (now - S[lastKey] < 30) return; // throttle to ~33fps max
  S[lastKey] = now;

  try {
    const results = S.poseLandmarker.detectForVideo(vid, now);
    drawPose(canvas, results, color, type);
    if (results.landmarks && results.landmarks.length > 0) {
      const metrics = computeMetrics(results.landmarks[0]);
      if (type === 'user') S.userMetrics = metrics; else S.proMetrics = metrics;
    }
  } catch (e) {
    // MediaPipe may throw on some frames; ignore
  }
}

function runSingleFrame() {
  if (!S.poseLandmarker) return;
  // Slight delay to let video seek settle
  setTimeout(() => {
    processVideoPose('user', USER_CLR, true);
    // Need a different timestamp for the second call
    setTimeout(() => {
      processVideoPose('pro', PRO_CLR, true);
      if (S.userMetrics && S.proMetrics) renderMetrics(S.userMetrics, S.proMetrics);
    }, 50);
  }, 100);
}

// ---------------------------------------------------------------------------
// Drawing
// ---------------------------------------------------------------------------
function drawPose(canvas, results, color, type) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  if (!results.landmarks || results.landmarks.length === 0) return;
  const lm = results.landmarks[0];

  if (S.showSkeleton) {
    // Connections
    ctx.strokeStyle = color;
    ctx.lineWidth = Math.max(2, w * 0.004);
    ctx.lineCap = 'round';
    for (const [i, j] of BODY_CONNECTIONS) {
      const a = lm[i], b = lm[j];
      if ((a.visibility ?? 0) > 0.4 && (b.visibility ?? 0) > 0.4) {
        ctx.beginPath();
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.stroke();
      }
    }

    // Spine line (shoulder midpoint → hip midpoint)
    const sMid = mid(lm[LM.LEFT_SHOULDER], lm[LM.RIGHT_SHOULDER]);
    const hMid = mid(lm[LM.LEFT_HIP], lm[LM.RIGHT_HIP]);
    ctx.strokeStyle = SPINE_CLR;
    ctx.lineWidth = Math.max(3, w * 0.005);
    ctx.setLineDash([8, 6]);
    ctx.beginPath();
    ctx.moveTo(sMid.x * w, sMid.y * h);
    ctx.lineTo(hMid.x * w, hMid.y * h);
    ctx.stroke();
    ctx.setLineDash([]);

    // Club line (extend from hand midpoint outward)
    drawClubLine(ctx, lm, w, h, color);

    // Landmarks (dots)
    for (const idx of KEY_LANDMARKS) {
      const p = lm[idx];
      if ((p.visibility ?? 0) > 0.4) {
        const px = p.x * w, py = p.y * h;
        const r = Math.max(4, w * 0.006);
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(px, py, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  }

  if (S.showLabels) {
    ctx.font = `bold ${Math.max(10, w * 0.018)}px Inter, sans-serif`;
    ctx.textBaseline = 'bottom';
    for (const idx of KEY_LANDMARKS) {
      const p = lm[idx];
      if ((p.visibility ?? 0) > 0.4 && LANDMARK_LABELS[idx]) {
        const px = p.x * w, py = p.y * h;
        const label = LANDMARK_LABELS[idx];
        const tw = ctx.measureText(label).width;
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.fillRect(px + 6, py - 14, tw + 6, 16);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, px + 9, py);
      }
    }
  }

  if (S.showAngles) {
    drawAngleArc(ctx, lm, LM.LEFT_SHOULDER, LM.LEFT_ELBOW, LM.LEFT_WRIST, w, h, color, 'L.Elbow');
    drawAngleArc(ctx, lm, LM.RIGHT_SHOULDER, LM.RIGHT_ELBOW, LM.RIGHT_WRIST, w, h, color, 'R.Elbow');
    drawAngleArc(ctx, lm, LM.LEFT_HIP, LM.LEFT_KNEE, LM.LEFT_ANKLE, w, h, color, 'L.Knee');
    drawAngleArc(ctx, lm, LM.RIGHT_HIP, LM.RIGHT_KNEE, LM.RIGHT_ANKLE, w, h, color, 'R.Knee');

    // Spine angle indicator
    const sMid2 = mid(lm[LM.LEFT_SHOULDER], lm[LM.RIGHT_SHOULDER]);
    const hMid2 = mid(lm[LM.LEFT_HIP], lm[LM.RIGHT_HIP]);
    const spAng = angleToVertical(hMid2, sMid2);
    const hx = hMid2.x * w, hy = hMid2.y * h;
    ctx.fillStyle = SPINE_CLR;
    ctx.font = `bold ${Math.max(11, w * 0.02)}px Inter, sans-serif`;
    ctx.fillText(`Spine ${Math.abs(spAng).toFixed(0)}°`, hx + 10, hy - 6);
  }
}

function drawClubLine(ctx, lm, w, h, color) {
  // Approximate club line extending from wrist midpoint through the index/pinky finger direction
  const lw = lm[LM.LEFT_WRIST], rw = lm[LM.RIGHT_WRIST];
  const li = lm[LM.LEFT_INDEX], ri = lm[LM.RIGHT_INDEX];
  if ((lw.visibility ?? 0) < 0.3 || (rw.visibility ?? 0) < 0.3) return;

  const wristMid  = mid(lw, rw);
  const fingerMid = mid(li, ri);

  // Direction from wrist to fingers, extend it
  const dx = fingerMid.x - wristMid.x;
  const dy = fingerMid.y - wristMid.y;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 0.005) return;

  const extend = 0.25; // extend club line this far
  const endX = fingerMid.x + (dx / len) * extend;
  const endY = fingerMid.y + (dy / len) * extend;

  ctx.strokeStyle = '#b0bec5';
  ctx.lineWidth = Math.max(2, w * 0.003);
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(wristMid.x * w, wristMid.y * h);
  ctx.lineTo(endX * w, endY * h);
  ctx.stroke();
  ctx.setLineDash([]);

  // Club head dot
  ctx.fillStyle = '#b0bec5';
  ctx.beginPath();
  ctx.arc(endX * w, endY * h, 4, 0, Math.PI * 2);
  ctx.fill();
}

function drawAngleArc(ctx, lm, ai, bi, ci, w, h, color, label) {
  const a = lm[ai], b = lm[bi], c = lm[ci];
  if ((a.visibility ?? 0) < 0.4 || (b.visibility ?? 0) < 0.4 || (c.visibility ?? 0) < 0.4) return;

  const angle = angleBetween(a, b, c);
  const bx = b.x * w, by = b.y * h;

  // Small arc
  const r = Math.max(16, w * 0.03);
  const angA = Math.atan2((a.y - b.y) * h, (a.x - b.x) * w);
  const angC = Math.atan2((c.y - b.y) * h, (c.x - b.x) * w);

  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.globalAlpha = 0.6;
  ctx.beginPath();
  ctx.arc(bx, by, r, Math.min(angA, angC), Math.max(angA, angC));
  ctx.stroke();
  ctx.globalAlpha = 1;

  // Angle text
  ctx.fillStyle = '#fff';
  ctx.font = `bold ${Math.max(9, w * 0.016)}px Inter, sans-serif`;
  ctx.fillText(`${angle.toFixed(0)}°`, bx + r + 4, by + 4);
}

// ---------------------------------------------------------------------------
// Metrics computation
// ---------------------------------------------------------------------------
function computeMetrics(lm) {
  const ls = lm[LM.LEFT_SHOULDER], rs = lm[LM.RIGHT_SHOULDER];
  const lh = lm[LM.LEFT_HIP],     rh = lm[LM.RIGHT_HIP];
  const le = lm[LM.LEFT_ELBOW],    re = lm[LM.RIGHT_ELBOW];
  const lw = lm[LM.LEFT_WRIST],    rw = lm[LM.RIGHT_WRIST];
  const lk = lm[LM.LEFT_KNEE],     rk = lm[LM.RIGHT_KNEE];
  const la = lm[LM.LEFT_ANKLE],    ra = lm[LM.RIGHT_ANKLE];
  const nose = lm[LM.NOSE];

  const sMid = mid(ls, rs);
  const hMid = mid(lh, rh);
  const aMid = mid(la, ra);

  return {
    spineAngle:    angleToVertical(hMid, sMid),
    shoulderTurn:  Math.abs(ls.x - rs.x),
    hipRotation:   Math.abs(lh.x - rh.x),
    leadArmAngle:  angleBetween(ls, le, lw),
    trailArmAngle: angleBetween(rs, re, rw),
    leadKneeFlex:  angleBetween(lh, lk, la),
    trailKneeFlex: angleBetween(rh, rk, ra),
    headLateral:   nose.x - hMid.x,
    weightShift:   hMid.x - aMid.x,
    shoulderTilt:  angleToHorizontal(ls, rs),
  };
}

// ---------------------------------------------------------------------------
// Metrics display
// ---------------------------------------------------------------------------
function renderMetrics(um, pm) {
  const isSide = S.angle === 'side';

  const defs = isSide ? [
    { name: 'Spine Angle',    uv: um.spineAngle,     pv: pm.spineAngle,     unit: '°', th: 5  },
    { name: 'Lead Arm',       uv: um.leadArmAngle,   pv: pm.leadArmAngle,   unit: '°', th: 10 },
    { name: 'Trail Arm',      uv: um.trailArmAngle,  pv: pm.trailArmAngle,  unit: '°', th: 10 },
    { name: 'Lead Knee',      uv: um.leadKneeFlex,    pv: pm.leadKneeFlex,   unit: '°', th: 8  },
    { name: 'Trail Knee',     uv: um.trailKneeFlex,   pv: pm.trailKneeFlex,  unit: '°', th: 8  },
    { name: 'Head Position',  uv: um.headLateral*100,  pv: pm.headLateral*100,  unit: '',  th: 3  },
    { name: 'Weight Shift',   uv: um.weightShift*100,  pv: pm.weightShift*100,  unit: '',  th: 4  },
    { name: 'Shoulder Tilt',  uv: um.shoulderTilt,    pv: pm.shoulderTilt,   unit: '°', th: 5  },
  ] : [
    { name: 'Shoulder Turn',  uv: um.shoulderTurn*100, pv: pm.shoulderTurn*100, unit: '', th: 5  },
    { name: 'Hip Rotation',   uv: um.hipRotation*100,  pv: pm.hipRotation*100,  unit: '', th: 5  },
    { name: 'Spine Angle',    uv: um.spineAngle,      pv: pm.spineAngle,      unit: '°', th: 5  },
    { name: 'Lead Arm',       uv: um.leadArmAngle,    pv: pm.leadArmAngle,    unit: '°', th: 10 },
    { name: 'Trail Arm',      uv: um.trailArmAngle,   pv: pm.trailArmAngle,   unit: '°', th: 10 },
    { name: 'Lead Knee',      uv: um.leadKneeFlex,     pv: pm.leadKneeFlex,    unit: '°', th: 8  },
    { name: 'Trail Knee',     uv: um.trailKneeFlex,    pv: pm.trailKneeFlex,   unit: '°', th: 8  },
    { name: 'Weight Shift',   uv: um.weightShift*100,  pv: pm.weightShift*100,  unit: '', th: 4  },
  ];

  const grid = $('#metrics-grid');
  grid.innerHTML = defs.map(d => {
    const diff = Math.abs(d.uv - d.pv);
    const grade = diff < d.th ? 'good' : diff < d.th * 2 ? 'warn' : 'bad';
    const gradeLabel = diff < d.th ? 'Similar' : diff < d.th * 2 ? 'Slight diff' : 'Significant';
    return `
      <div class="metric-card ${grade}">
        <div class="metric-name">${d.name}</div>
        <div class="metric-values">
          <span class="user-val">${d.uv.toFixed(1)}${d.unit}</span>
          <span class="vs">vs</span>
          <span class="pro-val">${d.pv.toFixed(1)}${d.unit}</span>
        </div>
        <div class="metric-diff ${grade}">${gradeLabel} (${diff.toFixed(1)}${d.unit})</div>
      </div>`;
  }).join('');
}

// ---------------------------------------------------------------------------
// Frame capture
// ---------------------------------------------------------------------------
function captureFrame() {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  const uCan = $('#user-canvas');
  const pCan = $('#pro-canvas');

  // Create composite snapshot (video + overlay)
  const snap = (vid, overlay) => {
    const c = document.createElement('canvas');
    c.width = vid.videoWidth; c.height = vid.videoHeight;
    const cx = c.getContext('2d');
    cx.drawImage(vid, 0, 0);
    cx.drawImage(overlay, 0, 0, c.width, c.height);
    return c.toDataURL('image/jpeg', 0.85);
  };

  const phase = SWING_PHASES[S.frames.length] || `Frame ${S.frames.length + 1}`;
  S.frames.push({
    phase,
    time: uVid.currentTime,
    userImg: snap(uVid, uCan),
    proImg:  snap(pVid, pCan),
    userMetrics: S.userMetrics ? { ...S.userMetrics } : null,
    proMetrics:  S.proMetrics  ? { ...S.proMetrics }  : null,
  });
  renderCapturedFrames();
}

function renderCapturedFrames() {
  const grid = $('#keyframes-grid');
  grid.innerHTML = S.frames.map(f => `
    <div class="keyframe-card">
      <div class="keyframe-label">${f.phase}</div>
      <div class="keyframe-images">
        <div class="keyframe-img">
          <img src="${f.userImg}" alt="Your swing – ${f.phase}">
          <span>You</span>
        </div>
        <div class="keyframe-img">
          <img src="${f.proImg}" alt="Pro swing – ${f.phase}">
          <span>Pro</span>
        </div>
      </div>
    </div>`).join('');
}

// ---------------------------------------------------------------------------
// AI Phase Detection — Smart Playback
// ---------------------------------------------------------------------------
const PHASE_NAMES = ['Address', 'Takeaway', 'Top of Backswing', 'Mid-Downswing', 'Impact', 'Follow-Through'];

function extractFrameAsBase64(video, time) {
  return new Promise((resolve) => {
    const c = document.createElement('canvas');
    c.width = video.videoWidth;
    c.height = video.videoHeight;
    const ctx = c.getContext('2d');

    const onSeeked = () => {
      video.removeEventListener('seeked', onSeeked);
      ctx.drawImage(video, 0, 0);
      resolve(c.toDataURL('image/jpeg', 0.7));
    };

    video.addEventListener('seeked', onSeeked);
    video.currentTime = time;
  });
}

async function detectPhasesForVideo(video, label) {
  const duration = video.duration;
  const numSamples = 12;
  const interval = duration / (numSamples + 1);
  const frames = [];

  const statusText = $('#phase-status-text');
  const progressBar = $('#phase-progress-bar');

  for (let i = 1; i <= numSamples; i++) {
    const t = interval * i;
    statusText.textContent = `Extracting ${label} frame ${i}/${numSamples}...`;
    progressBar.style.width = `${(i / numSamples) * 30}%`;
    const dataUrl = await extractFrameAsBase64(video, t);
    frames.push({ time: t, dataUrl });
  }

  statusText.textContent = `Sending ${label} frames to AI for phase detection...`;
  progressBar.style.width = '40%';

  const imageContents = frames.map((f, idx) => ({
    type: 'image',
    source: { type: 'base64', media_type: 'image/jpeg', data: f.dataUrl.split(',')[1] },
  }));

  const textPrompt = {
    type: 'text',
    text: `You are analyzing ${numSamples} sequential frames from a golf swing video. The frames are evenly spaced across the full swing. For each frame (numbered 1-${numSamples}), identify which swing phase it belongs to. The phases IN ORDER are:
1. Address (setup position before swing starts)
2. Takeaway (club moving back, hands below chest)
3. Top of Backswing (hands/club at highest point behind)
4. Mid-Downswing (club coming down, roughly 45° from top)
5. Impact (club contacting the ball)
6. Follow-Through (after impact, club swinging through to finish)

Respond ONLY with a JSON array of objects. Each object must have "frame" (1-based index) and "phase" (exact phase name from the list above). Example:
[{"frame":1,"phase":"Address"},{"frame":2,"phase":"Address"},{"frame":3,"phase":"Takeaway"},...]}

If a frame is unclear or shows no golfer, use the phase that makes most sense given adjacent frames. The phases must be monotonically non-decreasing (a later frame cannot be an earlier phase).`
  };

  const messages = [{
    role: 'user',
    content: [...imageContents, textPrompt],
  }];

  try {
    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': S.apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1024,
        messages,
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`API ${resp.status}: ${err}`);
    }

    const data = await resp.json();
    const text = data.content[0].text;

    // Parse JSON from response (may be wrapped in markdown code block)
    const jsonMatch = text.match(/\[[\s\S]*\]/);
    if (!jsonMatch) throw new Error('Could not parse phase detection response');

    const phaseResults = JSON.parse(jsonMatch[0]);

    // Map frame indices back to timestamps and find phase transitions
    const phases = [];
    let currentPhase = null;

    for (const item of phaseResults) {
      const frameIdx = item.frame - 1;
      if (frameIdx >= 0 && frameIdx < frames.length) {
        if (item.phase !== currentPhase) {
          phases.push({ phase: item.phase, time: frames[frameIdx].time });
          currentPhase = item.phase;
        }
      }
    }

    return phases;
  } catch (e) {
    throw new Error(`Phase detection failed for ${label}: ${e.message}`);
  }
}

async function startSmartPlayback() {
  if (!S.apiKey) {
    alert('Enter your Anthropic API key in Settings (Step 2) to use AI Phase Play.');
    return;
  }

  const uVid = $('#user-video');
  const pVid = $('#pro-video');

  if (!uVid.duration || !pVid.duration) {
    alert('Both videos must be loaded before using AI Phase Play.');
    return;
  }

  // Show status
  const statusEl = $('#phase-status');
  const statusText = $('#phase-status-text');
  const progressBar = $('#phase-progress-bar');
  const smartBtn = $('#smart-play-btn');

  statusEl.classList.remove('hidden');
  smartBtn.classList.add('active');
  smartBtn.disabled = true;
  progressBar.style.width = '0%';

  // Stop any current playback
  stopPlay();

  // Clear previous captures for fresh AI analysis
  S.frames = [];
  $('#keyframes-grid').innerHTML = '';

  try {
    // Detect phases for user video
    statusText.textContent = 'Analyzing your swing...';
    const userPhases = await detectPhasesForVideo(uVid, 'Your Swing');
    progressBar.style.width = '50%';

    // Detect phases for pro video
    statusText.textContent = 'Analyzing pro swing...';
    const proPhases = await detectPhasesForVideo(pVid, 'Pro Swing');
    progressBar.style.width = '80%';

    statusText.textContent = 'Starting synchronized phase playback...';
    progressBar.style.width = '100%';

    // Wait briefly to show completion
    await sleep(500);
    statusEl.classList.add('hidden');

    // Run the synchronized phase-by-phase playback
    await playPhaseByPhase(userPhases, proPhases);

  } catch (e) {
    statusText.textContent = `Error: ${e.message}`;
    progressBar.style.width = '0%';
    setTimeout(() => statusEl.classList.add('hidden'), 4000);
  } finally {
    smartBtn.classList.remove('active');
    smartBtn.disabled = false;
  }
}

async function playPhaseByPhase(userPhases, proPhases) {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  const uBadge = $('#user-phase-badge');
  const pBadge = $('#pro-phase-badge');

  // For each of the 6 canonical phases, find best matching timestamp in each video
  for (const targetPhase of PHASE_NAMES) {
    const userMatch = userPhases.find(p => p.phase === targetPhase);
    const proMatch = proPhases.find(p => p.phase === targetPhase);

    if (!userMatch && !proMatch) continue;

    // Seek both videos to their respective phase timestamps
    const userTime = userMatch ? userMatch.time : estimateTime(uVid.duration, targetPhase);
    const proTime = proMatch ? proMatch.time : estimateTime(pVid.duration, targetPhase);

    // Seek and wait for both to settle
    await seekAndWait(uVid, userTime);
    await seekAndWait(pVid, proTime);

    // Show phase badges
    uBadge.textContent = targetPhase;
    uBadge.classList.remove('hidden');
    pBadge.textContent = targetPhase;
    pBadge.classList.remove('hidden');

    // Update seek bar position
    if (uVid.duration) {
      $('#seek-bar').value = (uVid.currentTime / uVid.duration) * 1000;
    }
    updateTimeDisplay();

    // Run pose detection at this frame
    runSingleFrame();
    await sleep(200); // allow pose detection to process

    // Auto-capture this phase
    captureFrameWithLabel(targetPhase);

    // Pause at this phase for 2 seconds so user can examine
    await sleep(2000);
  }

  // Hide badges at end
  uBadge.classList.add('hidden');
  pBadge.classList.add('hidden');
}

function captureFrameWithLabel(phaseName) {
  const uVid = $('#user-video');
  const pVid = $('#pro-video');
  const uCan = $('#user-canvas');
  const pCan = $('#pro-canvas');

  const snap = (vid, overlay) => {
    const c = document.createElement('canvas');
    c.width = vid.videoWidth; c.height = vid.videoHeight;
    const cx = c.getContext('2d');
    cx.drawImage(vid, 0, 0);
    cx.drawImage(overlay, 0, 0, c.width, c.height);
    return c.toDataURL('image/jpeg', 0.85);
  };

  S.frames.push({
    phase: phaseName,
    time: uVid.currentTime,
    userImg: snap(uVid, uCan),
    proImg:  snap(pVid, pCan),
    userMetrics: S.userMetrics ? { ...S.userMetrics } : null,
    proMetrics:  S.proMetrics  ? { ...S.proMetrics }  : null,
  });
  renderCapturedFrames();
}

function estimateTime(duration, phase) {
  // Fallback: distribute phases evenly across the video duration
  const idx = PHASE_NAMES.indexOf(phase);
  return (duration * (idx + 0.5)) / PHASE_NAMES.length;
}

function seekAndWait(video, time) {
  return new Promise((resolve) => {
    if (Math.abs(video.currentTime - time) < 0.05) {
      resolve();
      return;
    }
    const onSeeked = () => {
      video.removeEventListener('seeked', onSeeked);
      resolve();
    };
    video.addEventListener('seeked', onSeeked);
    video.currentTime = time;
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// AI Feedback (Claude API)
// ---------------------------------------------------------------------------
async function getAIFeedback() {
  if (!S.apiKey) {
    alert('Enter your Anthropic API key in Settings (Step 2) to use AI coaching.');
    return;
  }

  const feedEl = $('#feedback-content');
  feedEl.innerHTML = '<div class="loading-feedback"><div class="mini-spinner"></div> Analyzing your swing&hellip;</div>';

  // Build comparison summary from captured frames or current metrics
  const summary = buildSummary();

  try {
    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': S.apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1500,
        messages: [{
          role: 'user',
          content: `You are an expert PGA-level golf swing coach. Analyse the following swing comparison data between an amateur golfer and ${S.proName || 'a professional'}. Club used: ${S.club || 'unknown'}. Camera angle: ${S.angle} view.

METRIC DATA (each line: Metric — User value vs Pro value):
${summary}

Provide a structured coaching report:

1. **Overall Assessment** — one sentence summary of the swing.
2. **Key Differences** (3–5 bullet points) — what the user is doing differently from the pro and *why it matters* for ball flight / consistency. Use specific angle numbers.
3. **Priority Fixes** (top 2–3) — for each, describe the issue, explain the ideal position, and give a concrete drill or feel cue the golfer can practice.
4. **What You're Doing Well** — at least one positive observation where the user is close to the pro.

Use plain language. Reference specific body parts and angles. Be encouraging but honest.`
        }],
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      feedEl.innerHTML = `<p class="error">API error (${resp.status}): ${err}</p>`;
      return;
    }

    const data = await resp.json();
    if (data.content && data.content[0]) {
      feedEl.innerHTML = markdownToHtml(data.content[0].text);
    } else {
      feedEl.innerHTML = '<p class="error">Unexpected API response. Please try again.</p>';
    }
  } catch (e) {
    feedEl.innerHTML = `<p class="error">Request failed: ${e.message}</p>`;
  }
}

function buildSummary() {
  // Use captured frames if available, otherwise current metrics
  const frames = S.frames.length > 0 ? S.frames : [];

  if (frames.length > 0) {
    return frames.map(f => {
      if (!f.userMetrics || !f.proMetrics) return `${f.phase}: no metrics`;
      return formatMetricsPair(f.phase, f.userMetrics, f.proMetrics);
    }).join('\n\n');
  }

  if (S.userMetrics && S.proMetrics) {
    return formatMetricsPair('Current Frame', S.userMetrics, S.proMetrics);
  }

  return 'No metrics captured yet. Play the videos and capture some frames first.';
}

function formatMetricsPair(phase, um, pm) {
  const lines = [
    `[${phase}]`,
    `Spine Angle: ${um.spineAngle.toFixed(1)}° vs ${pm.spineAngle.toFixed(1)}°`,
    `Shoulder Turn: ${(um.shoulderTurn*100).toFixed(1)} vs ${(pm.shoulderTurn*100).toFixed(1)}`,
    `Hip Rotation: ${(um.hipRotation*100).toFixed(1)} vs ${(pm.hipRotation*100).toFixed(1)}`,
    `Lead Arm Angle: ${um.leadArmAngle.toFixed(1)}° vs ${pm.leadArmAngle.toFixed(1)}°`,
    `Trail Arm Angle: ${um.trailArmAngle.toFixed(1)}° vs ${pm.trailArmAngle.toFixed(1)}°`,
    `Lead Knee Flex: ${um.leadKneeFlex.toFixed(1)}° vs ${pm.leadKneeFlex.toFixed(1)}°`,
    `Trail Knee Flex: ${um.trailKneeFlex.toFixed(1)}° vs ${pm.trailKneeFlex.toFixed(1)}°`,
    `Head Position: ${(um.headLateral*100).toFixed(1)} vs ${(pm.headLateral*100).toFixed(1)}`,
    `Weight Shift: ${(um.weightShift*100).toFixed(1)} vs ${(pm.weightShift*100).toFixed(1)}`,
    `Shoulder Tilt: ${um.shoulderTilt.toFixed(1)}° vs ${pm.shoulderTilt.toFixed(1)}°`,
  ];
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Simple markdown → HTML
// ---------------------------------------------------------------------------
function markdownToHtml(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .split('\n')
    .map(line => {
      if (line.startsWith('### '))  return `<h4>${line.slice(4)}</h4>`;
      if (line.startsWith('## '))   return `<h3>${line.slice(3)}</h3>`;
      if (line.startsWith('# '))    return `<h3>${line.slice(2)}</h3>`;
      if (/^\d+\.\s/.test(line))    return `<li>${line.replace(/^\d+\.\s/, '')}</li>`;
      if (line.startsWith('- '))    return `<li>${line.slice(2)}</li>`;
      if (line.trim() === '')       return '<br>';
      return `<p>${line}</p>`;
    })
    .join('\n');
}

// ---------------------------------------------------------------------------
// Reset
// ---------------------------------------------------------------------------
function resetAll() {
  stopPlay();
  S.frames = [];
  S.userMetrics = null;
  S.proMetrics = null;
  S.metricsHistory = { user: [], pro: [] };
  $('#metrics-grid').innerHTML = '<p class="placeholder-text">Metrics will appear here once you play both videos.</p>';
  $('#keyframes-grid').innerHTML = '';
  $('#feedback-content').innerHTML = '<p class="placeholder-text">Play your swing, capture key positions, then click "Get AI Analysis" for personalized coaching.</p>';
  goTo(1);
}

// ---------------------------------------------------------------------------
// Math helpers
// ---------------------------------------------------------------------------
function mid(a, b) {
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: ((a.z || 0) + (b.z || 0)) / 2 };
}

function angleBetween(a, b, c) {
  const ab = { x: a.x - b.x, y: a.y - b.y };
  const cb = { x: c.x - b.x, y: c.y - b.y };
  const dot = ab.x * cb.x + ab.y * cb.y;
  const magAB = Math.sqrt(ab.x ** 2 + ab.y ** 2);
  const magCB = Math.sqrt(cb.x ** 2 + cb.y ** 2);
  const denom = magAB * magCB;
  if (denom === 0) return 0;
  return Math.acos(Math.min(1, Math.max(-1, dot / denom))) * (180 / Math.PI);
}

function angleToVertical(bottom, top) {
  const dx = top.x - bottom.x;
  const dy = top.y - bottom.y;
  return Math.atan2(dx, -dy) * (180 / Math.PI);
}

function angleToHorizontal(left, right) {
  const dx = right.x - left.x;
  const dy = right.y - left.y;
  return Math.atan2(dy, dx) * (180 / Math.PI);
}

// ---------------------------------------------------------------------------
// Loading
// ---------------------------------------------------------------------------
function showLoading(msg) {
  $('#loading-overlay').classList.remove('hidden');
  $('#loading-text').textContent = msg;
}
function hideLoading() {
  $('#loading-overlay').classList.add('hidden');
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
init();

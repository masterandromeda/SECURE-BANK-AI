// SecureBank AI — main.js  (Cyber Security Edition)
'use strict';

/* ─── Live Clock ─── */
function updateClock() {
  const el = document.getElementById('topbar-clock');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-IN', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

/* ─── Sidebar Toggle ─── */
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  // Auto-dismiss alerts
  document.querySelectorAll('.alert.alert-dismissible').forEach(al => {
    setTimeout(() => {
      try { bootstrap.Alert.getOrCreateInstance(al).close(); } catch(e){}
    }, 6000);
  });
});

/* ─────────────────────────────────────────
   SENTINEL AI AGENT — Radar + Threat Feed
─────────────────────────────────────────── */
let agentInterval = null;

function initAgent() {
  const radarSvg  = document.getElementById('agent-radar-svg');
  const feedEl    = document.getElementById('threat-feed');
  const levelEl   = document.getElementById('agent-threat-level');
  const scoreEl   = document.getElementById('agent-threat-score');
  const msgEl     = document.getElementById('agent-msg-text');
  const tlFill    = document.getElementById('tl-fill-bar');
  const tlPct     = document.getElementById('tl-pct');
  const tlSidebar = document.getElementById('sidebar-threat-text');
  const alertDot  = document.getElementById('topbar-alert-dot');

  if (!radarSvg) return;

  function refreshAgent() {
    fetch('/api/agent/status')
      .then(r => r.json())
      .then(data => {
        if (levelEl) {
          levelEl.textContent = data.threat_level;
          levelEl.className = 'badge-cyber ' +
            (data.threat_level === 'LOW' ? 'badge-success' :
             data.threat_level === 'MEDIUM' ? 'badge-warning' : 'badge-danger');
        }
        if (scoreEl)  scoreEl.textContent  = data.threat_score + '%';
        if (msgEl)    msgEl.textContent     = data.message;

        const pct = Math.max(5, data.threat_score);
        if (tlFill)    tlFill.style.width = pct + '%';
        if (tlFill)    tlFill.style.background =
          data.threat_level === 'LOW'    ? 'linear-gradient(90deg,#10b981,#00e5ff)' :
          data.threat_level === 'MEDIUM' ? 'linear-gradient(90deg,#f59e0b,#ef4444)' :
                                           'linear-gradient(90deg,#ef4444,#7c3aed)';
        if (tlPct)     tlPct.textContent  = pct + '%';
        if (tlSidebar) tlSidebar.textContent = 'Threat: ' + data.threat_level;
        if (alertDot) alertDot.style.display = data.threat_level !== 'LOW' ? 'block' : 'none';

        renderBlips(radarSvg, data.blips);

        if (feedEl) {
          feedEl.innerHTML = '';
          data.events.forEach(ev => {
            const icon = ev.type === 'high' ? 'fa-exclamation-triangle' :
                         ev.type === 'medium' ? 'fa-exclamation-circle' : 'fa-check-circle';
            feedEl.innerHTML += `
              <div class="threat-item">
                <div class="threat-icon ${ev.type}"><i class="fas ${icon}"></i></div>
                <div>
                  <div class="threat-text">${ev.msg}</div>
                  <div class="threat-time">${data.timestamp} · ${ev.time}</div>
                </div>
              </div>`;
          });
        }
      })
      .catch(() => {});
  }

  refreshAgent();
  agentInterval = setInterval(refreshAgent, 4000);
}

function renderBlips(svg, blips) {
  svg.querySelectorAll('.radar-blip').forEach(b => b.remove());
  if (!blips) return;
  blips.forEach(b => {
    const color = b.type === 'high' ? '#ef4444' : b.type === 'medium' ? '#f59e0b' : '#00e5ff';
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', b.x);
    circle.setAttribute('cy', b.y);
    circle.setAttribute('r', '4');
    circle.setAttribute('fill', color);
    circle.setAttribute('class', 'radar-blip');
    circle.setAttribute('filter', 'url(#blip-glow)');
    svg.appendChild(circle);
  });
}

/* ─────────────────────────────────────────
   QR SCANNER  (jsQR)
───────────────────────────────────────── */
function initQRScanner() {
  const video   = document.getElementById('qr-video');
  const canvas  = document.getElementById('qr-canvas');
  const resultEl= document.getElementById('qr-result');
  const upiInput= document.getElementById('upi_id');
  const startBtn= document.getElementById('qr-start-btn');
  const stopBtn = document.getElementById('qr-stop-btn');

  if (!video || !canvas) return;

  let stream = null;
  let scanning = false;

  function stopScan() {
    scanning = false;
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
    video.srcObject = null;
    if (stopBtn)  stopBtn.style.display = 'none';
    if (startBtn) startBtn.style.display = 'block';
  }

  function tick() {
    if (!scanning) return;
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      const ctx = canvas.getContext('2d');
      canvas.height = video.videoHeight;
      canvas.width  = video.videoWidth;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = window.jsQR ? jsQR(imgData.data, imgData.width, imgData.height) : null;
      if (code) {
        const val = code.data;
        if (resultEl) { resultEl.textContent = 'Scanned: ' + val; resultEl.style.color = '#10b981'; }
        if (upiInput) upiInput.value = val;
        stopScan();
        return;
      }
    }
    requestAnimationFrame(tick);
  }

  if (startBtn) {
    startBtn.addEventListener('click', () => {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(s => {
          stream = s;
          video.srcObject = s;
          video.play();
          scanning = true;
          if (startBtn) startBtn.style.display = 'none';
          if (stopBtn)  stopBtn.style.display  = 'block';
          requestAnimationFrame(tick);
        })
        .catch(() => {
          if (resultEl) { resultEl.textContent = 'Camera access denied.'; resultEl.style.color = '#ef4444'; }
        });
    });
  }
  if (stopBtn) stopBtn.addEventListener('click', stopScan);
}

/* ─────────────────────────────────────────
   LOGIN RISK PANEL
───────────────────────────────────────── */
function checkLoginRisk(email) {
  const riskBox = document.getElementById('login-risk-box');
  if (!riskBox) return;
  fetch('/api/agent/login-risk', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  }).then(r => r.json()).then(data => {
    riskBox.style.display = 'block';
    document.getElementById('risk-level-badge').textContent = data.risk;
    document.getElementById('risk-level-badge').className = 'badge-cyber ' +
      (data.risk === 'LOW' ? 'badge-warning' : data.risk === 'MEDIUM' ? 'badge-warning' : 'badge-danger');
    document.getElementById('risk-detail-text').textContent = data.risk_msg;
    document.getElementById('risk-attempts').textContent = 'Failed attempts: ' + data.attempts;
    document.getElementById('risk-time').textContent = data.timestamp;
  }).catch(() => {});
}

/* ─── Init on DOM ready ─── */
document.addEventListener('DOMContentLoaded', function () {
  initAgent();
  initQRScanner();
});

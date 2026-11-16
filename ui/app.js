/*
   WJC GLOBAL GROUP — JARVIS COMMAND CENTER
   OpenClaw Gateway Native Frontend.
*/

const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

// Application state
const STATE = {
  activeView: 'chat',
  activeAgent: 'main',
  activeSession: null,
  running: false,
  convo: false,
  suppress: false,
  muted: false,
  speechEnabled: true,
  voiceMode: 'auto',
  stt: false,
  tts: false,
  agents: [],
  sessions: [],
  goals: '',
  tasks: [],
};

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSynth = window.speechSynthesis;

// Standard headers for API calls (cookie is automatically sent by browser)
const apiHeaders = (extra = {}) => ({
  'X-Requested-With': 'JarvisDashboard',
  ...extra,
});

const now = () => new Date().toLocaleTimeString('en-GB', { hour12: false });
const esc = s => String(s ?? '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

// ── 3D Reactor ticks generation ──
(() => {
  const g = $('#ticks480');
  if (!g) return;
  for (let i = 0; i < 128; i++) {
    const a = (i / 128) * Math.PI * 2;
    const maj = i % 8 === 0;
    const r0 = maj ? 246 : 250, r1 = 260;
    const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    l.setAttribute('x1', 260 + Math.cos(a) * r0);
    l.setAttribute('y1', 260 + Math.sin(a) * r0);
    l.setAttribute('x2', 260 + Math.cos(a) * r1);
    l.setAttribute('y2', 260 + Math.sin(a) * r1);
    if (maj) l.setAttribute('class', 'maj');
    g.appendChild(l);
  }
})();

// ── Reactor state machine ──
function setReactorState(cls, word, sub) {
  document.body.classList.remove('running', 'speaking', 'done', 'error', 'listening');
  if (cls) document.body.classList.add(cls);
  if (word && $('#stword')) $('#stword').textContent = word;
  if (sub != null && $('#strun')) $('#strun').textContent = sub;
}

function setResponseTag(cls, text) {
  const t = $('#rtag');
  if (!t) return;
  t.className = 'rtag ' + (cls || '');
  t.textContent = text || 'IDLE';
}

// ── Telemetry and Action Logging ──
function log(kind, label, msg, extra = '') {
  const e = document.createElement('div');
  e.className = 'entry k-' + kind;
  e.innerHTML = `<div class="top"><span class="ts">${now()}</span><span class="kind">${esc(label)}</span></div>`
    + (msg ? `<div class="msg">${esc(msg)}</div>` : '')
    + (extra ? `<div class="jsonblk">${esc(extra)}</div>` : '');

  const box = $('#log');
  if (box) {
    box.insertBefore(e, box.firstChild);
    while (box.children.length > 50) box.removeChild(box.lastChild);
  }

  // Also duplicate to Audit Log in Activity View
  const auditBox = $('#auditLog');
  if (auditBox) {
    const a = document.createElement('div');
    a.className = 'audit-item';
    a.innerHTML = `<span style="color:var(--dim)">[${now()}]</span> <b>${esc(label)}</b>: ${esc(msg || extra)}`;
    auditBox.insertBefore(a, auditBox.firstChild);
    while (auditBox.children.length > 100) auditBox.removeChild(auditBox.lastChild);
  }
}

// ── Simple Markdown Renderer for Streamed Chat ──
function renderMarkdown(raw) {
  if (!raw) return '';
  let html = esc(raw);

  // Code blocks: ```lang ... ```
  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (m, lang, code) => {
    return `<pre><code class="language-${lang}">${code}</code></pre>`;
  });

  // Inline code: `...`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers: ###, ##, #
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold & Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  html = html.replace(/\*([^*]+)\*/g, '<i>$1</i>');

  // Blockquotes
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

  // Unordered list items
  html = html.replace(/^\• (.*$)/gim, '<li>$1</li>');
  html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');

  // Paragraph breaks
  html = html.replace(/\n\n+/g, '<br><br>');
  html = html.replace(/\n/g, '<br>');

  return html;
}

// ── Clean Text for Voice Synthesis ──
function cleanForSpeech(text) {
  return String(text || '')
    .replace(/\x1b\[[0-9;?]*[A-Za-z]/g, '')
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line && !/^(session_id:|session:|duration:|messages:|query:|initializing agent)/i.test(line))
    .join(' ')
    .replace(/```[\s\S]*?```/g, ' [code omitted] ')
    .replace(/[*_#>`•\-]/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

// ── Audio Speech Synthesis ──
let player = null;
function speak(text) {
  return new Promise(resolve => {
    const cleaned = cleanForSpeech(text);
    if (!STATE.speechEnabled || STATE.muted || !cleaned) return resolve();

    STATE.suppress = true;
    const spoken = cleaned.length > 600 ? cleaned.slice(0, 580) + '…' : cleaned;

    // Use browser TTS if ElevenLabs is unavailable or set
    if (!STATE.tts && speechSynth) {
      try {
        speechSynth.cancel();
        const u = new SpeechSynthesisUtterance(spoken);
        u.rate = 1.0;
        u.pitch = 0.9;
        document.body.classList.add('speaking');
        u.onend = u.onerror = () => {
          document.body.classList.remove('speaking');
          resolve();
        };
        speechSynth.speak(u);
        return;
      } catch (_) {
        return resolve();
      }
    }

    if (!STATE.tts) return resolve();

    fetch('/api/speak', {
      method: 'POST',
      headers: apiHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ text: spoken }),
    })
      .then(r => (r.ok ? r.blob() : Promise.reject()))
      .then(blob => {
        const url = URL.createObjectURL(blob);
        if (player) player.pause();
        player = new Audio(url);
        document.body.classList.add('speaking');
        const done = () => {
          document.body.classList.remove('speaking');
          URL.revokeObjectURL(url);
          resolve();
        };
        player.onended = done;
        player.onerror = done;
        return player.play();
      })
      .catch(() => resolve());
  });
}

// ── Stream Transmission to OpenClaw ──
let activeController = null;
let currentAnswer = '';
let speakDone = Promise.resolve();

async function transmit(message, options = {}) {
  if (!message || !message.trim()) return;
  if (STATE.running) {
    log('note', 'BUSY', `Jarvis is executing an active task. Please wait or abort.`);
    return;
  }

  STATE.running = true;
  currentAnswer = '';
  const speakThisRun = options.speak !== false;

  setReactorState('running', 'THINKING', 'Interfacing with OpenClaw Gateway…');
  setResponseTag('run', 'RUNNING');
  $('#response').innerHTML = '<span class="cur"></span>';
  log('run', 'DIRECTIVE', message.slice(0, 80));

  const t0 = performance.now();
  const tick = setInterval(() => {
    if (!STATE.running) return;
    const s = ((performance.now() - t0) / 1000).toFixed(1);
    if (!currentAnswer && $('#strun')) {
      $('#strun').textContent = `Jarvis Processing… ${s}s`;
    }
  }, 250);

  try {
    activeController = new AbortController();
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: apiHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        message: message.trim(),
        agent_id: STATE.activeAgent,
        session_id: STATE.activeSession,
      }),
      signal: activeController.signal,
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.error || `Server HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let nl;
      while ((nl = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (line) handleEvent(JSON.parse(line));
      }
    }
  } catch (e) {
    if (e?.name === 'AbortError') {
      log('note', 'ABORT', 'Instruction execution halted.');
      setReactorState('', 'STANDBY', 'Operation aborted');
      setResponseTag('', 'IDLE');
    } else {
      log('error', 'FAULT', String(e).slice(0, 200));
      setReactorState('error', 'FAULT', 'OpenClaw error');
      setResponseTag('err', 'ERROR');
      if (!currentAnswer) {
        $('#response').innerHTML = `<span style="color:var(--red)">⚠ ${esc(e.message || 'Execution failed.')}</span>`;
      }
    }
  } finally {
    clearInterval(tick);
    activeController = null;
    STATE.running = false;
    await speakDone;
  }
}

function handleEvent(ev) {
  switch (ev.t) {
    case 'status':
      if (ev.session_id) {
        STATE.activeSession = ev.session_id;
        sys('session', ev.session_id.slice(0, 16) + '…');
      }
      log('status', 'OPENCLAW', `Agent: ${ev.agent_id || 'Jarvis'} · Session: ${ev.session_id || 'new'}`);
      break;

    case 'latency':
      setReactorState('running', 'RESPONDING', `First token in ${ev.ms}ms`);
      log('latency', 'LATENCY', `Inference started in ${ev.ms}ms`);
      break;

    case 'tool':
      log('tool', 'TOOL USE', `${ev.name} [${ev.status || 'running'}]`);
      if ($('#strun')) $('#strun').textContent = `Tool: ${ev.name}`;
      break;

    case 'delta':
      currentAnswer += ev.text;
      renderAnswer();
      break;

    case 'complete':
      setReactorState('done', 'STANDBY', ev.ms != null ? `Finished in ${ev.ms}ms` : 'Completed');
      setResponseTag('done', 'DONE');
      log('complete', 'COMPLETE', `Turn finalized (${ev.ms || 0}ms)`);
      renderAnswer(true);
      speakDone = speak(currentAnswer);
      refreshSessions();
      break;

    case 'error':
      setReactorState('error', 'FAULT', ev.message?.slice(0, 40) || 'Error');
      setResponseTag('err', 'ERROR');
      log('error', 'ERROR', ev.message || 'Unknown error');
      if (!currentAnswer) {
        $('#response').innerHTML = `<span style="color:var(--red)">⚠ ${esc(ev.message || 'Generation error.')}</span>`;
      }
      break;

    case 'note':
      log('note', 'NOTE', ev.message || '');
      break;
  }
}

function renderAnswer(finaldone = false) {
  const el = $('#response');
  if (!el) return;
  el.innerHTML = renderMarkdown(currentAnswer) + (finaldone ? '' : '<span class="cur"></span>');
  el.scrollTop = el.scrollHeight;
}

// ── Voice Conversation Engine ──
let recognition = null;
let micStream = null;
let mediaRecorder = null;
let audioChunks = [];

async function toggleVoice() {
  if (STATE.convo) {
    stopVoice();
    return;
  }

  STATE.convo = true;
  STATE.suppress = false;
  $('#mic').classList.add('on');
  $('#mic').textContent = '● Voice Active';
  setReactorState('listening', 'LISTENING', 'Executive Voice Active');

  if (STATE.stt) {
    // ElevenLabs server-side STT
    try {
      micStream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      });
      startMediaRecording();
    } catch (e) {
      log('error', 'VOICE', 'Microphone permission denied.');
      stopVoice();
    }
  } else if (SpeechRecognition) {
    // Browser Web Speech Recognition
    startBrowserSpeech();
  } else {
    log('error', 'VOICE', 'Speech recognition not supported in this browser.');
    stopVoice();
  }
}

function stopVoice() {
  STATE.convo = false;
  STATE.suppress = false;
  $('#mic').classList.remove('on');
  $('#mic').textContent = '◉ Voice Mode';

  if (recognition) {
    try { recognition.stop(); } catch (_) {}
    recognition = null;
  }
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    try { mediaRecorder.stop(); } catch (_) {}
  }
  if (micStream) {
    micStream.getTracks().forEach(t => t.stop());
    micStream = null;
  }

  setReactorState('', 'STANDBY', 'Awaiting Executive Uplink');
  log('voice', 'VOICE', 'Voice session closed.');
}

function startBrowserSpeech() {
  if (!STATE.convo || STATE.suppress || !SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = true;
  recognition.continuous = false;
  let finalText = '';

  recognition.onresult = e => {
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) finalText += e.results[i][0].transcript;
      else interim += e.results[i][0].transcript;
    }
    const txt = (finalText || interim).trim();
    if (txt && $('#strun')) $('#strun').textContent = 'HEARD: ' + txt.slice(0, 35);
  };

  let fatalError = false;

  recognition.onerror = e => {
    if (e.error === 'no-speech') return;
    
    // Fatal speech recognition errors that shouldn't loop
    if (e.error === 'network' || e.error === 'not-allowed' || e.error === 'service-not-allowed') {
      fatalError = true;
      log('error', 'VOICE', `Browser speech error (${e.error}): Browser cannot reach speech service (common in Brave/Edge or if blocked). Voice mode paused.`);
      stopVoice();
    } else {
      log('error', 'VOICE', `Speech recognition error: ${e.error}`);
    }
  };

  recognition.onend = async () => {
    if (fatalError || !STATE.convo) return;
    const text = finalText.trim();
    if (text) {
      log('voice', 'TRANSCRIPTION', `"${text}"`);
      await transmit(text);
    }
    if (STATE.convo && !STATE.suppress) {
      setTimeout(startBrowserSpeech, 350);
    }
  };

  try {
    recognition.start();
  } catch (_) {}
}

function startMediaRecording() {
  if (!micStream || !STATE.convo || STATE.suppress) return;
  audioChunks = [];

  const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
  mediaRecorder = new MediaRecorder(micStream, { mimeType: mime });

  mediaRecorder.ondataavailable = e => {
    if (e.data?.size > 0) audioChunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    if (!STATE.convo || audioChunks.length === 0) return;
    const blob = new Blob(audioChunks, { type: mime });
    audioChunks = [];

    if (blob.size < 2000) {
      if (STATE.convo && !STATE.suppress) setTimeout(startMediaRecording, 300);
      return;
    }

    setReactorState('running', 'TRANSCRIBING', 'Transcribing audio…');
    try {
      const res = await fetch('/api/listen', {
        method: 'POST',
        headers: apiHeaders({ 'Content-Type': mime }),
        body: blob,
      }).then(r => r.json());

      const text = (res.text || '').trim();
      if (text) {
        log('voice', 'ELEVENLABS', `"${text}"`);
        await transmit(text);
      }
    } catch (e) {
      log('error', 'VOICE', 'Transcription failed.');
    }

    if (STATE.convo && !STATE.suppress) {
      setTimeout(startMediaRecording, 300);
    }
  };

  mediaRecorder.start();
  // Auto slice after 5 seconds of speaking
  setTimeout(() => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      try { mediaRecorder.stop(); } catch (_) {}
    }
  }, 5000);
}

// ── UI Navigation (6 Sections) ──
function switchView(viewName) {
  STATE.activeView = viewName;
  $$('.navtab').forEach(b => b.classList.toggle('active', b.dataset.view === viewName));
  $$('.view').forEach(v => v.classList.toggle('active', v.id === `view-${viewName}`));

  if (viewName === 'agents') loadAgentsGrid();
  if (viewName === 'missions') loadMissionsView();
  if (viewName === 'activity') { refreshSessions(); }
  if (viewName === 'system') refreshSystemDiagnostics();
}

// ── Corporate Agent Discovery & Operations ──
async function refreshAgents() {
  try {
    const res = await fetch('/api/agents', { headers: apiHeaders() }).then(r => r.json());
    if (res.agents) {
      STATE.agents = res.agents;
      populateAgentDropdown();
      if (STATE.activeView === 'agents') loadAgentsGrid();
    }
  } catch (e) {
    log('error', 'AGENTS', 'Could not fetch agent directory from OpenClaw.');
  }
}

function populateAgentDropdown() {
  const sel = $('#agentSelect');
  if (!sel) return;
  sel.innerHTML = '';
  STATE.agents.forEach(a => {
    const opt = document.createElement('option');
    opt.value = a.id;
    opt.textContent = `${a.emoji || '🤖'} ${a.name} (${a.role || a.id})`;
    if (a.id === STATE.activeAgent) opt.selected = true;
    sel.appendChild(opt);
  });
}

function loadAgentsGrid() {
  const divisions = {
    executive: ['main'],
    tech: ['coddy', 'moddy', 'vera'],
    media: ['sniper', 'nova', 'marco'],
    trading: ['vortex', 'dave', 'june', 'kyle'],
  };

  Object.entries(divisions).forEach(([divId, agentIds]) => {
    const container = $(`#agents-${divId}`);
    if (!container) return;
    container.innerHTML = '';

    const divAgents = STATE.agents.filter(a => agentIds.includes(a.id));
    divAgents.forEach(a => {
      const card = document.createElement('div');
      card.className = 'agent-card';
      card.innerHTML = `
        <div class="agent-card-top">
          <div class="agent-avatar">${a.emoji || '🤖'}</div>
          <div class="agent-info">
            <div class="agent-name">${esc(a.name)}</div>
            <div class="agent-id">ID: ${esc(a.id)}</div>
          </div>
        </div>
        <div class="agent-role">${esc(a.role || 'Autonomous Operational Agent')}</div>
        <div class="agent-meta">
          <span>Model: ${esc(a.model ? a.model.split('/').pop() : 'Default')}</span>
          <span>Access: ${esc(a.permission || 'Standard')}</span>
        </div>
        <button class="agent-btn" data-id="${a.id}">Launch Direct Directive</button>
      `;
      container.appendChild(card);
    });
  });

  // Attach click handler to agent launch buttons
  $$('.agent-btn').forEach(btn => {
    btn.onclick = () => {
      const aid = btn.dataset.id;
      STATE.activeAgent = aid;
      if ($('#agentSelect')) $('#agentSelect').value = aid;
      sys('agent', aid);
      switchView('chat');
      $('#input').focus();
      log('command', 'ROUTING', `Direct channel aligned with agent: ${aid}`);
    };
  });
}

// ── Mission Control Functions ──
async function loadMissionsView() {
  try {
    const res = await fetch('/api/missions', { headers: apiHeaders() }).then(r => r.json());
    STATE.goals = res.goal || '';
    STATE.tasks = res.tasks || [];

    if ($('#goalInput')) $('#goalInput').value = STATE.goals;

    const taskList = $('#taskList');
    if (taskList) {
      if (!STATE.tasks || STATE.tasks.length === 0) {
        taskList.innerHTML = '<div class="empty-state">Mission queue is clear. No pending items.</div>';
      } else {
        taskList.innerHTML = STATE.tasks.map((t, i) => `
          <div class="task-item ${t.done ? 'done' : ''}">
            <input type="checkbox" class="toggle-task" data-index="${i}" ${t.done ? 'checked' : ''}>
            <div class="task-text">${esc(t.text)}</div>
          </div>
        `).join('');
      }
    }
  } catch (e) {
    log('error', 'MISSIONS', 'Failed to load mission telemetry.');
  }
}

// ── Session Index & Switching ──
async function refreshSessions() {
  try {
    const res = await fetch('/api/sessions', { headers: apiHeaders() }).then(r => r.json());
    STATE.sessions = res.sessions || [];
    const container = $('#sessionsList');
    if (!container) return;

    if (STATE.sessions.length === 0) {
      container.innerHTML = '<div class="empty-state">No Gateway sessions found.</div>';
      return;
    }

    container.innerHTML = STATE.sessions.map(s => {
      const isCur = s.key === STATE.activeSession;
      return `
        <div class="session-item ${isCur ? 'active' : ''}" data-key="${s.key}" data-agent="${s.agent_id}">
          <div class="session-key">${esc(s.key)}</div>
          <div class="session-sub">
            <span>Agent: ${esc(s.agent_id)}</span>
            <span>${s.active ? '● Active' : 'Idle'}</span>
          </div>
        </div>
      `;
    }).join('');

    $$('.session-item').forEach(item => {
      item.onclick = () => {
        STATE.activeSession = item.dataset.key;
        STATE.activeAgent = item.dataset.agent;
        if ($('#agentSelect')) $('#agentSelect').value = STATE.activeAgent;
        sys('session', STATE.activeSession.slice(0, 16) + '…');
        sys('agent', STATE.activeAgent);
        switchView('chat');
        log('note', 'SESSION', `Resumed session ${STATE.activeSession}`);
      };
    });
  } catch (e) {
    log('error', 'SESSIONS', 'Failed to retrieve sessions list.');
  }
}

// ── System Diagnostics ──
async function refreshSystemDiagnostics() {
  try {
    const s = await fetch('/api/status').then(r => r.json());
    if ($('#diag-status')) $('#diag-status').textContent = s.gateway?.connected ? 'ONLINE' : 'OFFLINE';
    if ($('#diag-version')) $('#diag-version').textContent = `v${s.gateway?.version || '2026.11.3'}`;
    if ($('#diag-uptime')) $('#diag-uptime').textContent = `Uptime: ${s.gateway?.uptime || 0}s`;
    if ($('#diag-agentcount')) $('#diag-agentcount').textContent = `${STATE.agents.length || 11} Agents`;
  } catch (e) {
    log('error', 'DIAGNOSTICS', 'Could not refresh system telemetry.');
  }
}

// ── UI Helpers ──
function sys(id, val, cls) {
  const el = $('#sy-' + id);
  if (!el) return;
  el.textContent = val;
  if (cls != null) el.className = cls;
}

function sendInput() {
  const raw = $('#input').value.trim();
  const armed = $('#input').dataset.cmd || '';
  if (!raw && !armed) return;

  const full = (armed && !raw.startsWith('/')) ? `${armed} ${raw}` : (raw || armed);
  $('#input').value = '';
  disarm();
  transmit(full);
}

function disarm() {
  $$('.cmd').forEach(c => c.classList.remove('armed'));
  if ($('#input')) $('#input').dataset.cmd = '';
}

// ── Event Handlers & Initialization ──
function initEvents() {
  // Navigation tabs
  $$('.navtab').forEach(b => {
    b.onclick = () => switchView(b.dataset.view);
  });

  // Transmit button & Enter key
  $('#run').onclick = sendInput;
  $('#input').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      sendInput();
    }
  });

  // Mic toggle
  $('#mic').onclick = toggleVoice;

  // New Chat session
  $('#btnNew').onclick = async () => {
    try {
      const res = await fetch('/api/new', {
        method: 'POST',
        headers: apiHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ agent_id: STATE.activeAgent }),
      }).then(r => r.json());

      if (res.session_id) {
        STATE.activeSession = res.session_id;
        sys('session', STATE.activeSession.slice(0, 16) + '…');
        $('#response').innerHTML = '<span class="rplaceholder">Fresh OpenClaw session initiated with Jarvis. Standing by.</span>';
        log('note', 'NEW SESSION', `Initialized ${res.session_id}`);
      }
    } catch (e) {
      log('error', 'SESSION', 'Failed to create new session.');
    }
  };

  // Abort execution
  $('#btnCancel').onclick = () => {
    if (activeController) activeController.abort();
    fetch('/api/cancel', {
      method: 'POST',
      headers: apiHeaders({ 'Content-Type': 'application/json' }),
      body: '{}',
    }).catch(() => {});
  };

  // Clear display
  $('#clearBtn').onclick = () => {
    currentAnswer = '';
    $('#response').innerHTML = '<span class="rplaceholder">Display cleared. OpenClaw session maintained.</span>';
    setResponseTag('', 'IDLE');
  };

  // Copy response
  $('#btnCopy').onclick = () => {
    if (currentAnswer) {
      navigator.clipboard.writeText(currentAnswer);
      $('#btnCopy').textContent = 'Copied!';
      setTimeout(() => { $('#btnCopy').textContent = 'Copy'; }, 1500);
    }
  };

  // Mute audio
  $('#mute').onclick = () => {
    STATE.muted = !STATE.muted;
    $('#mute').textContent = STATE.muted ? '🔇' : '🔊';
    $('#mute').classList.toggle('on', !STATE.muted);
    $('#mute').classList.toggle('off', STATE.muted);
    if (STATE.muted && player) player.pause();
  };

  // Command Matrix buttons
  const PAYLOAD_COMMANDS = new Set(['/goal', '/browser', '/background', '/mission']);
  $('#cmds').addEventListener('click', e => {
    const b = e.target.closest('.cmd');
    if (!b) return;
    const cmd = b.dataset.cmd;

    disarm();
    if (PAYLOAD_COMMANDS.has(cmd)) {
      b.classList.add('armed');
      $('#input').dataset.cmd = cmd;
      $('#input').focus();
    }
    transmit(cmd, { speak: !['/status', '/agents', '/sessions'].includes(cmd) });
  });

  // Quick directive buttons
  $$('[data-quick]').forEach(b => {
    b.onclick = () => transmit(b.dataset.quick, { speak: false });
  });

  // Agent dropdown change
  $('#agentSelect').addEventListener('change', e => {
    STATE.activeAgent = e.target.value;
    sys('agent', STATE.activeAgent);
    log('note', 'ROUTING', `Target agent aligned to: ${STATE.activeAgent}`);
  });

  // Mission control actions
  const saveGoalBtn = $('#btnSaveGoal');
  if (saveGoalBtn) {
    saveGoalBtn.onclick = () => {
      const g = $('#goalInput').value.trim();
      transmit(`/goal ${g}`);
    };
  }
  const clearGoalBtn = $('#btnClearGoal');
  if (clearGoalBtn) {
    clearGoalBtn.onclick = () => transmit('/goal clear');
  }
  const addTaskBtn = $('#btnAddTask');
  if (addTaskBtn) {
    addTaskBtn.onclick = () => {
      const t = $('#newTaskInput').value.trim();
      if (t) {
        transmit(`/mission ${t}`);
        $('#newTaskInput').value = '';
      }
    };
  }

  // Refresh buttons
  const refAgents = $('#btnRefreshAgents');
  if (refAgents) refAgents.onclick = refreshAgents;
  const refHealth = $('#btnRefreshHealth');
  if (refHealth) refHealth.onclick = refreshSystemDiagnostics;

  // Settings toggles
  const speechToggle = $('#settingSpeechEnabled');
  if (speechToggle) {
    speechToggle.onchange = e => { STATE.speechEnabled = e.target.checked; };
  }
  const motionToggle = $('#settingReducedMotion');
  if (motionToggle) {
    motionToggle.onchange = e => {
      document.body.classList.toggle('reduced-motion', e.target.checked);
    };
  }
  const resetBtn = $('#btnResetSession');
  if (resetBtn) {
    resetBtn.onclick = () => {
      $('#btnNew').click();
      switchView('chat');
    };
  }

  // Keyboard shortcut Esc
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (STATE.running && activeController) {
        activeController.abort();
      }
      if (STATE.convo) stopVoice();
    }
  });

  // Clock
  setInterval(() => sys('clock', now()), 1000);

  // Poll gateway status every 4 seconds
  setInterval(async () => {
    try {
      const s = await fetch('/api/status', { headers: apiHeaders() }).then(r => r.json());
      const gwOk = s.gateway?.connected;
      sys('gw', gwOk ? 'Connected' : 'Offline', gwOk ? 'ok' : 'warn');
      if ($('#top-gw')) $('#top-gw').textContent = `Gateway: ${gwOk ? 'Online' : 'Offline'}`;
      if ($('#pill-gw')) $('#pill-gw').className = 'pill ' + (gwOk ? 'ok' : 'warn');

      // If gateway just reconnected, discover agents and sessions
      if (gwOk && STATE.agents.length === 0) {
        refreshAgents();
        refreshSessions();
      }
    } catch (_) {}
  }, 4000);

  // Poll for background mission completions
  setInterval(async () => {
    try {
      const j = await fetch('/api/jobs', { headers: apiHeaders() }).then(r => r.json());
      for (const d of (j.done || [])) {
        log('complete', 'BACKGROUND MISSION', `${d.mission} → ${(d.result || '').slice(0, 160)}`);
        if (!STATE.running && STATE.speechEnabled) {
          speak(`Mission complete: ${(d.result || '').slice(0, 200)}`);
        }
      }
    } catch (_) {}
  }, 4000);
}

// ── Boot Sequence ──
(async () => {
  initEvents();
  try {
    const s = await fetch('/api/status').then(r => r.json());
    STATE.stt = s.voice?.available;
    STATE.tts = s.voice?.available;

    const gwOk = s.gateway?.connected;
    sys('gw', gwOk ? 'Connected' : 'Offline', gwOk ? 'ok' : 'warn');
    sys('brain', 'OpenClaw Gateway', 'ok');
    sys('agent', 'Jarvis (COO)');
    sys('voice', STATE.stt ? 'ElevenLabs' : 'Browser Speech');

    $('#top-gw').textContent = `Gateway: ${gwOk ? 'Online' : 'Offline'}`;
    $('#pill-gw').className = 'pill ' + (gwOk ? 'ok' : 'warn');

    $('#top-voice').textContent = `Voice: ${STATE.stt ? 'ElevenLabs' : 'Browser'}`;
    $('#top-agent').textContent = 'Agent: Jarvis (COO)';

    if (gwOk) {
      log('status', 'BOOT', `JARVIS Command Center initialized · Connected to OpenClaw Gateway (${s.gateway?.version || 'v4'})`);
      setReactorState('', 'STANDBY', 'Ready for Executive Uplink');
    } else {
      log('note', 'BOOT', 'JARVIS Command Center initialized · Awaiting OpenClaw Gateway connection (Gateway is updating)...');
      setReactorState('', 'WAITING', 'Awaiting OpenClaw Gateway (Updating)');
    }

    // Discover agents from OpenClaw
    await refreshAgents();
    await refreshSessions();
  } catch (e) {
    sys('gw', 'Offline', 'warn');
    log('error', 'BOOT', 'Could not establish connection to local backend.');
  }
})();

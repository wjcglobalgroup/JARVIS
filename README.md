# WJC GLOBAL GROUP — JARVIS COMMAND CENTER

[![Repository](https://img.shields.io/badge/GitHub-wjcglobalgroup%2FJARVIS-cyan.svg)](https://github.com/wjcglobalgroup/JARVIS)
[![Architecture](https://img.shields.io/badge/Architecture-OpenClaw%20Gateway%20Native%20v4-blue.svg)](#architecture)
[![Executive](https://img.shields.io/badge/Principal-Willy%20%7C%20Chairman%20%26%20CEO-gold.svg)](#executive-roster)
[![Main Agent](https://img.shields.io/badge/COO-Jarvis%20%28agentId%3A%20main%29-teal.svg)](#verified-corporate-agent-directory)

An enterprise-grade executive AI command center for **WJC GLOBAL GROUP**, powered by a direct, native integration with the **OpenClaw Gateway (Protocol v4 over WebSocket)**.

- **Principal / Owner:** Willy — Chairman & CEO, WJC GLOBAL GROUP
- **Chief AI Operating Officer:** Jarvis (`main`) — Group COO
- **Official Repository:** [https://github.com/wjcglobalgroup/JARVIS](https://github.com/wjcglobalgroup/JARVIS)
- **Local Console:** [http://127.0.0.1:8730](http://127.0.0.1:8730) (IPv4/IPv6 Dual-Stack)

---

## 1. Executive Architecture

The Command Center connects directly to the OpenClaw Gateway runtime over WebSocket (Protocol v4) with full operator credentials, session persistence, and real-time token streaming:

```
┌─────────────────────────────────────────────────────────────┐
│                    WJC GLOBAL GROUP                         │
│                 JARVIS COMMAND CENTER                       │
├─────────────────────────────────────────────────────────────┤
│  Executive HUD: Chat · Agents · Missions · Telemetry        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / NDJSON Event Stream
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   DASHBOARD BACKEND                         │
│          server.py · runtime.py · commands.py               │
│         HttpOnly Cookie Auth & Host/CSRF Validation         │
└──────────────────────────────┬──────────────────────────────┘
                               │ WebSocket (Protocol v4)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  OPENCLAW GATEWAY (18789)                   │
│          Handshake · Operator Scopes · Tool Events          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Agent Routing
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  JARVIS (Group COO - 'main')                │
│  Corporate Divisions:                                       │
│  • Executive Office: Jarvis                                 │
│  • Technology & Automation: Coddy, Moddy, Vera              │
│  • STZ Crypto Media & OFW Media: Sniper, Nova, Marco        │
│  • Trading, Investment & Mobility: Vortex, Dave, June, Kyle │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Capabilities

- **100% Native OpenClaw Protocol v4**: Direct, persistent WebSocket integration to the local OpenClaw Gateway on port 18789.
- **Standalone Windows Background Service**: Configured to run independently in the Windows background via the user Startup folder (`shell:startup`) and desktop shortcuts. Fully isolated from external terminal sessions.
- **Real-Time Streaming Chat**: Live executive response streaming with token delivery, latency metrics, tool execution feedback, and session continuity.
- **Enterprise Workforce Directory**: Dynamic discovery of 11 verified corporate agents categorized into 5 operational divisions.
- **Executive Mission Control**: Real-time management of standing corporate objectives, prioritized mission queue, and asynchronous background operations.
- **Dynamic 3D Reactor HUD**: Real-time SVG visualizer reflecting live operational states (`STANDBY`, `LISTENING`, `THINKING`, `RESPONDING`, `OFFLINE`, and `ERROR`).
- **Continuous Voice Briefing**: Hands-free executive voice conversation supporting server-side ElevenLabs or local browser Web Speech API.
- **Security Hardened**:
  - OpenClaw Gateway credentials remain strictly isolated server-side.
  - Zero token exposure in DOM, meta tags, or client-side storage.
  - SameSite HttpOnly session cookie authentication.
  - Dual-stack IPv4/IPv6 support (`::` and `127.0.0.1`).

---

## 3. Verified Corporate Agent Directory

| Division | Agent Name | Agent ID | Corporate Role |
| :--- | :--- | :--- | :--- |
| **Executive Office** | **Jarvis** | `main` | **Group Chief Operating Officer (COO)** |
| **Technology & Automation** | **Coddy** | `coddy` | Chief Automation Architect |
| | **Moddy** | `moddy` | System Integration Specialist |
| | **Vera** | `vera` | Security & Compliance Auditor |
| **STZ Crypto Media** | **Sniper** | `sniper` | Market Intelligence & Crypto Editor |
| | **Nova** | `nova` | Digital Content Strategist |
| **OFW Digital Media** | **Marco** | `marco` | Community & Media Coordinator |
| **Trading & Investment** | **Vortex** | `vortex` | Algorithmic Trading Strategist |
| | **Dave** | `dave` | Portfolio & Risk Analyst |
| | **June** | `june` | Financial Data Operations |
| **KYLEXINE Traveler** | **Kyle** | `kyle` | Mobility & Logistics Director |

---

## 4. Operation & Management

### Launching the Dashboard

#### Option A: Windows Background Service (Automatic)
The service automatically boots on Windows login via:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\JarvisCommandCenter.vbs
```

#### Option B: Desktop Shortcuts
* **`Start JARVIS Dashboard.bat`** — Launches the background server and opens your browser.
* **`Stop JARVIS Dashboard.bat`** — Terminates the active server instance.

#### Option C: Manual Command Line
```cmd
cd /d "C:\Javis Command Center\jarvis-command-center"
start.bat
```

Access the web interface at **[http://localhost:8730](http://localhost:8730)**.

---

## 5. Configuration (`.env`)

```ini
# Dashboard Web Server
JARVIS_HOST=127.0.0.1
JARVIS_PORT=8730
JARVIS_OPEN=1

# OpenClaw Gateway Integration
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:18789

# Gateway Operator Token (Auto-discovered from ~/.openclaw/openclaw.json if empty)
OPENCLAW_GATEWAY_TOKEN=

# Default Agent ID
OPENCLAW_DEFAULT_AGENT=main

# Optional Voice (ElevenLabs TTS/STT)
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_turbo_v2_5
```

---

## 6. Executive Slash Commands

| Command | Action |
| :--- | :--- |
| `/new` | Initialize a fresh OpenClaw session with Jarvis |
| `/agents` | List verified corporate agents and operational divisions |
| `/sessions` | Display active and recent Gateway sessions |
| `/status` | View OpenClaw Gateway health, server version, and uptime |
| `/goal <text>` | Set, review, or clear the standing executive objective |
| `/mission [task]` | Add directives to the mission queue or inspect pending tasks |
| `/background <mission>` | Launch an asynchronous background mission through OpenClaw |
| `/browser <task>` | Instruct Jarvis to execute browser automation |
| `/personality <tone>` | Adjust Jarvis executive tone overlay |
| `/clear` | Clear the display console (retains OpenClaw session) |
| `/help` | Show executive command reference |

---

## 7. Security Architecture

1. **Token Isolation**: The OpenClaw Gateway token is kept strictly in server memory. It is never transmitted to the browser or placed in HTML meta tags.
2. **HttpOnly Session Cookies**: Browser requests authenticate via an `HttpOnly`, `SameSite=Lax` cookie generated upon serving `index.html`.
3. **No Shell Injections**: User-configurable goals and mission text are bounded and sanitized before inclusion into agent prompts.
4. **Host & Origin Validation**: The backend checks `Host` and `Origin` headers to prevent cross-site websocket and DNS rebinding attacks.

---

## 8. License

Proprietary — Executive Office of Willy, Chairman & CEO, **WJC GLOBAL GROUP**. All rights reserved.

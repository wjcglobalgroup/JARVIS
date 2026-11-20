# WJC GLOBAL — JARVIS COMMAND CENTER

[![Repository](https://img.shields.io/badge/GitHub-wjcglobalgroup%2FJARVIS-cyan.svg)](https://github.com/wjcglobalgroup/JARVIS)
[![Architecture](https://img.shields.io/badge/Architecture-OpenClaw%20Gateway%20Native%20v4-blue.svg)](#architecture)
[![Executive](https://img.shields.io/badge/Principal-Willy%20%7C%20Chairman%20%26%20CEO-gold.svg)](#leadership-and-command)

The executive command center for **WJC GLOBAL**, powered by a direct integration with the **OpenClaw Gateway (Protocol v4 over WebSocket)**.

- **Chairman & CEO:** Willy — owner and final executive authority.
- **COO:** Jarvis (`main`) — coordinates daily operations across WJC Global's divisions and agent teams.
- **Repository:** [wjcglobalgroup/JARVIS](https://github.com/wjcglobalgroup/JARVIS)
- **Local Console:** [http://127.0.0.1:8730](http://127.0.0.1:8730)

> **Roster accuracy:** This README documents the intended organizational responsibilities. Agent IDs shown below are the configured/conventional IDs currently documented for known agents; the Kaixin Transport agents are documented as existing team members; live runtime presence and connectivity should still be verified separately.

---

## 1. Leadership and Command

| Person / Agent | Title | Accountability |
| :--- | :--- | :--- |
| **Willy** | **Chairman & CEO** | Sets WJC Global's direction, approves strategic decisions, and retains final authority over business-critical actions. |
| **Jarvis** (`main`) | **Chief Operating Officer (COO)** | Coordinates daily execution across divisions, assigns work to specialist agents, tracks handoffs and blockers, and reports operational outcomes to the Chairman. |

Jarvis is WJC Global's operational coordinator—not the owner and not a replacement for the specialist agents. Each specialist remains responsible for its assigned function. Jarvis coordinates priorities, dependencies, and cross-division execution.

---

## 2. Corporate Structure and Agent Directory

### Executive Office

| Agent | Agent ID | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Jarvis** | `main` | **COO** | Daily WJC Global operations; agent coordination; mission delegation; cross-division follow-up; escalation of blockers; executive reporting to Willy. |

### Technology & Automation

| Agent | Agent ID | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Coddy** | `coddy` | **Development Engineer** | Software engineering, application development, debugging, integrations, infrastructure automation, and technical implementation. Jarvis coordinates priorities and delivery. |

### STZ Crypto Media

| Agent | Agent ID | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |

| **Vera** | `vera` | **STZ Crypto Content Scriptwriter** | Converts approved Notion briefs and, where relevant, Marco's market/macro research supplied from the Trading & Investment division into publish-ready scripts. Maintains the script handoff in Notion. Vera is a writing role: she does not generate videos or images and does not own the Google Drive production workflow. |
| **Vortex** | `vortex` | **STZ Video & Visual Production Editor** | Retrieves Vera's approved Notion scripts, produces video and image assets, uses Google Flow for video generation, manages production assets in Google Drive, and hands final deliverables to Moddy. |
| **Moddy** | `moddy` | **STZ Social Media Operations Manager** | Owns publishing operations and community management for STZ; prepares and publishes approved content, monitors platform activity, manages comments/community workflows, and reports publishing results. |

**STZ production handoff**

```text
Vera (scriptwriting + Notion handoff)
        |
        v
Vortex (video/image production + Drive assets)
        |
        v
Moddy (publishing + community operations)
```

- **Script ownership:** Vera.
- **Video and visual production ownership:** Vortex.
- **Publishing and community ownership:** Moddy.
- **Publishing authorization:** Moddy must follow the owner's approval requirements. Default permission is read/draft; publishing requires explicit authorization for the relevant platform, account, operation, and content. A connected account is not, by itself, permission to publish.

**Integration boundaries (STZ):**
- Vera's workflow is Notion-based; she is not the Drive production operator. Her STZ script briefs must use approved STZ research inputs.
- Vortex uses Notion for approved scripts and Google Drive for production assets. Google Flow is the designated video-generation workflow.
- Moddy's intended Composio-connected publishing/operations apps are Facebook Page, YouTube, Instagram, Google Drive, and Google Calendar. Binance Square is connected directly through its API; Notion is accessed through the OpenClaw Notion MCP integration. Actual availability and permissions must be checked in the running environment.

### Trading & Investment

| Agent | Agent ID | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Marco** | `marco` | **Trading Macro & Market Intelligence Analyst** | Monitors macroeconomic conditions and crypto-market intelligence; produces the macro-gate assessment used by the trading operation; sends actionable macro context and gate results to the designated trading Discord channel; supports Sniper's market decisions. Marco belongs to Trading & Investment, not STZ Crypto Media. |
| **Sniper** | `sniper` | **SMC Crypto Trader** | Scans crypto markets for deterministic Smart Money Concepts (SMC) setups; evaluates market structure, liquidity sweeps, market structure shifts, order blocks, entries, and risk; uses LLM interpretation after a potential setup is found; executes only when configured trading and risk gates permit; monitors open positions and trade management rules. |

**Trading team responsibilities:** Marco owns macro research and the macro-environment gate; Sniper owns SMC setup detection, trade evaluation, execution logic, and open-position management. Marco's macro assessment informs the trading workflow but does not replace Sniper's deterministic setup and risk checks.

Sniper is the execution-focused trading specialist—not a media editor. Trading execution must remain subject to explicit account configuration, risk controls, and the owner's authorization. A detected setup is not a guarantee of profit.

### OFW Media

| Agent | Agent ID | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Nova** | `nova` | **OFW Media Scriptwriter** | Develops OFW-focused content ideas and scripts for the media production pipeline. |
| **Dave** | `dave` | **OFW Media Video Editor** | Produces and edits video assets from Nova's approved scripts and prepares final media deliverables for publishing. |
| **June** | `june` | **OFW Media Publisher & Social Media Manager** | Schedules and publishes approved OFW content, manages social media operations, and reports publishing outcomes. |

**OFW production handoff**

```text
Nova (script)
   |
   v
Dave (video production and QA)
   |
   v
June (publishing and social media operations)
```

### Kaixin Transport

**Business / Content Niche:** Uber-style van rental and travel tourism, featuring a branded avatar/vlogger-driver who showcases Luzon tourist destinations and promotes Kaixin Transport's van rental services.

**Team Status:** Existing team. Ethan, Axel, and Kyle are established members of the Kaixin Transport team.

| Agent | Agent ID | Status | Official Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **Ethan** | `ethan` | **Existing** | **Scriptwriter** | Writes scripts for the Kaixin Transport niche, including Luzon destination features, travel storytelling, van-rental promotions, and avatar/vlogger-driver video concepts. |
| **Axel** | `axel` | **Existing** | **Video Editor** | Edits and produces Kaixin Transport videos, including avatar/vlogger-driver content, destination features, and promotional videos. |
| **Kyle** | `kyle` | **Existing** | **Social Media, Publishing & Marketing Manager** | Publishes approved content on the Kaixin Transport Facebook Page; looks for and attracts potential passengers and rental clients; monitors and answers comments; responds to Facebook DMs and inquiries; handles initial customer engagement and helps convert inquiries into potential bookings. Kyle also supports existing van-rental customer-service and reservation inquiries. |

**Kaixin content workflow:** Ethan (scriptwriting) → Axel (video editing/production) → Kyle (publishing, audience engagement, lead generation, comments and DM inquiries).

**Business concept:** Kaixin Transport offers Uber-style van rental with a driver. Content will use a branded avatar/vlogger-driver to feature Luzon tourism destinations and introduce potential passengers to the service.

**Team note:** Ethan, Axel, and Kyle are existing Kaixin Transport team members. Their responsibilities and handoffs are documented above; live runtime availability should be checked in OpenClaw.

### Discord agent routing

The sanitized OpenClaw configuration snapshot on the `master` branch defines 11 agents and 11 Discord accounts, with 22 explicit route bindings: one Discord account-ID match and one channel-peer match for each agent. All bindings target configured agent IDs, every configured Discord account has an account route, and the saved snapshot contains no duplicate account or channel-peer matches. This validates the stored routing map only; it does not confirm live bot connectivity, Discord permissions, or end-to-end message delivery.

```text
┌─────────────────────────────────────────────────────────────┐
│                       WJC GLOBAL                            │
│                 JARVIS COMMAND CENTER                       │
│          Chat · Agents · Missions · Telemetry                │
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
│                       JARVIS — COO                          │
│       Coordinates WJC GLOBAL specialist teams     │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Core Capabilities

- **Native OpenClaw Protocol v4:** Direct WebSocket integration with the local OpenClaw Gateway on port 18789.
- **Windows Background Service:** Supports background startup and desktop shortcuts.
- **Real-Time Streaming Chat:** Executive chat with streaming responses and session continuity.
- **Workforce Directory:** Presents WJC Global's organizational agent roster and role boundaries. Runtime presence should be verified separately.
- **Executive Mission Control:** Management of objectives, mission queues, and background operations.
- **Operational Telemetry:** Displays agent and system operational states where available.
- **Voice Briefing:** Supports configured server-side ElevenLabs or browser Web Speech API voice features.
- **Security Controls:** Keeps Gateway credentials server-side and uses authenticated sessions and request validation.

---

## 6. Operation & Management

### Launching the Dashboard

#### Option A: Windows Background Service

The service can be configured to start on Windows login through:

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\JarvisCommandCenter.vbs
```

#### Option B: Desktop Shortcuts

- **Start JARVIS Dashboard.bat** — launches the background server and opens the browser.
- **Stop JARVIS Dashboard.bat** — terminates the active server instance.

#### Option C: Manual Command Line

```cmd
cd /d "C:\Javis Command Center\jarvis-command-center"
start.bat
```

Open the web interface at **[http://localhost:8730](http://localhost:8730)**.

---

## 7. Configuration (`.env`)

```ini
# Dashboard Web Server
JARVIS_HOST=127.0.0.1
JARVIS_PORT=8730
JARVIS_OPEN=1

# OpenClaw Gateway Integration
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:18789

# Gateway Operator Token (auto-discovered from ~/.openclaw/openclaw.json if empty)
OPENCLAW_GATEWAY_TOKEN=

# Default Agent ID
OPENCLAW_DEFAULT_AGENT=main

# Optional Voice (ElevenLabs TTS/STT)
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_turbo_v2_5
```

---

## 8. Executive Slash Commands

| Command | Action |
| :--- | :--- |
| `/new` | Initialize a fresh OpenClaw session with Jarvis |
| `/agents` | List agents and operational divisions |
| `/sessions` | Display active and recent Gateway sessions |
| `/status` | View Gateway health, server version, and uptime |
| `/goal <text>` | Set, review, or clear the standing executive objective |
| `/mission [task]` | Add directives to the mission queue or inspect pending tasks |
| `/background <mission>` | Launch an asynchronous background mission |
| `/browser <task>` | Instruct Jarvis to execute browser automation |
| `/personality <tone>` | Adjust Jarvis's tone overlay |
| `/clear` | Clear the display console while retaining the OpenClaw session |
| `/help` | Show the command reference |

---

## 9. Security Architecture

1. **Token Isolation:** The OpenClaw Gateway token remains server-side and is not sent to the browser.
2. **HttpOnly Session Cookies:** Browser requests use an `HttpOnly`, `SameSite=Lax` session cookie.
3. **Input Handling:** User-configurable goals and mission text are bounded and sanitized before prompt use.
4. **Host & Origin Validation:** The backend validates request origin and host to mitigate cross-site and DNS-rebinding risks.
5. **Operational Authorization:** Publishing and other consequential external actions require the applicable authorization; connected credentials alone are not approval.

---

## 10. License

Proprietary — Executive Office of Willy, Chairman & CEO, **WJC GLOBAL**. All rights reserved.

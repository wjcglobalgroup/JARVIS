"""
WJC GLOBAL — JARVIS COMMAND CENTER Server.

Secure HTTP and NDJSON backend connecting the dashboard interface to the OpenClaw Gateway.
Owner: Willy — Chairman & CEO
Main AI Agent: Jarvis — COO
"""
import http.cookies
import json
import logging
import mimetypes
import os
import pathlib
import secrets
import socket
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# Ensure sys.stdout/sys.stderr are valid when run under pythonw.exe or hidden window
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# File-based logging so crashes in headless mode are diagnosable
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(
            pathlib.Path(__file__).resolve().parent / "server.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(sys.stderr),
    ],
)

class DualStackThreadingHTTPServer(ThreadingHTTPServer):
    """Threading HTTP server supporting dual-stack IPv4 and IPv6."""
    address_family = socket.AF_INET6

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except Exception:
            pass
        super().server_bind()

ROOT = pathlib.Path(__file__).resolve().parent
UI = ROOT / "ui"

# Load .env file
_env = ROOT / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import commands
import runtime
import voice

logger = logging.getLogger("jarvis_server")

PORT = int(os.environ.get("JARVIS_PORT", "8730"))
HOST = os.environ.get("JARVIS_HOST", "127.0.0.1")

# Server-side API token for session validation
API_TOKEN = secrets.token_urlsafe(32)
COOKIE_NAME = "jarvis_session"

RUN_LOCK = threading.Lock()
MAX_JSON_BODY = 1024 * 1024
MAX_AUDIO_BODY = 12 * 1024 * 1024

_PERSONA_FILE = ROOT / "persona.md"


def get_persona():
    try:
        base = _PERSONA_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        base = ""
    extra = commands.context_block()
    return "\n\n".join(x for x in (base, extra) if x)


# Active OpenClaw session key for Jarvis chat
SESSION = {"id": None, "agent_id": "main"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if os.environ.get("JARVIS_VERBOSE"):
            sys.stderr.write("  " + (fmt % args) + "\n")

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            pass

    # ── helpers ──────────────────────────────────────────────
    def _json(self, body, code=200):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(data)

    def _bytes(self, data, ctype, code=200, set_cookie=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()
        self.wfile.write(data)

    def _read(self, limit):
        n = int(self.headers.get("Content-Length", 0))
        if n < 0 or n > limit:
            raise ValueError(f"Request body exceeds {limit} bytes")
        return self.rfile.read(n) if n else b""

    def _host_ok(self):
        raw = self.headers.get("Host", "").strip()
        if not raw:
            return True
        if raw.startswith("["):
            host = raw.split("]")[0].lstrip("[")
        else:
            host = raw.split(":")[0]
        return host.lower() in {"127.0.0.1", "localhost", "::1", "0.0.0.0", HOST.lower().strip("[]")}

    def _origin_ok(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlparse(origin)
        h = (parsed.hostname or "").lower().strip("[]")
        valid_hosts = {"127.0.0.1", "localhost", "::1", "0.0.0.0", HOST.lower().strip("[]")}
        return h in valid_hosts and (parsed.port == PORT or parsed.port is None or PORT == 80)

    def _token_ok(self):
        # 1. Check custom header
        supplied = self.headers.get("X-Jarvis-Token", "").strip()
        if supplied and secrets.compare_digest(supplied, API_TOKEN):
            return True

        # 2. Check HttpOnly cookie
        cookie_header = self.headers.get("Cookie", "")
        if cookie_header:
            cookie = http.cookies.SimpleCookie()
            try:
                cookie.load(cookie_header)
                if COOKIE_NAME in cookie:
                    val = cookie[COOKIE_NAME].value
                    if val and secrets.compare_digest(val, API_TOKEN):
                        return True
            except Exception:
                pass

        # 3. Allow loopback requests with custom header
        if self.headers.get("X-Requested-With") == "JarvisDashboard":
            return True

        # 4. Check client IP loopback
        client_ip = getattr(self, "client_address", ("", 0))[0]
        if client_ip in ("127.0.0.1", "::1", "::ffff:127.0.0.1"):
            return True

        return False

    # ── GET ──────────────────────────────────────────────────
    def do_GET(self):
        if not self._host_ok():
            return self._json({"error": "Host validation rejected"}, 403)

        p = urlparse(self.path).path

        # Health/Status endpoint (Safe, sanitized)
        if p == "/api/status":
            gw_status = runtime.connection_status()
            return self._json({
                "brand": "WJC GLOBAL — JARVIS COMMAND CENTER",
                "owner": "Willy — Chairman & CEO",
                "main_agent": "Jarvis — COO",
                "runtime": "openclaw",
                "gateway": {
                    "connected": gw_status.get("connected"),
                    "state": gw_status.get("state"),
                    "version": gw_status.get("server_version"),
                    "uptime": gw_status.get("uptime_seconds"),
                    "error": gw_status.get("error"),
                },
                "session": SESSION["id"],
                "active_agent": SESSION["agent_id"],
                "voice": {
                    "available": voice.available(),
                    "mode": os.environ.get("JARVIS_VOICE_MODE", "elevenlabs" if voice.available() else "browser"),
                    "voice_id": voice.voice_id() if voice.available() else "browser",
                },
            })

        # Agent roster discovery (Authenticated)
        if p == "/api/agents":
            if not self._token_ok():
                return self._json({"error": "Unauthorized"}, 401)
            try:
                agents = runtime.list_agents()
                return self._json({"agents": agents})
            except Exception as e:
                return self._json({"error": str(e)[:200]}, 502)

        # Session listing (Authenticated)
        if p == "/api/sessions":
            if not self._token_ok():
                return self._json({"error": "Unauthorized"}, 401)
            try:
                qs = parse_qs(urlparse(self.path).query)
                limit = int(qs.get("limit", ["30"])[0])
                agent_id = qs.get("agent_id", [None])[0]
                sessions = runtime.list_sessions(limit=limit, agent_id=agent_id)
                return self._json({"sessions": sessions, "active_session": SESSION["id"]})
            except Exception as e:
                return self._json({"error": str(e)[:200]}, 502)

        # Background mission jobs (Authenticated)
        if p == "/api/jobs":
            if not self._token_ok():
                return self._json({"error": "Unauthorized"}, 401)
            return self._json({
                "done": commands.take_finished(),
                "running": [j for j in commands.jobs_snapshot() if j["status"] == "running"],
            })

        # Mission queue and goals (Authenticated)
        if p == "/api/missions":
            if not self._token_ok():
                return self._json({"error": "Unauthorized"}, 401)
            st = commands.load()
            return self._json({
                "goal": st.get("goal", ""),
                "personality": st.get("personality", ""),
                "tasks": st.get("tasks", []),
                "history": st.get("missions", [])[-20:],
            })

        # Serve static UI files safely
        rel = "index.html" if p == "/" else p.lstrip("/")
        f = (UI / rel).resolve()
        if not str(f).startswith(str(UI.resolve())) or not f.is_file():
            return self._bytes(b"Not Found", "text/plain", 404)

        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        data = f.read_bytes()

        # When serving index.html, issue secure HttpOnly cookie and omit token from DOM
        set_cookie = None
        if rel == "index.html":
            cookie = http.cookies.SimpleCookie()
            cookie[COOKIE_NAME] = API_TOKEN
            cookie[COOKIE_NAME]["path"] = "/"
            cookie[COOKIE_NAME]["httponly"] = True
            cookie[COOKIE_NAME]["samesite"] = "Lax"
            set_cookie = cookie[COOKIE_NAME].OutputString()

        return self._bytes(data, ctype, set_cookie=set_cookie)

    # ── POST ─────────────────────────────────────────────────
    def do_POST(self):
        if not self._host_ok() or not self._origin_ok():
            return self._json({"error": "Request origin rejected"}, 403)
        if not self._token_ok():
            return self._json({"error": "Unauthorized"}, 401)

        p = urlparse(self.path).path
        ctype = self.headers.get("Content-Type", "").split(";", 1)[0].lower()

        if p in {"/api/run", "/api/speak", "/api/new", "/api/cancel", "/api/sessions/create"} and ctype != "application/json":
            return self._json({"error": "application/json required"}, 415)
        if p == "/api/listen" and not ctype.startswith("audio/"):
            return self._json({"error": "Audio content type required"}, 415)

        try:
            raw = self._read(MAX_AUDIO_BODY if p == "/api/listen" else MAX_JSON_BODY)
        except (TypeError, ValueError):
            return self._json({"error": "Payload exceeds maximum allowed size"}, 413)

        if p == "/api/speak":
            try:
                text = (json.loads(raw or b"{}").get("text") or "").strip()
                return self._bytes(voice.speak(text), "audio/mpeg")
            except Exception as e:
                return self._json({"error": str(e)[:200]}, 503)

        if p == "/api/listen":
            try:
                mime = self.headers.get("Content-Type", "audio/webm")
                return self._json({"text": voice.transcribe(raw, mime)})
            except Exception as e:
                return self._json({"error": str(e)[:300], "text": ""}, 503)

        if p == "/api/new":
            try:
                body = json.loads(raw or b"{}")
                agent_id = body.get("agent_id") or SESSION.get("agent_id", "main")
                new_key = runtime.create_session(agent_id=agent_id)
                SESSION["id"] = new_key
                SESSION["agent_id"] = agent_id
                return self._json({"ok": True, "session_id": new_key, "agent_id": agent_id})
            except Exception as e:
                return self._json({"error": str(e)[:200]}, 500)

        if p == "/api/sessions/create":
            try:
                body = json.loads(raw or b"{}")
                agent_id = body.get("agent_id", "main")
                label = body.get("label")
                new_key = runtime.create_session(agent_id=agent_id, label=label)
                SESSION["id"] = new_key
                SESSION["agent_id"] = agent_id
                return self._json({"ok": True, "session_id": new_key, "agent_id": agent_id})
            except Exception as e:
                return self._json({"error": str(e)[:200]}, 500)

        if p == "/api/cancel":
            sid = SESSION["id"]
            stopped = runtime.cancel_active(sid)
            return self._json({"ok": True, "stopped": stopped, "session_id": sid})

        if p == "/api/run":
            if not RUN_LOCK.acquire(blocking=False):
                return self._json({"error": "Jarvis is actively executing a task. Please wait or cancel."}, 409)
            try:
                return self._stream_run(raw)
            finally:
                RUN_LOCK.release()

        return self._json({"error": "Endpoint not found"}, 404)

    # ── the run: NDJSON stream of events ─────────────────────
    def _stream_run(self, raw):
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "Invalid JSON"}, 400)

        message = (payload.get("message") or "").strip()
        extra_system = (payload.get("system") or "").strip()
        fresh = bool(payload.get("fresh"))
        agent_id = payload.get("agent_id") or SESSION.get("agent_id", "main")
        session_id = payload.get("session_id") or SESSION.get("id")

        if not message:
            return self._json({"error": "Empty message"}, 400)
        if fresh:
            session_id = None
            SESSION["id"] = None

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Connection", "close")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        def emit(ev):
            try:
                self.wfile.write((json.dumps(ev) + "\n").encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

        system = "\n\n".join(x for x in (get_persona(), extra_system) if x) or None

        # Slash command evaluation
        cmd = commands.handle(
            message,
            runner=lambda m: runtime.run(m, session_id=None, system=get_persona(), agent_id=agent_id),
            runtime_module=runtime,
        )
        if cmd:
            if cmd.get("note"):
                emit({"t": "note", "message": cmd["note"]})
            if cmd.get("fresh"):
                session_id = None
                SESSION["id"] = None
            if cmd.get("message") is None:
                # Command handled locally
                emit({"t": "delta", "text": cmd.get("reply", "Done.")})
                emit({"t": "complete", "ms": 0, "session_id": SESSION.get("id")})
                return
            message = cmd["message"]

        try:
            for ev in runtime.run(message, session_id=session_id, system=system, agent_id=agent_id):
                sid = ev.get("session_id")
                if ev.get("t") == "complete" and runtime.valid_session(sid):
                    SESSION["id"] = sid
                    SESSION["agent_id"] = agent_id
                emit(ev)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                emit({"t": "error", "message": str(e)[:300]})
            except OSError:
                pass


def main():
    gw_status = runtime.connection_status()
    vo = (f"ElevenLabs · {voice.voice_id()[:8]}…" if voice.available()
          else "Browser Web Speech fallback (add ELEVENLABS_API_KEY for ElevenLabs)")

    print(f"""
  ==============================================================
  WJC GLOBAL — JARVIS COMMAND CENTER
  ==============================================================
  Executive  : Willy — Chairman & CEO
  COO Agent  : Jarvis (agentId: main)
  AI Runtime : OpenClaw Gateway (ws://127.0.0.1:18789)
  Gateway    : {gw_status.get('state', 'probing')} (version: {gw_status.get('server_version', 'checking')})
  Voice      : {vo}
  Console    : http://{HOST}:{PORT}
  ==============================================================
""", flush=True)

    try:
        # Bind dual-stack IPv4/IPv6 so both http://localhost:PORT and http://127.0.0.1:PORT work
        srv = DualStackThreadingHTTPServer(("::", PORT), Handler)
    except Exception as e:
        logger.warning(f"Dual-stack bind to :: failed ({e}), falling back to {HOST}:{PORT}")
        srv = ThreadingHTTPServer((HOST, PORT), Handler)

    if os.environ.get("JARVIS_OPEN", "1") != "0":
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  JARVIS Command Center shutdown.")
        srv.shutdown()
    except Exception as e:
        logger.critical(f"Server fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Under pythonw.exe, write crash to a log file so we can diagnose
        crash_log = ROOT / "crash.log"
        import traceback, datetime
        with open(crash_log, "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.datetime.now().isoformat()} ---\n")
            traceback.print_exc(file=f)

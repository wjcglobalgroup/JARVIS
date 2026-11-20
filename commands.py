"""
Command matrix for WJC GLOBAL — JARVIS COMMAND CENTER.

Handles local commands, mission queue management, and OpenClaw agent coordination.
OpenClaw-native executive commands and direct API routing.
"""
import json
import os
import pathlib
import re
import threading
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
STATE_FILE = pathlib.Path(os.environ.get("JARVIS_STATE", ROOT / "state.json"))
_LOCK = threading.Lock()
_DEFAULT = {"profile": [], "goal": "", "personality": "", "tasks": [], "missions": []}


def _load_unlocked():
    try:
        d = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {**_DEFAULT, **d}
    except (OSError, json.JSONDecodeError):
        return dict(_DEFAULT)


def load():
    with _LOCK:
        return _load_unlocked()


def _save_unlocked(d):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_FILE.with_name(f".{STATE_FILE.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, STATE_FILE)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def save(d):
    with _LOCK:
        _save_unlocked(d)


def update_state(mutator):
    """Apply one read-modify-write transaction safely."""
    with _LOCK:
        d = _load_unlocked()
        result = mutator(d)
        _save_unlocked(d)
        return result


def _sanitize_for_prompt(text, max_len=300):
    """Strip prompt injection control characters and bound text length."""
    if not text:
        return ""
    clean = re.sub(r"[\r\n]+", " ", str(text)).strip()
    clean = clean.replace("<|", "").replace("|>", "")
    return clean[:max_len]


def context_block():
    """Build context notes safely without allowing prompt injection."""
    d = load()
    out = []
    if d["goal"]:
        clean_goal = _sanitize_for_prompt(d["goal"], 500)
        out.append(f"Standing objective: {clean_goal}")
    if d["personality"]:
        clean_tone = _sanitize_for_prompt(d["personality"], 200)
        out.append(f"Tone guideline: {clean_tone}")
    open_tasks = [t for t in d["tasks"] if not t.get("done")]
    if open_tasks:
        tasks_text = "; ".join(_sanitize_for_prompt(t["text"], 100) for t in open_tasks[:10])
        out.append(f"Active mission queue items: {tasks_text}")
    return "\n".join(out)


# Background missions tracker
JOBS = {}
_JOB_LOCK = threading.Lock()


def start_background(mission, runner):
    """Run an OpenClaw background mission asynchronously."""
    jid = uuid.uuid4().hex[:8]
    with _JOB_LOCK:
        JOBS[jid] = {
            "id": jid,
            "status": "running",
            "mission": mission,
            "result": "",
            "started": time.time(),
            "finished": None,
        }
    update_state(lambda d: d["missions"].append(
        {"id": jid, "mission": mission, "status": "running", "at": time.time()}
    ))

    def _work():
        text = ""
        status = "done"
        try:
            for ev in runner(mission):
                if ev.get("t") == "delta":
                    text += ev.get("text", "")
                elif ev.get("t") == "error":
                    status = "failed"
                    text = text or (f"failed: {ev.get('message', '')}"[:260])
        except Exception as e:
            status = "failed"
            text = f"failed: {e}"[:260]

        with _JOB_LOCK:
            if jid in JOBS:
                JOBS[jid].update(status=status, result=text.strip(), finished=time.time())

        def finish(d2):
            for item in d2.get("missions", []):
                if item.get("id") == jid:
                    item.update(status=status, finished=time.time(), result=text.strip()[:500])

        update_state(finish)

    threading.Thread(target=_work, name=f"Mission-{jid}", daemon=True).start()
    return jid


def jobs_snapshot():
    with _JOB_LOCK:
        return [dict(j) for j in JOBS.values()]


def take_finished():
    with _JOB_LOCK:
        done = [dict(j) for j in JOBS.values() if j["status"] in ("done", "failed")]
        for j in done:
            JOBS.pop(j["id"], None)
        return done


_CMD = re.compile(
    r"^\s*/(new|goal|personality|kanban|mission|missions|background|status|commands|help|clear|agents|sessions|browser|tools)\b\s*(.*)$",
    re.I | re.S,
)


def _commands_reply():
    return """**WJC GLOBAL — JARVIS COMMAND CENTER**
Available slash commands:

• **/new** — Start a fresh OpenClaw session with Jarvis
• **/agents** — List verified corporate agents and operational divisions
• **/sessions** — List active and recent Gateway sessions
• **/status** — OpenClaw Gateway connectivity, uptime, and runtime telemetry
• **/goal** `<text|status|clear>` — Set, inspect, or clear standing executive objective
• **/personality** `<tone>` — Adjust Jarvis tone overlay
• **/mission** `[task]` — Add or review items in the mission queue
• **/background** `<task>` — Launch an asynchronous background mission through OpenClaw
• **/browser** `<instruction>` — Direct Jarvis to execute browser automation
• **/clear** — Clear the local console display
• **/help** or **/commands** — Display this command reference"""


def handle(message, runner=None, runtime_module=None):
    """
    Handle slash commands.
    Returns:
      None if not a slash command (forward to OpenClaw).
      dict with keys:
        - fresh: bool (optional)
        - message: prompt string or None (if handled locally)
        - reply: local response text (if message is None)
        - note: short telemetry label
    """
    m = _CMD.match(message or "")
    if not m:
        return None

    cmd, arg = m.group(1).lower(), m.group(2).strip()
    d = load()

    if cmd in ("help", "commands"):
        return dict(message=None, reply=_commands_reply(), note="commands shown")

    if cmd == "clear":
        return dict(message=None, reply="Console display cleared. Gateway session preserved.", note="display clear")

    if cmd == "new":
        return dict(
            fresh=True,
            message=arg or "Initialize a fresh Jarvis session for WJC Global. Greet Willy concisely.",
            note="fresh session initialized",
        )

    if cmd == "status":
        if runtime_module:
            st = runtime_module.connection_status()
            reply = (
                f"**WJC GLOBAL — RUNTIME STATUS**\n"
                f"• **AI Runtime**: OpenClaw Gateway (Protocol v4)\n"
                f"• **Gateway URL**: {st.get('gateway_url')}\n"
                f"• **Connection State**: {st.get('state')}\n"
                f"• **Server Version**: OpenClaw {st.get('server_version')}\n"
                f"• **Default COO Agent**: Jarvis (`{st.get('default_agent')}`)\n"
                f"• **Uptime**: {st.get('uptime_seconds')} seconds"
            )
        else:
            reply = "OpenClaw Gateway status check."
        return dict(message=None, reply=reply, note="status read")

    if cmd == "agents":
        if runtime_module:
            try:
                agents = runtime_module.list_agents()
                lines = ["**WJC GLOBAL — VERIFIED AGENT ROSTER**\n"]
                for a in agents:
                    is_def = " *(Default / COO)*" if a.get("is_default") else ""
                    lines.append(f"• **{a.get('name')}** (`{a.get('id')}`){is_def} — {a.get('role')}")
                reply = "\n".join(lines)
            except Exception as e:
                reply = f"Failed to retrieve agent roster from Gateway: {e}"
        else:
            reply = "Agent directory unavailable."
        return dict(message=None, reply=reply, note="agents roster")

    if cmd == "sessions":
        if runtime_module:
            try:
                sessions = runtime_module.list_sessions(limit=10)
                lines = ["**OPENCLAW GATEWAY — RECENT SESSIONS**\n"]
                for s in sessions:
                    active_tag = " [ACTIVE]" if s.get("active") else ""
                    lines.append(f"• `{s.get('key')}` (Agent: `{s.get('agent_id')}`){active_tag}")
                reply = "\n".join(lines)
            except Exception as e:
                reply = f"Failed to retrieve sessions from Gateway: {e}"
        else:
            reply = "Sessions listing unavailable."
        return dict(message=None, reply=reply, note="sessions list")

    if cmd == "tools":
        return dict(
            message=None,
            reply=(
                "**OpenClaw Tool Architecture**\n"
                "In OpenClaw, toolsets and MCP servers are configured per-agent on the Gateway. "
                "Jarvis automatically invokes tools (e.g. browser, file system, APIs, web search) as needed."
            ),
            note="tools architecture",
        )

    if cmd == "browser":
        task = arg or "inspect the browser environment and report status"
        return dict(
            message=f"Use your browser automation tool to perform this task: {task}",
            note="browser instruction armed",
        )

    if cmd == "goal":
        if arg.lower() == "clear":
            update_state(lambda state: state.__setitem__("goal", ""))
            return dict(message=None, reply="Standing objective cleared.", note="goal cleared")
        if not arg or arg.lower() == "status":
            return dict(
                message=None,
                reply=f"Standing objective: {d['goal']}" if d["goal"] else "No standing objective set.",
                note="goal read",
            )
        clean_arg = _sanitize_for_prompt(arg, 500)
        update_state(lambda state: state.__setitem__("goal", clean_arg))
        return dict(
            message=f'The CEO set this standing objective: "{clean_arg}". Acknowledge concisely as Jarvis.',
            note=f"goal set: {clean_arg[:40]}",
        )

    if cmd == "personality":
        if not arg:
            return dict(
                message=None,
                reply=f"Active tone overlay: {d['personality']}" if d["personality"] else "Running standard Jarvis executive persona.",
                note="persona read",
            )
        clean_tone = _sanitize_for_prompt(arg, 200)
        update_state(lambda state: state.__setitem__("personality", clean_tone))
        return dict(
            message=f'Executive tone overlay set to: "{clean_tone}". Acknowledge in one short sentence.',
            note=f"persona: {clean_tone[:40]}",
        )

    if cmd in ("kanban", "mission", "missions"):
        if arg:
            clean_task = _sanitize_for_prompt(arg, 200)
            update_state(lambda state: state["tasks"].append(
                {"text": clean_task, "done": False, "at": time.time()}
            ))
            return dict(
                message=f'Added to WJC mission queue: "{clean_task}". Acknowledge concisely as Jarvis.',
                note=f"mission += {clean_task[:40]}",
            )
        open_t = [t["text"] for t in d["tasks"] if not t.get("done")]
        if not open_t:
            return dict(message=None, reply="Mission queue is currently empty.", note="queue empty")
        return dict(
            message=None,
            reply="**WJC GLOBAL — MISSION QUEUE**\n" + "\n".join(f"• {t}" for t in open_t),
            note=f"queue read ({len(open_t)})",
        )

    if cmd == "background":
        if not arg:
            return dict(message=None, reply="Specify a mission to execute in the background.", note="background empty")
        if runner is None:
            return dict(message=None, reply="Background mission execution unavailable.", note="background unavailable")
        jid = start_background(arg, runner)
        return dict(
            message=None,
            reply=f"Background mission `{jid}` dispatched to OpenClaw. Telemetry will update upon completion.",
            note=f"mission {jid} started",
        )

    return None

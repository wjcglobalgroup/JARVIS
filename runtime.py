"""
OpenClaw runtime for WJC GLOBAL — JARVIS COMMAND CENTER.

Connects to the OpenClaw Gateway as the sole AI runtime.
Directs all operations to the verified Jarvis agent ('main') and other organizational agents.
OpenClaw Gateway WebSocket interface for unified executive task execution.
"""
import logging
import os
import re
import threading
from openclaw_client import OpenClawClient

logger = logging.getLogger("runtime")

# Configuration
DEFAULT_AGENT = os.environ.get("OPENCLAW_DEFAULT_AGENT", "main").strip()
GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789").strip()
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()

# Valid OpenClaw session keys: e.g. agent:main:main or agent:main:dashboard:uuid or uuid
_SESSION_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{3,128}$")

# Singleton OpenClaw Client
_CLIENT = None
_CLIENT_LOCK = threading.Lock()


def get_client():
    """Get or initialize the OpenClawClient singleton."""
    global _CLIENT
    with _CLIENT_LOCK:
        if _CLIENT is None:
            _CLIENT = OpenClawClient(
                gateway_url=GATEWAY_URL,
                token=GATEWAY_TOKEN or None,
                default_agent=DEFAULT_AGENT,
            )
        return _CLIENT


def runtime_kind():
    """Report active AI runtime kind. Always 'openclaw'."""
    return "openclaw"


def valid_session(sid):
    """Validate OpenClaw session key."""
    return bool(sid) and bool(_SESSION_KEY_RE.match(str(sid)))


def connection_status():
    """Return live status of the OpenClaw Gateway connection."""
    client = get_client()
    state = client.get_state()
    return {
        "runtime": "openclaw",
        "gateway_url": state.get("url"),
        "connected": state.get("connected"),
        "state": state.get("state"),
        "server_version": state.get("server", {}).get("version", "unknown"),
        "uptime_seconds": state.get("uptime", 0),
        "error": state.get("error"),
        "default_agent": DEFAULT_AGENT,
    }


def list_agents():
    """List verified agents from OpenClaw Gateway."""
    client = get_client()
    return client.list_agents()


def list_sessions(limit=30, agent_id=None):
    """List sessions from OpenClaw Gateway."""
    client = get_client()
    return client.list_sessions(limit=limit, agent_id=agent_id)


def create_session(agent_id=None, label=None):
    """Create a new OpenClaw session."""
    client = get_client()
    return client.create_session(agent_id=agent_id or DEFAULT_AGENT, label=label)


def cancel_active(session_id=None):
    """Abort an active agent run."""
    client = get_client()
    if not session_id:
        return False
    try:
        client.abort_session(session_id)
        return True
    except Exception as e:
        logger.warning(f"Error cancelling session {session_id}: {e}")
        return False


def run(message, session_id=None, system=None, agent_id=None):
    """
    Execute an instruction through the real OpenClaw Gateway.
    Streams NDJSON events back to the dashboard.
    """
    client = get_client()

    if not client.is_connected():
        status = connection_status()
        yield {
            "t": "error",
            "message": (
                f"OpenClaw Gateway is not connected at {status.get('gateway_url')} "
                f"(state: {status.get('state')}). Error: {status.get('error') or 'Waiting for handshake'}"
            ),
        }
        return

    try:
        yield from client.stream_chat(
            message=message,
            session_key=session_id,
            agent_id=agent_id or DEFAULT_AGENT,
            system=system,
        )
    except Exception as e:
        logger.exception("Error in OpenClaw execution")
        yield {"t": "error", "message": f"OpenClaw execution error: {e}"}

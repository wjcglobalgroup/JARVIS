"""
OpenClaw Gateway WebSocket Adapter for WJC GLOBAL — JARVIS COMMAND CENTER.

Connects to the local OpenClaw Gateway (Protocol v4) over WebSocket as an operator client.
Provides thread-safe synchronous and streaming interfaces for the Python HTTP backend.
"""
import asyncio
import json
import logging
import os
import pathlib
import queue
import threading
import time
import uuid
import websockets

logger = logging.getLogger("openclaw_client")

# Default configuration
DEFAULT_GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789").strip()
DEFAULT_AGENT_ID = os.environ.get("OPENCLAW_DEFAULT_AGENT", "main").strip()


def discover_gateway_token():
    """Discover Gateway token from environment or ~/.openclaw/openclaw.json."""
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()
    if token:
        return token
    try:
        cfg_file = pathlib.Path.home() / ".openclaw" / "openclaw.json"
        if cfg_file.is_file():
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            token = data.get("gateway", {}).get("auth", {}).get("token", "")
            if token:
                return str(token).strip()
    except Exception as e:
        logger.warning(f"Failed to read OpenClaw config: {e}")
    return ""


class OpenClawClient:
    """Thread-safe OpenClaw Gateway WebSocket Client."""

    def __init__(self, gateway_url=None, token=None, default_agent=DEFAULT_AGENT_ID):
        self.gateway_url = gateway_url or DEFAULT_GATEWAY_URL
        self.token = token or discover_gateway_token()
        self.default_agent = default_agent

        self._loop = None
        self._thread = None
        self._ws = None
        self._stop_event = threading.Event()

        self._state = "disconnected"  # disconnected, connecting, handshaking, connected, error
        self._state_lock = threading.Lock()
        self._last_error = None
        self._server_info = {}
        self._policy = {}
        self._connect_time = None

        # RPC tracking: req_id -> Future
        self._pending_rpc = {}
        # Event listeners: event_name -> list of callable(payload)
        self._event_listeners = {}
        # Session event queues: session_key -> list of queue.Queue
        self._session_queues = {}
        self._queue_lock = threading.Lock()

        # Start background event loop thread
        self._start_thread()

    def _set_state(self, state, error=None):
        with self._state_lock:
            self._state = state
            self._last_error = error
            if state == "connected":
                self._connect_time = time.time()
            elif state in ("disconnected", "error"):
                self._connect_time = None

    def get_state(self):
        with self._state_lock:
            return {
                "state": self._state,
                "connected": self._state == "connected",
                "url": self.gateway_url,
                "server": self._server_info,
                "uptime": int(time.time() - self._connect_time) if self._connect_time else 0,
                "error": self._last_error,
            }

    def is_connected(self):
        return self._state == "connected" and self._ws is not None

    def _start_thread(self):
        self._thread = threading.Thread(target=self._run_loop, name="OpenClaw-WS", daemon=True)
        self._thread.start()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._supervise_connection())

    async def _supervise_connection(self):
        backoff = 1.0
        while not self._stop_event.is_set():
            try:
                self._set_state("connecting")
                async with websockets.connect(
                    self.gateway_url,
                    open_timeout=15,
                    close_timeout=10,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=26214400,
                ) as ws:
                    self._ws = ws
                    self._set_state("handshaking")

                    # Step 1: Wait for connect.challenge
                    chal_raw = await asyncio.wait_for(ws.recv(), timeout=15)
                    chal = json.loads(chal_raw)
                    if chal.get("event") != "connect.challenge":
                        raise RuntimeError(f"Expected connect.challenge, got: {chal.get('event')}")

                    # Step 2: Send connect request
                    conn_id = f"conn-{uuid.uuid4().hex[:8]}"
                    connect_req = {
                        "type": "req",
                        "id": conn_id,
                        "method": "connect",
                        "params": {
                            "minProtocol": 4,
                            "maxProtocol": 4,
                            "role": "operator",
                            "scopes": [
                                "operator.read",
                                "operator.write",
                                "operator.approvals",
                            ],
                            "caps": ["tool-events"],
                            "auth": {"token": self.token},
                            "client": {
                                "id": "gateway-client",
                                "version": "1.0.0",
                                "platform": "windows",
                                "mode": "backend",
                            },
                        },
                    }
                    await ws.send(json.dumps(connect_req))

                    # Step 3: Wait for hello-ok
                    hello_raw = await asyncio.wait_for(ws.recv(), timeout=20)
                    hello = json.loads(hello_raw)
                    if not hello.get("ok") or hello.get("payload", {}).get("type") != "hello-ok":
                        err_msg = hello.get("error", {}).get("message", "Handshake rejected")
                        raise RuntimeError(f"Handshake failed: {err_msg}")

                    payload = hello.get("payload", {})
                    self._server_info = payload.get("server", {})
                    self._policy = payload.get("policy", {})
                    self._set_state("connected")
                    backoff = 1.0
                    logger.info("Connected to OpenClaw Gateway.")

                    # Step 4: Dispatch incoming frames
                    await self._read_frames(ws)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._set_state("error", str(e))
                self._cleanup_pending_rpc(f"Connection lost: {e}")
                logger.warning(f"OpenClaw Gateway connection error: {e}. Retrying in {backoff:.1f}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5, 15.0)

        self._set_state("disconnected")

    async def _read_frames(self, ws):
        async for raw in ws:
            try:
                frame = json.loads(raw)
                frame_type = frame.get("type")

                if frame_type == "res":
                    req_id = frame.get("id")
                    fut = self._pending_rpc.pop(req_id, None)
                    if fut and not fut.done():
                        fut.set_result(frame)

                elif frame_type == "event":
                    self._dispatch_event(frame)

            except Exception as e:
                logger.error(f"Error processing frame: {e}")

    def _dispatch_event(self, frame):
        event_name = frame.get("event")
        payload = frame.get("payload", {})

        # Debug print for event tracing
        if event_name not in ("tick", "health"):
            logger.info(f"[Gateway Event] {event_name}: keys={list(payload.keys())} state={payload.get('state')}")

        # Route chat and session events to active session queues
        session_key = (
            payload.get("sessionKey")
            or payload.get("key")
            or payload.get("session_key")
            or (payload.get("message", {}).get("sessionKey") if isinstance(payload.get("message"), dict) else None)
        )

        with self._queue_lock:
            # If session_key is found and matched
            if session_key and session_key in self._session_queues:
                for q in self._session_queues[session_key]:
                    try:
                        q.put_nowait(frame)
                    except Exception:
                        pass
            else:
                # If event is chat or agent and session_key is absent or not matched,
                # broadcast to ALL active session queues (since operator connection subscribes per session)
                if event_name in ("chat", "agent", "session.message", "session.operation"):
                    for q_list in self._session_queues.values():
                        for q in q_list:
                            try:
                                q.put_nowait(frame)
                            except Exception:
                                pass

            # Broadcast to wildcard session subscribers
            if "*" in self._session_queues:
                for q in self._session_queues["*"]:
                    try:
                        q.put_nowait(frame)
                    except Exception:
                        pass

        # Also trigger registered listeners
        listeners = self._event_listeners.get(event_name, [])
        for cb in listeners:
            try:
                cb(payload)
            except Exception as e:
                logger.error(f"Error in event callback for {event_name}: {e}")

    def _cleanup_pending_rpc(self, reason):
        for req_id, fut in list(self._pending_rpc.items()):
            if not fut.done():
                fut.set_exception(RuntimeError(reason))
        self._pending_rpc.clear()

    # ── Public RPC methods ──────────────────────────────────────────

    def rpc(self, method, params=None, timeout=30):
        """Execute a Gateway RPC method synchronously."""
        if not self.is_connected():
            # Wait up to 5 seconds if connecting
            for _ in range(50):
                if self.is_connected():
                    break
                time.sleep(0.1)
            if not self.is_connected():
                state = self.get_state()
                raise RuntimeError(f"OpenClaw Gateway is not connected (state: {state['state']}, error: {state['error']})")

        fut = asyncio.run_coroutine_threadsafe(
            self._async_rpc(method, params or {}, timeout),
            self._loop,
        )
        return fut.result(timeout=timeout + 2)

    async def _async_rpc(self, method, params, timeout):
        req_id = uuid.uuid4().hex
        fut = self._loop.create_future()
        self._pending_rpc[req_id] = fut

        frame = {
            "type": "req",
            "id": req_id,
            "method": method,
            "params": params,
        }
        await self._ws.send(json.dumps(frame))
        res = await asyncio.wait_for(fut, timeout=timeout)

        if not res.get("ok"):
            err = res.get("error", {})
            msg = err.get("message") or f"RPC {method} failed"
            code = err.get("code", "UNKNOWN_ERROR")
            raise RuntimeError(f"OpenClaw Gateway Error ({code}): {msg}")

        return res.get("payload", {})

    # ── Agent and Session Helpers ────────────────────────────────────

    def list_agents(self):
        """Discover available agents from the Gateway."""
        res = self.rpc("agents.list")
        agents = res.get("agents", [])
        sanitized = []
        for a in agents:
            ident = a.get("identity", {})
            sanitized.append({
                "id": a.get("id"),
                "name": ident.get("name") or a.get("name") or a.get("id"),
                "role": ident.get("role", "Autonomous Agent"),
                "emoji": ident.get("emoji", "🤖"),
                "model": a.get("model", {}).get("primary", "Default"),
                "workspace": a.get("workspace"),
                "permission": a.get("defaultPermissionMode", "normal"),
                "is_default": a.get("id") == self.default_agent,
            })
        return sanitized

    def list_sessions(self, limit=50, agent_id=None):
        """List active/recent sessions."""
        params = {"limit": limit}
        if agent_id:
            params["agentId"] = agent_id
        res = self.rpc("sessions.list", params)
        sessions = res.get("sessions", [])
        out = []
        for s in sessions:
            out.append({
                "key": s.get("key"),
                "agent_id": s.get("agentId"),
                "session_id": s.get("sessionId"),
                "title": s.get("displayName") or s.get("label") or s.get("key"),
                "active": bool(s.get("hasActiveRun")),
                "updated_at": s.get("updatedAt"),
                "created_at": s.get("createdAt"),
            })
        return out

    def create_session(self, agent_id=None, label=None):
        """Create a new OpenClaw session for an agent."""
        agent = agent_id or self.default_agent
        params = {"agentId": agent}
        if label:
            params["label"] = label
        res = self.rpc("sessions.create", params)
        return res.get("key")

    def subscribe_session(self, session_key):
        """Subscribe to message events for a session."""
        return self.rpc("sessions.messages.subscribe", {"key": session_key})

    def abort_session(self, session_key):
        """Abort any active run in a session."""
        try:
            return self.rpc("sessions.abort", {"key": session_key})
        except Exception:
            return self.rpc("chat.abort", {"sessionKey": session_key})

    def get_chat_history(self, session_key, limit=50):
        """Fetch normalized chat history for a session."""
        return self.rpc("chat.history", {"sessionKey": session_key, "limit": limit})

    # ── Real-time Chat Streaming ─────────────────────────────────────

    def stream_chat(self, message, session_key=None, agent_id=None, system=None, timeout=120):
        """
        Send a message and yield events in real-time.
        Yields:
          {"t": "status", "model": ..., "session_id": ...}
          {"t": "latency", "ms": ...}
          {"t": "delta", "text": ...}
          {"t": "tool", "name": ..., "status": ...}
          {"t": "complete", "session_id": ..., "ms": ...}
          {"t": "error", "message": ...}
        """
        agent = agent_id or self.default_agent
        if not session_key:
            session_key = self.create_session(agent)

        # Ensure session subscription
        try:
            self.subscribe_session(session_key)
        except Exception as e:
            logger.warning(f"Could not subscribe to {session_key}: {e}")

        q = queue.Queue()
        with self._queue_lock:
            if session_key not in self._session_queues:
                self._session_queues[session_key] = []
            self._session_queues[session_key].append(q)

        start_time = time.monotonic()
        first_delta = True
        accumulated_text = []

        try:
            yield {
                "t": "status",
                "runtime": "openclaw",
                "model": "OpenClaw / Jarvis",
                "agent_id": agent,
                "session_id": session_key,
            }

            # Prepend system persona if provided
            full_prompt = message
            if system:
                full_prompt = f"{system}\n\n## Current user request\n{message}"

            idempotency_key = uuid.uuid4().hex
            send_params = {
                "sessionKey": session_key,
                "message": full_prompt,
                "idempotencyKey": idempotency_key,
            }
            if agent:
                send_params["agentId"] = agent

            # Send the chat turn
            self.rpc("chat.send", send_params, timeout=20)

            # Consume events from queue
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = max(0.1, deadline - time.monotonic())
                try:
                    frame = q.get(timeout=min(remaining, 5.0))
                except queue.Empty:
                    # Check if connection is still healthy
                    if not self.is_connected():
                        yield {"t": "error", "message": "Lost connection to OpenClaw Gateway during generation."}
                        return
                    continue

                event_name = frame.get("event")
                payload = frame.get("payload", {})

                # 1. Chat events
                if event_name == "chat":
                    state = payload.get("state")
                    if state == "delta":
                        if first_delta:
                            first_delta = False
                            yield {"t": "latency", "ms": int((time.monotonic() - start_time) * 1000)}
                        delta_text = payload.get("deltaText", "")
                        if delta_text:
                            accumulated_text.append(delta_text)
                            yield {"t": "delta", "text": delta_text}

                    elif state == "status":
                        phase = payload.get("phase") or "Processing..."
                        yield {"t": "note", "message": f"Jarvis: {phase}"}

                    elif state == "final":
                        total_ms = int((time.monotonic() - start_time) * 1000)
                        yield {
                            "t": "complete",
                            "session_id": session_key,
                            "ms": total_ms,
                        }
                        return

                    elif state == "error":
                        err_msg = (
                            payload.get("errorMessage")
                            or payload.get("errorDetail", {}).get("providerErrorMessagePreview")
                            or payload.get("errorKind")
                            or "OpenClaw generation error"
                        )
                        yield {"t": "error", "message": str(err_msg)[:350]}
                        return

                # 2. Agent stream events
                elif event_name == "agent":
                    stream = payload.get("stream")
                    data = payload.get("data", {})
                    if stream == "assistant":
                        text_chunk = data.get("delta") or data.get("text")
                        if text_chunk and not accumulated_text:
                            # If chat stream didn't deliver, use agent stream
                            if first_delta:
                                first_delta = False
                                yield {"t": "latency", "ms": int((time.monotonic() - start_time) * 1000)}
                            accumulated_text.append(text_chunk)
                            yield {"t": "delta", "text": text_chunk}

                    elif stream == "tool":
                        tool_name = data.get("name") or data.get("tool", "tool")
                        tool_status = data.get("status", "executing")
                        yield {"t": "tool", "name": tool_name, "status": tool_status}

                    elif stream == "lifecycle":
                        kind = data.get("kind")
                        if kind == "run.completed":
                            total_ms = int((time.monotonic() - start_time) * 1000)
                            yield {
                                "t": "complete",
                                "session_id": session_key,
                                "ms": total_ms,
                            }
                            return
                        elif kind == "run.failed":
                            err_msg = data.get("error") or data.get("message") or "Agent run failed"
                            yield {"t": "error", "message": str(err_msg)[:350]}
                            return

                # 3. Session message events (final committed assistant messages)
                elif event_name == "session.message":
                    msg_obj = payload.get("message", {})
                    role = msg_obj.get("role")
                    if role in ("assistant", "custom"):
                        raw_content = msg_obj.get("content", "")
                        extracted_text = ""
                        if isinstance(raw_content, str):
                            extracted_text = raw_content
                        elif isinstance(raw_content, list):
                            for block in raw_content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    extracted_text += block.get("text", "")

                        if extracted_text and not accumulated_text:
                            if first_delta:
                                first_delta = False
                                yield {"t": "latency", "ms": int((time.monotonic() - start_time) * 1000)}
                            accumulated_text.append(extracted_text)
                            yield {"t": "delta", "text": extracted_text}
                            total_ms = int((time.monotonic() - start_time) * 1000)
                            yield {
                                "t": "complete",
                                "session_id": session_key,
                                "ms": total_ms,
                            }
                            return

            # If we reached here, timeout occurred
            yield {"t": "error", "message": f"OpenClaw generation timed out after {timeout}s."}

        finally:
            with self._queue_lock:
                if session_key in self._session_queues and q in self._session_queues[session_key]:
                    self._session_queues[session_key].remove(q)
                    if not self._session_queues[session_key]:
                        del self._session_queues[session_key]

    def close(self):
        """Shutdown client."""
        self._stop_event.set()
        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)

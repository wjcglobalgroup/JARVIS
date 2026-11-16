"""
Voice synthesis and speech transcription module for WJC GLOBAL GROUP — JARVIS COMMAND CENTER.

Server-side proxy for ElevenLabs Text-to-Speech (TTS) and Speech-to-Text (STT).
All API keys and credentials remain strictly server-side.
When ElevenLabs is unconfigured, the frontend automatically falls back to browser Web Speech API.
"""
import json
import os
import urllib.error
import urllib.request

# Default voice: Rachel or configured voice ID
DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"
MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_turbo_v2_5")


def available():
    """Check if ElevenLabs API key is configured."""
    return bool(os.environ.get("ELEVENLABS_API_KEY"))


def voice_id():
    """Active ElevenLabs voice ID."""
    return os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE)


def speak(text):
    """
    Synthesize speech via ElevenLabs API.
    Returns mp3 bytes.
    """
    if not available():
        raise RuntimeError("ELEVENLABS_API_KEY is not configured on the server.")
    text = (text or "").strip()
    if not text:
        raise ValueError("Cannot synthesize empty text.")

    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id()}",
        data=json.dumps({
            "text": text[:2500],
            "model_id": MODEL,
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.85,
                "style": 0.20,
                "use_speaker_boost": True,
            },
        }).encode("utf-8"),
        method="POST",
        headers={
            "content-type": "application/json",
            "accept": "audio/mpeg",
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def transcribe(audio, mime="audio/webm"):
    """
    Transcribe audio via ElevenLabs speech-to-text.
    Returns transcribed string.
    """
    if not available():
        raise RuntimeError("ELEVENLABS_API_KEY is not configured on the server.")
    if not audio:
        raise ValueError("Audio buffer is empty.")

    ext = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "mp4",
           "audio/mpeg": "mp3", "audio/wav": "wav"}.get(mime.split(";")[0], "webm")
    boundary = "----jarvis" + os.urandom(8).hex()
    b = boundary.encode("utf-8")

    body = b"".join([
        b"--", b, b"\r\n",
        b'Content-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n',
        b"--", b, b"\r\n",
        f'Content-Disposition: form-data; name="file"; filename="audio.{ext}"\r\n'.encode("utf-8"),
        f"Content-Type: {mime}\r\n\r\n".encode("utf-8"),
        audio, b"\r\n",
        b"--", b, b"--\r\n",
    ])

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/speech-to-text",
        data=body, method="POST",
        headers={
            "content-type": f"multipart/form-data; boundary={boundary}",
            "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return (json.loads(r.read().decode("utf-8")).get("text") or "").strip()


def voices():
    """List account voices for configuration discovery."""
    if not available():
        return []
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v2/voices",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    return [
        {
            "id": v.get("voice_id"),
            "name": v.get("name"),
            "labels": v.get("labels", {}),
        }
        for v in body.get("voices", [])
    ]

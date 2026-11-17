"""Groq-powered speech-to-text for downloaded audio chunks."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from groq import Groq
from pydub import AudioSegment


# 64 kbps mono MP3 keeps a 10-minute chunk well below Groq's upload limit.
GROQ_MODEL = os.getenv("GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3")
MAX_UPLOAD_BYTES = 24 * 1024 * 1024


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env. Add it and restart Streamlit.")
    return Groq(api_key=api_key)


def _make_upload_file(chunk_path: str) -> str:
    """Compress a WAV chunk to an API-friendly temporary MP3 file."""
    source = Path(chunk_path)
    if not source.is_file():
        raise FileNotFoundError(f"Audio chunk not found: {source}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        upload_path = temp_file.name

    try:
        audio = AudioSegment.from_file(source).set_channels(1).set_frame_rate(16000)
        audio.export(upload_path, format="mp3", bitrate="64k")
        if Path(upload_path).stat().st_size > MAX_UPLOAD_BYTES:
            raise RuntimeError(
                "This audio chunk is too large for Groq after compression. "
                "Use a shorter video or reduce the chunk length."
            )
        return upload_path
    except Exception:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        raise


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """Upload one chunk to Groq's hosted Whisper model."""
    upload_path = _make_upload_file(chunk_path)
    try:
        with open(upload_path, "rb") as audio_file:
            result = _get_client().audio.transcriptions.create(
                file=(Path(upload_path).name, audio_file.read()),
                model=GROQ_MODEL,
                temperature=0,
                response_format="verbose_json",
            )
        return result.text.strip()
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)


def transcribe_all(chunks: list[str], language: str = "english") -> str:
    """Transcribe all chunks with Groq; no local Whisper model is loaded."""
    if not chunks:
        raise RuntimeError("No audio chunks were created for transcription.")

    print(f"Using Groq {GROQ_MODEL} for transcription.")
    transcript_parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        print(f"Uploading and transcribing chunk {index}/{len(chunks)}...")
        transcript_parts.append(transcribe_chunk(chunk, language=language))

    print("Transcription complete.")
    return " ".join(part for part in transcript_parts if part).strip()

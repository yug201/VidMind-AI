"""Download and prepare audio for transcription."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import yt_dlp
from pydub import AudioSegment


PROJECT_DIR = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = PROJECT_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)


def _ffmpeg_location() -> str:
    """Return FFmpeg's location, including the common Windows Winget install."""
    configured = os.getenv("FFMPEG_LOCATION")
    if configured and Path(configured).exists():
        return configured

    on_path = shutil.which("ffmpeg")
    if on_path:
        return str(Path(on_path).parent)

    winget_dir = Path.home() / (
        "AppData/Local/Microsoft/WinGet/Packages/"
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    )
    if winget_dir.exists():
        matches = list(winget_dir.glob("*/bin/ffmpeg.exe"))
        if matches:
            return str(matches[0].parent)

    raise FileNotFoundError(
        "FFmpeg was not found. Install FFmpeg and add its bin folder to PATH, "
        "or set FFMPEG_LOCATION to that folder."
    )


def _configure_ffmpeg() -> str:
    location = _ffmpeg_location()
    ffmpeg = Path(location) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    ffprobe = Path(location) / ("ffprobe.exe" if os.name == "nt" else "ffprobe")
    AudioSegment.converter = str(ffmpeg)
    if ffprobe.exists():
        AudioSegment.ffprobe = str(ffprobe)
    return location


def download_youtube_audio(url: str) -> str:
    """Download one URL and return the WAV path created by yt-dlp/FFmpeg."""
    ffmpeg_location = _configure_ffmpeg()
    output_template = str(DOWNLOAD_DIR / "%(title).120s-%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "restrictfilenames": True,
        "ffmpeg_location": ffmpeg_location,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            original_path = Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as exc:
        raise RuntimeError(
            "The video could not be downloaded. Check that the link is public, "
            "not age-restricted, and that yt-dlp is up to date."
        ) from exc

    wav_path = original_path.with_suffix(".wav")
    if not wav_path.is_file():
        raise RuntimeError("Audio download finished, but FFmpeg did not create the WAV file.")
    return str(wav_path)


def convert_to_wav(input_path: str) -> str:
    """Convert a local audio/video file to 16 kHz mono WAV."""
    _configure_ffmpeg()
    source = Path(input_path).expanduser()
    if not source.is_file():
        raise FileNotFoundError(f"Local file not found: {source}")
    output_path = source.with_name(f"{source.stem}_converted.wav")
    audio = AudioSegment.from_file(source).set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return str(output_path)


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    audio = AudioSegment.from_wav(wav_path)
    if len(audio) == 0:
        raise RuntimeError("The downloaded audio is empty.")

    chunk_ms = chunk_minutes * 60 * 1000
    chunks: list[str] = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        audio[start : start + chunk_ms].export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list[str]:
    source = source.strip()
    if source.startswith(("http://", "https://")):
        print("Downloading audio from video link...")
        wav_path = download_youtube_audio(source)
    else:
        print("Converting local file to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks

"""Google Cloud Text-to-Speech integration."""
from __future__ import annotations

import json

from google.cloud import texttospeech
from google.oauth2 import service_account

try:
    import streamlit as st
except ImportError:  # pragma: no cover - fallback when Streamlit isn't available
    st = None  # type: ignore


def generate_tts(script: str, voice_name: str = "en-US-Standard-C") -> bytes:
    """
    Generate MP3 audio bytes for the given script using Google Cloud Text-to-Speech.
    """
    if not script:
        raise ValueError("Script text is required for TTS generation.")

    project_id = st.secrets.get("GOOGLE_TTS_PROJECT_ID", "") if st is not None else ""
    credentials_json = st.secrets.get("GOOGLE_TTS_CREDENTIALS_JSON", "") if st is not None else ""

    if not project_id or not credentials_json:
        raise RuntimeError("Google TTS configuration is missing in secrets.")

    try:
        info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(info)
    except Exception as exc:  # pragma: no cover - depends on runtime secrets
        raise RuntimeError("Failed to parse Google TTS credentials JSON.") from exc

    client = texttospeech.TextToSpeechClient(credentials=credentials)

    synthesis_input = texttospeech.SynthesisInput(text=script)
    language_code = "en-US"
    if "-" in voice_name:
        language_code = "-".join(voice_name.split("-", 2)[:2])

    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    try:
        response = client.synthesize_speech(
            request=texttospeech.SynthesizeSpeechRequest(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
            )
        )
    except Exception as exc:  # pragma: no cover - external dependency
        raise RuntimeError(f"Google TTS synthesis failed: {exc}") from exc

    return response.audio_content

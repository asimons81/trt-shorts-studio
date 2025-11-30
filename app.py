"""Streamlit app for Tony Shorts Studio."""
from __future__ import annotations

import io
import json
from zipfile import ZipFile

import streamlit as st

from services import llm, tts, wordpress, images
from utils.parsing import clean_article_text

st.set_page_config(page_title="Tony Shorts Studio", layout="wide")
st.title("Tony Reviews Things – Shorts Studio")


def _secret_present(key: str) -> bool:
    try:
        return bool(st.secrets.get(key))
    except Exception:
        return False


def _sidebar():
    st.sidebar.header("Settings")
    st.sidebar.write("API keys are read from st.secrets. Ensure they are configured before generating.")
    st.sidebar.write("Gemini configured:", _secret_present("GEMINI_API_KEY"))
    st.sidebar.write("Google TTS configured:", _secret_present("GOOGLE_TTS_PROJECT_ID"))


_sidebar()

tabs = st.tabs([
    "Source",
    "Script",
    "Voiceover",
    "Visuals",
    "Export",
])


# Tab: Source
with tabs[0]:
    st.subheader("Source content")
    url_input = st.text_input("Article URL")
    text_input = st.text_area("Or paste article text", height=200)
    if st.button("Fetch & analyze", type="primary"):
        try:
            if url_input:
                article_text = wordpress.fetch_article(url_input)
            elif text_input:
                article_text = clean_article_text(text_input)
            else:
                st.error("Provide a URL or paste article text to continue.")
                article_text = None

            if article_text:
                st.session_state["article_text"] = article_text
                st.success("Article loaded and analyzed.")
        except Exception as exc:
            st.error(f"Failed to fetch article: {exc}")

    if "article_text" in st.session_state:
        preview = st.session_state["article_text"][:500]
        st.text_area("Article preview (first 500 chars)", preview, height=150, disabled=True)


# Tab: Script
with tabs[1]:
    st.subheader("Script generation")
    if "article_text" not in st.session_state:
        st.info("Add a source article in the Source tab first.")
    else:
        topic_hint = st.text_input("Optional topic hint", help="e.g., Free AI tools 2025")
        if st.button("Generate Short package", type="primary"):
            try:
                pkg = llm.generate_short_package(
                    st.session_state["article_text"], topic_hint
                )
                st.session_state["short_pkg"] = pkg
                st.session_state["script_edit"] = pkg.get("script", "")
                st.success("Short package generated.")
            except Exception as exc:
                st.error(f"LLM generation failed: {exc}")

        short_pkg = st.session_state.get("short_pkg")
        if short_pkg:
            st.markdown(f"**Summary:** {short_pkg.get('summary', '')}")
            st.markdown("**Concepts:**")
            st.write(short_pkg.get("concepts", []))

            st.text_area(
                "Voiceover script",
                st.session_state.get("script_edit", short_pkg.get("script", "")),
                height=250,
                key="script_edit",
            )

            st.markdown("**On-screen text suggestions:**")
            for line in short_pkg.get("onscreen_text", []):
                st.write(f"• {line}")

            st.markdown("**Visual ideas:**")
            for idea in short_pkg.get("visual_ideas", []):
                st.write(f"- {idea}")

            st.markdown("**Metadata:**")
            st.write(f"Title: {short_pkg.get('title', '')}")
            st.write(f"Description: {short_pkg.get('description', '')}")
            st.write(f"Tags: {', '.join(short_pkg.get('tags', []))}")


# Tab: Voiceover
with tabs[2]:
    st.subheader("Voiceover")
    short_pkg = st.session_state.get("short_pkg")
    if not short_pkg:
        st.info("Generate a script in the Script tab first.")
    else:
        voice_name = st.selectbox(
            "Voice name",
            ["en-US-Standard-C", "en-US-Standard-D", "en-US-Neural2-C"],
        )
        if st.button("Generate TTS", type="primary"):
            script_text = st.session_state.get("script_edit") or short_pkg.get("script", "")
            try:
                audio_bytes = tts.generate_tts(script_text, voice_name=voice_name)
                st.session_state["voiceover_audio"] = audio_bytes
                st.success("Voiceover generated.")
            except Exception as exc:
                st.error(f"TTS generation failed: {exc}")

        audio_bytes = st.session_state.get("voiceover_audio")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="Download voiceover",
                data=audio_bytes,
                file_name="voiceover.mp3",
                mime="audio/mpeg",
            )


# Tab: Visuals
with tabs[3]:
    st.subheader("Visuals (prompts & previews)")
    short_pkg = st.session_state.get("short_pkg")
    if not short_pkg:
        st.info("Generate a script in the Script tab first.")
    else:
        visual_ideas = short_pkg.get("visual_ideas", [])
        if visual_ideas:
            for idx, prompt in enumerate(visual_ideas, 1):
                st.code(prompt, language="text")
        else:
            st.write("No visual ideas available.")

        if st.button("Generate preview images"):
            with st.spinner("Creating previews..."):
                previews = images.generate_preview_images(visual_ideas[:3])
                st.session_state["preview_images"] = previews

        previews = st.session_state.get("preview_images", [])
        if previews:
            st.image(previews, caption=["Preview" for _ in previews])


# Tab: Export
with tabs[4]:
    st.subheader("Export bundle")
    short_pkg = st.session_state.get("short_pkg")
    if not short_pkg:
        st.info("Generate a script in the Script tab first.")
    else:
        title = st.text_input("Title", value=short_pkg.get("title", ""))
        description = st.text_area("Description", value=short_pkg.get("description", ""))
        tags_str = st.text_input("Tags (comma-separated)", value=", ".join(short_pkg.get("tags", [])))
        script_text = st.session_state.get("script_edit") or short_pkg.get("script", "")
        st.text_area("Final script", value=script_text, height=200, key="final_script", disabled=True)

        voiceover_present = "voiceover_audio" in st.session_state
        st.markdown("**Bundle summary:**")
        st.write(f"Voiceover included: {voiceover_present}")
        st.write(f"Visual prompts: {len(short_pkg.get('visual_ideas', []))}")
        st.write(f"On-screen text lines: {len(short_pkg.get('onscreen_text', []))}")

        if st.button("Prepare export bundle", type="primary"):
            buffer = io.BytesIO()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            metadata = {"title": title, "description": description, "tags": tags}

            with ZipFile(buffer, "w") as zf:
                zf.writestr("script.txt", script_text)
                zf.writestr("metadata.json", json.dumps(metadata, indent=2))
                zf.writestr("visual_prompts.txt", "\n".join(short_pkg.get("visual_ideas", [])))
                zf.writestr("onscreen_text.txt", "\n".join(short_pkg.get("onscreen_text", [])))
                if voiceover_present:
                    zf.writestr("voiceover.mp3", st.session_state.get("voiceover_audio"))

            buffer.seek(0)
            st.download_button(
                label="Download short bundle",
                data=buffer,
                file_name="short_bundle.zip",
                mime="application/zip",
            )

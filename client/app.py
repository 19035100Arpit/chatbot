import os
import base64
import streamlit as st
from state.session import setup_session_state, is_chat_ready
from components.chat import (
    render_chat_history,
    render_download_chat_history,
    render_uploaded_files_expander,
    render_user_input
)
from components.sidebar import (
    render_model_selector,
    render_view_selector,
    sidebar_file_upload,
    sidebar_provider_change_check,
    sidebar_utilities
)
from components.inspector import render_inspect_query

# Robust path: go up one level from client/ to project root and into assets/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "images.png")

# Fallback inline SVG robot avatar if PNG missing
FALLBACK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none">
  <rect x="2" y="2" width="20" height="20" rx="4" fill="#0e1117"/>
  <g transform="translate(3,3)" fill="#4facfe">
    <rect x="3" y="3" width="10" height="6" rx="1.2" fill="#0f1724"/>
    <circle cx="4" cy="8" r="1.1" fill="#4facfe"/>
    <circle cx="9" cy="8" r="1.1" fill="#00f2fe"/>
    <rect x="2.5" y="11.2" width="11" height="1.6" rx="0.6" fill="#132029"/>
  </g>
</svg>
"""

def get_image_data_uri(image_path):
    """
    Return a data URI for the PNG if it exists, otherwise a data URI for the fallback SVG.
    This avoids FileNotFoundError and keeps UI consistent.
    """
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        return f"data:image/png;base64,{b64}"
    else:
        svg_b64 = base64.b64encode(FALLBACK_SVG.encode("utf-8")).decode()
        return f"data:image/svg+xml;base64,{svg_b64}"

logo_data_uri = get_image_data_uri(LOGO_PATH)

def header_html(logo_uri, ready=False, model_name="—"):
    status_color = "#22c55e" if ready else "#f59e0b"
    status_text = "READY" if ready else "INITIALIZING..."
    return f"""
    <style>
    /* Header container */
    .ai-header {{
        display: flex;
        gap: 18px;
        align-items: center;
        padding: 18px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(10,12,15,0.95), rgba(20,26,34,0.9));
        box-shadow: 0 8px 30px rgba(2,6,23,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
        margin-bottom: 18px;
    }}

    /* Logo card */
    .logo-card {{
        width: 72px;
        height: 72px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        position: relative;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(0,0,0,0.5);
    }}
    .logo-card::after {{
        content: "";
        position: absolute;
        left: -40%;
        top: -40%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 20%, rgba(79,172,254,0.12), transparent 12%),
                    radial-gradient(circle at 70% 80%, rgba(0,242,254,0.08), transparent 14%);
        transform: rotate(25deg);
        animation: drift 6s linear infinite;
        pointer-events: none;
    }}
    @keyframes drift {{
        0% {{ transform: rotate(0deg) translateX(0px); }}
        50% {{ transform: rotate(12deg) translateX(6px); }}
        100% {{ transform: rotate(0deg) translateX(0px); }}
    }}

    .logo-card img {{
        width: 56px;
        height: 56px;
        object-fit: contain;
        z-index: 2;
    }}

    /* Title block */
    .title-block h1 {{
        margin: 0;
        color: #e6eef8;
        font-size: 24px;
        letter-spacing: 0.3px;
        font-family: "Segoe UI", Roboto, sans-serif;
    }}
    .title-block p {{
        margin: 4px 0 0 0;
        color: #9fb0c8;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
        font-size: 12px;
    }}

    /* Status badge */
    .status-badge {{
        margin-left: 16px;
        display: inline-flex;
        gap: 10px;
        align-items: center;
        font-family: ui-monospace, monospace;
        color: #cfeffd;
    }}
    .pulse {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: {status_color};
        box-shadow: 0 0 0 0 {status_color};
        animation: pulse 2s infinite;
        box-shadow: 0 0 10px {status_color};
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.9); opacity: 1; box-shadow: 0 0 0 0 rgba(255,255,255,0.0); }}
        70% {{ transform: scale(1.4); opacity: 0.7; box-shadow: 0 0 24px 6px rgba(0,0,0,0.05); }}
        100% {{ transform: scale(0.9); opacity: 1; }}
    }}

    /* Accent bar */
    .accent-bar {{
        height: 6px;
        border-radius: 8px;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #7b61ff);
        margin-top: 12px;
        box-shadow: 0 6px 20px rgba(79,172,254,0.12);
    }}
    </style>

    <div class="ai-header">
      <div class="logo-card">
        <img src="{logo_uri}" alt="Aionos logo" />
      </div>
      <div style="flex:1">
        <div style="display:flex; align-items:baseline; gap:12px;">
          <div class="title-block">
            <h1>Aionos Cognition — RAG PDFBot</h1>
            <p>AI-Powered Retrieval-Augmented Intelligence · {model_name}</p>
          </div>
          <div class="status-badge">
            <div class="pulse" title="{status_text}"></div>
            <div style="font-size:12px; color:#cfeffd;">{status_text}</div>
          </div>
        </div>
        <div class="accent-bar"></div>
      </div>
    </div>
    """

def main():
    st.set_page_config(page_title="Aionos Cognition RAG PDFBot", layout="wide")
    # Ensure session state keys exist to avoid KeyErrors
    if "chat_ready" not in st.session_state:
        st.session_state["chat_ready"] = False
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = "Model: —"

    # Render header with dynamic ready status and model name
    header = header_html(logo_data_uri, ready=st.session_state["chat_ready"], model_name=st.session_state["model_name"])
    st.markdown(header, unsafe_allow_html=True)

    st.caption("📚 Chat seamlessly with multiple PDFs and retrieve context-rich answers — built by Aionos")

    setup_session_state()

    if st.session_state.get("chat_history"):
        render_download_chat_history()

    with st.sidebar:
        with st.expander("⚙️ Configuration", expanded=True):
            model_provider, model = render_model_selector()
            sidebar_file_upload(model_provider)
            sidebar_provider_change_check(model_provider, model)

        view_option = render_view_selector()
        sidebar_utilities()

    if not st.session_state.get(f"uploaded_files_{st.session_state.uploader_key}", []):
        st.info("📄 Please upload and submit PDFs to start chatting.")

    if st.session_state.get("unsubmitted_files", False):
        st.warning("📄 New PDFs uploaded. Please submit before chatting.")

    if st.session_state.get("chat_ready") and st.session_state.get("pdf_files", []):
        render_uploaded_files_expander()

    if view_option == "💬 Chat":
        if st.session_state.get("chat_history", []):
            render_chat_history()
        if is_chat_ready():
            render_user_input(model_provider, model)
    elif view_option == "🔬 Inspector":
        if is_chat_ready():
            render_inspect_query(model_provider)

if __name__ == "__main__":
    main()

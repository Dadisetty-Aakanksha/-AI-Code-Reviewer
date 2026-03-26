"""
app.py
Intelligent Code Analysis — AI-powered code reviewer built with Streamlit.
"""

import streamlit as st
import json
import time
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Code Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

/* Cards */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    text-align: center;
}
.metric-card h2 {
    font-size: 2.4rem;
    margin: 0;
    font-family: 'JetBrains Mono', monospace;
}
.metric-card p  { margin: 4px 0 0 0; color: #8b949e; font-size: 0.85rem; }

/* Issue badges */
.badge-error   { background:#3d1212; color:#f85149; border:1px solid #f85149; }
.badge-warning { background:#2d2108; color:#d29922; border:1px solid #d29922; }
.badge-info    { background:#0d1f2d; color:#58a6ff; border:1px solid #58a6ff; }
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
}

/* Grade circle */
.grade-circle {
    display: inline-flex;
    align-items: center; justify-content: center;
    width: 72px; height: 72px;
    border-radius: 50%;
    font-size: 2.2rem; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    border: 3px solid;
}
.grade-A { border-color:#3fb950; color:#3fb950; background:#0d2618; }
.grade-B { border-color:#58a6ff; color:#58a6ff; background:#0d1f2d; }
.grade-C { border-color:#d29922; color:#d29922; background:#2d2108; }
.grade-D { border-color:#f0883e; color:#f0883e; background:#2d1508; }
.grade-F { border-color:#f85149; color:#f85149; background:#3d1212; }

/* Issue list item */
.issue-item {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}
.issue-item code {
    font-family: 'JetBrains Mono', monospace;
    color: #79c0ff;
    font-size: 0.82rem;
}

/* Chat messages */
.chat-user {
    background: #1f2937; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 8px;
    text-align: right;
}
.chat-ai {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
}

/* Headings */
h1 { color: #e6edf3 !important; }
h2, h3 { color: #c9d1d9 !important; }

/* Streamlit overrides */
.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: #238636 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    background: #2ea043 !important;
}
div[data-testid="stProgress"] > div > div {
    background: #238636 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Code Reviewer")
    st.markdown("---")
    st.markdown("**Navigation**")
    page = st.radio(
        "",
        ["📝 Code Editor", "📊 Analysis Report", "🔒 Security Audit",
         "💬 AI Assistant", "📜 History", "⚙️ Configuration"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Settings**")
    run_ai = st.toggle("Enable AI Review (Groq)", value=True)
    language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++"])
    st.markdown("---")
    st.markdown(
        "<small style='color:#8b949e'>Powered by Groq LLaMA 3.1<br>Built with Streamlit</small>",
        unsafe_allow_html=True,
    )


# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "code" not in st.session_state:
    st.session_state.code = ""


# ── Helper ────────────────────────────────────────────────────────────────────
SEVERITY_ICON = {"error": "🔴", "warning": "🟡", "info": "🔵"}
GRADE_COLOR   = {"A": "#3fb950", "B": "#58a6ff", "C": "#d29922", "D": "#f0883e", "F": "#f85149"}


def score_color(score: int) -> str:
    if score >= 90: return "#3fb950"
    if score >= 75: return "#58a6ff"
    if score >= 60: return "#d29922"
    if score >= 40: return "#f0883e"
    return "#f85149"


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Code Editor
# ══════════════════════════════════════════════════════════════════════════════
if "Code Editor" in page:
    st.markdown("# 🔍 Intelligent Code Analysis")
    st.markdown(
        "<p style='color:#8b949e'>Automated code review, security auditing, and optimization recommendations</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col_editor, col_tip = st.columns([3, 1])
    with col_editor:
        st.markdown("### 📋 Source Code Input")
    with col_tip:
        st.markdown(
            "<p style='color:#8b949e; text-align:right; padding-top:8px'>Paste Python code below</p>",
            unsafe_allow_html=True,
        )

    code_input = st.text_area(
        "",
        value=st.session_state.code,
        height=380,
        placeholder="Paste your Python code here...",
        label_visibility="collapsed",
    )
    st.session_state.code = code_input

    col_btn, col_clear = st.columns([1, 5])
    with col_btn:
        analyze_btn = st.button("▶  Analyze Code", use_container_width=True)
    with col_clear:
        if st.button("🗑 Clear", use_container_width=False):
            st.session_state.code = ""
            st.rerun()

    if analyze_btn:
        if not code_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Running analysis…"):
                from ai_code_reviewer.code_analyzer import analyze_code
                result = analyze_code(code_input, run_ai=run_ai)
                result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result["code_snippet"] = code_input[:200]
                st.session_state.last_result = result
                st.session_state.history.insert(0, result)
            st.success("✅ Analysis complete! Switch to **Analysis Report** in the sidebar.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Analysis Report
# ══════════════════════════════════════════════════════════════════════════════
elif "Analysis Report" in page:
    st.markdown("# 📊 Analysis Report")
    st.markdown("---")

    if not st.session_state.last_result:
        st.info("No analysis yet. Go to **Code Editor**, paste code, and click **Analyze Code**.")
    else:
        r = st.session_state.last_result
        m = r["metrics"]
        s = r["issue_summary"]

        # ── Score + Grade ──────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        score = r["quality_score"]
        grade = r["grade"]

        with c1:
            color = score_color(score)
            st.markdown(f"""
            <div class="metric-card">
              <h2 style="color:{color}">{score}</h2>
              <p>Quality Score</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card" style="padding-top:10px">
              <div class="grade-circle grade-{grade}">{grade}</div>
              <p style="margin-top:6px">Grade</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
              <h2 style="color:#f85149">{s['error']}</h2>
              <p>Errors</p>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
              <h2 style="color:#d29922">{s['warning']}</h2>
              <p>Warnings</p>
            </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""
            <div class="metric-card">
              <h2 style="color:#58a6ff">{s['info']}</h2>
              <p>Suggestions</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Metrics row ────────────────────────────────────────────────────
        st.markdown("### 📏 Code Metrics")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Total Lines",     m["total_lines"])
        mc2.metric("Code Lines",      m["code_lines"])
        mc3.metric("Functions",       m["function_count"])
        mc4.metric("Classes",         m["class_count"])

        st.markdown("---")

        # ── Syntax errors ──────────────────────────────────────────────────
        if r["parse"]["syntax_errors"]:
            st.markdown("### 🚨 Syntax Errors")
            for err in r["parse"]["syntax_errors"]:
                st.error(err)

        # ── Issues list ────────────────────────────────────────────────────
        st.markdown("### 🔎 Static Analysis Issues")
        if r["issues"]:
            for issue in r["issues"]:
                sev  = issue["severity"]
                icon = SEVERITY_ICON.get(sev, "⚪")
                line = issue["line"]
                msg  = issue["message"]
                st.markdown(
                    f'<div class="issue-item">'
                    f'{icon} <span class="badge badge-{sev}">{sev.upper()}</span>'
                    f'<code>Line {line}</code>  {msg}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("🎉 No static issues found!")

        # ── AI Suggestions ─────────────────────────────────────────────────
        ai = r.get("ai", {})
        if ai.get("summary"):
            st.markdown("---")
            st.markdown("### 🤖 AI Review Summary")
            st.info(ai["summary"])

        if ai.get("suggestions"):
            st.markdown("#### 💡 Suggestions")
            for s_item in ai["suggestions"]:
                st.markdown(f"- {s_item}")

        if ai.get("optimizations"):
            st.markdown("#### ⚡ Optimizations")
            for opt in ai["optimizations"]:
                st.markdown(f"- {opt}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Security Audit
# ══════════════════════════════════════════════════════════════════════════════
elif "Security Audit" in page:
    st.markdown("# 🔒 Security Audit")
    st.markdown("---")

    if not st.session_state.last_result:
        st.info("Run an analysis first from the **Code Editor** tab.")
    else:
        r = st.session_state.last_result

        # Static security issues
        security_static = [i for i in r["issues"] if i["severity"] == "error"]
        st.markdown("### 🔴 Critical Issues (Static)")
        if security_static:
            for issue in security_static:
                st.error(f"Line {issue['line']}: {issue['message']}")
        else:
            st.success("No critical static issues found.")

        st.markdown("---")

        # AI security issues
        ai_security = r.get("ai", {}).get("security_issues", [])
        st.markdown("### 🤖 AI-Detected Security Issues")
        if ai_security:
            for issue in ai_security:
                st.warning(issue)
        else:
            st.success("No AI-detected security issues.")

        st.markdown("---")
        st.markdown("### 🛡️ Security Checklist")
        checks = [
            ("No use of eval()/exec()", not any("eval" in i["message"] or "exec" in i["message"] for i in r["issues"])),
            ("No bare except clauses",  not any("Bare" in i["message"] for i in r["issues"])),
            ("No mutable default args", not any("mutable" in i["message"].lower() for i in r["issues"])),
            ("No unused imports",       not any("Unused import" in i["message"] for i in r["issues"])),
        ]
        for check, passed in checks:
            icon = "✅" if passed else "❌"
            st.markdown(f"{icon} {check}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: AI Assistant
# ══════════════════════════════════════════════════════════════════════════════
elif "AI Assistant" in page:
    st.markdown("# 💬 AI Assistant")
    st.markdown("<p style='color:#8b949e'>Ask anything about your code</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Display chat history
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">👤 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-ai">🤖 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    user_input = st.text_input("Ask about your code…", key="chat_input")
    if st.button("Send 💬") and user_input.strip():
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking…"):
            from ai_code_reviewer.ai_suggestor import get_chat_response
            response = get_chat_response(user_input, st.session_state.code)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: History
# ══════════════════════════════════════════════════════════════════════════════
elif "History" in page:
    st.markdown("# 📜 Analysis History")
    st.markdown("---")

    if not st.session_state.history:
        st.info("No history yet. Run some analyses first!")
    else:
        for i, entry in enumerate(st.session_state.history):
            with st.expander(f"🕐 {entry.get('timestamp', 'Unknown')}  —  Score: {entry['quality_score']}  Grade: {entry['grade']}"):
                col1, col2 = st.columns(2)
                col1.metric("Score", entry["quality_score"])
                col2.metric("Grade", entry["grade"])
                st.markdown("**Code snippet:**")
                st.code(entry.get("code_snippet", "")[:300] + "…", language="python")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Configuration
# ══════════════════════════════════════════════════════════════════════════════
elif "Configuration" in page:
    st.markdown("# ⚙️ Configuration")
    st.markdown("---")

    st.markdown("### 🔑 API Configuration")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    current_key = os.getenv("GROQ_API_KEY", "")
    masked = ("*" * (len(current_key) - 4) + current_key[-4:]) if len(current_key) > 4 else "Not set"
    st.markdown(f"**Current Groq API Key:** `{masked}`")
    st.markdown(
        "Get a free API key at [console.groq.com](https://console.groq.com) (free tier available)",
        unsafe_allow_html=False,
    )

    st.markdown("---")
    st.markdown("### 📁 How to set your API key")
    st.code("# Create a .env file in the project root and add:\nGROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx", language="bash")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
| Item | Detail |
|------|--------|
| **Framework** | Streamlit |
| **AI Provider** | Groq (LLaMA 3.1 8B Instant) |
| **Static Analysis** | Python AST |
| **Language** | Python 3.8+ |
    """)

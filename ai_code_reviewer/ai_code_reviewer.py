"""
ai_code_reviewer.py
Main Reflex application — Intelligent Code Analysis UI.
"""

import reflex as rx
from typing import List
from ai_code_reviewer.code_analyzer import analyze_code


# ── Typed classes for Reflex State ────────────────────────────────────────────
class Issue(rx.Base):
    severity: str = ""
    line: int = 0
    message: str = ""


class ChatMessage(rx.Base):
    role: str = ""
    content: str = ""


class HistoryEntry(rx.Base):
    timestamp: str = ""
    score: int = 0
    grade: str = ""
    snippet: str = ""


# ── State ─────────────────────────────────────────────────────────────────────
class State(rx.State):
    code: str = ""
    active_tab: str = "editor"
    is_analyzing: bool = False
    is_chatting: bool = False

    quality_score: int = 0
    grade: str = "-"
    total_lines: int = 0
    code_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    issues: List[Issue] = []
    syntax_errors: List[str] = []
    ai_summary: str = ""
    ai_suggestions: List[str] = []
    ai_security: List[str] = []
    ai_optimizations: List[str] = []

    chat_input: str = ""
    chat_messages: List[ChatMessage] = []

    history: List[HistoryEntry] = []
    run_ai: bool = True

    def set_code(self, value: str):
        self.code = value

    def set_chat_input(self, value: str):
        self.chat_input = value

    def set_run_ai(self, value: bool):
        self.run_ai = value

    def switch_tab(self, tab: str):
        self.active_tab = tab

    def clear_code(self):
        self.code = ""

    async def run_analysis(self):
        if not self.code.strip():
            return
        self.is_analyzing = True
        yield

        try:
            result = analyze_code(self.code, run_ai=self.run_ai)

            self.quality_score  = result["quality_score"]
            self.grade          = result["grade"]
            self.total_lines    = result["metrics"]["total_lines"]
            self.code_lines     = result["metrics"]["code_lines"]
            self.function_count = result["metrics"]["function_count"]
            self.class_count    = result["metrics"]["class_count"]
            self.error_count    = result["issue_summary"]["error"]
            self.warning_count  = result["issue_summary"]["warning"]
            self.info_count     = result["issue_summary"]["info"]

            self.issues = [
                Issue(
                    severity=i.get("severity", "info"),
                    line=i.get("line", 0),
                    message=i.get("message", ""),
                )
                for i in result["issues"]
            ]

            self.syntax_errors    = result["parse"]["syntax_errors"]
            self.ai_summary       = result["ai"].get("summary", "")
            self.ai_suggestions   = result["ai"].get("suggestions", [])
            self.ai_security      = result["ai"].get("security_issues", [])
            self.ai_optimizations = result["ai"].get("optimizations", [])

            import datetime
            self.history.insert(0, HistoryEntry(
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                score=self.quality_score,
                grade=self.grade,
                snippet=self.code[:120] + ("..." if len(self.code) > 120 else ""),
            ))

            self.active_tab = "report"

        except Exception as e:
            self.ai_summary = f"Analysis error: {str(e)}"

        self.is_analyzing = False
        yield

    async def send_chat(self):
        if not self.chat_input.strip() or self.is_chatting:
            return

        msg = self.chat_input
        self.chat_input = ""
        self.is_chatting = True
        self.chat_messages.append(ChatMessage(role="user", content=msg))
        yield  # ← push user message to UI immediately

        try:
            from ai_code_reviewer.ai_suggestor import get_chat_response
            reply = get_chat_response(msg, self.code)
        except Exception as e:
            reply = f"Error calling AI: {str(e)}"

        self.chat_messages.append(ChatMessage(role="assistant", content=reply))
        self.is_chatting = False
        yield  # ← push AI reply to UI

    def clear_chat(self):
        self.chat_messages = []
        self.is_chatting = False


# ── Reusable components ───────────────────────────────────────────────────────
def sidebar_item(label: str, tab: str, icon: str) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.text(icon, font_size="1rem"),
            rx.text(label, font_size="0.88rem"),
            spacing="2",
            align="center",
        ),
        on_click=State.switch_tab(tab),
        background=rx.cond(State.active_tab == tab, "#21262d", "transparent"),
        color=rx.cond(State.active_tab == tab, "#e6edf3", "#8b949e"),
        border=rx.cond(State.active_tab == tab, "1px solid #30363d", "1px solid transparent"),
        border_radius="8px",
        padding="10px 14px",
        width="100%",
        text_align="left",
        cursor="pointer",
        _hover={"background": "#21262d", "color": "#e6edf3"},
        margin_bottom="4px",
    )


def metric_card(value: rx.Var, label: str, color: str = "#e6edf3") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(value, font_size="2rem", font_weight="700",
                    color=color, font_family="'JetBrains Mono', monospace"),
            rx.text(label, font_size="0.8rem", color="#8b949e"),
            spacing="1", align="center",
        ),
        background="#161b22",
        border="1px solid #30363d",
        border_radius="10px",
        padding="16px",
        text_align="center",
        flex="1",
    )


def issue_item(issue: Issue) -> rx.Component:
    sev_color = rx.match(
        issue.severity,
        ("error",   "#f85149"),
        ("warning", "#d29922"),
        ("info",    "#58a6ff"),
        "#8b949e",
    )
    sev_bg = rx.match(
        issue.severity,
        ("error",   "#3d1212"),
        ("warning", "#2d2108"),
        ("info",    "#0d1f2d"),
        "#161b22",
    )
    return rx.box(
        rx.hstack(
            rx.badge(
                issue.severity.upper(),
                color=sev_color,
                background=sev_bg,
                border_radius="10px",
                padding="2px 8px",
                font_size="0.72rem",
                font_weight="700",
            ),
            rx.text(
                "Line " + issue.line.to_string() + ": " + issue.message,
                font_size="0.88rem",
                color="#c9d1d9",
            ),
            spacing="3", align="center", flex_wrap="wrap",
        ),
        background="#161b22",
        border="1px solid #30363d",
        border_radius="8px",
        padding="10px 14px",
        margin_bottom="8px",
    )


def chat_bubble(msg: ChatMessage) -> rx.Component:
    return rx.cond(
        msg.role == "user",
        rx.box(
            rx.hstack(
                rx.spacer(),
                rx.box(
                    rx.text(msg.content, color="#e6edf3", font_size="0.9rem"),
                    background="#1f6feb",
                    border_radius="12px 12px 2px 12px",
                    padding="10px 14px",
                    max_width="80%",
                ),
            ),
            width="100%",
            margin_bottom="10px",
        ),
        rx.box(
            rx.hstack(
                rx.box(
                    rx.text("🤖", font_size="1rem"),
                    background="#21262d",
                    border_radius="50%",
                    padding="6px",
                    flex_shrink="0",
                ),
                rx.box(
                    rx.text(msg.content, color="#c9d1d9", font_size="0.9rem",
                            line_height="1.5"),
                    background="#161b22",
                    border="1px solid #30363d",
                    border_radius="2px 12px 12px 12px",
                    padding="10px 14px",
                    max_width="80%",
                ),
                spacing="2", align="start",
            ),
            width="100%",
            margin_bottom="10px",
        ),
    )


def history_card(entry: HistoryEntry) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(entry.timestamp, color="#8b949e", font_size="0.8rem"),
                rx.text(entry.snippet, color="#c9d1d9", font_size="0.85rem",
                        font_family="'JetBrains Mono', monospace"),
                spacing="1", align="stretch", flex="1",
            ),
            rx.vstack(
                rx.text(entry.score.to_string(), color="#3fb950",
                        font_size="1.4rem", font_weight="700"),
                rx.text("Grade: " + entry.grade, color="#58a6ff", font_size="0.85rem"),
                spacing="1", align="center",
            ),
            spacing="3", align="start",
        ),
        background="#161b22",
        border="1px solid #30363d",
        border_radius="10px",
        padding="14px 18px",
        margin_bottom="10px",
    )


def section_card(*children, title: str = "") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(title, font_size="1rem", font_weight="700",
                    color="#e6edf3", margin_bottom="12px") if title else rx.box(),
            *children,
            spacing="2", align="stretch",
        ),
        background="#161b22",
        border="1px solid #30363d",
        border_radius="12px",
        padding="20px",
        margin_bottom="16px",
        width="100%",
    )


# ── Tab pages ─────────────────────────────────────────────────────────────────
def editor_tab() -> rx.Component:
    return rx.vstack(
        rx.text("📋 Source Code Input", font_size="1rem",
                font_weight="600", color="#e6edf3"),
        rx.text_area(
            value=State.code,
            on_change=State.set_code,
            placeholder="Paste your Python code here...",
            height="420px",
            width="100%",
            background="#0d1117",
            border="1px solid #30363d",
            border_radius="8px",
            color="#e6edf3",
            font_family="'JetBrains Mono', monospace",
            font_size="0.9rem",
            padding="14px",
            _focus={"border_color": "#58a6ff", "outline": "none"},
            resize="vertical",
        ),
        rx.hstack(
            rx.button(
                rx.cond(State.is_analyzing, "⏳ Analyzing...", "▶  Analyze Code"),
                on_click=State.run_analysis,
                background="#238636",
                color="white",
                border="none",
                border_radius="8px",
                padding="10px 24px",
                font_weight="600",
                font_size="0.95rem",
                cursor="pointer",
                _hover={"background": "#2ea043"},
                disabled=State.is_analyzing,
            ),
            rx.button(
                "🗑 Clear",
                on_click=State.clear_code,
                background="transparent",
                color="#8b949e",
                border="1px solid #30363d",
                border_radius="8px",
                padding="10px 20px",
                cursor="pointer",
                _hover={"background": "#21262d", "color": "#e6edf3"},
            ),
            rx.hstack(
                rx.text("AI Review", color="#8b949e", font_size="0.88rem"),
                rx.switch(checked=State.run_ai, on_change=State.set_run_ai,
                          color_scheme="green"),
                spacing="2", align="center",
            ),
            spacing="3", align="center",
        ),
        spacing="3", align="stretch", width="100%",
    )


def report_tab() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            metric_card(State.quality_score.to_string(), "Quality Score", color="#3fb950"),
            metric_card(State.grade,                     "Grade",         color="#58a6ff"),
            metric_card(State.error_count.to_string(),   "Errors",        color="#f85149"),
            metric_card(State.warning_count.to_string(), "Warnings",      color="#d29922"),
            metric_card(State.info_count.to_string(),    "Info",          color="#58a6ff"),
            spacing="3", width="100%",
        ),

        section_card(
            rx.hstack(
                metric_card(State.total_lines.to_string(),    "Total Lines"),
                metric_card(State.code_lines.to_string(),     "Code Lines"),
                metric_card(State.function_count.to_string(), "Functions"),
                metric_card(State.class_count.to_string(),    "Classes"),
                spacing="3", width="100%",
            ),
            title="📏 Code Metrics",
        ),

        rx.cond(
            State.syntax_errors.length() > 0,
            section_card(
                rx.foreach(
                    State.syntax_errors,
                    lambda e: rx.box(
                        rx.text(e, color="#f85149", font_size="0.9rem"),
                        background="#3d1212",
                        border="1px solid #f85149",
                        border_radius="8px",
                        padding="10px 14px",
                        margin_bottom="6px",
                    ),
                ),
                title="🚨 Syntax Errors",
            ),
            rx.box(),
        ),

        section_card(
            rx.cond(
                State.issues.length() > 0,
                rx.foreach(State.issues, issue_item),
                rx.text("🎉 No static issues found!", color="#3fb950", font_size="0.95rem"),
            ),
            title="🔎 Static Analysis Issues",
        ),

        rx.cond(
            State.ai_summary != "",
            section_card(
                rx.box(
                    rx.text(State.ai_summary, color="#c9d1d9",
                            font_size="0.92rem", line_height="1.6"),
                    background="#0d1f2d",
                    border="1px solid #1f6feb",
                    border_radius="8px",
                    padding="14px",
                    margin_bottom="12px",
                ),
                rx.cond(
                    State.ai_suggestions.length() > 0,
                    rx.vstack(
                        rx.text("💡 Suggestions", font_weight="600",
                                color="#e6edf3", font_size="0.9rem"),
                        rx.foreach(
                            State.ai_suggestions,
                            lambda s: rx.text("• " + s, color="#c9d1d9", font_size="0.88rem"),
                        ),
                        spacing="1", align="stretch",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    State.ai_optimizations.length() > 0,
                    rx.vstack(
                        rx.text("⚡ Optimizations", font_weight="600",
                                color="#e6edf3", font_size="0.9rem", margin_top="10px"),
                        rx.foreach(
                            State.ai_optimizations,
                            lambda o: rx.text("• " + o, color="#c9d1d9", font_size="0.88rem"),
                        ),
                        spacing="1", align="stretch",
                    ),
                    rx.box(),
                ),
                title="🤖 AI Review",
            ),
            rx.box(),
        ),

        spacing="3", align="stretch", width="100%",
    )


def security_tab() -> rx.Component:
    return rx.vstack(
        section_card(
            rx.cond(
                State.error_count > 0,
                rx.foreach(
                    State.issues,
                    lambda i: rx.cond(
                        i.severity == "error",
                        rx.box(
                            rx.text("🔴 Line " + i.line.to_string() + ": " + i.message,
                                    color="#f85149", font_size="0.9rem"),
                            background="#3d1212",
                            border="1px solid #f85149",
                            border_radius="8px",
                            padding="10px 14px",
                            margin_bottom="6px",
                        ),
                        rx.box(),
                    ),
                ),
                rx.text("✅ No critical issues found.", color="#3fb950"),
            ),
            title="🔴 Critical Issues",
        ),
        section_card(
            rx.cond(
                State.ai_security.length() > 0,
                rx.foreach(
                    State.ai_security,
                    lambda s: rx.box(
                        rx.text("⚠️ " + s, color="#d29922", font_size="0.9rem"),
                        background="#2d2108",
                        border="1px solid #d29922",
                        border_radius="8px",
                        padding="10px 14px",
                        margin_bottom="6px",
                    ),
                ),
                rx.text("✅ No AI-detected security issues.", color="#3fb950"),
            ),
            title="🤖 AI Security Issues",
        ),
        spacing="3", align="stretch", width="100%",
    )


def chat_tab() -> rx.Component:
    return rx.vstack(
        # Chat window
        rx.box(
            rx.cond(
                State.chat_messages.length() > 0,
                rx.vstack(
                    rx.foreach(State.chat_messages, chat_bubble),
                    rx.cond(
                        State.is_chatting,
                        rx.box(
                            rx.hstack(
                                rx.box(
                                    rx.text("🤖", font_size="1rem"),
                                    background="#21262d",
                                    border_radius="50%",
                                    padding="6px",
                                ),
                                rx.text("Thinking...", color="#8b949e",
                                        font_size="0.9rem", font_style="italic"),
                                spacing="2", align="center",
                            ),
                            margin_bottom="10px",
                        ),
                        rx.box(),
                    ),
                    spacing="0", align="stretch", width="100%",
                ),
                rx.vstack(
                    rx.text("💬", font_size="2rem"),
                    rx.text("Ask anything about your code!",
                            color="#8b949e", font_size="0.95rem"),
                    rx.text("Paste code in the Editor tab first, then ask questions here.",
                            color="#484f58", font_size="0.82rem"),
                    spacing="2", align="center",
                    padding_top="40px",
                ),
            ),
            height="460px",
            overflow_y="auto",
            padding="16px",
            background="#0d1117",
            border="1px solid #30363d",
            border_radius="10px",
            width="100%",
        ),

        # Input row
        rx.hstack(
            rx.input(
                value=State.chat_input,
                on_change=State.set_chat_input,
                placeholder="Ask about your code… (e.g. 'What does this function do?')",
                background="#161b22",
                border="1px solid #30363d",
                border_radius="8px",
                color="#e6edf3",
                padding="10px 14px",
                flex="1",
                _focus={"border_color": "#238636", "outline": "none"},
                _placeholder={"color": "#484f58"},
                on_key_down=lambda k: rx.cond(
                    k == "Enter",
                    State.send_chat(),
                    rx.noop(),
                ),
            ),
            rx.button(
                rx.cond(State.is_chatting, "⏳", "Send ➤"),
                on_click=State.send_chat,
                background=rx.cond(State.is_chatting, "#21262d", "#238636"),
                color="white",
                border="none",
                border_radius="8px",
                padding="10px 20px",
                font_weight="600",
                cursor="pointer",
                _hover={"background": "#2ea043"},
                disabled=State.is_chatting,
            ),
            rx.button(
                "🗑",
                on_click=State.clear_chat,
                background="transparent",
                color="#8b949e",
                border="1px solid #30363d",
                border_radius="8px",
                padding="10px 14px",
                cursor="pointer",
                _hover={"background": "#21262d", "color": "#e6edf3"},
                title="Clear chat",
            ),
            spacing="2", width="100%",
        ),

        # Tip
        rx.text(
            "💡 Tip: Paste your code in the Code Editor tab first — the AI will use it as context.",
            color="#484f58", font_size="0.8rem",
        ),

        spacing="3", align="stretch", width="100%",
    )


def history_tab() -> rx.Component:
    return rx.cond(
        State.history.length() > 0,
        rx.vstack(
            rx.foreach(State.history, history_card),
            spacing="1", align="stretch", width="100%",
        ),
        rx.vstack(
            rx.text("📜", font_size="2rem"),
            rx.text("No history yet.", color="#8b949e", font_size="0.95rem"),
            rx.text("Run an analysis first!", color="#484f58", font_size="0.85rem"),
            spacing="2", align="center", padding_top="40px",
        ),
    )


# ── Main layout ───────────────────────────────────────────────────────────────
def index() -> rx.Component:
    return rx.box(
        rx.hstack(
            # Sidebar
            rx.vstack(
                rx.vstack(
                    rx.text("🔍", font_size="1.6rem"),
                    rx.text("Intelligent", font_size="0.85rem",
                            font_weight="700", color="#e6edf3"),
                    rx.text("Code Analysis", font_size="0.85rem", color="#8b949e"),
                    spacing="0", align="center", padding_bottom="20px",
                ),
                rx.divider(border_color="#30363d", margin_bottom="12px"),
                rx.text("NAVIGATION", color="#484f58", font_size="0.72rem",
                        font_weight="600", letter_spacing="0.08em",
                        padding_left="4px", margin_bottom="8px"),
                sidebar_item("Code Editor",     "editor",   "📝"),
                sidebar_item("Analysis Report", "report",   "📊"),
                sidebar_item("Security Audit",  "security", "🔒"),
                sidebar_item("AI Assistant",    "chat",     "💬"),
                sidebar_item("History",         "history",  "📜"),
                rx.divider(border_color="#30363d", margin_top="12px", margin_bottom="12px"),
                rx.text("Powered by Groq LLaMA 3.1",
                        color="#484f58", font_size="0.75rem", text_align="center"),
                spacing="0", align="stretch",
                width="220px", min_height="100vh",
                background="#161b22",
                border_right="1px solid #30363d",
                padding="24px 16px",
                flex_shrink="0",
            ),

            # Main content
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Intelligent Code Analysis",
                                font_size="1.6rem", font_weight="700", color="#e6edf3"),
                        rx.text(
                            "Automated code review, security auditing, and optimization recommendations",
                            color="#8b949e", font_size="0.9rem",
                        ),
                        spacing="1", align="start",
                    ),
                    rx.spacer(),
                    spacing="3", width="100%", align="center",
                ),
                rx.divider(border_color="#30363d", margin_y="4px"),

                rx.cond(State.active_tab == "editor",   editor_tab(),   rx.box()),
                rx.cond(State.active_tab == "report",   report_tab(),   rx.box()),
                rx.cond(State.active_tab == "security", security_tab(), rx.box()),
                rx.cond(State.active_tab == "chat",     chat_tab(),     rx.box()),
                rx.cond(State.active_tab == "history",  history_tab(),  rx.box()),

                spacing="4", align="stretch", flex="1",
                padding="28px 32px", min_height="100vh", overflow_y="auto",
            ),
            spacing="0", align="start", width="100%",
        ),
        background="#0d1117",
        min_height="100vh",
        font_family="'Inter', sans-serif",
        color="#e6edf3",
        width="100%",
    )


# ── App ───────────────────────────────────────────────────────────────────────
app = rx.App(
    style={
        "background_color": "#0d1117",
        "color": "#e6edf3",
        "font_family": "Inter, sans-serif",
    }
)
app.add_page(index, route="/", title="Intelligent Code Analysis")

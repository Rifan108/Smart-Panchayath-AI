"""
Smart AI Panchayat – Multilingual Voice & AI Assistant Component
Floating drawer interface supporting English, Kannada, Hindi, Marathi, and Malayalam.
Provides live speech-to-text, natural Indic text-to-speech, data grounding, and Explain This integration.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from services.i18n import t

SUPPORTED_LANGUAGES = [
    {"label": "English (EN)", "value": "en"},
    {"label": "ಕನ್ನಡ (KN)", "value": "kn"},
    {"label": "हिन्दी (HI)", "value": "hi"},
    {"label": "मराठी (MR)", "value": "mr"},
    {"label": "മലയാളം (ML)", "value": "ml"},
    {"label": "தமிழ் (TA)", "value": "ta"},
    {"label": "తెలుగు (TE)", "value": "te"},
]


def create_voice_assistant_widget():
    """
    Constructs the floating trigger button, sliding conversation drawer,
    and all associated Dash stores and audio elements.
    """
    return html.Div(
        [
            # Floating Action Trigger Button
            html.Button(
                [
                    html.Span("🎙️", className="assistant-fab-icon"),
                    html.Span("AI Assistant", className="assistant-fab-text ms-2 d-none d-md-inline"),
                    html.Span(className="assistant-fab-pulse"),
                ],
                id="btn-open-assistant",
                className="assistant-fab-btn shadow-lg",
                title="Open Smart AI Panchayat Multilingual Voice Assistant",
                n_clicks=0,
            ),
            # Sliding Assistant Drawer
            html.Div(
                [
                    # Drawer Header
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("🎙️", style={"fontSize": "1.3rem"}, className="me-2"),
                                    html.Div(
                                        [
                                            html.H5("Smart AI Voice Assistant", className="mb-0 text-white", style={"fontSize": "1.05rem", "fontWeight": "700"}),
                                            html.Small("Institutional Multi-State Decision Intelligence", style={"color": "#93C5FD", "fontSize": "0.72rem"}),
                                        ]
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                            html.Div(
                                [
                                    html.Span("🟢 Grounded", className="badge bg-success me-2", style={"fontSize": "0.68rem"}),
                                    html.Button(
                                        "✕",
                                        id="btn-close-assistant",
                                        className="btn btn-sm btn-outline-light py-0 px-2",
                                        style={"borderRadius": "50%", "fontSize": "0.9rem"},
                                        n_clicks=0,
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                        ],
                        className="assistant-drawer-header p-3 d-flex justify-content-between align-items-center",
                        style={"background": "linear-gradient(135deg, #142D4E 0%, #245B91 100%)", "color": "#FFFFFF"},
                    ),
                    # Subheader Controls (Language + Current Location Sync)
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("📍 Jurisdiction: ", style={"fontWeight": "600", "color": "#475569"}),
                                    html.Span("All States (National)", id="assistant-jurisdiction-badge", style={"color": "#142D4E", "fontWeight": "700"}),
                                ],
                                className="mb-2 text-truncate",
                                style={"fontSize": "0.78rem"},
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label("Language:", className="mb-0 me-2 text-muted", style={"fontSize": "0.74rem", "fontWeight": "600"}),
                                            dcc.Dropdown(
                                                id="assistant-lang-selector",
                                                options=SUPPORTED_LANGUAGES,
                                                value="en",
                                                clearable=False,
                                                style={"width": "140px", "fontSize": "0.78rem"},
                                                className="light-dropdown",
                                            ),
                                        ],
                                        className="d-flex align-items-center",
                                    ),
                                    html.Div(
                                        [
                                            html.Button("🔊 Auto-Play", id="btn-toggle-autoplay", className="btn btn-xs btn-outline-secondary py-1 px-2", style={"fontSize": "0.72rem", "borderRadius": "12px", "whiteSpace": "nowrap"}, n_clicks=0),
                                        ],
                                        className="d-flex align-items-center ms-auto",
                                    ),
                                ],
                                className="d-flex justify-content-between align-items-center",
                            ),
                        ],
                        className="p-2 border-bottom",
                        style={"background": "#F8FAFC"},
                    ),
                    # Quick Suggestion Action Pills
                    html.Div(
                        [
                            html.Button("💡 Explain Budget", id="chip-explain-budget", className="assistant-chip-pill", n_clicks=0),
                            html.Button("📊 Ward Deficit Profile", id="chip-explain-deficit", className="assistant-chip-pill", n_clicks=0),
                            html.Button("👥 Census Demographics", id="chip-explain-demo", className="assistant-chip-pill", n_clicks=0),
                            html.Button("🏛️ Governance & MLA", id="chip-explain-gov", className="assistant-chip-pill", n_clicks=0),
                        ],
                        className="assistant-chips-container p-2 border-bottom d-flex gap-1 flex-wrap",
                        style={"background": "#FFFFFF"},
                    ),
                    # Message History Scroll Container
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("🎙️ Smart AI Panchayat Assistant", style={"fontWeight": "700", "color": "#142D4E", "fontSize": "0.85rem", "marginBottom": "4px"}),
                                    html.P(
                                        "Namaste! I am your AI Development Planning Assistant for Grama Panchayats. "
                                        "I understand all 6 dashboard modules, Census demographics, and SFC budget outlays. "
                                        "Speak or type in English, Kannada, Hindi, Marathi, or Malayalam.",
                                        style={"margin": "0", "fontSize": "0.82rem", "lineHeight": "1.4", "color": "#334155"},
                                    ),
                                ],
                                className="assistant-msg-bubble assistant-msg-bot p-3 mb-2 shadow-sm",
                                style={"background": "#F1F5F9", "borderRadius": "12px", "borderLeft": "4px solid #245B91"},
                            ),
                        ],
                        id="assistant-chat-history",
                        className="assistant-chat-history p-3 flex-grow-1 overflow-auto",
                        style={"minHeight": "280px", "maxHeight": "380px", "background": "#F8FAFC"},
                    ),
                    # Audio Status Waveform / Listening Indicator
                    html.Div(
                        [
                            html.Span("🔴 Listening...", id="assistant-stt-indicator", className="d-none text-danger fw-bold me-2", style={"fontSize": "0.78rem"}),
                            html.Span("🔊 Speaking...", id="assistant-tts-indicator", className="d-none text-primary fw-bold me-2", style={"fontSize": "0.78rem"}),
                        ],
                        id="assistant-status-bar",
                        className="px-3 py-1 text-muted text-end border-top",
                        style={"fontSize": "0.72rem", "background": "#FFFFFF", "minHeight": "24px"},
                    ),
                    # Bottom Input Dock (Microphone + Text Input + Send)
                    html.Div(
                        [
                            html.Div(
                                [
                                    # Microphone Button with STT trigger
                                    html.Button(
                                        "🎤",
                                        id="assistant-mic-btn",
                                        className="btn btn-outline-primary btn-sm me-2 rounded-circle",
                                        style={"width": "38px", "height": "38px", "fontSize": "1.1rem", "padding": "0", "display": "flex", "alignItems": "center", "justifyContent": "center"},
                                        title="Click to speak (Web Speech STT)",
                                        n_clicks=0,
                                    ),
                                    # Text input
                                    dcc.Input(
                                        id="assistant-text-input",
                                        type="text",
                                        placeholder="Ask in English, ಕನ್ನಡ, हिन्दी, मराठी, മലയാളം, தமிழ், తెలుగు...",
                                        className="form-control form-control-sm flex-grow-1",
                                        style={"fontSize": "0.85rem", "borderRadius": "20px"},
                                        debounce=False,
                                    ),
                                    # Send Button
                                    html.Button(
                                        "➤",
                                        id="assistant-send-btn",
                                        className="btn btn-primary btn-sm ms-2 rounded-circle",
                                        style={"width": "38px", "height": "38px", "fontSize": "0.95rem", "padding": "0", "background": "#142D4E", "borderColor": "#142D4E"},
                                        title="Send message",
                                        n_clicks=0,
                                    ),
                                ],
                                className="d-flex align-items-center",
                            ),
                        ],
                        className="assistant-drawer-dock p-3 border-top",
                        style={"background": "#FFFFFF"},
                    ),
                ],
                id="voice-assistant-panel",
                className="voice-assistant-panel shadow-lg d-none",
                style={
                    "position": "fixed",
                    "bottom": "85px",
                    "right": "28px",
                    "width": "420px",
                    "maxWidth": "92vw",
                    "borderRadius": "16px",
                    "background": "#FFFFFF",
                    "zIndex": 9999,
                    "overflow": "hidden",
                    "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.08)",
                    "border": "1px solid #CBD5E1",
                    "display": "flex",
                    "flexDirection": "column",
                },
            ),
            # Hidden Dynamic Audio Player
            html.Audio(id="assistant-audio-player", autoPlay=True, style={"display": "none"}),
            # Storage Containers for assistant state
            dcc.Store(id="assistant-open-store", data=False),
            dcc.Store(id="assistant-history-store", data=[]),
            dcc.Store(id="assistant-audio-store", data=""),
            dcc.Store(id="assistant-autoplay-store", data=True),
            dcc.Store(id="explain-this-trigger-store", data={}),
        ],
        id="voice-assistant-container",
    )





import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="BrandPulse — Social Media Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  CUSTOM CSS — Dark luxury theme
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #080c14;
    color: #e8eaf0;
}

.main { background: #080c14; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1221 0%, #080c14 100%);
    border-right: 1px solid #1e2a42;
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

/* ── Header banner ── */
.brand-header {
    background: linear-gradient(135deg, #0d1221 0%, #111827 50%, #0a1628 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.brand-header::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.brand-header::after {
    content: '';
    position: absolute; bottom: -40px; left: 30%;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(99,102,241,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.brand-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(90deg, #38bdf8 0%, #818cf8 60%, #c084fc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -0.5px;
}
.brand-header p {
    color: #64748b; font-size: 0.95rem;
    margin: 6px 0 0; font-weight: 300;
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #0d1627 0%, #111827 100%);
    border: 1px solid #1e2a42;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative; overflow: hidden;
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: #2563eb; }
.metric-card .icon {
    font-size: 1.8rem; margin-bottom: 0.5rem;
}
.metric-card .val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem; font-weight: 700; color: #f1f5f9;
}
.metric-card .label {
    font-size: 0.78rem; color: #64748b;
    text-transform: uppercase; letter-spacing: 1px;
    margin-top: 2px;
}
.metric-card .accent-line {
    position: absolute; bottom: 0; left: 0;
    height: 3px; width: 100%;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    border-radius: 0 0 14px 14px;
}

/* ── Result cards ── */
.result-up {
    background: linear-gradient(135deg, #052e16 0%, #0d1f13 100%);
    border: 1px solid #16a34a;
    border-radius: 16px; padding: 1.8rem 2rem;
    text-align: center;
}
.result-down {
    background: linear-gradient(135deg, #1c0a0a 0%, #1a0e0e 100%);
    border: 1px solid #dc2626;
    border-radius: 16px; padding: 1.8rem 2rem;
    text-align: center;
}
.result-up h2 { color: #4ade80; font-family: 'Syne', sans-serif; font-size: 2rem; margin: 0; }
.result-down h2 { color: #f87171; font-family: 'Syne', sans-serif; font-size: 2rem; margin: 0; }
.trend-badge-up {
    display: inline-block;
    background: rgba(74,222,128,0.15); color: #4ade80;
    border: 1px solid #16a34a;
    border-radius: 999px; padding: 4px 16px;
    font-size: 0.78rem; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 8px;
}
.trend-badge-down {
    display: inline-block;
    background: rgba(248,113,113,0.15); color: #f87171;
    border: 1px solid #dc2626;
    border-radius: 999px; padding: 4px 16px;
    font-size: 0.78rem; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 8px;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem; font-weight: 700;
    color: #cbd5e1;
    border-left: 3px solid #38bdf8;
    padding-left: 12px; margin: 1.5rem 0 1rem;
    letter-spacing: 0.3px;
}

/* ── Recommendation box ── */
.rec-box {
    background: #0d1627;
    border: 1px solid #1e3a5f;
    border-radius: 12px; padding: 1.2rem 1.5rem;
    font-size: 0.92rem; line-height: 1.7;
    color: #94a3b8;
}

/* ── Sentiment badge ── */
.sent-positive { color: #4ade80; font-weight: 600; }
.sent-negative { color: #f87171; font-weight: 600; }
.sent-neutral  { color: #94a3b8; font-weight: 600; }

/* ── Divider ── */
.stylish-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e3a5f, transparent);
    margin: 2rem 0;
}

/* ── Input styling ── */
.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    background: #0d1627 !important;
    border: 1px solid #1e2a42 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #4f46e5 100%) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(79,70,229,0.4) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1221 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #1e2a42 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #64748b !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5) !important;
    color: white !important;
}

/* ── Table ── */
.dataframe {
    background: #0d1627 !important;
    border-radius: 12px !important;
    border: 1px solid #1e2a42 !important;
}

/* ── Sidebar labels ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.2rem;
}
.sidebar-sub {
    color: #475569; font-size: 0.75rem;
    text-align: center; margin-bottom: 1.5rem;
}
.nav-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e3a5f, transparent);
    margin: 1rem 0;
}

/* ── Status dot ── */
.status-dot-green { color: #4ade80; }
.status-dot-red   { color: #f87171; }

/* ── Word chips ── */
.word-chip-pos {
    display: inline-block;
    background: rgba(74,222,128,0.12); color: #4ade80;
    border: 1px solid rgba(74,222,128,0.3);
    border-radius: 999px; padding: 2px 12px;
    font-size: 0.78rem; margin: 3px;
}
.word-chip-neg {
    display: inline-block;
    background: rgba(248,113,113,0.12); color: #f87171;
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 999px; padding: 2px 12px;
    font-size: 0.78rem; margin: 3px;
}

/* Hide streamlit default elements safely without breaking sidebar buttons */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background-color: transparent !important;
    background: transparent !important;
}
/* Ensure the toggle button remains visible and clickable */
header[data-testid="stHeader"] button {
    background: transparent !important;
    color: #e8eaf0 !important;
    box-shadow: none !important;
    transform: none !important;
}
.block-container { padding-top: 1.5rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def api_call(method: str, endpoint: str, payload: dict = None):
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            r = requests.get(url, timeout=8)
        else:
            r = requests.post(url, json=payload, timeout=8)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to FastAPI server. Make sure `uvicorn app:app --reload` is running on port 8000."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"API Error: {detail}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def confidence_gauge(value: float, label: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"size": 32, "color": "#f1f5f9", "family": "Syne"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#334155", "tickfont": {"color": "#64748b"}},
            "bar":  {"color": "#38bdf8", "thickness": 0.25},
            "bgcolor": "#0d1627",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40],  "color": "#1c1f2e"},
                {"range": [40, 70], "color": "#162032"},
                {"range": [70, 100],"color": "#0f2640"},
            ],
            "threshold": {
                "line": {"color": "#818cf8", "width": 3},
                "thickness": 0.8,
                "value": value,
            },
        },
        title={"text": label, "font": {"color": "#64748b", "size": 13, "family": "DM Sans"}},
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=10, l=20, r=20), height=200,
    )
    return fig


def sentiment_bar(score: int):
    color = "#4ade80" if score > 0 else ("#f87171" if score < 0 else "#94a3b8")
    fig = go.Figure(go.Bar(
        x=[abs(score)], y=["Score"],
        orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        text=[f"{score:+d}"],
        textposition="outside",
        textfont=dict(color=color, size=16, family="Syne"),
        width=[0.4],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=60), height=80,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 12]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div class="sidebar-logo">📡 BrandPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Social Media Brand Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Dashboard", "🔮  Predict Trend", "📊  Batch Analysis", "🧠  Sentiment Lab", "ℹ️  API Status"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    # API health in sidebar
    health_data, err = api_call("GET", "/health")
    if health_data:
        dot = "🟢" if health_data["status"] == "healthy" else "🟡"
        st.markdown(f"""
        <div style="background:#0d1221;border:1px solid #1e2a42;border-radius:10px;padding:1rem;">
            <div style="font-size:0.72rem;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">System Status</div>
            <div style="font-size:0.85rem;color:#94a3b8;">{dot} API: <span style="color:#f1f5f9">{health_data['status'].upper()}</span></div>
            <div style="font-size:0.85rem;color:#94a3b8;margin-top:4px">🏷️ Brands: <span style="color:#f1f5f9">{health_data['known_brands']}</span></div>
            <div style="font-size:0.85rem;color:#94a3b8;margin-top:4px">🤖 Model: <span style="color:#4ade80">Loaded ✓</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1c0a0a;border:1px solid #dc2626;border-radius:10px;padding:1rem;">
            <div style="color:#f87171;font-size:0.85rem;">🔴 API Offline</div>
            <div style="color:#64748b;font-size:0.75rem;margin-top:4px">Start FastAPI server first</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:2rem;color:#334155;font-size:0.72rem;text-align:center;">
        v1.0.0 · FYP Project · {datetime.now().strftime('%b %Y')}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════

if "🏠" in page:
    st.markdown("""
    <div class="brand-header">
        <h1>Brand Monitoring Intelligence</h1>
        <p>Real-time social media trend prediction · Sentiment analysis · Powered by Random Forest ML</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch brand data
    brands_data, err = api_call("GET", "/brands")

    col1, col2, col3, col4 = st.columns(4)
    cards = [
        ("📦", str(brands_data["total_brands"] if brands_data else "—"), "BRANDS MONITORED", "#38bdf8"),
        ("🌐", str(brands_data["total_platforms"] if brands_data else "—"), "PLATFORMS TRACKED", "#818cf8"),
        ("🤖", "RF Classifier", "ML MODEL", "#4ade80"),
        ("⚡", "Real-time", "ANALYSIS MODE", "#f59e0b"),
    ]
    for col, (icon, val, label, color) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">{icon}</div>
                <div class="val" style="color:{color}">{val}</div>
                <div class="label">{label}</div>
                <div class="accent-line" style="background:linear-gradient(90deg,{color},transparent)"></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="stylish-divider"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-title">Supported Brands</div>', unsafe_allow_html=True)
        if brands_data:
            brands = brands_data["known_brands"]
            # Display as grid chips
            chips_html = ""
            for b in brands:
                chips_html += f'<span style="display:inline-block;background:#0d1627;border:1px solid #1e3a5f;border-radius:8px;padding:5px 14px;margin:4px;font-size:0.82rem;color:#94a3b8;">{b}</span>'
            st.markdown(f'<div style="line-height:2.2">{chips_html}</div>', unsafe_allow_html=True)
        else:
            st.error("Could not fetch brands from API.")

    with col_r:
        st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
        steps = [
            ("1", "Input brand name, platform, likes & shares"),
            ("2", "Paste a customer review comment"),
            ("3", "NLP engine scores the sentiment"),
            ("4", "Random Forest predicts UP / DOWN trend"),
            ("5", "Get confidence score & actionable advice"),
        ]
        for num, text in steps:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;margin-bottom:10px;">
                <div style="background:linear-gradient(135deg,#1d4ed8,#4f46e5);color:white;
                    border-radius:50%;width:24px;height:24px;display:flex;align-items:center;
                    justify-content:center;font-size:0.72rem;font-weight:700;flex-shrink:0;
                    margin-right:12px;margin-top:2px;">{num}</div>
                <div style="color:#94a3b8;font-size:0.88rem;line-height:1.5">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="stylish-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Platforms Coverage</div>', unsafe_allow_html=True)
    if brands_data and brands_data["known_platforms"]:
        platforms = brands_data["known_platforms"]
        fig = px.bar(
            x=platforms, y=[1]*len(platforms),
            color=platforms,
            color_discrete_sequence=["#38bdf8","#818cf8","#4ade80","#f59e0b","#f87171","#c084fc"],
            labels={"x": "Platform", "y": ""},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False, height=200,
            margin=dict(t=10, b=30, l=10, r=10),
            xaxis=dict(color="#64748b", showgrid=False),
            yaxis=dict(showgrid=False, showticklabels=False),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Platform encoder not loaded — platform data unavailable.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: PREDICT TREND
# ═══════════════════════════════════════════════════════════════════

elif "🔮" in page:
    st.markdown("""
    <div class="brand-header">
        <h1>Trend Predictor</h1>
        <p>Enter brand details and get an AI-powered trend prediction with confidence score</p>
    </div>
    """, unsafe_allow_html=True)

    brands_data, _ = api_call("GET", "/brands")
    brand_list = brands_data["known_brands"] if brands_data else []
    platform_list = (brands_data["known_platforms"] if brands_data and brands_data["known_platforms"]
                     else ["Instagram", "Facebook", "TikTok", "Twitter", "YouTube"])

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="section-title">Brand Information</div>', unsafe_allow_html=True)

        brand_input = st.selectbox("Brand Name", options=brand_list, help="Select a brand from training data")
        platform    = st.selectbox("Platform", options=platform_list)

        c1, c2 = st.columns(2)
        with c1:
            likes  = st.number_input("👍 Likes", min_value=0, value=2500, step=100)
        with c2:
            shares = st.number_input("🔁 Shares", min_value=0, value=500, step=50)

        st.markdown('<div class="section-title">Customer Review</div>', unsafe_allow_html=True)

        input_mode = st.radio("Input Mode", ["Auto (from review text)", "Manual score override"],
                              horizontal=True, label_visibility="collapsed")

        comment, sentiment_override = "", None
        if "Auto" in input_mode:
            comment = st.text_area("Paste customer comment / review",
                                   placeholder="e.g. Zabardast quality! Best brand ever, love it!",
                                   height=120)
        else:
            sentiment_override = st.slider("Sentiment Score", min_value=-10, max_value=10, value=1)
            st.markdown(f"""
            <div style="text-align:center;font-size:1.5rem;margin:8px 0">
                {"😊 Positive" if sentiment_override > 0 else ("😐 Neutral" if sentiment_override == 0 else "😡 Negative")}
            </div>""", unsafe_allow_html=True)

        predict_btn = st.button("🔮  Predict Brand Trend", use_container_width=True)

    with col_result:
        st.markdown('<div class="section-title">Prediction Result</div>', unsafe_allow_html=True)

        if predict_btn:
            if not brand_input:
                st.error("Please select a brand.")
            else:
                payload = {
                    "brand_name": brand_input,
                    "platform":   platform,
                    "likes":      float(likes),
                    "shares":     float(shares),
                }
                if "Auto" in input_mode:
                    if not comment.strip():
                        st.error("Please enter a review comment.")
                        st.stop()
                    payload["comment_review"] = comment
                else:
                    payload["sentiment_score"] = sentiment_override

                with st.spinner("Analyzing..."):
                    time.sleep(0.4)
                    result, err = api_call("POST", "/predict", payload)

                if err:
                    st.error(err)
                else:
                    trend = result["trend"]
                    css_class = "result-up" if trend == "UP" else "result-down"
                    badge_class = "trend-badge-up" if trend == "UP" else "trend-badge-down"
                    arrow = "▲" if trend == "UP" else "▼"

                    st.markdown(f"""
                    <div class="{css_class}">
                        <h2>{arrow}  {trend}TRENDING</h2>
                        <div class="{badge_class}">{brand_input} · {platform}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.plotly_chart(
                        confidence_gauge(result["confidence"], "Model Confidence"),
                        use_container_width=True
                    )

                    # Stats row
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Sentiment Score", f"{result['sentiment_score']:+d}")
                    s2.metric("Likes", f"{int(result['likes']):,}")
                    s3.metric("Shares", f"{int(result['shares']):,}")

                    st.markdown('<div class="section-title">Recommendation</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="rec-box">{result["recommendation"]}</div>',
                                unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;color:#334155;">
                <div style="font-size:4rem;margin-bottom:1rem">🔮</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#475569">
                    Fill in the form and hit Predict
                </div>
                <div style="font-size:0.82rem;color:#334155;margin-top:8px">
                    Results appear here instantly
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE: BATCH ANALYSIS
# ═══════════════════════════════════════════════════════════════════

elif "📊" in page:
    st.markdown("""
    <div class="brand-header">
        <h1>Batch Analysis</h1>
        <p>Analyze multiple brands at once — compare trends across your entire portfolio</p>
    </div>
    """, unsafe_allow_html=True)

    brands_data, _ = api_call("GET", "/brands")
    brand_list    = brands_data["known_brands"]    if brands_data else []
    platform_list = (brands_data["known_platforms"] if brands_data and brands_data["known_platforms"]
                     else ["Instagram", "Facebook", "TikTok", "Twitter", "YouTube"])

    st.markdown('<div class="section-title">Add Brands to Batch</div>', unsafe_allow_html=True)

    if "batch_rows" not in st.session_state:
        st.session_state.batch_rows = []

    with st.form("batch_form", clear_on_submit=True):
        bc1, bc2, bc3, bc4, bc5 = st.columns([2, 1.5, 1, 1, 2])
        b_brand    = bc1.selectbox("Brand",    options=brand_list,    key="b_brand")
        b_platform = bc2.selectbox("Platform", options=platform_list, key="b_plat")
        b_likes    = bc3.number_input("Likes",  min_value=0, value=1000, key="b_likes")
        b_shares   = bc4.number_input("Shares", min_value=0, value=200,  key="b_shares")
        b_comment  = bc5.text_input("Comment / Review", key="b_comment",
                                    placeholder="Amazing quality!")
        add_btn = st.form_submit_button("➕  Add to Batch", use_container_width=False)

    if add_btn and b_brand:
        st.session_state.batch_rows.append({
            "brand_name": b_brand, "platform": b_platform,
            "likes": float(b_likes), "shares": float(b_shares),
            "comment_review": b_comment or "neutral",
        })
        st.success(f"Added **{b_brand}** to batch.")

    if st.session_state.batch_rows:
        df_preview = pd.DataFrame(st.session_state.batch_rows)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)

        col_run, col_clear = st.columns([1, 5])
        run_batch   = col_run.button("🚀  Run Batch", use_container_width=True)
        clear_batch = col_clear.button("🗑️  Clear", use_container_width=False)

        if clear_batch:
            st.session_state.batch_rows = []
            st.rerun()

        if run_batch:
            with st.spinner("Running batch predictions..."):
                time.sleep(0.5)
                payload = {"predictions": st.session_state.batch_rows}
                result, err = api_call("POST", "/predict/batch", payload)

            if err:
                st.error(err)
            else:
                rows = result["results"]
                st.markdown('<div class="stylish-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Batch Results</div>', unsafe_allow_html=True)

                up_count   = sum(1 for r in rows if r["trend"] == "UP")
                down_count = len(rows) - up_count
                avg_conf   = sum(r["confidence"] for r in rows) / len(rows)

                m1, m2, m3 = st.columns(3)
                m1.metric("📈 Trending UP",   up_count)
                m2.metric("📉 Trending DOWN", down_count)
                m3.metric("⚡ Avg Confidence", f"{avg_conf:.1f}%")

                # Results table
                df_results = pd.DataFrame([{
                    "Brand":       r["brand_name"],
                    "Platform":    r["platform"],
                    "Likes":       int(r["likes"]),
                    "Shares":      int(r["shares"]),
                    "Sentiment":   f'{r["sentiment_score"]:+d}',
                    "Trend":       ("▲ UP" if r["trend"] == "UP" else "▼ DOWN"),
                    "Confidence":  f'{r["confidence"]}%',
                } for r in rows])
                st.dataframe(df_results, use_container_width=True, hide_index=True)

                # Donut chart
                fig_donut = go.Figure(go.Pie(
                    labels=["Trending UP", "Trending DOWN"],
                    values=[up_count, down_count],
                    hole=0.65,
                    marker=dict(colors=["#4ade80", "#f87171"],
                                line=dict(color="#080c14", width=3)),
                    textinfo="label+percent",
                    textfont=dict(color="#e2e8f0", family="DM Sans"),
                ))
                fig_donut.add_annotation(
                    text=f"{len(rows)}<br>Brands",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#f1f5f9", family="Syne"),
                )
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                    legend=dict(font=dict(color="#64748b")),
                    margin=dict(t=20, b=20), height=280,
                )

                # Confidence bar chart
                fig_conf = go.Figure(go.Bar(
                    x=[r["brand_name"] for r in rows],
                    y=[r["confidence"] for r in rows],
                    marker=dict(
                        color=["#4ade80" if r["trend"]=="UP" else "#f87171" for r in rows],
                        line=dict(width=0),
                    ),
                    text=[f'{r["confidence"]}%' for r in rows],
                    textposition="outside",
                    textfont=dict(color="#94a3b8", size=11),
                ))
                fig_conf.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=30, l=10, r=10), height=280,
                    xaxis=dict(color="#64748b", showgrid=False),
                    yaxis=dict(color="#64748b", showgrid=True,
                               gridcolor="#1e2a42", range=[0, 115]),
                    title=dict(text="Confidence per Brand", font=dict(color="#94a3b8", size=13)),
                )

                ch1, ch2 = st.columns(2)
                with ch1:
                    st.markdown('<div class="section-title">Trend Distribution</div>', unsafe_allow_html=True)
                    st.plotly_chart(fig_donut, use_container_width=True)
                with ch2:
                    st.markdown('<div class="section-title">Confidence Scores</div>', unsafe_allow_html=True)
                    st.plotly_chart(fig_conf, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#334155;">
            <div style="font-size:3rem">📋</div>
            <div style="color:#475569;margin-top:8px">Add brands above to start batch analysis</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE: SENTIMENT LAB
# ═══════════════════════════════════════════════════════════════════

elif "🧠" in page:
    st.markdown("""
    <div class="brand-header">
        <h1>Sentiment Lab</h1>
        <p>Test the NLP engine · Analyze any Urdu or English customer review in real-time</p>
    </div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown('<div class="section-title">Enter Text</div>', unsafe_allow_html=True)
        sample_texts = {
            "Select a sample...": "",
            "😊 Positive (EN)": "Amazing quality! Best brand ever, love it! Highly recommend.",
            "😊 Positive (UR)": "Zabardast quality! Lajawab service, dil jeet liya!",
            "😡 Negative (EN)": "Worst experience. Very bad quality, fake product. Never buy again!",
            "😡 Negative (UR)": "Bekar brand hai. Delivery late thi, quality kharab. Complaint karna padega.",
            "😐 Neutral": "Received the order. It was okay.",
        }
        sample = st.selectbox("Quick samples", list(sample_texts.keys()))
        review_text = st.text_area(
            "Review Text",
            value=sample_texts[sample],
            height=160,
            placeholder="Type or paste any customer review here..."
        )
        analyze_btn = st.button("🧠  Analyze Sentiment", use_container_width=True)

    with col_out:
        st.markdown('<div class="section-title">Analysis Result</div>', unsafe_allow_html=True)

        if analyze_btn:
            if not review_text.strip():
                st.error("Please enter text to analyze.")
            else:
                with st.spinner("Analyzing sentiment..."):
                    time.sleep(0.3)
                    result, err = api_call("POST", "/sentiment", {"text": review_text})

                if err:
                    st.error(err)
                else:
                    label = result["label"]
                    score = result["sentiment_score"]
                    emoji = "😊" if label == "Positive" else ("😡" if label == "Negative" else "😐")
                    color_class = "sent-positive" if label == "Positive" else ("sent-negative" if label == "Negative" else "sent-neutral")

                    st.markdown(f"""
                    <div style="background:#0d1627;border:1px solid #1e2a42;border-radius:14px;padding:1.5rem;text-align:center;">
                        <div style="font-size:3.5rem;margin-bottom:0.5rem">{emoji}</div>
                        <div style="font-size:0.8rem;color:#64748b;text-transform:uppercase;letter-spacing:1px">Detected Sentiment</div>
                        <div class="{color_class}" style="font-family:'Syne',sans-serif;font-size:1.8rem;margin-top:2px">{label.upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.plotly_chart(sentiment_bar(score), use_container_width=True)

                    # Feature Highlights
                    st.markdown('<div class="section-title" style="margin-top:1rem">Engine Notes</div>', unsafe_allow_html=True)
                    pos_words = result.get("matched_positive", [])
                    neg_words = result.get("matched_negative", [])

                    html_chips = ""
                    for pw in pos_words:
                        html_chips += f'<span class="word-chip-pos">+{pw}</span>'
                    for nw in neg_words:
                        html_chips += f'<span class="word-chip-neg">-{nw}</span>'

                    if html_chips:
                        st.markdown(f"""
                        <div style="background:#090d16;border:1px solid #141b2d;border-radius:10px;padding:1rem;">
                            <div style="font-size:0.75rem;color:#475569;margin-bottom:6px">Matched Sentiment Keywords:</div>
                            {html_chips}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="rec-box" style="padding:1rem;font-size:0.85rem">
                            No explicit positive/negative roman-urdu or english keywords detected. Model fell back to baseline scoring rules.
                        </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;color:#334155;">
                <div style="font-size:4rem;margin-bottom:0.5rem">🧠</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;color:#475569">NLP Analyzer Output</div>
                <div style="font-size:0.82rem;color:#334155;margin-top:4px">Run analysis to see score breakdown</div>
            </div>""", unsafe_allow_html=True)

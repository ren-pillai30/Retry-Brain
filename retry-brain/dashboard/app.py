import streamlit as st
import pandas as pd
from pathlib import Path

# 1. Page Configuration
st.set_page_config(
    page_title="Retry Brain — AI Recovery Agent",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Design system — warm, editorial fintech look (Butter Payments-inspired)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --cream:      #FBF6EA;
        --card:       #FFFFFF;
        --ink:        #23261C;
        --ink-muted:  #6E6A56;
        --butter:     #F4C13B;
        --butter-deep:#D89A1C;
        --sage:       #3F7A5C;
        --sage-bg:    rgba(63, 122, 92, 0.12);
        --clay:       #BE6A2E;
        --clay-bg:    rgba(190, 106, 46, 0.13);
        --brick:      #AE4038;
        --brick-bg:   rgba(174, 64, 56, 0.12);
        --line:       #E8DFC7;
    }

    /* Hide default chrome */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: var(--cream);
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4 {
        font-family: 'Fraunces', Georgia, serif !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    p, span, label, div { color: var(--ink); }

    /* --- Masthead --- */
    .eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--butter-deep);
        margin-bottom: 0.6rem;
    }

    .masthead-row {
        display: flex;
        align-items: baseline;
        gap: 0.7rem;
        margin-bottom: 0.15rem;
        flex-wrap: wrap;
    }

    .title-serif {
        font-family: 'Fraunces', Georgia, serif;
        font-size: 2.6rem;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.05;
        position: relative;
        display: inline-block;
    }
    .title-serif::after {
        content: "";
        position: absolute;
        left: 4px;
        right: 8px;
        bottom: 2px;
        height: 0.42em;
        background: var(--butter);
        opacity: 0.55;
        z-index: -1;
        border-radius: 3px 8px 3px 8px;
    }

    .pill-tag {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--ink);
        background: var(--card);
        border: 1px solid var(--line);
        padding: 5px 13px;
        border-radius: 999px;
        white-space: nowrap;
    }

    .subtitle {
        color: var(--ink-muted);
        font-size: 1.06rem;
        margin-top: 0.5rem;
        margin-bottom: 1.6rem;
        max-width: 640px;
    }

    /* --- Dividers --- */
    hr {
        border: none;
        border-top: 1px solid var(--line) !important;
        margin: 1.6rem 0 !important;
    }

    /* --- Metrics --- */
    div[data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.1rem 1.3rem 1rem 1.3rem;
        box-shadow: 0 1px 2px rgba(35,38,28,0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--ink-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--ink);
        font-weight: 600;
    }
    div[data-testid="stMetricDelta"] {
        font-family: 'Inter', sans-serif;
    }

    /* --- Bordered containers (spotlight card) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--card);
        border: 1px solid var(--line) !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 10px rgba(35,38,28,0.05);
    }

    /* --- Badges --- */
    .badge {
        padding: 4px 13px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        display: inline-block;
        font-family: 'Inter', sans-serif;
    }
    .badge-abort   { background: var(--brick-bg); color: var(--brick); border: 1px solid rgba(174,64,56,0.25); }
    .badge-retry   { background: var(--clay-bg);  color: var(--clay);  border: 1px solid rgba(190,106,46,0.25); }
    .badge-success { background: var(--sage-bg);  color: var(--sage);  border: 1px solid rgba(63,122,92,0.25); }

    /* --- Section labels --- */
    .section-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ink-muted);
        margin-bottom: -0.4rem;
    }

    /* --- Selectbox / filters --- */
    div[data-baseweb="select"] > div {
        background: var(--card);
        border-color: var(--line) !important;
        border-radius: 10px;
    }

    /* --- Dataframe --- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }

    /* --- Streamlit native alerts --- */
    div[data-testid="stCaptionContainer"] { color: var(--ink-muted); }
</style>
""", unsafe_allow_html=True)

# 3. Data Loader
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_CSV = BASE_DIR / "data" / "audit_trail.csv"

@st.cache_data
def load_data():
    if not AUDIT_CSV.exists():
        st.error(f"Audit trail file not found at `{AUDIT_CSV}`. Run `python backend/simulator.py` first.")
        st.stop()
    return pd.read_csv(AUDIT_CSV)

df = load_data()

# 4. Header Section
st.markdown('<div class="eyebrow">Payment Intelligence</div>', unsafe_allow_html=True)
st.markdown("""
<div class="masthead-row">
    <span class="title-serif">Retry Brain</span>
    <span class="pill-tag">AI Recovery Agent</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Root-cause-aware payment recovery, measured against a naive blind-retry baseline.</div>', unsafe_allow_html=True)

# 5. Metrics Section (Using native Streamlit)
total_at_risk = df["amount"].sum()
ai_recovered = df["ai_recovered_amount"].sum()
naive_recovered = df["naive_recovered_amount"].sum()
ai_retries = df["ai_attempts_used"].sum()
naive_retries = df["naive_attempts_used"].sum()
retry_savings = ((naive_retries - ai_retries) / max(1, naive_retries)) * 100

st.divider()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Amount at Risk", f"₹{total_at_risk:,.2f}")
with m2:
    st.metric("Retry Brain Recovered", f"₹{ai_recovered:,.2f}", f"{(ai_recovered/total_at_risk)*100:.1f}% Recovery")
with m3:
    st.metric("Naive Baseline Recovered", f"₹{naive_recovered:,.2f}", f"{(naive_recovered/total_at_risk)*100:.1f}% Recovery")
with m4:
    st.metric("Wasted Retries Avoided", f"{retry_savings:.1f}%", f"{naive_retries - ai_retries} Retries Saved")

st.divider()

# 6. Graceful Failure Spotlight Card (Using native container with border)
st.markdown('<div class="section-eyebrow">Case Study</div>', unsafe_allow_html=True)
st.subheader("Graceful Failure Spotlight")
st.caption("A transaction where the agent deliberately stopped execution to protect merchant standing.")

graceful_cases = df[df["ai_action"].isin(["ABORT", "NOTIFY_UPDATE_METHOD", "ESCALATE_MANUAL"])]

if not graceful_cases.empty:
    sample = graceful_cases.iloc[0]
    badge_class = "badge-abort" if sample["ai_action"] == "ABORT" else "badge-retry" if sample["ai_action"] == "NOTIFY_UPDATE_METHOD" else "badge-success"

    # Native bordered container
    with st.container(border=True):
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin:0; font-family:'IBM Plex Mono',monospace; font-weight:600; color:var(--ink); font-size:1.05rem;">{sample['transaction_id']}</h4>
            <span class="badge {badge_class}">{sample['ai_action']}</span>
        </div>
        <p style="color:var(--ink-muted); margin-bottom: 16px; font-size:0.95rem;">
            <strong style="color:var(--ink);">Amount</strong> ₹{sample['amount']:,.2f} &nbsp;·&nbsp;
            <strong style="color:var(--ink);">Classified cause</strong> {sample['ai_root_cause']}
        </p>
        <blockquote style="border-left: 3px solid var(--butter); padding-left: 15px; margin: 0 0 16px 0; color: var(--ink); font-style: italic; font-family:'Fraunces',serif; font-size:1.02rem;">
            "{sample['ai_reasoning']}"
        </blockquote>
        <p style="margin:0; font-size: 0.85rem; color: var(--ink-muted);">
            ✓ Agent burned <strong style="color:var(--sage);">0</strong> retries &nbsp;·&nbsp; ⚠ Naive baseline burned <strong style="color:var(--clay);">{sample['naive_attempts_used']}</strong> useless retries
        </p>
        """, unsafe_allow_html=True)
else:
    st.info("No hard failures found in current batch.")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Charts Section
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-eyebrow">By Root Cause</div>', unsafe_allow_html=True)
    st.subheader("Recovery Rate")
    cause_summary = df.groupby("ai_root_cause").agg(
        total_risk=("amount", "sum"),
        ai_recovered=("ai_recovered_amount", "sum")
    ).reset_index()
    cause_summary["Recovery Rate (%)"] = (cause_summary["ai_recovered"] / cause_summary["total_risk"]) * 100
    st.bar_chart(cause_summary.set_index("ai_root_cause")["Recovery Rate (%)"], color="#D89A1C")

with col_right:
    st.markdown('<div class="section-eyebrow">Efficiency</div>', unsafe_allow_html=True)
    st.subheader("Retries Burned: Agent vs. Baseline")
    attempts_summary = df.groupby("ai_root_cause").agg(
        Agent_Retries=("ai_attempts_used", "sum"),
        Naive_Retries=("naive_attempts_used", "sum")
    )
    st.bar_chart(attempts_summary, color=["#3F7A5C", "#D7CFB4"])

st.divider()

# 8. Audit Trail Table
st.markdown('<div class="section-eyebrow">Full Ledger</div>', unsafe_allow_html=True)
st.subheader("Inspectable Audit Trail")

f1, f2 = st.columns(2)
with f1:
    selected_cause = st.selectbox("Filter by Root Cause", options=["All"] + list(df["ai_root_cause"].unique()))
with f2:
    selected_action = st.selectbox("Filter by Action Taken", options=["All"] + list(df["ai_action"].unique()))

filtered_df = df.copy()
if selected_cause != "All":
    filtered_df = filtered_df[filtered_df["ai_root_cause"] == selected_cause]
if selected_action != "All":
    filtered_df = filtered_df[filtered_df["ai_action"] == selected_action]

st.dataframe(
    filtered_df[[
        "transaction_id", "amount", "failure_code", "ai_root_cause",
        "ai_action", "ai_attempts_used", "ai_recovered_amount", "ai_reasoning"
    ]],
    use_container_width=True,
    hide_index=True
)
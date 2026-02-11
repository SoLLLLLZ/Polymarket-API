"""
Polymarket Live Data Platform - Streamlit App
Redesigned to match Polymarket's UI
"""
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from gamma_client import GammaClient
from clob_client import CLOBClient
from utils import (
    parse_markets_from_event,
    get_first_token_id,
    format_price,
    format_volume,
    safe_float
)

# Page configuration
st.set_page_config(
    page_title="Polymarket Live",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cyberpunk-style CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Force dark background everywhere */
    .stApp, .stApp > div, .main, .main > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    section[data-testid="stMain"],
    .block-container {
        background: transparent !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%) !important;
        background-attachment: fixed !important;
    }
    
    .main .block-container {
        padding: 2rem;
        max-width: 1400px;
    }
    
    /* Animated background grid */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers with glow */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 50%, #00f5ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
        margin-bottom: 2rem !important;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px #00f5ff); }
        to { filter: drop-shadow(0 0 20px #ff00ff); }
    }
    
    h2 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #00f5ff !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        margin: 2rem 0 1rem 0 !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    h3 {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #fff !important;
    }
    
    /* Neon buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff00ff 0%, #00f5ff 100%) !important;
        color: #000 !important;
        border: 2px solid #00f5ff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-family: 'Orbitron', sans-serif !important;
        padding: 0.75rem 1.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5), inset 0 0 20px rgba(255, 0, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.8), 0 0 50px rgba(255, 0, 255, 0.6) !important;
        border-color: #ff00ff !important;
    }
    
    /* Glowing search bar */
    .stTextInput > div > div > input {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        color: #00f5ff !important;
        font-weight: 500 !important;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3), inset 0 0 10px rgba(0, 245, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff00ff !important;
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.6), inset 0 0 15px rgba(255, 0, 255, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 245, 255, 0.5) !important;
    }
    
    /* Cyberpunk metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #00f5ff !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 8px !important;
        color: #00f5ff !important;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.3) !important;
    }
    
    /* Neon dividers */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #00f5ff, #ff00ff, #00f5ff, transparent) !important;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.5) !important;
        margin: 2rem 0 !important;
    }
    
    /* Captions */
    .stCaption {
        color: #00f5ff !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    /* Fix all text elements to ensure visibility */
    p, span, label {
        color: #fff !important;
    }
    
    /* Ensure text is visible on dark background */
    p, span, label, .stMarkdown, .stMarkdown p {
        color: #fff !important;
    }
    
    /* Selectbox styling - force all parts to be visible */
    .stSelectbox label {
        color: #00f5ff !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Target the actual select container */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.95) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(0, 245, 255, 0.3) !important;
    }
    
    /* Target the select element itself */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(26, 26, 46, 0.95) !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(26, 26, 46, 0.95) !important;
        color: #00f5ff !important;
        border: 2px solid #00f5ff !important;
    }
    
    /* Force all text inside selectbox to be cyan */
    .stSelectbox > div > div {
        background-color: rgba(26, 26, 46, 0.95) !important;
    }
    
    .stSelectbox span {
        color: #00f5ff !important;
    }
    
    .stSelectbox svg {
        fill: #00f5ff !important;
    }
    
    /* Dropdown menu options */
    [role="listbox"] {
        background: #1a1a2e !important;
        border: 2px solid #00f5ff !important;
    }
    
    [role="option"] {
        background: #1a1a2e !important;
        color: #00f5ff !important;
    }
    
    [role="option"]:hover {
        background: rgba(0, 245, 255, 0.2) !important;
        color: #ff00ff !important;
    }
    
    /* Force dropdown text to be visible */
    option {
        background: #1a1a2e !important;
        color: #00f5ff !important;
    }
    
    /* Target specific selectbox elements by data attributes */
    [data-baseweb="popover"] {
        background: #1a1a2e !important;
    }
    
    [data-baseweb="menu"] {
        background: #1a1a2e !important;
    }
    
    [data-baseweb="list"] {
        background: #1a1a2e !important;
    }
    
    [data-baseweb="list-item"] {
        background: #1a1a2e !important;
        color: #00f5ff !important;
    }
    
    [data-baseweb="list-item"]:hover {
        background: rgba(0, 245, 255, 0.3) !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #fff !important;
    }
    
    .stMarkdown p {
        color: #fff !important;
    }
    
    /* Strong/bold text */
    strong, b {
        color: #00f5ff !important;
    }
    
    /* Chart text */
    .js-plotly-plot .plotly text {
        fill: #00f5ff !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(0, 245, 255, 0.1) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 10px !important;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00f5ff !important;
        border-right-color: #ff00ff !important;
    }
    
    /* Glitch effect on hover */
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def get_gamma_client():
    return GammaClient()

@st.cache_resource
def get_clob_client():
    return CLOBClient()

gamma = get_gamma_client()
clob = get_clob_client()

# Session state
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""


def is_real_market(market_dict):
    """Check if a market has real, meaningful outcomes (not placeholders)."""
    import re
    
    question = market_dict.get("question", "").lower()
    outcomes = market_dict.get("outcomes", [])
    
    if not outcomes or len(outcomes) == 0:
        return False
    
    # First check the question itself for placeholder patterns
    question_placeholder_patterns = [
        r'\bindividual\s+[a-z0-9]\b',
        r'\bleader\s+\d+\b',
        r'\bperson\s+[a-z0-9]\b',
        r'\bcandidate\s+[a-z]\b',
        r'\boption\s+[a-z0-9]\b',
        r'\bchoice\s+[a-z0-9]\b',
        r'\bteam\s+[a-z0-9]\b',
        r'\bplayer\s+[a-z0-9]\b',
        r'\bcompany\s+[a-z0-9]\b',
    ]
    
    # If question contains placeholder patterns, skip it
    for pattern in question_placeholder_patterns:
        if re.search(pattern, question):
            return False
    
    # Check test/placeholder keywords in question
    if any(kw in question for kw in ["test market", "placeholder", "example", "dummy", "sample"]):
        return False
    
    # Check each outcome
    real_outcomes = 0
    for outcome in outcomes:
        outcome_str = str(outcome).strip().lower()
        
        # Skip if it matches placeholder patterns
        placeholder_patterns = [
            r'^(individual|leader|person|candidate|option|choice|team|player|company)\s*[a-z0-9]$',
            r'^(individual|leader|person|candidate|option|choice|team|player|company)\s*\d+$',
            r'^[a-z]$',  # Single letter
            r'^\d+$',    # Just a number
        ]
        
        is_placeholder = any(re.match(pattern, outcome_str) for pattern in placeholder_patterns)
        
        # Also check for very generic outcomes
        if outcome_str in ["yes", "no", "up", "down", "true", "false"]:
            # These are OK
            real_outcomes += 1
        elif not is_placeholder and len(outcome_str) > 1:
            real_outcomes += 1
    
    # Need at least 1 real outcome
    return real_outcomes > 0


def render_market_card(event, key_prefix=""):
    """Render a cyberpunk-style neon card - pure HTML for the card body."""
    title = event.get("title", "Untitled")
    markets = event.get("markets", [])

    if not markets:
        return

    volume = safe_float(markets[0].get("volume", 0))

    # Use parse_markets_from_event so outcomes/prices are properly decoded from JSON strings
    parsed = parse_markets_from_event(event)
    first_market = parsed[0] if parsed else None
    outcomes = first_market.get("outcomes", []) if first_market else []
    prices = first_market.get("outcome_prices", []) if first_market else []

    # Build outcome pills in pure HTML
    pills_html = ""
    for i, outcome in enumerate(outcomes[:4]):
        price = safe_float(prices[i] if i < len(prices) else 0, 0)
        if price > 0.6:
            border_color = "#00f5ff"
            glow = "0, 245, 255"
            bg = "rgba(0, 245, 255, 0.15)"
            text_color = "#00f5ff"
        elif price > 0.4:
            border_color = "#ffff00"
            glow = "255, 255, 0"
            bg = "rgba(255, 255, 0, 0.15)"
            text_color = "#ffff00"
        else:
            border_color = "#ff00ff"
            glow = "255, 0, 255"
            bg = "rgba(255, 0, 255, 0.15)"
            text_color = "#ff00ff"

        pills_html += (
            f'<div style="flex:1;background:{bg};border:2px solid {border_color};color:{text_color};'
            f'padding:0.75rem 0.5rem;border-radius:10px;text-align:center;font-weight:700;'
            f'font-size:0.85rem;box-shadow:0 0 15px rgba({glow},0.4);text-transform:uppercase;'
            f'letter-spacing:1px;min-width:80px;">'
            f'<div style="color:{text_color};">{outcome}</div>'
            f'<div style="font-size:1.2rem;margin-top:4px;color:{text_color};">{format_price(price)}</div>'
            f'</div>'
        )

    card = (
        f'<div style="background:linear-gradient(135deg,rgba(26,26,46,0.97),rgba(16,20,55,0.97));'
        f'border:2px solid #00f5ff;border-radius:16px;padding:1.5rem;margin-bottom:1rem;'
        f'box-shadow:0 0 25px rgba(0,245,255,0.25),0 0 50px rgba(255,0,255,0.15);">'
        f'<div style="font-size:1.15rem;font-weight:600;color:#ffffff;line-height:1.4;'
        f'margin-bottom:1.2rem;text-shadow:0 0 8px rgba(0,245,255,0.4);">{title}</div>'
        f'<div style="display:flex;gap:0.75rem;margin-bottom:1.2rem;flex-wrap:wrap;">{pills_html}</div>'
        f'<div style="color:#00f5ff;font-size:0.85rem;font-weight:600;letter-spacing:1px;">'
        f'&#x1F48E; {format_volume(volume)} VOL</div>'
        f'</div>'
    )
    st.markdown(card, unsafe_allow_html=True)

    if st.button("⚡ ENTER", key=f"{key_prefix}_{event.get('id', title)}", use_container_width=True):
        st.session_state.selected_event = event
        st.rerun()


def render_landing():
    """Cyberpunk landing page."""
    # Epic cyberpunk title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="
            font-family: 'Orbitron', sans-serif;
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 50%, #00f5ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px rgba(0, 245, 255, 0.8);
            margin: 0;
            animation: glow 2s ease-in-out infinite alternate;
        ">
            POLYMARKET NEXUS
        </h1>
        <p style="
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.2rem;
            color: #00f5ff;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 1rem;
            text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        ">
            ⚡ REAL-TIME PREDICTION MARKETS ⚡
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search with neon glow
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Search", placeholder="🔍 SCAN THE MATRIX...", label_visibility="collapsed", key="search_input")
    with col2:
        if st.button("⚡ SEARCH", use_container_width=True):
            if query:
                st.session_state.search_query = query
                st.rerun()
    
    # Results
    if st.session_state.search_query:
        st.markdown(f"""
        <h2 style="
            font-family: 'Orbitron', sans-serif;
            color: #ff00ff;
            text-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
            text-transform: uppercase;
            letter-spacing: 2px;
        ">
            ⟨ SEARCH RESULTS: {st.session_state.search_query} ⟩
        </h2>
        """, unsafe_allow_html=True)
        
        if st.button("⬅ BACK TO NEXUS"):
            st.session_state.search_query = ""
            st.rerun()
        
        results = gamma.search_events_public(st.session_state.search_query, 20)
        if results:
            for idx, event in enumerate(results):
                render_market_card(event, f"search_{idx}")
        else:
            st.info("🔴 NO SIGNALS DETECTED")
    else:
        st.markdown("""
        <h2 style="
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, #ff00ff, #00f5ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 2rem;
        ">
            🔥 LIVE FEED // TRENDING MARKETS
        </h2>
        """, unsafe_allow_html=True)
        
        with st.spinner("⚡ SYNCING WITH THE GRID..."):
            events = gamma.get_popular_events(40)
        
        if events:
            # Filter placeholders
            real_events = []
            for event in events:
                markets = parse_markets_from_event(event)
                has_real_market = any(is_real_market(m) for m in markets)
                if has_real_market:
                    real_events.append(event)
            
            for idx, event in enumerate(real_events[:20]):
                render_market_card(event, f"pop_{idx}")


def render_event_detail():
    """Event detail page."""
    event = st.session_state.selected_event
    
    if st.button("← Back"):
        st.session_state.selected_event = None
        st.rerun()
    
    st.title(event.get("title", "Event"))
    
    if event.get("description"):
        st.markdown(event["description"])
    
    st.divider()
    
    # Stats
    markets = event.get("markets", [])
    total_vol = sum(safe_float(m.get("volume", 0)) for m in markets)
    total_liq = sum(safe_float(m.get("liquidity", 0)) for m in markets)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volume", format_volume(total_vol))
    col2.metric("Liquidity", format_volume(total_liq))
    col3.metric("Markets", len(markets))
    
    st.divider()
    
    # Markets
    st.subheader("Markets")
    
    parsed = parse_markets_from_event(event)
    real_markets = [m for m in parsed if is_real_market(m)]
    
    if not real_markets:
        st.info("No markets available")
        return
    
    for market in real_markets:
        question = market.get("question", "")
        outcomes = market.get("outcomes", [])
        prices = market.get("outcome_prices", [])
        
        # Cyberpunk question styling
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(255, 0, 255, 0.1));
            border-left: 4px solid #00f5ff;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        ">
            <strong style="color: #fff; font-size: 1.1rem; text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);">
                {question}
            </strong>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(outcomes) if len(outcomes) <= 4 else 4)
        for i, outcome in enumerate(outcomes[:4]):
            with cols[i]:
                price = safe_float(prices[i] if i < len(prices) else 0, 0)
                st.metric(outcome, format_price(price))
        
        st.divider()
    
    # Chart
    st.markdown("""
    <h2 style="
        font-family: 'Orbitron', sans-serif;
        color: #ff00ff;
        text-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 2rem;
    ">
        📊 PRICE HISTORY MATRIX
    </h2>
    """, unsafe_allow_html=True)
    
    if real_markets:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_idx = 0
            if len(real_markets) > 1:
                options = [m.get("question", f"Market {i}")[:60] for i, m in enumerate(real_markets)]
                st.markdown('<p style="color: #00f5ff; font-weight: 600; margin-bottom: 0.5rem;">SELECT MARKET:</p>', unsafe_allow_html=True)
                selected = st.selectbox("Market", options, label_visibility="collapsed", key="market_select")
                selected_idx = options.index(selected)
        
        with col2:
            st.markdown('<p style="color: #00f5ff; font-weight: 600; margin-bottom: 0.5rem;">TIME RANGE:</p>', unsafe_allow_html=True)
            interval = st.selectbox(
                "Interval", 
                ["1d", "all", "max"], 
                format_func=lambda x: {"1d": "⚡ 1 DAY", "all": "⚡ 1 WEEK", "max": "⚡ ALL TIME"}[x],
                label_visibility="collapsed",
                key="interval_select"
            )
        
        market = real_markets[selected_idx]
        token_ids = market.get("clob_token_ids", [])
        
        if token_ids:
            history = clob.get_price_history(token_ids[0], interval)
            if history:
                times = [datetime.fromtimestamp(t) for t, p in history]
                prices = [p * 100 for t, p in history]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=times, y=prices,
                    mode='lines',
                    line=dict(color='#00f5ff', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 245, 255, 0.2)',
                    hovertemplate='%{y:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(
                        showgrid=True, 
                        gridcolor='rgba(0, 245, 255, 0.1)',
                        color='#00f5ff'
                    ),
                    yaxis=dict(
                        range=[0, 100], 
                        showgrid=True, 
                        gridcolor='rgba(255, 0, 255, 0.1)',
                        color='#ff00ff'
                    ),
                    plot_bgcolor='rgba(10, 14, 39, 0.8)',
                    paper_bgcolor='rgba(10, 14, 39, 0.8)',
                    font=dict(family='Rajdhani', color='#00f5ff')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔴 NO DATA AVAILABLE FOR THIS TIMEFRAME")
        else:
            st.info("🔴 NO CHART DATA AVAILABLE")


def main():
    if st.session_state.selected_event:
        render_event_detail()
    else:
        render_landing()


if __name__ == "__main__":
    main()
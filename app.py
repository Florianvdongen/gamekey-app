# -*- coding: utf-8 -*-
# app.py
# GameKey - Light consumer prototype (Streamlit) with phone frame
# - Auto-scroll to Selected/Checkout after Buy/Details
# - Auto-scroll to Now Playing after Watch
# - Working YouTube demo videos
# - Wider phone, light UI, button fit, league logos, safe guards

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pandas as pd
import uuid
import base64
import os

st.set_page_config(page_title="GameKey", page_icon="GameKey", layout="wide")

# ----------------------------
# Session state
# ----------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if "display_name" not in st.session_state:
    st.session_state.display_name = "Guest"
if "wallet" not in st.session_state:
    st.session_state.wallet = 12.00
if "purchases" not in st.session_state:
    st.session_state.purchases = {}
if "toast_msg" not in st.session_state:
    st.session_state.toast_msg = None
if "active_game" not in st.session_state:
    st.session_state.active_game = None
if "now_playing" not in st.session_state:
    st.session_state.now_playing = None  # dict: {title, league, url}
if "scroll_to" not in st.session_state:
    st.session_state.scroll_to = None  # "selected" or "player"

def toast(msg: str):
    st.session_state.toast_msg = msg

# ----------------------------
# Scroll helper (works on Streamlit Cloud)
# ----------------------------
def request_scroll(target: str):
    # target: "selected" or "player"
    st.session_state.scroll_to = target

def run_scroll_if_requested():
    target = st.session_state.scroll_to
    if target not in ("selected", "player"):
        return

    anchor_id = "selected_anchor" if target == "selected" else "player_anchor"
    components.html(
        f"""
        <script>
        const el = window.parent.document.getElementById("{anchor_id}");
        if (el) {{
          el.scrollIntoView({{behavior: "smooth", block: "start"}});
        }}
        </script>
        """,
        height=0,
    )
    # Clear after firing once
    st.session_state.scroll_to = None

# ----------------------------
# YouTube demo videos (working examples)
# Replace anytime with your preferred ones.
# ----------------------------
YOUTUBE_DEMOS = {
    "UCL":  "https://www.youtube.com/watch?v=pKrgnOI39Wk",  # UCL highlights example :contentReference[oaicite:1]{index=1}
    "NBA":  "https://www.youtube.com/watch?v=212qcAyAMuE",  # NBA full game highlights example :contentReference[oaicite:2]{index=2}
    "NFL":  "https://www.youtube.com/watch?v=CgCJ2nBAEaU",  # NFL game highlights example :contentReference[oaicite:3]{index=3}
    "MLS":  "https://www.youtube.com/watch?v=NXAQuATHNa0",  # MLS match highlights example :contentReference[oaicite:4]{index=4}
    "MLB":  "https://www.youtube.com/watch?v=cutEVnQkOX8",  # MLB highlights example :contentReference[oaicite:5]{index=5}
    "NWSL": "https://www.youtube.com/watch?v=r7hkQM55SGk",  # NWSL highlights example :contentReference[oaicite:6]{index=6}
}

def start_demo_playback(title: str, league: str):
    st.session_state.now_playing = {
        "title": title,
        "league": league,
        "url": YOUTUBE_DEMOS.get(league),
    }
    request_scroll("player")

# ----------------------------
# CSS: Light UI + wider phone + button fit
# ----------------------------
st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: #f3f5f9; }

    .block-container {
      max-width: 600px !important;
      padding-top: 1rem;
      padding-bottom: 3rem;
    }

    .phone {
      background: #ffffff;
      border-radius: 30px;
      border: 1px solid rgba(15,23,42,0.10);
      box-shadow: 0 24px 70px rgba(15,23,42,0.12);
      overflow: hidden;
    }

    .phone-inner { padding: 18px 16px 20px 16px; }

    .notch {
      height: 18px;
      width: 140px;
      margin: 0 auto;
      border-radius: 0 0 16px 16px;
      background: rgba(15,23,42,0.08);
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 10px;
    }

    .brand { font-weight: 950; font-size: 18px; color: #0f172a; }
    .subtle { font-size: 12px; color: #64748b; }
    .wallet { text-align: right; font-weight: 950; color: #0f172a; }

    .hero {
      margin-top: 14px;
      padding: 18px;
      border-radius: 20px;
      background: linear-gradient(135deg, rgba(229,9,20,0.10), rgba(15,23,42,0.04));
      border: 1px solid rgba(15,23,42,0.08);
    }

    .hero-title { font-size: 26px; font-weight: 950; color: #0f172a; line-height: 1.05; }
    .hero-sub { margin-top: 6px; font-size: 13px; color: #475569; }

    .pill {
      display: inline-block;
      margin-top: 10px;
      margin-right: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(15,23,42,0.06);
      border: 1px solid rgba(15,23,42,0.08);
      color: #0f172a;
      font-size: 11px;
      font-weight: 850;
    }

    .rowtitle {
      margin: 18px 0 10px 0;
      font-size: 14px;
      font-weight: 950;
      color: #0f172a;
    }

    .poster {
      background: #ffffff;
      border-radius: 18px;
      border: 1px solid rgba(15,23,42,0.10);
      box-shadow: 0 10px 30px rgba(15,23,42,0.06);
      padding: 12px;
    }

    .poster-art {
      height: 132px;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(229,9,20,0.14), rgba(59,130,246,0.10));
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(15,23,42,0.10);
    }

    .poster-badge {
      position: absolute;
      top: 10px;
      left: 10px;
      background: rgba(255,255,255,0.92);
      padding: 6px 10px;
      border-radius: 999px;
      color: #0f172a;
      font-size: 11px;
      font-weight: 900;
      display: flex;
      gap: 8px;
      align-items: center;
      border: 1px solid rgba(15,23,42,0.10);
      box-shadow: 0 10px 24px rgba(15,23,42,0.08);
    }

    .logo {
      width: 22px;
      height: 22px;
      border-radius: 6px;
      object-fit: contain;
      display: block;
      background: transparent;
    }

    .poster-main { margin-top: 10px; font-size: 16px; font-weight: 950; color: #0f172a; }
    .poster-meta { margin-top: 4px; font-size: 12px; color: #64748b; }

    .price-chip {
      display: inline-block;
      margin-top: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(229,9,20,0.10);
      border: 1px solid rgba(229,9,20,0.20);
      color: #b91c1c;
      font-size: 11px;
      font-weight: 900;
    }

    .stButton > button {
      width: 100%;
      border-radius: 14px;
      font-weight: 950;
      border: none;
      padding: 0.38rem 0.45rem !important;
      font-size: 0.78rem !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      line-height: 1 !important;
      background: #e50914;
      color: #ffffff;
    }
    .stButton > button:hover { background: #ff1f2d; }

    .stTabs [data-baseweb="tab"] { font-size: 12px; color: #64748b; }
    .stTabs [aria-selected="true"] { color: #0f172a; border-bottom: 2px solid #e50914; }
    </style>
    """,
    unsafe_allow_html=True
)
.poster-art {
  position: relative;
  overflow: hidden;
}

.poster-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

# ----------------------------
# Logos: local assets + fallback badge
# ----------------------------
LEAGUE_COLORS = {
    "UCL": ("#0b5fff", "#ffffff"),
    "NBA": ("#ff2a5b", "#ffffff"),
    "NFL": ("#00a3ff", "#ffffff"),
    "MLS": ("#ff7a00", "#ffffff"),
    "NWSL": ("#8a5cff", "#ffffff"),
    "MLB": ("#00d18f", "#0b0b0f"),
}

def file_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "image/png"
    if ext == "svg":
        mime = "image/svg+xml"
    elif ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext == "webp":
        mime = "image/webp"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def svg_badge(text: str, bg: str, fg: str) -> str:
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">
      <circle cx="11" cy="11" r="10" fill="{bg}" stroke="rgba(15,23,42,0.18)" stroke-width="1"/>
      <text x="11" y="14" text-anchor="middle" font-family="Arial" font-size="8.5" font-weight="900" fill="{fg}">{text}</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def league_logo_uri(league: str) -> str:
    for ext in ("png", "svg", "jpg", "jpeg", "webp"):
        path = os.path.join("assets", "logos", f"{league}.{ext}")
        if os.path.exists(path):
            return file_to_data_uri(path)
    bg, fg = LEAGUE_COLORS.get(league, ("#0f172a", "#ffffff"))
    return svg_badge(league, bg, fg)
def sport_art_uri(sport: str, league: str = "") -> str:
    """
    Returns a base64 SVG background that matches the sport.
    No external images required.
    """
    sport_key = (sport or "").lower()

    if "soccer" in sport_key:
        bg1, bg2, accent = "#16a34a", "#14532d", "rgba(255,255,255,0.55)"
        label = "SOCCER"
        lines = """
          <rect x="18" y="14" width="324" height="168" rx="18" fill="none" stroke="{accent}" stroke-width="3"/>
          <line x1="180" y1="14" x2="180" y2="182" stroke="{accent}" stroke-width="3"/>
          <circle cx="180" cy="98" r="28" fill="none" stroke="{accent}" stroke-width="3"/>
        """
    elif "basket" in sport_key:
        bg1, bg2, accent = "#f97316", "#7c2d12", "rgba(255,255,255,0.55)"
        label = "BASKETBALL"
        lines = """
          <rect x="18" y="14" width="324" height="168" rx="18" fill="none" stroke="{accent}" stroke-width="3"/>
          <circle cx="180" cy="98" r="30" fill="none" stroke="{accent}" stroke-width="3"/>
        """
    elif "baseball" in sport_key:
        bg1, bg2, accent = "#2563eb", "#1e3a8a", "rgba(255,255,255,0.6)"
        label = "BASEBALL"
        lines = """
          <path d="M180 168 L240 108 L180 48 L120 108 Z" fill="none" stroke="{accent}" stroke-width="3"/>
          <circle cx="180" cy="108" r="6" fill="{accent}"/>
        """
    elif "football" in sport_key:
        bg1, bg2, accent = "#111827", "#020617", "rgba(255,255,255,0.55)"
        label = "FOOTBALL"
        lines = """
          <rect x="18" y="14" width="324" height="168" rx="18" fill="none" stroke="{accent}" stroke-width="3"/>
        """
    else:
        bg1, bg2, accent = "#7c3aed", "#312e81", "rgba(255,255,255,0.5)"
        label = (league or "SPORT").upper()
        lines = ""

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="360" height="196" viewBox="0 0 360 196">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="{bg1}"/>
          <stop offset="1" stop-color="{bg2}"/>
        </linearGradient>
      </defs>
      <rect width="360" height="196" rx="18" fill="url(#g)"/>
      {lines.format(accent=accent)}
      <text x="20" y="180" font-size="14" font-weight="800"
            fill="rgba(255,255,255,0.7)">{label}</text>
    </svg>
    """
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

# ----------------------------
# Demo catalog
# ----------------------------
def demo_catalog():
    now = datetime.now()
    games = [
        {"game_id": "GK-7001", "sport": "Soccer", "league": "UCL", "home": "Manchester City", "away": "Galatasaray",
         "start": now + timedelta(hours=7), "platform": "Paramount+", "market": "US", "base_price": 2.99,
         "tags": ["Decision Day", "High stakes", "Prime time"], "about": "A must-win night. One game. One key."},

        {"game_id": "GK-7002", "sport": "Basketball", "league": "NBA", "home": "Knicks", "away": "Celtics",
         "start": now + timedelta(days=1, hours=2), "platform": "ESPN", "market": "US", "base_price": 1.99,
         "tags": ["MSG energy", "Playoff race", "Big matchup"], "about": "Classic rivalry energy in the Garden."},

        {"game_id": "GK-7003", "sport": "American Football", "league": "NFL", "home": "Eagles", "away": "Cowboys",
         "start": now + timedelta(days=2, hours=4), "platform": "FOX Sports", "market": "US", "base_price": 3.99,
         "tags": ["Rivalry", "Sunday", "Must watch"], "about": "Two brands. One statement game."},

        {"game_id": "GK-7004", "sport": "Soccer", "league": "MLS", "home": "NYCFC", "away": "Inter Miami",
         "start": now + timedelta(days=3, hours=1), "platform": "Apple TV", "market": "US", "base_price": 2.49,
         "tags": ["Stars", "Weekend", "Big draw"], "about": "When the stars come to town, you tap in."},

        {"game_id": "GK-7005", "sport": "Soccer", "league": "NWSL", "home": "Gotham FC", "away": "Angel City",
         "start": now + timedelta(days=4, hours=3), "platform": "Prime Video", "market": "US", "base_price": 1.49,
         "tags": ["Womens sports", "Community", "Rising"], "about": "Elite talent. Big moment. Easy access."},

        {"game_id": "GK-7006", "sport": "Baseball", "league": "MLB", "home": "Yankees", "away": "Red Sox",
         "start": now + timedelta(days=5, hours=2), "platform": "MLB.TV", "market": "US", "base_price": 3.49,
         "tags": ["Classic rivalry", "Prime series", "History"], "about": "A rivalry you do not need a subscription for."},
    ]
    df_ = pd.DataFrame(games)
    df_["start_str"] = df_["start"].dt.strftime("%a, %b %d - %I:%M %p")
    return df_.sort_values("start")

df = demo_catalog()

# ----------------------------
# Purchase + pricing
# ----------------------------
def is_purchased(game_id: str) -> bool:
    return game_id in st.session_state.purchases

def price_for(base_price: float, deal_on: bool, deal_pct: int) -> float:
    if deal_on:
        return round(float(base_price) * (1 - deal_pct / 100), 2)
    return float(base_price)

def tier_prices(base: float):
    return {
        "Standard": round(base, 2),
        "Plus (24h replay)": round(base + 1.00, 2),
        "Party (watch link)": round(base + 2.00, 2),
    }

def purchase(game_row: pd.Series, tier: str, price_paid: float):
    title = f"{game_row['away']} @ {game_row['home']}"
    st.session_state.purchases[game_row["game_id"]] = {
        "game_id": game_row["game_id"],
        "title": title,
        "league": game_row["league"],
        "platform": game_row["platform"],
        "start": game_row["start_str"],
        "tier": tier,
        "price_paid": float(price_paid),
        "purchased_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ----------------------------
# UI components
# ----------------------------
def poster_card(row: pd.Series, section_key: str, deal_on=False, deal_pct=0):
    game_id = row["game_id"]
    key_prefix = f"{section_key}__{game_id}"

    title = f"{row['away']} @ {row['home']}"
    p = price_for(row["base_price"], deal_on, deal_pct)
    purchased = is_purchased(game_id)
    logo_uri = league_logo_uri(row["league"])

art_uri = sport_art_uri(row["sport"], row["league"])
    st.markdown(
        f"""
       <div class="poster-art">
  <img class="poster-bg" src="{art_uri}" />
  <div class="poster-badge">
    <img class="logo" src="{logo_uri}" width="22" height="22"/>
    <span>{row["league"]}</span>
  </div>
</div>

          <div class="poster-main">{title}</div>
          <div class="poster-meta">{row["start_str"]} - {row["platform"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Details", key=f"details_{key_prefix}", use_container_width=True):
            st.session_state.active_game = game_id
            request_scroll("selected")
            st.rerun()
    with c2:
        if purchased:
            if st.button("Watch", key=f"watch_{key_prefix}", use_container_width=True):
                start_demo_playback(title=title, league=row["league"])
                toast("Starting demo playback...")
                st.rerun()
        else:
            if st.button(f"Buy ${p:,.2f}", key=f"buy_{key_prefix}", use_container_width=True):
                st.session_state.active_game = game_id
                request_scroll("selected")
                st.rerun()

def row_section(title: str, subset: pd.DataFrame, section_key: str, deal_on=False, deal_pct=0, max_items=4):
    st.markdown(f"<div class='rowtitle'>{title}</div>", unsafe_allow_html=True)
    subset = subset.head(max_items)
    cols = st.columns(2)
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 2]:
            poster_card(row, section_key=section_key, deal_on=deal_on, deal_pct=deal_pct)

def checkout_sheet(game_row: pd.Series, section_key: str, deal_on=False, deal_pct=0):
    game_id = game_row["game_id"]
    key_prefix = f"{section_key}__checkout__{game_id}"

    title = f"{game_row['away']} @ {game_row['home']}"
    base = price_for(game_row["base_price"], deal_on, deal_pct)
    tiers = tier_prices(base)

    with st.expander("Checkout", expanded=True):
        st.write(f"**{title}**")
        st.write(f"League: {game_row['league']} | Start: {game_row['start_str']}")
        st.write(f"Watch on: {game_row['platform']}")
        if deal_on:
            st.markdown(f"<span class='price-chip'>Deal -{deal_pct}%</span>", unsafe_allow_html=True)

        st.write("---")
        tier = st.radio("Access", options=list(tiers.keys()), index=0, key=f"tier_{key_prefix}")
        price_paid = tiers[tier]
        st.write(f"**Total: ${price_paid:,.2f}**")
        st.write("---")

        if st.session_state.wallet < price_paid:
            st.error("Not enough wallet balance (demo). Add funds in Profile.")
            return

        if st.button(f"Confirm ${price_paid:,.2f}", key=f"confirm_{key_prefix}", use_container_width=True):
            st.session_state.wallet = round(st.session_state.wallet - price_paid, 2)
            purchase(game_row, tier=tier, price_paid=price_paid)
            toast("Purchased. Unlocked in Library.")
            st.session_state.active_game = None
            st.rerun()

def social_sheet(game_row: pd.Series, section_key: str):
    game_id = game_row["game_id"]
    key_prefix = f"{section_key}__social__{game_id}"
    share_url = f"https://gamekey.app/game/{game_id}"

    with st.expander("Watch Party (demo)", expanded=False):
        st.write("Invite friends (placeholder).")
        st.text_input("Emails (comma-separated)", "", key=f"emails_{key_prefix}")
        st.button("Send", key=f"invite_{key_prefix}", use_container_width=True)

    with st.expander("Share (demo)", expanded=False):
        st.code(share_url, language="text")

# ----------------------------
# Render: phone frame
# ----------------------------
st.markdown("<div class='phone'><div class='notch'></div><div class='phone-inner'>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="brand">GameKey</div>
        <div class="subtle">Watch one game. Pay once.</div>
      </div>
      <div class="wallet">
        <div class="subtle">Wallet</div>
        <div>${st.session_state.wallet:,.2f}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.toast_msg:
    st.success(st.session_state.toast_msg)
    st.session_state.toast_msg = None

tab_home, tab_explore, tab_library, tab_profile = st.tabs(["Home", "Explore", "Library", "Profile"])

# HOME
with tab_home:
    st.markdown(
        """
        <div class="hero">
          <div class="hero-title">Tonight is<br>for big games.</div>
          <div class="hero-sub">Instant, low-cost access - no subscription needed.</div>
          <div>
            <span class="pill">Trending</span>
            <span class="pill">Rivalries</span>
            <span class="pill">For You</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    upcoming = df[df["start"] > datetime.now()].head(6)
    rivalries = df[df["tags"].apply(lambda x: any(("Rivalry" in t) or ("Classic rivalry" in t) for t in x))].head(6)

    row_section("Trending Tonight", upcoming, section_key="home_trending", deal_on=True, deal_pct=20, max_items=4)
    row_section("Rivalries", rivalries if not rivalries.empty else df.sample(min(6, len(df)), random_state=1),
                section_key="home_rivalries", deal_on=False, max_items=4)

    rec = df.sample(min(6, len(df)), random_state=7)
    row_section("For You", rec, section_key="home_foryou", deal_on=False, max_items=4)

# EXPLORE
with tab_explore:
    st.markdown("<div class='rowtitle'>Search and Filter</div>", unsafe_allow_html=True)

    q = st.text_input("Search teams / league / platform", "", key="explore_search")
    f1, f2 = st.columns(2)
    with f1:
        sport = st.selectbox("Sport", ["All"] + sorted(df["sport"].unique().tolist()), key="explore_sport")
    with f2:
        league = st.selectbox("League", ["All"] + sorted(df["league"].unique().tolist()), key="explore_league")

    max_price = st.slider("Max price", 0.99, 9.99, 4.99, 0.50, key="explore_max_price")
    deal_on = st.toggle("Show Deals", value=False, key="explore_deals")
    deal_pct = st.slider("Deal percent", 10, 60, 20, 5, key="explore_deal_pct") if deal_on else 0

    filtered = df.copy()
    if q.strip():
        mask = (
            filtered["home"].str.contains(q, case=False) |
            filtered["away"].str.contains(q, case=False) |
            filtered["league"].str.contains(q, case=False) |
            filtered["platform"].str.contains(q, case=False)
        )
        filtered = filtered[mask]
    if sport != "All":
        filtered = filtered[filtered["sport"] == sport]
    if league != "All":
        filtered = filtered[filtered["league"] == league]
    filtered = filtered[filtered["base_price"] <= max_price]

    if filtered.empty:
        st.info("No matches. Tweak filters or increase max price.")
    else:
        row_section("Browse", filtered, section_key="explore_browse", deal_on=deal_on, deal_pct=deal_pct, max_items=6)

# LIBRARY
with tab_library:
    st.markdown("<div class='rowtitle'>My Library</div>", unsafe_allow_html=True)

    if not st.session_state.purchases:
        st.info("No games unlocked yet. Unlock a game from Home or Explore.")
    else:
        lib = pd.DataFrame(st.session_state.purchases.values()).sort_values("purchased_at", ascending=False)
        for _, r in lib.iterrows():
            game_id = r["game_id"]
            logo_uri = league_logo_uri(r["league"])
            st.markdown(
                f"""
                <div class="poster">
                  <div class="poster-art" style="height:110px;">
                    <div class="poster-badge">
                      <img class="logo" src="{logo_uri}" width="22" height="22"/>
                      <span>{r["league"]}</span>
                    </div>
                  </div>
                  <div class="poster-main">{r["title"]}</div>
                  <div class="poster-meta">{r["start"]} - {r["platform"]} - {r["tier"]} - Paid ${float(r["price_paid"]):,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Watch", key=f"lib_watch__{game_id}", use_container_width=True):
                start_demo_playback(title=r["title"], league=r["league"])
                toast("Starting demo playback...")
                st.rerun()

            st.write("")

# PROFILE
with tab_profile:
    st.markdown("<div class='rowtitle'>Profile</div>", unsafe_allow_html=True)
    st.write(f"User: {st.session_state.user_id}")

    name = st.text_input("Display name", st.session_state.display_name, key="profile_name")
    if st.button("Save", key="profile_save", use_container_width=True):
        st.session_state.display_name = name.strip() or "Guest"
        toast("Saved.")
        st.rerun()

    st.markdown("<div class='rowtitle'>Wallet (demo)</div>", unsafe_allow_html=True)
    add = st.number_input("Add funds", min_value=0.0, max_value=200.0, value=5.0, step=1.0, key="wallet_add_amt")
    if st.button("Add funds", key="wallet_add_btn", use_container_width=True):
        st.session_state.wallet = round(st.session_state.wallet + float(add), 2)
        toast("Wallet updated.")
        st.rerun()

    st.markdown("<div class='rowtitle'>Reset</div>", unsafe_allow_html=True)
    if st.button("Reset demo data", key="reset_demo", use_container_width=True):
        st.session_state.purchases = {}
        st.session_state.wallet = 12.00
        st.session_state.active_game = None
        st.session_state.now_playing = None
        st.session_state.scroll_to = None
        toast("Reset complete.")
        st.rerun()

# ----------------------------
# Selected / Checkout (with anchor)
# ----------------------------
st.markdown("<div id='selected_anchor'></div>", unsafe_allow_html=True)

if st.session_state.active_game:
    sel = df[df["game_id"] == st.session_state.active_game]
    if sel.empty:
        st.session_state.active_game = None
        toast("Selection refreshed. Please pick a game again.")
        st.rerun()

    game_row = sel.iloc[0]
    game_id = game_row["game_id"]

    st.markdown("<div class='rowtitle'>Selected</div>", unsafe_allow_html=True)
    st.info(f"{game_row['away']} @ {game_row['home']} - {game_row['league']} - {game_row['start_str']}")
    st.write(game_row["about"])

    within_24 = (game_row["start"] - datetime.now()) <= timedelta(hours=24)
    deal_on = bool(within_24)
    deal_pct = 20 if deal_on else 0

    if is_purchased(game_id):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Watch", key=f"selected_watch__{game_id}", use_container_width=True):
                start_demo_playback(title=f"{game_row['away']} @ {game_row['home']}", league=game_row["league"])
                toast("Starting demo playback...")
                st.rerun()
        with c2:
            if st.button("Close", key=f"selected_close__{game_id}", use_container_width=True):
                st.session_state.active_game = None
                st.rerun()
        social_sheet(game_row, section_key="selected_purchased")
    else:
        checkout_sheet(game_row, section_key="selected", deal_on=deal_on, deal_pct=deal_pct)
        social_sheet(game_row, section_key="selected")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Close", key=f"checkout_close__{game_id}", use_container_width=True):
                st.session_state.active_game = None
                st.rerun()
        with c2:
            if st.button("Add $5", key=f"checkout_add5__{game_id}", use_container_width=True):
                st.session_state.wallet = round(st.session_state.wallet + 5.0, 2)
                toast("Wallet +$5.")
                request_scroll("selected")
                st.rerun()

# ----------------------------
# Now Playing (with anchor)
# ----------------------------
st.markdown("<div id='player_anchor'></div>", unsafe_allow_html=True)

if st.session_state.now_playing:
    vid = st.session_state.now_playing
    st.markdown("<div class='rowtitle'>Now Playing</div>", unsafe_allow_html=True)
    st.info(f"{vid['title']} (demo playback)")

    if vid.get("url"):
        st.video(vid["url"])
    else:
        st.warning("No demo video is set for this league. Add a URL in YOUTUBE_DEMOS for this league code.")

    if st.button("Close Player", key="close_player", use_container_width=True):
        st.session_state.now_playing = None
        st.rerun()

# Fire scroll (after anchors exist on the page)
run_scroll_if_requested()

# Close phone frame
st.markdown("</div></div>", unsafe_allow_html=True)

st.caption("Demo only - No real payments/rights/streams - Prototype presentation.")

# app.py
# GameKey — Netflix-style consumer prototype (Streamlit)
# Demo only: no real payments/rights/streams.

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import uuid
import base64
import random

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="GameKey", page_icon="🔑", layout="wide")

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
if "toast" not in st.session_state:
    st.session_state.toast = None
if "active_game" not in st.session_state:
    st.session_state.active_game = None  # selected game_id

def toast(msg: str):
    st.session_state.toast = msg

# ----------------------------
# Netflix-ish + Phone frame CSS
# ----------------------------
st.markdown(
    """
    <style>
      /* Hide Streamlit chrome */
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      header {visibility: hidden;}

      /* Page background */
      .stApp {
        background: radial-gradient(1200px 600px at 15% 10%, rgba(255,0,80,0.16), transparent 60%),
                    radial-gradient(900px 500px at 80% 20%, rgba(0,120,255,0.18), transparent 55%),
                    #0b0b0f;
      }

      /* Center content like a phone */
      .block-container {
        max-width: 440px !important;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
      }

      /* Phone frame */
      .phone {
        border-radius: 38px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(10,10,16,0.86);
        box-shadow: 0 30px 80px rgba(0,0,0,0.55);
        overflow: hidden;
      }
      .phone-inner {
        padding: 18px 16px 20px 16px;
      }
      .notch {
        height: 22px;
        width: 140px;
        margin: 0 auto;
        border-radius: 0 0 18px 18px;
        background: rgba(0,0,0,0.65);
        border: 1px solid rgba(255,255,255,0.07);
        border-top: none;
      }

      /* Top bar */
      .topbar {
        display:flex; justify-content:space-between; align-items:center;
        margin-top: 10px;
      }
      .brand {
        font-weight: 900;
        letter-spacing: -0.5px;
        font-size: 18px;
      }
      .subtle {
        opacity: 0.75;
      }
      .wallet {
        text-align:right;
        font-weight: 800;
        font-size: 14px;
      }

      /* Hero banner */
      .hero {
        border-radius: 22px;
        padding: 18px 16px;
        margin-top: 14px;
        border: 1px solid rgba(255,255,255,0.09);
        background:
          radial-gradient(900px 260px at 0% 0%, rgba(255,0,80,0.30), transparent 55%),
          radial-gradient(900px 260px at 100% 20%, rgba(255,122,0,0.22), transparent 55%),
          linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
      }
      .hero-title {
        font-size: 28px;
        font-weight: 950;
        line-height: 1.05;
        margin: 0;
      }
      .hero-sub {
        margin-top: 8px;
        font-size: 13px;
        opacity: 0.80;
      }
      .pill {
        display:inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        font-size: 11px;
        margin-right: 6px;
        margin-top: 8px;
      }

      /* Row headings */
      .rowtitle {
        margin: 18px 0 8px 0;
        font-size: 14px;
        font-weight: 850;
        letter-spacing: -0.2px;
      }

      /* Poster cards */
      .poster {
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        padding: 12px;
      }
      .poster-art {
        height: 140px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        background:
          radial-gradient(260px 120px at 20% 30%, rgba(255,0,80,0.26), transparent 55%),
          radial-gradient(260px 120px at 80% 20%, rgba(0,120,255,0.24), transparent 55%),
          linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01));
        position: relative;
        overflow: hidden;
      }
      .poster-badge {
        position:absolute;
        top:10px; left:10px;
        display:flex; align-items:center; gap:8px;
        background: rgba(0,0,0,0.55);
        border: 1px solid rgba(255,255,255,0.10);
        padding: 6px 8px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
      }
      .poster-main {
        margin-top: 10px;
        font-weight: 850;
        font-size: 13px;
        line-height: 1.1;
      }
      .poster-meta {
        margin-top: 6px;
        font-size: 11px;
        opacity: 0.75;
      }

      /* Buttons rounder */
      .stButton>button {
        border-radius: 14px;
        padding: 0.58rem 0.9rem;
        font-weight: 800;
      }
      .stTextInput input, .stNumberInput input {
        border-radius: 14px;
      }
      .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 14px;
      }

      /* Tabs style */
      .stTabs [data-baseweb="tab"] {
        font-size: 12px;
        padding: 10px 12px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# League "logo" badges (SVG)
# (These are stylized badges, not official trademarks)
# ----------------------------
LEAGUE_COLORS = {
    "UCL": ("#0b5fff", "#ffffff"),
    "NBA": ("#ff2a5b", "#ffffff"),
    "NFL": ("#00a3ff", "#ffffff"),
    "MLS": ("#ff7a00", "#ffffff"),
    "NWSL": ("#8a5cff", "#ffffff"),
    "MLB": ("#00d18f", "#0b0b0f"),
}

def svg_badge(text: str, bg: str, fg: str) -> str:
    # Simple circular badge with initials
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">
      <circle cx="11" cy="11" r="10" fill="{bg}" stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
      <text x="11" y="14" text-anchor="middle" font-family="Inter, Arial" font-size="8.5" font-weight="900" fill="{fg}">
        {text}
      </text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def league_icon_uri(league: str) -> str:
    bg, fg = LEAGUE_COLORS.get(league, ("#ffffff", "#000000"))
    return svg_badge(league, bg, fg)

# ----------------------------
# Demo catalog
# ----------------------------
def demo_catalog():
    now = datetime.now()
    games = [
        {"game_id":"GK-3001","sport":"Soccer","league":"UCL","home":"Manchester City","away":"Galatasaray",
         "start": now + timedelta(hours=7), "platform":"Paramount+","market":"US","base_price":2.99,
         "tags":["Decision Day","High stakes","Prime time"], "about":"A must-win night. One game. One key."},
        {"game_id":"GK-3002","sport":"Basketball","league":"NBA","home":"Knicks","away":"Celtics",
         "start": now + timedelta(days=1, hours=2), "platform":"ESPN","market":"US","base_price":1.99,
         "tags":["MSG energy","Playoff race","Big matchup"], "about":"Classic rivalry energy in the Garden."},
        {"game_id":"GK-3003","sport":"American Football","league":"NFL","home":"Eagles","away":"Cowboys",
         "start": now + timedelta(days=2, hours=4), "platform":"FOX Sports","market":"US","base_price":3.99,
         "tags":["Rivalry","Sunday","Must watch"], "about":"Two brands. One statement game."},
        {"game_id":"GK-3004","sport":"Soccer","league":"MLS","home":"NYCFC","away":"Inter Miami",
         "start": now + timedelta(days=3, hours=1), "platform":"Apple TV","market":"US","base_price":2.49,
         "tags":["Stars","Weekend","Big draw"], "about":"When the stars come to town, you tap in."},
        {"game_id":"GK-3005","sport":"Soccer","league":"NWSL","home":"Gotham FC","away":"Angel City",
         "start": now + timedelta(days=4, hours=3), "platform":"Prime Video","market":"US","base_price":1.49,
         "tags":["Women’s sports","Community","Rising"], "about":"Elite talent. Big moment. Easy access."},
        {"game_id":"GK-3006","sport":"Baseball","league":"MLB","home":"Yankees","away":"Red Sox",
         "start": now + timedelta(days=5, hours=2), "platform":"MLB.TV","market":"US","base_price":3.49,
         "tags":["Classic rivalry","Prime series","History"], "about":"A rivalry you don’t need a subscription for."},
    ]
    df = pd.DataFrame(games)
    df["start_str"] = df["start"].dt.strftime("%a, %b %d • %I:%M %p")
    return df.sort_values("start")

df = demo_catalog()

# ----------------------------
# Purchase helpers
# ----------------------------
def is_purchased(game_id: str) -> bool:
    return game_id in st.session_state.purchases

def purchase(game_id: str, title: str, price_paid: float, platform: str, start_str: str, league: str):
    st.session_state.purchases[game_id] = {
        "game_id": game_id,
        "title": title,
        "league": league,
        "price_paid": price_paid,
        "platform": platform,
        "start": start_str,
        "purchased_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def price_for(base_price: float, deal_on: bool, deal_pct: int) -> float:
    if deal_on:
        return round(base_price * (1 - deal_pct/100), 2)
    return float(base_price)

# ----------------------------
# UI building blocks
# ----------------------------
def poster_card(row, deal_on=False, deal_pct=0):
    game_id = row["game_id"]
    title = f"{row['away']} @ {row['home']}"
    p = price_for(row["base_price"], deal_on, deal_pct)
    purchased = is_purchased(game_id)

    icon_uri = league_icon_uri(row["league"])

    # Poster "art" + badge via HTML
    st.markdown(
        f"""
        <div class="poster">
          <div class="poster-art">
            <div class="poster-badge">
              <img src="{icon_uri}" width="22" height="22"/>
              {row["league"]}
            </div>
          </div>
          <div class="poster-main">{title}</div>
          <div class="poster-meta">{row["start_str"]} • {row["platform"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Actions (Streamlit buttons under the card)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Details", key=f"details_{game_id}", use_container_width=True):
            st.session_state.active_game = game_id
    with c2:
        if purchased:
            if st.button("Watch ▶", key=f"watch_{game_id}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. In production, this deep-links into the broadcaster stream with auth.")
        else:
            if st.button(f"Unlock ${p:,.2f}", key=f"unlock_{game_id}", use_container_width=True):
                st.session_state.active_game = game_id
                # Open checkout via state (below)

def row_section(title: str, subset: pd.DataFrame, deal_on=False, deal_pct=0):
    st.markdown(f"<div class='rowtitle'>{title}</div>", unsafe_allow_html=True)
    cols = st.columns(2)  # phone layout: 2 posters per row
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 2]:
            poster_card(row, deal_on=deal_on, deal_pct=deal_pct)

def checkout_sheet(game_row, deal_on=False, deal_pct=0):
    title = f"{game_row['away']} @ {game_row['home']}"
    p = price_for(game_row["base_price"], deal_on, deal_pct)

    with st.expander("🧾 Checkout", expanded=True):
        st.write(f"**{title}**")
        st.write(f"**League:** {game_row['league']}  |  **Start:** {game_row['start_str']}")
        st.write(f"**Watch on:** {game_row['platform']}")
        st.write(f"**Price:** ${p:,.2f}" + (" (deal)" if deal_on else ""))
        st.write("---")
        if st.session_state.wallet < p:
            st.error("Not enough wallet balance (demo). Add funds in Profile.")
        else:
            if st.button(f"Confirm Purchase • ${p:,.2f}", use_container_width=True, key="confirm_purchase"):
                st.session_state.wallet = round(st.session_state.wallet - p, 2)
                purchase(game_row["game_id"], title, p, game_row["platform"], game_row["start_str"], game_row["league"])
                toast("Purchased ✅ Unlocked in My Library.")
                st.session_state.active_game = None
                st.rerun()

# ----------------------------
# Render inside phone frame
# ----------------------------
st.markdown("<div class='phone'><div class='notch'></div><div class='phone-inner'>", unsafe_allow_html=True)

# Top bar
st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="brand">🔑 GameKey</div>
        <div class="subtle" style="font-size:12px;">Watch one game. Pay once.</div>
      </div>
      <div class="wallet">
        <div class="subtle">Wallet</div>
        <div>${st.session_state.wallet:,.2f}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.toast:
    st.success(st.session_state.toast)
    st.session_state.toast = None

# Tabs (app nav)
tab_home, tab_explore, tab_library, tab_profile = st.tabs(["Home", "Explore", "Library", "Profile"])

# ----------------------------
# HOME (Netflix feed)
# ----------------------------
with tab_home:
    st.markdown(
        """
        <div class="hero">
          <div class="hero-title">Tonight is<br>for big games.</div>
          <div class="hero-sub">Instant, low-cost access — without subscribing to another platform.</div>
          <div>
            <span class="pill">Trending now</span>
            <span class="pill">Rivalries</span>
            <span class="pill">Playoff energy</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    upcoming = df[df["start"] > datetime.now()].head(4)
    rivalries = df[df["tags"].apply(lambda x: "Rivalry" in x or "Classic rivalry" in x)].head(4)

    # "Netflix rows"
    row_section("🔥 Trending Tonight", upcoming, deal_on=True, deal_pct=20)
    row_section("⚔️ Rivalries", rivalries if not rivalries.empty else df.sample(min(4, len(df)), random_state=1), deal_on=False)

    # Personalized-ish row
    random.seed(7)
    rec = df.sample(min(4, len(df)), random_state=7)
    row_section("✨ For You", rec)

# ----------------------------
# EXPLORE
# ----------------------------
with tab_explore:
    st.markdown("<div class='rowtitle'>Search & Filter</div>", unsafe_allow_html=True)
    q = st.text_input("Search teams / league / platform", "")

    f1, f2 = st.columns(2)
    with f1:
        sport = st.selectbox("Sport", ["All"] + sorted(df["sport"].unique().tolist()))
    with f2:
        league = st.selectbox("League", ["All"] + sorted(df["league"].unique().tolist()))

    max_price = st.slider("Max price", 0.99, 9.99, 4.99, 0.50)

    deal_on = st.toggle("Show Deals", value=False)
    deal_pct = st.slider("Deal %", 10, 60, 20, 5) if deal_on else 0

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
        st.info("No matches — tweak filters or increase max price.")
    else:
        row_section("Browse", filtered.head(6), deal_on=deal_on, deal_pct=deal_pct)

# ----------------------------
# LIBRARY
# ----------------------------
with tab_library:
    st.markdown("<div class='rowtitle'>My Library</div>", unsafe_allow_html=True)
    if not st.session_state.purchases:
        st.info("No games unlocked yet. Unlock a game from Home or Explore.")
    else:
        lib = pd.DataFrame(st.session_state.purchases.values()).sort_values("purchased_at", ascending=False)
        for _, r in lib.iterrows():
            icon_uri = league_icon_uri(r["league"])
            st.markdown(
                f"""
                <div class="poster">
                  <div class="poster-art" style="height:110px;">
                    <div class="poster-badge">
                      <img src="{icon_uri}" width="22" height="22"/>
                      {r["league"]}
                    </div>
                  </div>
                  <div class="poster-main">{r["title"]}</div>
                  <div class="poster-meta">{r["start"]} • {r["platform"]} • Paid ${float(r["price_paid"]):,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Watch ▶", key=f"lib_watch_{r['game_id']}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. Production would deep-link into broadcaster stream.")
            st.write("")

# ----------------------------
# PROFILE
# ----------------------------
with tab_profile:
    st.markdown("<div class='rowtitle'>Profile</div>", unsafe_allow_html=True)
    st.write(f"**User:** {st.session_state.user_id}")
    name = st.text_input("Display name", st.session_state.display_name)
    if st.button("Save", use_container_width=True):
        st.session_state.display_name = name.strip() or "Guest"
        toast("Saved ✅")
        st.rerun()

    st.markdown("<div class='rowtitle'>Wallet (demo)</div>", unsafe_allow_html=True)
    add = st.number_input("Add funds", min_value=0.0, max_value=200.0, value=5.0, step=1.0)
    if st.button("Add funds", use_container_width=True):
        st.session_state.wallet = round(st.session_state.wallet + float(add), 2)
        toast("Wallet updated ✅")
        st.rerun()

    st.markdown("<div class='rowtitle'>Reset</div>", unsafe_allow_html=True)
    if st.button("Reset demo data", use_container_width=True):
        st.session_state.purchases = {}
        st.session_state.wallet = 12.00
        st.session_state.active_game = None
        toast("Reset complete ✅")
        st.rerun()

# ----------------------------
# Details + Checkout “sheet”
# (Shown when a game is selected)
# ----------------------------
if st.session_state.active_game:
    game_row = df[df["game_id"] == st.session_state.active_game].iloc[0]
    st.markdown("<div class='rowtitle'>Selected</div>", unsafe_allow_html=True)
    st.info(f"{game_row['away']} @ {game_row['home']} • {game_row['league']} • {game_row['start_str']}")
    st.write(game_row["about"])

    # Deal logic for the checkout from Home vibe
    # (simple: if it’s within next 24h, we show a small deal)
    within_24 = (game_row["start"] - datetime.now()) <= timedelta(hours=24)
    deal_on = bool(within_24)
    deal_pct = 20 if deal_on else 0

    if is_purchased(game_row["game_id"]):
        if st.button("Watch ▶", use_container_width=True, key="watch_selected"):
            toast("Launching player (demo)…")
            st.info("Demo player placeholder. Production would deep-link into broadcaster stream.")
        if st.button("Close", use_container_width=True, key="close_selected"):
            st.session_state.active_game = None
            st.rerun()
    else:
        checkout_sheet(game_row, deal_on=deal_on, deal_pct=deal_pct)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Close", use_container_width=True, key="close_checkout"):
                st.session_state.active_game = None
                st.rerun()
        with c2:
            # Social layer placeholders (for demo)
            with st.expander("👥 Watch Party (demo)"):
                st.write("Invite friends to unlock together (placeholder).")
                st.text_input("Friend emails (comma-separated)", "")
                st.button("Send invites", use_container_width=True, key="invite_demo")
            with st.expander("🔗 Share (demo)"):
                st.code(f"https://gamekey.app/game/{game_row['game_id']}", language="text")

# Close phone frame
st.markdown("</div></div>", unsafe_allow_html=True)

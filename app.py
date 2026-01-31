# app.py
# GameKey — Netflix-style consumer prototype (Streamlit) with phone frame
# ✅ Netflix look/feel (hero + rows)
# ✅ League "logo" badges (stylized SVG badges)
# ✅ Ticketing-style checkout (tiers + quick confirm)
# ✅ Social layer (share link + watch party placeholder)
# ✅ FIXED: Unique widget keys across repeated rows/sections

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
    st.session_state.purchases = {}  # game_id -> meta
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
   <style>
/* Hide Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* App background */
.stApp {
  background: #0b0b0f;
}

/* Phone container */
.block-container {
  max-width: 460px !important;
  padding-top: 1rem;
  padding-bottom: 3rem;
}

.phone {
  background: #111318;
  border-radius: 36px;
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 30px 80px rgba(0,0,0,0.6);
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
  background: #000;
}

/* Top bar */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-weight: 900;
  font-size: 18px;
  color: #ffffff;
}

.subtle {
  font-size: 12px;
  color: #b5b8c5;
}

.wallet {
  text-align: right;
  font-weight: 800;
  color: #ffffff;
}

/* HERO */
.hero {
  margin-top: 14px;
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(135deg, #2b0f1c, #15182a);
  border: 1px solid rgba(255,255,255,0.08);
}

.hero-title {
  font-size: 28px;
  font-weight: 900;
  color: #ffffff;
}

.hero-sub {
  margin-top: 6px;
  font-size: 13px;
  color: #d1d4e0;
}

.pill {
  display: inline-block;
  margin-top: 10px;
  margin-right: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
}

/* Section headers */
.rowtitle {
  margin: 18px 0 10px 0;
  font-size: 14px;
  font-weight: 900;
  color: #ffffff;
}

/* Cards */
.poster {
  background: #161923;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 12px;
}

.poster-art {
  height: 140px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2c1a2e, #1a1f33);
  position: relative;
}

.poster-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #000000cc;
  padding: 6px 10px;
  border-radius: 999px;
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
}

.poster-main {
  margin-top: 10px;
  font-size: 13px;
  font-weight: 900;
  color: #ffffff;
}

.poster-meta {
  margin-top: 4px;
  font-size: 11px;
  color: #aeb3c7;
}

/* Buttons */
.stButton > button {
  background: #e50914;
  color: #ffffff;
  border-radius: 14px;
  font-weight: 900;
  border: none;
}

.stButton > button:hover {
  background: #ff1f2d;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
  font-size: 12px;
  color: #9aa0b5;
}

.stTabs [aria-selected="true"] {
  color: #ffffff;
  border-bottom: 2px solid #e50914;
}
</style>

# ----------------------------
# League "logo" badges (stylized SVG)
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
        {"game_id":"GK-4001","sport":"Soccer","league":"UCL","home":"Manchester City","away":"Galatasaray",
         "start": now + timedelta(hours=7), "platform":"Paramount+","market":"US","base_price":2.99,
         "tags":["Decision Day","High stakes","Prime time"], "about":"A must-win night. One game. One key."},
        {"game_id":"GK-4002","sport":"Basketball","league":"NBA","home":"Knicks","away":"Celtics",
         "start": now + timedelta(days=1, hours=2), "platform":"ESPN","market":"US","base_price":1.99,
         "tags":["MSG energy","Playoff race","Big matchup"], "about":"Classic rivalry energy in the Garden."},
        {"game_id":"GK-4003","sport":"American Football","league":"NFL","home":"Eagles","away":"Cowboys",
         "start": now + timedelta(days=2, hours=4), "platform":"FOX Sports","market":"US","base_price":3.99,
         "tags":["Rivalry","Sunday","Must watch"], "about":"Two brands. One statement game."},
        {"game_id":"GK-4004","sport":"Soccer","league":"MLS","home":"NYCFC","away":"Inter Miami",
         "start": now + timedelta(days=3, hours=1), "platform":"Apple TV","market":"US","base_price":2.49,
         "tags":["Stars","Weekend","Big draw"], "about":"When the stars come to town, you tap in."},
        {"game_id":"GK-4005","sport":"Soccer","league":"NWSL","home":"Gotham FC","away":"Angel City",
         "start": now + timedelta(days=4, hours=3), "platform":"Prime Video","market":"US","base_price":1.49,
         "tags":["Women’s sports","Community","Rising"], "about":"Elite talent. Big moment. Easy access."},
        {"game_id":"GK-4006","sport":"Baseball","league":"MLB","home":"Yankees","away":"Red Sox",
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

def purchase(game_row: pd.Series, tier: str, price_paid: float):
    title = f"{game_row['away']} @ {game_row['home']}"
    st.session_state.purchases[game_row["game_id"]] = {
        "game_id": game_row["game_id"],
        "title": title,
        "league": game_row["league"],
        "platform": game_row["platform"],
        "start": game_row["start_str"],
        "tier": tier,
        "price_paid": price_paid,
        "purchased_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def price_for(base_price: float, deal_on: bool, deal_pct: int) -> float:
    if deal_on:
        return round(float(base_price) * (1 - deal_pct / 100), 2)
    return float(base_price)

# ----------------------------
# Ticketing-style tiers
# ----------------------------
def tier_prices(base: float):
    # Simple tier ladder (demo)
    return {
        "Standard": round(base, 2),
        "Plus (24h replay)": round(base + 1.00, 2),
        "Party (watch link)": round(base + 2.00, 2),
    }

# ----------------------------
# UI building blocks
# ----------------------------
def poster_card(row: pd.Series, section_key: str, deal_on=False, deal_pct=0):
    """
    Renders one "poster" game card.
    IMPORTANT: widget keys include section_key to avoid StreamlitDuplicateElementKey
    """
    game_id = row["game_id"]
    key_prefix = f"{section_key}__{game_id}"  # unique per section+game
    title = f"{row['away']} @ {row['home']}"
    p = price_for(row["base_price"], deal_on, deal_pct)
    purchased = is_purchased(game_id)
    icon_uri = league_icon_uri(row["league"])

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
          <div class="poster-meta">{row["start_str"]} - {row["platform"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Details", key=f"details_{key_prefix}", use_container_width=True):
            st.session_state.active_game = game_id
    with c2:
        if purchased:
            if st.button("Watch ▶", key=f"watch_{key_prefix}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. In production, deep-link into broadcaster stream with auth.")
        else:
            if st.button(f"Unlock ${p:,.2f}", key=f"unlock_{key_prefix}", use_container_width=True):
                st.session_state.active_game = game_id

def row_section(title: str, subset: pd.DataFrame, section_key: str, deal_on=False, deal_pct=0, max_items=4):
    st.markdown(f"<div class='rowtitle'>{title}</div>", unsafe_allow_html=True)
    subset = subset.head(max_items)
    cols = st.columns(2)  # phone layout: 2 posters per row
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 2]:
            poster_card(row, section_key=section_key, deal_on=deal_on, deal_pct=deal_pct)

def checkout_sheet(game_row: pd.Series, section_key: str, deal_on=False, deal_pct=0):
    """
    Ticketing-style checkout: tier select + confirm.
    Keys are unique per section_key + game.
    """
    game_id = game_row["game_id"]
    key_prefix = f"{section_key}__checkout__{game_id}"

    title = f"{game_row['away']} @ {game_row['home']}"
    base = price_for(game_row["base_price"], deal_on, deal_pct)
    tiers = tier_prices(base)

    with st.expander("🧾 Checkout", expanded=True):
        st.write(f"**{title}**")
        st.write(f"**League:** {game_row['league']}  |  **Start:** {game_row['start_str']}")
        st.write(f"**Watch on:** {game_row['platform']}")
        if deal_on:
            st.markdown(f"<span class='price-chip'>Deal: -{deal_pct}%</span>", unsafe_allow_html=True)
        st.write("---")

        tier = st.radio(
            "Choose your access",
            options=list(tiers.keys()),
            index=0,
            key=f"tier_{key_prefix}"
        )
        price_paid = tiers[tier]
        st.write(f"**Total:** ${price_paid:,.2f}")

        st.write("---")

        if st.session_state.wallet < price_paid:
            st.error("Not enough wallet balance (demo). Add funds in Profile.")
            return

        if st.button(f"Confirm Purchase • ${price_paid:,.2f}", key=f"confirm_{key_prefix}", use_container_width=True):
            st.session_state.wallet = round(st.session_state.wallet - price_paid, 2)
            purchase(game_row, tier=tier, price_paid=price_paid)
            toast("Purchased ✅ Unlocked in Library.")
            st.session_state.active_game = None
            st.rerun()

def social_sheet(game_row: pd.Series, section_key: str):
    """
    Social layer: share + watch party placeholder.
    Keys are unique per section_key + game.
    """
    game_id = game_row["game_id"]
    key_prefix = f"{section_key}__social__{game_id}"
    share_url = f"https://gamekey.app/game/{game_id}"

    with st.expander("👥 Watch Party (demo)", expanded=False):
        st.write("Invite friends. Everyone unlocks. Then watch together (placeholder).")
        st.text_input("Friend emails (comma-separated)", "", key=f"emails_{key_prefix}")
        st.button("Send invites", key=f"invite_{key_prefix}", use_container_width=True)

    with st.expander("🔗 Share (demo)", expanded=False):
        st.caption("Share link (placeholder):")
        st.code(share_url, language="text")

# ----------------------------
# Render inside phone frame
# ----------------------------
st.markdown("<div class='phone'><div class='notch'></div><div class='phone-inner'>", unsafe_allow_html=True)

# Top bar
st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="brand"> GameKey</div>
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

    # Netflix-style rows (same games may appear multiple times — keys stay unique via section_key)
    row_section("🔥 Trending Tonight", upcoming, section_key="home_trending", deal_on=True, deal_pct=20, max_items=4)
    row_section(
        "⚔️ Rivalries",
        rivalries if not rivalries.empty else df.sample(min(6, len(df)), random_state=1),
        section_key="home_rivalries",
        deal_on=False,
        max_items=4
    )

    # Personalized-ish row
    rec = df.sample(min(6, len(df)), random_state=7)
    row_section("✨ For You", rec, section_key="home_foryou", deal_on=False, max_items=4)

# ----------------------------
# EXPLORE
# ----------------------------
with tab_explore:
    st.markdown("<div class='rowtitle'>Search & Filter</div>", unsafe_allow_html=True)

    q = st.text_input("Search teams / league / platform", "", key="explore_search")
    f1, f2 = st.columns(2)
    with f1:
        sport = st.selectbox("Sport", ["All"] + sorted(df["sport"].unique().tolist()), key="explore_sport")
    with f2:
        league = st.selectbox("League", ["All"] + sorted(df["league"].unique().tolist()), key="explore_league")

    max_price = st.slider("Max price", 0.99, 9.99, 4.99, 0.50, key="explore_max_price")
    deal_on = st.toggle("Show Deals", value=False, key="explore_deals")
    deal_pct = st.slider("Deal %", 10, 60, 20, 5, key="explore_deal_pct") if deal_on else 0

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
        row_section("Browse", filtered, section_key="explore_browse", deal_on=deal_on, deal_pct=deal_pct, max_items=6)

# ----------------------------
# LIBRARY
# ----------------------------
with tab_library:
    st.markdown("<div class='rowtitle'>My Library</div>", unsafe_allow_html=True)
    if not st.session_state.purchases:
        st.info("No games unlocked yet. Unlock a game from Home or Explore.")
    else:
        lib = pd.DataFrame(st.session_state.purchases.values()).sort_values("purchased_at", ascending=False)
        for idx, r in lib.iterrows():
            game_id = r["game_id"]
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
                  <div class="poster-meta">{r["start"]} • {r["platform"]} • {r["tier"]} • Paid ${float(r["price_paid"]):,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Unique keys for library actions
            if st.button("Watch ▶", key=f"lib_watch__{game_id}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. Production would deep-link into broadcaster stream.")
            st.write("")

# ----------------------------
# PROFILE
# ----------------------------
with tab_profile:
    st.markdown("<div class='rowtitle'>Profile</div>", unsafe_allow_html=True)
    st.write(f"**User:** {st.session_state.user_id}")

    name = st.text_input("Display name", st.session_state.display_name, key="profile_name")
    if st.button("Save", key="profile_save", use_container_width=True):
        st.session_state.display_name = name.strip() or "Guest"
        toast("Saved ✅")
        st.rerun()

    st.markdown("<div class='rowtitle'>Wallet (demo)</div>", unsafe_allow_html=True)
    add = st.number_input("Add funds", min_value=0.0, max_value=200.0, value=5.0, step=1.0, key="wallet_add_amt")
    if st.button("Add funds", key="wallet_add_btn", use_container_width=True):
        st.session_state.wallet = round(st.session_state.wallet + float(add), 2)
        toast("Wallet updated ✅")
        st.rerun()

    st.markdown("<div class='rowtitle'>Reset</div>", unsafe_allow_html=True)
    if st.button("Reset demo data", key="reset_demo", use_container_width=True):
        st.session_state.purchases = {}
        st.session_state.wallet = 12.00
        st.session_state.active_game = None
        toast("Reset complete ✅")
        st.rerun()

# ----------------------------
# Selected game: details + checkout + social
# ----------------------------
if st.session_state.active_game:
    game_row = df[df["game_id"] == st.session_state.active_game].iloc[0]
    game_id = game_row["game_id"]

    st.markdown("<div class='rowtitle'>Selected</div>", unsafe_allow_html=True)
    st.info(f"{game_row['away']} @ {game_row['home']} • {game_row['league']} • {game_row['start_str']}")
    st.write(game_row["about"])

    # Simple "dynamic deal": within 24h -> deal
    within_24 = (game_row["start"] - datetime.now()) <= timedelta(hours=24)
    deal_on = bool(within_24)
    deal_pct = 20 if deal_on else 0

    if is_purchased(game_id):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Watch ▶", key=f"selected_watch__{game_id}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. Production would deep-link into broadcaster stream.")
        with c2:
            if st.button("Close", key=f"selected_close__{game_id}", use_container_width=True):
                st.session_state.active_game = None
                st.rerun()
        # Social still available
        social_sheet(game_row, section_key="selected_purchased")

    else:
        # Ticketing checkout + social layer
        checkout_sheet(game_row, section_key="selected", deal_on=deal_on, deal_pct=deal_pct)
        social_sheet(game_row, section_key="selected")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Close", key=f"checkout_close__{game_id}", use_container_width=True):
                st.session_state.active_game = None
                st.rerun()
        with c2:
            # Add quick add-to-wallet nudge for demo
            if st.button("Add $5 to wallet", key=f"checkout_add5__{game_id}", use_container_width=True):
                st.session_state.wallet = round(st.session_state.wallet + 5.0, 2)
                toast("Wallet +$5 ✅")
                st.rerun()

# Close phone frame
st.markdown("</div></div>", unsafe_allow_html=True)

st.caption("Demo only • No real payments/rights/streams • Built for prototype presentation.")

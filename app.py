# app.py
# GameKey — Consumer App Prototype (Streamlit)
# Demo only: no real payments, no real rights, no real streaming.

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import uuid

# ----------------------------
# Page config + styling
# ----------------------------
st.set_page_config(page_title="GameKey", page_icon="🔑", layout="wide")

st.markdown(
    """
    <style>
      /* Layout tweaks */
      .block-container {padding-top: 1.2rem; padding-bottom: 2.5rem;}
      .gk-hero {
        border-radius: 22px; padding: 22px 22px;
        border: 1px solid rgba(255,255,255,0.08);
        background: radial-gradient(1200px 400px at 10% 10%, rgba(255,122,0,0.18), transparent 45%),
                    radial-gradient(800px 300px at 90% 30%, rgba(0,153,255,0.16), transparent 50%),
                    rgba(255,255,255,0.03);
      }
      .gk-title {font-size: 44px; font-weight: 900; margin: 0; line-height: 1.05;}
      .gk-sub {font-size: 16px; opacity: 0.80; margin-top: 10px;}
      .gk-pill {display:inline-block; padding: 5px 10px; border-radius: 999px;
                background: rgba(255,255,255,0.08); margin-right: 6px; font-size: 12px;}
      .gk-card {
        border-radius: 18px; padding: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
      }
      .gk-card:hover {border-color: rgba(255,255,255,0.16);}
      .gk-muted {opacity: 0.75;}
      .gk-big {font-size: 24px; font-weight: 850;}
      .gk-price {font-size: 18px; font-weight: 800;}
      .gk-divider {height: 1px; background: rgba(255,255,255,0.08); margin: 14px 0;}
      .stButton>button {border-radius: 14px; padding: 0.6rem 0.9rem;}
      .stTextInput input, .stNumberInput input {border-radius: 14px;}
      .stSelectbox div[data-baseweb="select"] > div {border-radius: 14px;}
      .stTabs [data-baseweb="tab"] {font-size: 14px; padding: 10px 14px;}
      /* Hide Streamlit chrome */
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Session state
# ----------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if "display_name" not in st.session_state:
    st.session_state.display_name = "Guest"
if "wallet" not in st.session_state:
    st.session_state.wallet = 12.00  # demo wallet
if "purchases" not in st.session_state:
    st.session_state.purchases = {}  # game_id -> meta
if "toast" not in st.session_state:
    st.session_state.toast = None

def toast(msg: str):
    st.session_state.toast = msg

# ----------------------------
# Demo catalog
# ----------------------------
def demo_catalog():
    now = datetime.now()
    games = [
        {"game_id":"GK-2001","sport":"Soccer","league":"UCL","home":"Manchester City","away":"Galatasaray",
         "start": now + timedelta(hours=7), "platform":"Paramount+","market":"US","base_price":2.99,
         "tags":["Decision Day","High stakes","Prime time"], "about":"A must-win night. One game. One key."},
        {"game_id":"GK-2002","sport":"Basketball","league":"NBA","home":"Knicks","away":"Celtics",
         "start": now + timedelta(days=1, hours=2), "platform":"ESPN","market":"US","base_price":1.99,
         "tags":["MSG energy","Playoff race","Big matchup"], "about":"Classic rivalry energy in the Garden."},
        {"game_id":"GK-2003","sport":"American Football","league":"NFL","home":"Eagles","away":"Cowboys",
         "start": now + timedelta(days=2, hours=4), "platform":"FOX Sports","market":"US","base_price":3.99,
         "tags":["Rivalry","Sunday","Must watch"], "about":"Two brands. One statement game."},
        {"game_id":"GK-2004","sport":"Soccer","league":"MLS","home":"NYCFC","away":"Inter Miami",
         "start": now + timedelta(days=3, hours=1), "platform":"Apple TV","market":"US","base_price":2.49,
         "tags":["Stars","Weekend","Big draw"], "about":"When the stars come to town, you tap in."},
        {"game_id":"GK-2005","sport":"Soccer","league":"NWSL","home":"Gotham FC","away":"Angel City",
         "start": now + timedelta(days=4, hours=3), "platform":"Prime Video","market":"US","base_price":1.49,
         "tags":["Women’s sports","Community","Rising"], "about":"Elite talent. Big moment. Easy access."},
        {"game_id":"GK-2006","sport":"Baseball","league":"MLB","home":"Yankees","away":"Red Sox",
         "start": now + timedelta(days=5, hours=2), "platform":"MLB.TV","market":"US","base_price":3.49,
         "tags":["Classic rivalry","Prime series","History"], "about":"A rivalry you don’t need a subscription for."},
    ]
    df = pd.DataFrame(games)
    df["start_str"] = df["start"].dt.strftime("%a, %b %d • %I:%M %p")
    df["day"] = df["start"].dt.strftime("%Y-%m-%d")
    return df.sort_values("start")

df = demo_catalog()

# ----------------------------
# Top bar (simple)
# ----------------------------
left, mid, right = st.columns([1.2, 2.4, 1.1])
with left:
    st.markdown("### 🔑 GameKey")
with mid:
    st.caption("Watch one game. Pay once. No subscriptions.")
with right:
    st.markdown(f"<div style='text-align:right;'><span class='gk-muted'>Wallet</span><br><span class='gk-big'>${st.session_state.wallet:,.2f}</span></div>", unsafe_allow_html=True)

if st.session_state.toast:
    st.success(st.session_state.toast)
    st.session_state.toast = None

# ----------------------------
# Tabs = consumer navigation
# ----------------------------
tab_home, tab_explore, tab_library, tab_profile = st.tabs(["Home", "Explore", "My Library", "Profile"])

# ----------------------------
# Helpers
# ----------------------------
def price_for(row, promo_on: bool, promo_pct: int):
    p = float(row["base_price"])
    if promo_on:
        p = round(p * (1 - promo_pct/100), 2)
    return p

def is_purchased(game_id: str) -> bool:
    return game_id in st.session_state.purchases

def purchase(game_id: str, title: str, price_paid: float, platform: str, start_str: str):
    st.session_state.purchases[game_id] = {
        "game_id": game_id,
        "title": title,
        "price_paid": price_paid,
        "platform": platform,
        "start": start_str,
        "purchased_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def game_card(row, promo_on=False, promo_pct=0, featured=False):
    game_id = row["game_id"]
    title = f"{row['away']} @ {row['home']}"
    p = price_for(row, promo_on, promo_pct)
    purchased = is_purchased(game_id)

    st.markdown("<div class='gk-card'>", unsafe_allow_html=True)
    if featured:
        st.markdown("<span class='gk-pill'>🔥 Featured</span>", unsafe_allow_html=True)

    st.markdown(f"**{title}**")
    st.markdown(f"<span class='gk-muted'>{row['league']} • {row['sport']} • {row['start_str']}</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='gk-muted'>Watch on</span> **{row['platform']}**", unsafe_allow_html=True)

    tag_line = " ".join([f"<span class='gk-pill'>{t}</span>" for t in row["tags"]])
    st.markdown(tag_line, unsafe_allow_html=True)

    st.markdown(f"<div class='gk-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='gk-price'>${p:,.2f} <span class='gk-muted' style='font-size:12px;'>{'(promo)' if promo_on else ''}</span></div>", unsafe_allow_html=True)

    # Actions
    a, b = st.columns([1, 1])
    with a:
        with st.popover("Details", use_container_width=True):
            st.write(row["about"])
            st.write("**Includes (demo):** live access + 24h rewatch + highlights.")
            st.caption("Note: regional restrictions/rights would apply in a real product.")
    with b:
        if purchased:
            if st.button("Watch now ▶", key=f"watch_{game_id}", use_container_width=True):
                toast("Launching player (demo)…")
                st.info("Demo player placeholder. In production, this deep-links into the broadcaster stream with auth.")
        else:
            if st.button(f"Unlock 🔓", key=f"unlock_{game_id}", use_container_width=True):
                # Checkout flow in a popover-like experience
                with st.popover("Checkout", use_container_width=True):
                    st.markdown(f"### Unlock this game")
                    st.write(f"**{title}**")
                    st.write(f"**Start:** {row['start_str']}")
                    st.write(f"**Platform:** {row['platform']}")
                    st.write(f"**Price:** ${p:,.2f}")
                    st.write("---")
                    if st.session_state.wallet < p:
                        st.error("Not enough wallet balance (demo). Add funds in Profile.")
                    else:
                        if st.button(f"Confirm purchase • ${p:,.2f}", key=f"confirm_{game_id}", use_container_width=True):
                            st.session_state.wallet = round(st.session_state.wallet - p, 2)
                            purchase(game_id, title, p, row["platform"], row["start_str"])
                            toast("Purchased ✅ Game unlocked in My Library.")
                            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# HOME
# ----------------------------
with tab_home:
    st.markdown(
        """
        <div class="gk-hero">
          <div class="gk-title">One game.<br>One key.</div>
          <div class="gk-sub">Skip the subscription. Unlock the match you actually want to watch.</div>
          <div style="margin-top:12px;">
            <span class="gk-pill">Instant access</span>
            <span class="gk-pill">Low-cost</span>
            <span class="gk-pill">Across platforms (demo)</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.subheader("Tonight's Top Picks")

    # Pick next 2 games as "Tonight"
    upcoming = df[df["start"] > datetime.now()].head(2)
    c1, c2 = st.columns(2)
    for col, (_, row) in zip([c1, c2], upcoming.iterrows()):
        with col:
            game_card(row, promo_on=True, promo_pct=20, featured=True)

    st.write("")
    st.subheader("Because you're a casual fan (demo personalization)")
    st.caption("In a real app, this would learn from your viewing and offer smarter recommendations.")
    rec = df.sample(min(3, len(df)), random_state=7)
    cols = st.columns(3)
    for i, (_, row) in enumerate(rec.iterrows()):
        with cols[i % 3]:
            game_card(row, promo_on=False)

# ----------------------------
# EXPLORE
# ----------------------------
with tab_explore:
    st.subheader("Explore Games")

    # Filters in a nice row
    f1, f2, f3, f4 = st.columns([1.2, 1.0, 1.0, 1.2])
    with f1:
        q = st.text_input("Search teams / leagues / platforms", "")
    with f2:
        sport = st.selectbox("Sport", ["All"] + sorted(df["sport"].unique().tolist()))
    with f3:
        league = st.selectbox("League", ["All"] + sorted(df["league"].unique().tolist()))
    with f4:
        max_price = st.slider("Max price", 0.99, 9.99, 4.99, 0.50)

    st.write("")

    # Optional promo toggle (consumer-friendly "Deal" vibe)
    d1, d2 = st.columns([1, 3])
    with d1:
        promo_on = st.toggle("Show deals", value=False)
    with d2:
        promo_pct = st.slider("Deal %", 10, 60, 20, 5) if promo_on else 0

    # Apply filters
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
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                game_card(row, promo_on=promo_on, promo_pct=promo_pct)

# ----------------------------
# MY LIBRARY
# ----------------------------
with tab_library:
    st.subheader("My Library")
    st.caption("Everything you've unlocked lives here.")

    if not st.session_state.purchases:
        st.info("No games unlocked yet. Head to Home or Explore and unlock one.")
    else:
        lib = pd.DataFrame(st.session_state.purchases.values()).sort_values("purchased_at", ascending=False)

        # Library as cards
        for _, r in lib.iterrows():
            st.markdown("<div class='gk-card'>", unsafe_allow_html=True)
            st.markdown(f"**{r['title']}**")
            st.markdown(f"<span class='gk-muted'>{r['start']} • Watch on {r['platform']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='gk-muted'>Paid</span> **${float(r['price_paid']):,.2f}**", unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Watch now ▶", key=f"lib_watch_{r['game_id']}", use_container_width=True):
                    toast("Launching player (demo)…")
                    st.info("Demo player placeholder. Production would deep-link into broadcaster stream.")
            with c2:
                with st.popover("Receipt", use_container_width=True):
                    st.write(f"Purchase time: {r['purchased_at']}")
                    st.write(f"Order ID: {r['game_id']}-{st.session_state.user_id}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

# ----------------------------
# PROFILE
# ----------------------------
with tab_profile:
    st.subheader("Profile & Settings")

    p1, p2 = st.columns([1.2, 1.8])
    with p1:
        st.markdown("<div class='gk-card'>", unsafe_allow_html=True)
        st.markdown("### Your profile")
        name = st.text_input("Display name", st.session_state.display_name)
        if st.button("Save profile", use_container_width=True):
            st.session_state.display_name = name.strip() or "Guest"
            toast("Saved ✅")
            st.rerun()

        st.markdown("<div class='gk-divider'></div>", unsafe_allow_html=True)
        st.markdown("### Wallet (demo)")
        add = st.number_input("Add funds", min_value=0.0, max_value=200.0, value=5.0, step=1.0)
        if st.button("Add funds", use_container_width=True):
            st.session_state.wallet = round(st.session_state.wallet + float(add), 2)
            toast("Wallet updated ✅")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with p2:
        st.markdown("<div class='gk-card'>", unsafe_allow_html=True)
        st.markdown("### About GameKey (demo)")
        st.write(
            "GameKey is built for casual, moment-driven fans. "
            "Unlock the one match you care about—without committing to a monthly subscription."
        )
        st.markdown("<div class='gk-divider'></div>", unsafe_allow_html=True)
        st.markdown("### Legal & rights note")
        st.caption(
            "This is a prototype UI only. Real-world availability depends on licensing, territory, and broadcaster rules."
        )

        st.markdown("<div class='gk-divider'></div>", unsafe_allow_html=True)
        if st.button("Reset demo data", use_container_width=True):
            st.session_state.purchases = {}
            st.session_state.wallet = 12.00
            toast("Reset complete ✅")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

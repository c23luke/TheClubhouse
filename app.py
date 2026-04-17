import streamlit as st
import pandas as pd
import requests
import json
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Fairway Sweats", layout="wide", page_icon="⛳")
st_autorefresh(interval=300000, key="refresh")

# ============================================================
# CONFIG
# ============================================================
TOURNAMENT_ID = "401811942"
ENTRY_FEE     = 5
DAILY_PCT     = 0.15
OVERALL_PCT   = 0.40

SHEET_URL = "https://docs.google.com/spreadsheets/d/1hH--Z2Ur1yN8p1R5uftC_nDF6TQz5T7Z5WJWKO6K07c/export?format=csv"

# ── Change this to your own password ──
ADMIN_PASSWORD = "fairway2025"

# ── Saved next to this script so settings survive restarts ──
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_state.json")

# ============================================================
# ADMIN STATE  (load / save)
# ============================================================
DEFAULT_STATE = {
    "daily_winners":       {"Thursday":"","Friday":"","Saturday":"","Sunday":""},
    "score_overrides":     {},
    "entries_frozen":      False,
    "tournament_finished": False,
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            for k, v in DEFAULT_STATE.items():
                data.setdefault(k, v)
            return data
        except:
            pass
    return dict(DEFAULT_STATE)

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2)

if "admin_state" not in st.session_state:
    st.session_state.admin_state = load_state()

admin = st.session_state.admin_state

# ============================================================
# STYLES
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0a0f0a !important;
    color: #e8ede8 !important;
}
.stApp { background: linear-gradient(160deg,#0a0f0a 0%,#0f1a0f 60%,#0a1208 100%) !important; }
.block-container { padding: 1.5rem 1.5rem !important; max-width: 1100px; }

.main-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 900; color:#fff; letter-spacing:-1px; line-height:1;
}
.main-subtitle { font-size:0.75rem; color:#4a6b4a; letter-spacing:3px; text-transform:uppercase; margin-top:4px; }

.stat-box {
    background: linear-gradient(135deg,#141f14,#1a2a1a);
    border:1px solid #2a3d2a; border-radius:12px; padding:14px 16px; text-align:center;
}
.stat-value { font-family:'Playfair Display',serif; font-size:clamp(1.4rem,4vw,2rem); font-weight:700; color:#fff; line-height:1; }
.stat-label { font-size:0.65rem; color:#4a6b4a; text-transform:uppercase; letter-spacing:2px; margin-top:4px; }

.section-title {
    font-family:'Playfair Display',serif; font-size:clamp(1rem,3vw,1.3rem);
    color:#fff; letter-spacing:1px; margin-bottom:12px;
    border-left:3px solid #fff; padding-left:12px;
}

.entry-card {
    background:linear-gradient(135deg,#111a11,#141f14);
    border:1px solid #1e2e1e; border-radius:12px;
    padding:12px 16px; margin-bottom:8px;
    display:flex; align-items:center; gap:12px;
}
.entry-card.leader { border-color:#ffffff44; background:linear-gradient(135deg,#141f14,#1a281a); }
.rank-badge { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:900; color:#4a6b4a; width:32px; text-align:center; flex-shrink:0; }
.rank-badge.top3 { color:#fff; }
.entry-name { font-size:0.95rem; font-weight:600; color:#e8ede8; line-height:1.1; }
.entry-venmo { font-size:0.72rem; color:#4a6b4a; margin-top:1px; }
.picks-area { flex:1; display:flex; gap:6px; flex-wrap:wrap; }
.pick-chip {
    background:#0d160d; border:1px solid #2a3d2a; border-radius:6px;
    padding:3px 8px; font-size:0.74rem; color:#8aad8a; white-space:nowrap;
}
.pick-chip.best { border-color:#ffffff33; background:#1a2a1a; }
.pick-score-under { color:#4ade80; font-weight:600; }
.pick-score-over  { color:#f87171; font-weight:600; }
.pick-score-even  { color:#8aad8a; font-weight:600; }
.total-score { font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:700; width:48px; text-align:right; flex-shrink:0; }
.total-under { color:#4ade80; }
.total-over  { color:#f87171; }
.total-even  { color:#8aad8a; }
.payout-badge {
    background:#ffffff15; border:1px solid #ffffff44; color:#fff;
    font-size:0.68rem; font-weight:700; padding:2px 7px; border-radius:20px; letter-spacing:.5px;
}
.override-badge {
    background:#2a1a00; border:1px solid #6b4a0044; color:#fbbf24;
    font-size:0.62rem; padding:1px 5px; border-radius:10px; margin-left:3px;
}

/* Mobile responsive */
@media (max-width: 640px) {
    .block-container { padding: 1rem 0.75rem !important; }
    .entry-card { flex-wrap: wrap; gap: 8px; padding: 10px 12px; }
    .picks-area { width: 100%; order: 3; }
    .total-score { order: 2; }
    .rank-badge { font-size: 1rem; width: 26px; }
    .entry-name { font-size: 0.85rem; }
    .pick-chip { font-size: 0.68rem; padding: 2px 6px; }
    .winners-grid { grid-template-columns: repeat(3,1fr) !important; }
    .tourney-row { padding: 8px 12px; font-size: 0.8rem; }
}

.winners-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-bottom:4px; }
.winner-card { background:linear-gradient(135deg,#111a11,#141f14); border:1px solid #1e2e1e; border-radius:10px; padding:12px 14px; text-align:center; }
.winner-card.has-winner { border-color:#2a4a2a; }
.winner-day { font-size:0.6rem; color:#4a6b4a; text-transform:uppercase; letter-spacing:2px; margin-bottom:5px; }
.winner-name { font-family:'Playfair Display',serif; font-size:0.95rem; font-weight:700; color:#fff; line-height:1.2; }
.winner-score { font-size:0.78rem; color:#4ade80; font-weight:600; margin-top:2px; }
.winner-payout { font-size:0.82rem; color:#e8ede8; font-weight:600; margin-top:5px; }
.winner-tbd { font-family:'Playfair Display',serif; font-size:1rem; color:#2a4a2a; }

.tourney-container { background:#111a11; border:1px solid #1e2e1e; border-radius:12px; overflow:hidden; }
.tourney-row { display:flex; align-items:center; gap:14px; padding:10px 18px; border-bottom:1px solid #1a2a1a; font-size:0.88rem; }
.tourney-row:last-child { border-bottom:none; }
.tourney-pos { color:#4a6b4a; font-weight:600; width:22px; flex-shrink:0; font-size:0.78rem; }
.tourney-name { flex:1; color:#c0d4c0; }
.tourney-score-under { color:#4ade80; font-weight:700; }
.tourney-score-over  { color:#f87171; font-weight:700; }
.tourney-score-even  { color:#8aad8a; }

.divider { border:none; border-top:1px solid #1e2e1e; margin:20px 0; }
#MainMenu, header, footer { visibility:hidden; }
.stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def clean(x):
    if pd.isna(x): return ""
    return str(x).split(" +")[0].strip()

def fmt_score(val):
    if val == 0:  return "E"
    if val < 0:   return str(val)
    return f"+{val}"

# ============================================================
# LOAD SHEET
# ============================================================
try:
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    df = df.astype(str).apply(lambda col: col.str.strip())
    df = df.replace("nan","").replace("None","")
    df = df.dropna(how="all")
    df = df[(df["Pick 1"].str.len()>0)|(df["Pick 2"].str.len()>0)|(df["Pick 3"].str.len()>0)]
except:
    df = pd.DataFrame(columns=["Name","Venmo","Pick 1","Pick 2","Pick 3"])

# ============================================================
# ESPN DATA
# ============================================================
def get_scores():
    try:
        url  = f"https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard?tournamentId={TOURNAMENT_ID}"
        data = requests.get(url, timeout=10).json()
        players = data["events"][0]["competitions"][0]["competitors"]
        score_map, leaderboard = {}, []
        for p in players:
            name = p["athlete"]["displayName"]
            raw  = p.get("score","E")
            leaderboard.append((name, raw))
            try:   val = 0 if str(raw) in ("E","") else int(raw)
            except: val = 0
            score_map[name] = val
        return score_map, leaderboard, data
    except:
        return {}, [], {}

score_map, espn_lb, raw_data = get_scores()

# Apply admin score overrides on top of ESPN data
for player, override_val in admin["score_overrides"].items():
    score_map[player] = override_val

def espn_finished(data):
    try:   return data["events"][0]["status"]["type"]["state"] == "post"
    except: return False

is_finished = admin["tournament_finished"] or espn_finished(raw_data)

# ============================================================
# BUILD POOL ROWS
# ============================================================
rows = []
for _, row in df.iterrows():
    picks  = [clean(row["Pick 1"]), clean(row["Pick 2"]), clean(row["Pick 3"])]
    scores = [score_map.get(p, 0) for p in picks]
    total  = sum(scores)
    best   = scores.index(min(scores))
    rows.append({"Name":row["Name"],"Venmo":row["Venmo"],
                 "Picks":list(zip(picks,scores)),"Total":total,"BestIndex":best})

df_display = pd.DataFrame(rows).sort_values("Total").reset_index(drop=True) if rows else pd.DataFrame()

pot            = len(df) * ENTRY_FEE
daily_payout   = round(pot * DAILY_PCT,   2)
overall_payout = round(pot * OVERALL_PCT, 2)

# ============================================================
# HEADER
# ============================================================
col_title, col_stats = st.columns([2, 1])

with col_title:
    st.markdown('<div class="main-title">⛳ Fairway Sweats</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">PGA Tournament Pool</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if not admin["entries_frozen"]:
        st.markdown("""
        <a href="https://forms.gle/D6yHxPGNE1pt61Cv6" target="_blank" style="
            background:#2a4a2a; color:#e8ede8; padding:10px 22px; border-radius:8px;
            font-weight:600; font-size:0.85rem; text-decoration:none; letter-spacing:1px;
            text-transform:uppercase; border:1px solid #3a6a3a; display:inline-block;">
            + Enter Pool
        </a>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:inline-block; background:#1a0a0a; border:1px solid #5a2a2a;
            color:#f87171; padding:10px 22px; border-radius:8px; font-weight:600;
            font-size:0.85rem; letter-spacing:1px; text-transform:uppercase;">
            🔒 Entries Closed
        </div>""", unsafe_allow_html=True)

with col_stats:
    st.markdown(f"""
    <div style="display:flex; gap:10px; margin-top:8px;">
        <div class="stat-box" style="flex:1;">
            <div class="stat-value">${pot}</div>
            <div class="stat-label">Prize Pot</div>
        </div>
        <div class="stat-box" style="flex:1;">
            <div class="stat-value">{len(df)}</div>
            <div class="stat-label">Entries</div>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# POOL STANDINGS
# ============================================================
st.markdown('<div class="section-title">Pool Standings</div>', unsafe_allow_html=True)

if not df_display.empty:
    min_score = df_display["Total"].min()
    n_leaders = len(df_display[df_display["Total"] == min_score])
    lead_pay  = round(pot / n_leaders, 2) if n_leaders else pot
    rank_emoji = ["🥇","🥈","🥉"]

    for i, row in df_display.iterrows():
        is_leader = (i == 0)
        is_top3   = (i < 3)
        rank_str  = rank_emoji[i] if is_top3 else str(i+1)
        total     = row["Total"]
        total_cls = "total-under" if total<0 else "total-over" if total>0 else "total-even"

        picks_html = ""
        for idx, (pname, pscore) in enumerate(row["Picks"]):
            is_best  = (idx == row["BestIndex"])
            sc_cls   = "pick-score-under" if pscore<0 else "pick-score-over" if pscore>0 else "pick-score-even"
            star     = "⭐ " if is_best else ""
            chip_cls = "pick-chip best" if is_best else "pick-chip"
            ov_badge = '<span class="override-badge">✎</span>' if pname in admin["score_overrides"] else ""
            picks_html += f'<div class="{chip_cls}">{star}{pname}{ov_badge} <span class="{sc_cls}">{fmt_score(pscore)}</span></div>'

        payout_html = f'<span class="payout-badge">${lead_pay}</span>' if is_leader else ""
        card_cls    = "entry-card leader" if is_leader else "entry-card"
        rank_cls    = "rank-badge top3"   if is_top3   else "rank-badge"

        st.markdown(f"""
        <div class="{card_cls}">
            <div class="{rank_cls}">{rank_str}</div>
            <div style="min-width:130px;">
                <div class="entry-name">{row['Name']} {payout_html}</div>
                <div class="entry-venmo">@{row['Venmo']}</div>
            </div>
            <div class="picks-area">{picks_html}</div>
            <div class="total-score {total_cls}">{fmt_score(total)}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#4a6b4a;">
        <div style="font-size:2rem;">⛳</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#fff;margin-top:8px;">No entries yet</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# WINNERS
# ============================================================
st.markdown('<div class="section-title">Winners</div>', unsafe_allow_html=True)

cards_html = ""
for day in ["Thursday","Friday","Saturday","Sunday"]:
    winner_name = admin["daily_winners"].get(day, "")
    if winner_name:
        w_rows = df_display[df_display["Name"]==winner_name] if not df_display.empty else pd.DataFrame()
        score_line = f'<div class="winner-score">{fmt_score(w_rows.iloc[0]["Total"])}</div>' if not w_rows.empty else ""
        cards_html += f"""
        <div class="winner-card has-winner">
            <div class="winner-day">{day}</div>
            <div class="winner-name">{winner_name}</div>
            {score_line}
            <div class="winner-payout">${daily_payout}</div>
        </div>"""
    else:
        cards_html += f"""
        <div class="winner-card">
            <div class="winner-day">{day}</div>
            <div class="winner-tbd">—</div>
            <div style="font-size:0.68rem;color:#2a4a2a;margin-top:6px;">${daily_payout}</div>
        </div>"""

if is_finished and not df_display.empty:
    ov = df_display.iloc[0]
    cards_html += f"""
    <div class="winner-card has-winner" style="border-color:#ffffff33;">
        <div class="winner-day">Overall</div>
        <div class="winner-name">{ov['Name']}</div>
        <div class="winner-score">{fmt_score(ov['Total'])}</div>
        <div class="winner-payout">${overall_payout}</div>
    </div>"""
else:
    cards_html += f"""
    <div class="winner-card">
        <div class="winner-day">Overall</div>
        <div class="winner-tbd">—</div>
        <div style="font-size:0.68rem;color:#2a4a2a;margin-top:6px;">${overall_payout}</div>
    </div>"""

st.markdown(f'<div class="winners-grid">{cards_html}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# TOURNAMENT LEADERS
# ============================================================
st.markdown('<div class="section-title">Tournament Leaders</div>', unsafe_allow_html=True)

if espn_lb:
    lb_html = ""
    for i, (name, raw_score) in enumerate(espn_lb[:10], 1):
        s = str(raw_score)
        try:    val = 0 if s in ("E","") else int(s)
        except: val = 0
        if name in admin["score_overrides"]:
            val = admin["score_overrides"][name]
        sc_cls  = "tourney-score-under" if val<0 else "tourney-score-over" if val>0 else "tourney-score-even"
        ov_flag = " ✎" if name in admin["score_overrides"] else ""
        lb_html += f"""
        <div class="tourney-row">
            <span class="tourney-pos">{i}</span>
            <span class="tourney-name">{name}{ov_flag}</span>
            <span class="{sc_cls}">{fmt_score(val)}</span>
        </div>"""
    st.markdown(f'<div class="tourney-container">{lb_html}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="color:#4a6b4a;font-size:0.9rem;padding:12px 0;">Live scores temporarily unavailable.</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ============================================================
# ADMIN PANEL
# ============================================================
with st.expander("🔐 Admin", expanded=False):
    pwd = st.text_input("Password", type="password", key="admin_pwd")

    if pwd == ADMIN_PASSWORD:
        st.success("✓ Logged in")
        st.markdown("---")

        # ── Freeze entries ──
        st.markdown("**🔒 Entry Gate**")
        freeze_val = st.toggle("Freeze entries (replaces Enter Pool button with 'Entries Closed')",
                               value=admin["entries_frozen"], key="freeze_toggle")
        if freeze_val != admin["entries_frozen"]:
            admin["entries_frozen"] = freeze_val
            save_state(admin)
            st.rerun()

        st.markdown("---")

        # ── Tournament finished ──
        st.markdown("**🏁 Tournament Status**")
        fin_val = st.toggle("Mark tournament finished (reveals Overall winner card)",
                            value=admin["tournament_finished"], key="fin_toggle")
        if fin_val != admin["tournament_finished"]:
            admin["tournament_finished"] = fin_val
            save_state(admin)
            st.rerun()

        st.markdown("---")

        # ── Daily winners ──
        st.markdown("**🏆 Set Daily Winners**")
        entry_names = [""] + sorted(df["Name"].tolist()) if not df.empty else [""]
        cols = st.columns(4)
        changed = False
        for col, day in zip(cols, ["Thursday","Friday","Saturday","Sunday"]):
            with col:
                current = admin["daily_winners"].get(day, "")
                idx     = entry_names.index(current) if current in entry_names else 0
                chosen  = st.selectbox(day, entry_names, index=idx, key=f"winner_{day}")
                if chosen != current:
                    admin["daily_winners"][day] = chosen
                    changed = True
        if changed:
            save_state(admin)
            st.rerun()

        st.markdown("---")

        # ── Score overrides ──
        st.markdown("**✎ Score Overrides**")
        st.caption("Override a player's score if ESPN data is wrong or they withdrew.")
        all_players = sorted(score_map.keys()) if score_map else []
        ov_player = st.selectbox("Player", [""] + all_players, key="ov_player")
        ov_score  = st.number_input("Score vs par", min_value=-30, max_value=30, value=0, step=1, key="ov_score")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Set Override", key="btn_set") and ov_player:
                admin["score_overrides"][ov_player] = int(ov_score)
                save_state(admin); st.rerun()
        with c2:
            if st.button("🗑 Remove Override", key="btn_clr") and ov_player:
                admin["score_overrides"].pop(ov_player, None)
                save_state(admin); st.rerun()

        if admin["score_overrides"]:
            st.markdown("**Active overrides:**")
            for p, v in list(admin["score_overrides"].items()):
                rc1, rc2 = st.columns([5,1])
                rc1.markdown(f"`{p}` → **{fmt_score(v)}**")
                if rc2.button("✕", key=f"rm_{p}"):
                    admin["score_overrides"].pop(p, None)
                    save_state(admin); st.rerun()

        st.markdown("---")

        if st.button("⚠️ Reset ALL admin settings"):
            st.session_state.admin_state = dict(DEFAULT_STATE)
            save_state(st.session_state.admin_state)
            st.rerun()

    elif pwd != "":
        st.error("Incorrect password.")

st.markdown("<br><br>", unsafe_allow_html=True)

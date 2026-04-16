import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Fairway Sweats", layout="wide", page_icon="⛳")
st_autorefresh(interval=300000, key="refresh")

# ------------------------
# CONFIG
# ------------------------
TOURNAMENT_ID = "401811942"
ENTRY_FEE = 5

SHEET_URL = "https://docs.google.com/spreadsheets/d/1hH--Z2Ur1yN8p1R5uftC_nDF6TQz5T7Z5WJWKO6K07c/export?format=csv"

# Payout percentages
DAILY_PCT   = 0.15   # Thu/Fri/Sat/Sun each = 15% of pot
OVERALL_PCT = 0.40   # Overall winner = 40% of pot

# ------------------------
# STYLES
# ------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0a0f0a !important;
    color: #e8ede8 !important;
}
.stApp {
    background: linear-gradient(160deg, #0a0f0a 0%, #0f1a0f 60%, #0a1208 100%) !important;
}
.block-container { padding: 2rem 3rem !important; max-width: 1100px; }

/* HEADER */
.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1px;
    line-height: 1;
}
.main-subtitle {
    font-size: 0.8rem;
    color: #4a6b4a;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}
.stat-box {
    background: linear-gradient(135deg, #141f14, #1a2a1a);
    border: 1px solid #2a3d2a;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
}
.stat-label {
    font-size: 0.7rem;
    color: #4a6b4a;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}
.divider { border: none; border-top: 1px solid #1e2e1e; margin: 20px 0; }

/* SECTION TITLE */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #ffffff;
    letter-spacing: 1px;
    margin-bottom: 12px;
    border-left: 3px solid #ffffff;
    padding-left: 12px;
}

/* ENTRY CARDS */
.entry-card {
    background: linear-gradient(135deg, #111a11, #141f14);
    border: 1px solid #1e2e1e;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.entry-card.leader {
    border-color: #ffffff44;
    background: linear-gradient(135deg, #141f14, #1a281a);
}
.rank-badge {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 900;
    color: #4a6b4a;
    width: 36px;
    text-align: center;
    flex-shrink: 0;
}
.rank-badge.top3 { color: #ffffff; }
.entry-name { font-size: 1rem; font-weight: 600; color: #e8ede8; line-height: 1.1; }
.entry-venmo { font-size: 0.75rem; color: #4a6b4a; margin-top: 1px; }
.picks-area { flex: 1; display: flex; gap: 8px; flex-wrap: wrap; }
.pick-chip {
    background: #0d160d;
    border: 1px solid #2a3d2a;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.78rem;
    color: #8aad8a;
    white-space: nowrap;
}
.pick-chip.best { border-color: #ffffff33; background: #1a2a1a; }
.pick-score-under { color: #4ade80; font-weight: 600; }
.pick-score-over  { color: #f87171; font-weight: 600; }
.pick-score-even  { color: #8aad8a; font-weight: 600; }
.total-score {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    width: 52px;
    text-align: right;
    flex-shrink: 0;
}
.total-under { color: #4ade80; }
.total-over  { color: #f87171; }
.total-even  { color: #8aad8a; }
.payout-badge {
    background: #ffffff15;
    border: 1px solid #ffffff44;
    color: #ffffff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}

/* DAILY WINNERS */
.winners-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 4px;
}
.winner-card {
    background: linear-gradient(135deg, #111a11, #141f14);
    border: 1px solid #1e2e1e;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.winner-card.has-winner { border-color: #2a4a2a; }
.winner-day {
    font-size: 0.65rem;
    color: #4a6b4a;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
}
.winner-name {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}
.winner-score {
    font-size: 0.8rem;
    color: #4ade80;
    font-weight: 600;
    margin-top: 2px;
}
.winner-payout {
    font-size: 0.85rem;
    color: #e8ede8;
    font-weight: 600;
    margin-top: 6px;
}
.winner-tbd {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #2a4a2a;
}

/* TOURNAMENT LEADERS */
.tourney-container {
    background: #111a11;
    border: 1px solid #1e2e1e;
    border-radius: 12px;
    overflow: hidden;
}
.tourney-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 18px;
    border-bottom: 1px solid #1a2a1a;
    font-size: 0.9rem;
}
.tourney-row:last-child { border-bottom: none; }
.tourney-pos { color: #4a6b4a; font-weight: 600; width: 22px; flex-shrink: 0; font-size: 0.8rem; }
.tourney-name { flex: 1; color: #c0d4c0; }
.tourney-score-under { color: #4ade80; font-weight: 700; }
.tourney-score-over  { color: #f87171; font-weight: 700; }
.tourney-score-even  { color: #8aad8a; }

/* Hide streamlit chrome */
#MainMenu, header, footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ------------------------
# HELPERS
# ------------------------
def clean(x):
    if pd.isna(x): return ""
    return str(x).split(" +")[0].strip()

def fmt_score(val, is_int=True):
    """Format an integer score as E / -N / +N"""
    if is_int:
        if val == 0: return "E"
        return str(val) if val < 0 else f"+{val}"
    # raw string from ESPN
    s = str(val)
    if s in ("E", "0"): return "E"
    return s

# ------------------------
# LOAD SHEET
# ------------------------
try:
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    df = df.astype(str).apply(lambda col: col.str.strip())
    df = df.replace("nan", "").replace("None", "")
    df = df.dropna(how="all")
    df = df[
        (df["Pick 1"].str.len() > 0) |
        (df["Pick 2"].str.len() > 0) |
        (df["Pick 3"].str.len() > 0)
    ]
except:
    df = pd.DataFrame(columns=["Name","Venmo","Pick 1","Pick 2","Pick 3"])

# ------------------------
# ESPN DATA
# ------------------------
def get_scores():
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard?tournamentId={TOURNAMENT_ID}"
        data = requests.get(url, timeout=10).json()
        players = data["events"][0]["competitions"][0]["competitors"]
        score_map = {}
        leaderboard = []
        for p in players:
            name = p["athlete"]["displayName"]
            raw  = p.get("score", "E")
            leaderboard.append((name, raw))
            try:
                val = 0 if str(raw) in ("E", "") else int(raw)
            except:
                val = 0
            score_map[name] = val
        return score_map, leaderboard, data
    except:
        return {}, [], {}

score_map, espn_lb, raw_data = get_scores()

def tournament_finished(data):
    try:
        state = data["events"][0]["status"]["type"]["state"]
        return state == "post"
    except:
        return False

is_finished = tournament_finished(raw_data)

# ------------------------
# HEADER
# ------------------------
col_title, col_stats = st.columns([2, 1])

with col_title:
    st.markdown('<div class="main-title">⛳ Fairway Sweats</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">PGA Tournament Pool</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <a href="https://forms.gle/D6yHxPGNE1pt61Cv6" target="_blank" style="
        background: #2a4a2a;
        color: #e8ede8;
        padding: 10px 22px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        text-decoration: none;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid #3a6a3a;
        display: inline-block;
    ">+ Enter Pool</a>
    """, unsafe_allow_html=True)

with col_stats:
    pot = len(df) * ENTRY_FEE
    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-top:8px;">
        <div class="stat-box" style="flex:1;">
            <div class="stat-value">${pot}</div>
            <div class="stat-label">Prize Pot</div>
        </div>
        <div class="stat-box" style="flex:1;">
            <div class="stat-value">{len(df)}</div>
            <div class="stat-label">Entries</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ------------------------
# BUILD POOL ROWS
# ------------------------
rows = []
for _, row in df.iterrows():
    picks  = [clean(row["Pick 1"]), clean(row["Pick 2"]), clean(row["Pick 3"])]
    scores = [score_map.get(p, 0) for p in picks]
    total  = sum(scores)
    best   = scores.index(min(scores))
    rows.append({
        "Name": row["Name"],
        "Venmo": row["Venmo"],
        "Picks": list(zip(picks, scores)),
        "Total": total,
        "BestIndex": best
    })

df_display = pd.DataFrame(rows).sort_values("Total").reset_index(drop=True) if rows else pd.DataFrame()

# ------------------------
# POOL STANDINGS
# ------------------------
st.markdown('<div class="section-title">Pool Standings</div>', unsafe_allow_html=True)

if not df_display.empty:
    min_score = df_display["Total"].min()
    n_leaders = len(df_display[df_display["Total"] == min_score])
    payout    = (len(df_display) * ENTRY_FEE) / n_leaders

    rank_emoji = ["🥇","🥈","🥉"]

    for i, row in df_display.iterrows():
        is_leader = (i == 0)
        is_top3   = (i < 3)
        rank_str  = rank_emoji[i] if is_top3 else str(i + 1)
        total     = row["Total"]

        if   total < 0: total_cls = "total-under"
        elif total > 0: total_cls = "total-over"
        else:           total_cls = "total-even"
        total_str = fmt_score(total)

        picks_html = ""
        for idx, (name, score) in enumerate(row["Picks"]):
            is_best = (idx == row["BestIndex"])
            sc_cls  = "pick-score-under" if score < 0 else "pick-score-over" if score > 0 else "pick-score-even"
            star    = "⭐ " if is_best else ""
            chip_cls = "pick-chip best" if is_best else "pick-chip"
            picks_html += f'<div class="{chip_cls}">{star}{name} <span class="{sc_cls}">{fmt_score(score)}</span></div>'

        payout_html  = f'<span class="payout-badge">${round(payout,2)}</span>' if is_leader else ""
        card_cls     = "entry-card leader" if is_leader else "entry-card"
        rank_cls     = "rank-badge top3"   if is_top3   else "rank-badge"

        st.markdown(f"""
        <div class="{card_cls}">
            <div class="{rank_cls}">{rank_str}</div>
            <div style="min-width:140px;">
                <div class="entry-name">{row['Name']} {payout_html}</div>
                <div class="entry-venmo">@{row['Venmo']}</div>
            </div>
            <div class="picks-area">{picks_html}</div>
            <div class="total-score {total_cls}">{total_str}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#4a6b4a;">
        <div style="font-size:2rem;">⛳</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#ffffff;margin-top:8px;">No entries yet</div>
        <div style="font-size:0.85rem;margin-top:4px;">Be the first to enter the pool</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ------------------------
# DAILY WINNERS
# Payouts: Thu/Fri/Sat/Sun = 15% each, Overall = 40%
# To set a winner, fill in the DAILY_WINNERS dict below.
# Key = day name, Value = exact name string matching the sheet.
# Leave as None if not yet determined.
# ------------------------
DAILY_WINNERS = {
    "Thursday":  None,
    "Friday":    None,
    "Saturday":  None,
    "Sunday":    None,
}

pot = len(df) * ENTRY_FEE
daily_payout   = round(pot * DAILY_PCT,   2)
overall_payout = round(pot * OVERALL_PCT, 2)

st.markdown('<div class="section-title">Winners</div>', unsafe_allow_html=True)

days_list = ["Thursday", "Friday", "Saturday", "Sunday"]

# Build winner cards HTML
cards_html = ""
for day in days_list:
    winner_name = DAILY_WINNERS.get(day)
    if winner_name and not df_display.empty:
        w_row = df_display[df_display["Name"] == winner_name]
        if not w_row.empty:
            w_score = w_row.iloc[0]["Total"]
            cards_html += f"""
            <div class="winner-card has-winner">
                <div class="winner-day">{day}</div>
                <div class="winner-name">{winner_name}</div>
                <div class="winner-score">{fmt_score(w_score)}</div>
                <div class="winner-payout">${daily_payout}</div>
            </div>"""
        else:
            cards_html += f"""
            <div class="winner-card has-winner">
                <div class="winner-day">{day}</div>
                <div class="winner-name">{winner_name}</div>
                <div class="winner-payout">${daily_payout}</div>
            </div>"""
    else:
        cards_html += f"""
        <div class="winner-card">
            <div class="winner-day">{day}</div>
            <div class="winner-tbd">—</div>
            <div style="font-size:0.7rem;color:#2a4a2a;margin-top:6px;">${daily_payout}</div>
        </div>"""

# Overall winner card
if is_finished and not df_display.empty:
    overall_row   = df_display.iloc[0]
    overall_name  = overall_row["Name"]
    overall_score = overall_row["Total"]
    cards_html += f"""
    <div class="winner-card has-winner" style="border-color:#ffffff33;">
        <div class="winner-day">Overall</div>
        <div class="winner-name">{overall_name}</div>
        <div class="winner-score">{fmt_score(overall_score)}</div>
        <div class="winner-payout">${overall_payout}</div>
    </div>"""
else:
    cards_html += f"""
    <div class="winner-card" style="border-color:#1e2e1e;">
        <div class="winner-day">Overall</div>
        <div class="winner-tbd">—</div>
        <div style="font-size:0.7rem;color:#2a4a2a;margin-top:6px;">${overall_payout}</div>
    </div>"""

st.markdown(f'<div class="winners-grid">{cards_html}</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ------------------------
# TOURNAMENT LEADERS
# ------------------------
st.markdown('<div class="section-title">Tournament Leaders</div>', unsafe_allow_html=True)

if espn_lb:
    lb_html = ""
    for i, (name, raw_score) in enumerate(espn_lb[:10], 1):
        s = str(raw_score)
        try:
            val = 0 if s in ("E", "") else int(s)
        except:
            val = 0

        if   val < 0: sc_cls = "tourney-score-under"; display = str(val)
        elif val > 0: sc_cls = "tourney-score-over";  display = f"+{val}"
        else:         sc_cls = "tourney-score-even";  display = "E"

        lb_html += f"""
        <div class="tourney-row">
            <span class="tourney-pos">{i}</span>
            <span class="tourney-name">{name}</span>
            <span class="{sc_cls}">{display}</span>
        </div>"""

    st.markdown(f'<div class="tourney-container">{lb_html}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="color:#4a6b4a;font-size:0.9rem;padding:12px 0;">Live scores temporarily unavailable.</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

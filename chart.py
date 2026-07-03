"""
San Antonio Spurs — 2025-26 Shot Chart
Two-panel dashboard: shot locations (left) + live zone-efficiency panel (right).

Reads spurs_data.csv with columns:
  PLAYER_NAME, LOC_X, LOC_Y, SHOT_DISTANCE, SHOT_TYPE, ACTION_TYPE, SHOT_MADE_FLAG
Outputs spurs_shot_chart.html (self-contained, deployable to GitHub Pages).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

chart = pd.read_csv("spurs_data.csv")

# ── Spurs palette (silver / black, gold accent) ────────────────
BG        = "#0b0b0c"   # paper
COURT_BG  = "#141416"   # court surface
LINE      = "#4a4a4f"   # court lines (muted so shots pop)
GOLD      = "#C4A35A"   # Spurs gold accent
MAKE      = "#7FCF9F"   # makes
MISS      = "#E06C6C"   # misses
TEXT      = "#ECECEC"
MUTE      = "#8a8a90"
PANEL     = "#161618"

FONT = "'Arial Narrow', 'Helvetica Neue', Arial, sans-serif"

players = [
    "De'Aaron Fox", "Stephon Castle", "Julian Champagnie",
    "Devin Vassell", "Victor Wembanyama", "Keldon Johnson", "Dylan Harper",
]

ZONE_ORDER = ["Restricted Area", "In The Paint", "Mid-Range", "Corner 3", "Above Break 3"]

# ── Zone + stat helpers ────────────────────────────────────────
def zone_of(x, y, dist, st):
    if st == "3PT Field Goal":
        return "Corner 3" if (y < 92.5 and abs(x) > 200) else "Above Break 3"
    if dist <= 4:
        return "Restricted Area"
    if abs(x) <= 80 and y <= 142.5:
        return "In The Paint"
    return "Mid-Range"

chart["ZONE"] = [zone_of(*r) for r in
                 chart[["LOC_X", "LOC_Y", "SHOT_DISTANCE", "SHOT_TYPE"]].itertuples(index=False)]

def player_stats(df):
    total = len(df); made = int(df["SHOT_MADE_FLAG"].sum())
    fg  = round(made/total*100, 1) if total else 0
    thr = df[df["SHOT_TYPE"] == "3PT Field Goal"]; two = df[df["SHOT_TYPE"] == "2PT Field Goal"]
    p3m = int(thr["SHOT_MADE_FLAG"].sum()); p2m = int(two["SHOT_MADE_FLAG"].sum())
    t3  = round(p3m/len(thr)*100, 1) if len(thr) else 0
    t2  = round(p2m/len(two)*100, 1) if len(two) else 0
    efg = round((made + 0.5*p3m)/total*100, 1) if total else 0
    return dict(total=total, made=made, fg=fg, t3a=len(thr), t3=t3,
                t2a=len(two), t2=t2, efg=efg)

def zone_stats(df):
    """Return FG% per zone, label text, and per-bar color (opacity = volume share)."""
    pct, txt, atts = [], [], []
    for z in ZONE_ORDER:
        zd = df[df["ZONE"] == z]; a = len(zd); m = int(zd["SHOT_MADE_FLAG"].sum())
        p = round(m/a*100, 1) if a else 0
        pct.append(p); atts.append(a)
        txt.append(f"  {p:.0f}%  ·  {m}/{a}" if a else "  —")
    mx = max(atts) or 1                       # opacity scales with shot volume
    colors = [f"rgba(196,163,90,{0.42 + 0.58*(a/mx):.2f})" for a in atts]
    return pct, txt, colors

# ── Court geometry (drawn on the left subplot) ─────────────────
def add_court(fig):
    def line(x0, y0, x1, y1, w=1.4, c=LINE):
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=c, width=w), row=1, col=1)
    def rect(x0, y0, x1, y1, w=1.4):
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=LINE, width=w), fillcolor="rgba(0,0,0,0)", row=1, col=1)
    def circle(x0, y0, x1, y1, c=LINE, w=1.4):
        fig.add_shape(type="circle", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=c, width=w), fillcolor="rgba(0,0,0,0)", row=1, col=1)

    rect(-250, -47.5, 250, 422.5)          # boundary
    rect(-80, -47.5, 80, 142.5)            # outer paint
    rect(-60, -47.5, 60, 142.5)            # inner paint
    circle(-60, 82.5, 60, 202.5)           # FT circle
    fig.add_shape(type="path", path="M -40 0 A 40 40 0 0 1 40 0",
                  line=dict(color=LINE, width=1.4), row=1, col=1)  # restricted
    circle(-7.5, -7.5, 7.5, 7.5, c=GOLD, w=1.8)   # hoop
    line(-30, -7.5, 30, -7.5, w=2.6, c=GOLD)      # backboard
    line(-220, -47.5, -220, 92.5)                 # corner 3s
    line(220, -47.5, 220, 92.5)
    th = np.linspace(np.radians(22), np.radians(158), 120)   # arc
    fig.add_trace(go.Scatter(x=237.5*np.cos(th), y=237.5*np.sin(th), mode="lines",
                             line=dict(color=LINE, width=1.4), hoverinfo="none",
                             showlegend=False), row=1, col=1)

# ── Build subplots: court | zone panel ─────────────────────────
fig = make_subplots(rows=1, cols=2, column_widths=[0.63, 0.37],
                    horizontal_spacing=0.06,
                    specs=[[{"type": "xy"}, {"type": "bar"}]])
add_court(fig)   # trace index 0 = arc

# Per-player shot scatter (col 1) + zone bar (col 2), all hidden but player 0
for p in players:
    pdf = chart[chart["PLAYER_NAME"] == p].copy()
    pdf["hover"] = (pdf["ACTION_TYPE"] + "<br>" + pdf["SHOT_TYPE"] + " · "
                    + pdf["SHOT_DISTANCE"].astype(str) + " ft<br>"
                    + pdf["SHOT_MADE_FLAG"].map({1: "● Made", 0: "○ Missed"}))
    fig.add_trace(go.Scatter(
        x=pdf["LOC_X"], y=pdf["LOC_Y"], mode="markers",
        marker=dict(color=pdf["SHOT_MADE_FLAG"].map({1: MAKE, 0: MISS}),
                    size=6.5, opacity=0.7, line=dict(width=0.4, color=BG)),
        customdata=pdf["hover"], hovertemplate="%{customdata}<extra></extra>",
        visible=False, showlegend=False), row=1, col=1)

for p in players:
    pct, txt, colors = zone_stats(chart[chart["PLAYER_NAME"] == p])
    fig.add_trace(go.Bar(
        x=pct, y=ZONE_ORDER, orientation="h", text=txt, textposition="outside",
        textfont=dict(color=TEXT, size=13, family=FONT), cliponaxis=False,
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
        visible=False, showlegend=False), row=1, col=2)

N = len(players)
fig.data[1].visible = True        # first player's court scatter
fig.data[1 + N].visible = True    # first player's zone bars

# ── Title / stat line (updates per player) ─────────────────────
HEADER = (
    "<span style='font-size:26px;color:#fff;font-weight:bold;letter-spacing:6px'>"
    "SAN ANTONIO SPURS</span>"
    "<span style='font-size:26px;color:" + GOLD + ";letter-spacing:6px'> ★</span><br>"
    "<span style='font-size:12px;color:" + MUTE + ";letter-spacing:5px'>"
    "2025–26 SEASON  ·  SHOT CHART</span>")

def title_for(p):
    s = player_stats(chart[chart["PLAYER_NAME"] == p])
    return (HEADER + "<br>"
            f"<span style='font-size:18px;color:{TEXT};font-weight:bold;letter-spacing:2px'>"
            f"{p.upper()}</span>"
            f"<span style='font-size:13px;color:{MUTE}'>"
            f"     FG <b style='color:{TEXT}'>{s['fg']}%</b> ({s['made']}/{s['total']})"
            f"     ·   2PT <b style='color:{TEXT}'>{s['t2']}%</b>"
            f"     ·   3PT <b style='color:{TEXT}'>{s['t3']}%</b> ({s['t3a']})"
            f"     ·   eFG <b style='color:{GOLD}'>{s['efg']}%</b></span>")

# ── Player selector (horizontal pill row) ──────────────────────
SHORT = {p: p.split()[-1].upper() for p in players}   # last-name pills
buttons = []
for i, p in enumerate(players):
    vis = [True] + [k == i for k in range(N)] + [k == i for k in range(N)]
    buttons.append(dict(label=SHORT[p], method="update",
                        args=[{"visible": vis}, {"title.text": title_for(p)}]))

# ── Layout ─────────────────────────────────────────────────────
fig.update_layout(
    title=dict(text=title_for(players[0]), x=0.5, xanchor="center",
               y=0.955, yanchor="top", font=dict(color=TEXT, family=FONT)),
    updatemenus=[dict(
        type="buttons", direction="right", buttons=buttons,
        x=0.005, xanchor="left", y=1.16, yanchor="top", pad=dict(l=2, r=2, t=2, b=2),
        bgcolor=PANEL, bordercolor=GOLD, borderwidth=1,
        font=dict(color=TEXT, size=12, family=FONT), showactive=True, active=0)],
    # court axes
    xaxis=dict(range=[-260, 260], visible=False, fixedrange=True),
    yaxis=dict(range=[-55, 430], visible=False, fixedrange=True,
               scaleanchor="x", scaleratio=1),   # lock court aspect
    # zone-panel axes
    xaxis2=dict(range=[0, 100], showgrid=True, gridcolor="#232327", gridwidth=1,
                zeroline=False, tickfont=dict(color=MUTE, size=11, family=FONT),
                ticksuffix="%", title=dict(text="FG% BY ZONE",
                font=dict(color=MUTE, size=12, family=FONT)), side="top"),
    yaxis2=dict(showgrid=False, zeroline=False, autorange="reversed",
                tickfont=dict(color=TEXT, size=13, family=FONT)),
    plot_bgcolor=COURT_BG, paper_bgcolor=BG,
    font=dict(family=FONT, color=TEXT),
    margin=dict(l=30, r=40, t=190, b=40),
    width=1180, height=760, bargap=0.45,
    annotations=[
        dict(   # compact make/miss key inside court
            x=0.005, y=0.02, xref="paper", yref="paper", xanchor="left", showarrow=False,
            align="left", font=dict(size=13, family=FONT),
            text=(f"<span style='color:{MAKE}'>●</span> "
                  f"<span style='color:{MUTE}'>MADE</span>&nbsp;&nbsp;&nbsp;"
                  f"<span style='color:{MISS}'>●</span> "
                  f"<span style='color:{MUTE}'>MISSED</span>")),
        dict(   # explain bar shading = volume
            x=1.0, y=-0.03, xref="paper", yref="paper", xanchor="right", showarrow=False,
            font=dict(size=11, family=FONT, color=MUTE),
            text="BAR SHADE = SHOT VOLUME")],
)

if __name__ == "__main__":
    fig.write_html("spurs_shot_chart.html", include_plotlyjs="cdn",
                   full_html=True, config={"displayModeBar": False})
    print("wrote spurs_shot_chart.html")
    # fig.show()  # uncomment for interactive local view
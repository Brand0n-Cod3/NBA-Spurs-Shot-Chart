import pandas as pd
import numpy as np
import plotly.graph_objects as go

chart = pd.read_csv("spurs_data.csv")

# ── Spurs palette ──────────────────────────────────────────────
BG         = "#0d0d0d"       # near-black background
COURT_BG   = "#1a1a1a"       # dark court surface
COURT_LINE = "#888888"       # silver court lines
HOOP_COL   = "#C4A35A"       # Spurs gold
MAKE_COL   = "#A8D8A8"       # soft green makes
MISS_COL   = "#E07070"       # soft red misses
TEXT_COL   = "#E8E8E8"       # off-white text
ACC_COL    = "#C0C0C0"       # silver accent

player_names = [
    "De'Aaron Fox", "Stephon Castle", "Julian Champagnie",
    "Devin Vassell", "Victor Wembanyama", "Keldon Johnson", "Dylan Harper"
]

# ── Per-player stats ───────────────────────────────────────────
def player_stats(df, player):
    p = df[df['PLAYER_NAME'] == player]
    total   = len(p)
    made    = p['SHOT_MADE_FLAG'].sum()
    fg_pct  = round(made / total * 100, 1) if total > 0 else 0
    threes  = p[p['SHOT_TYPE'] == '3PT Field Goal']
    twos    = p[p['SHOT_TYPE'] == '2PT Field Goal']
    t3_pct  = round(threes['SHOT_MADE_FLAG'].sum() / len(threes) * 100, 1) if len(threes) > 0 else 0
    t2_pct  = round(twos['SHOT_MADE_FLAG'].sum()   / len(twos)   * 100, 1) if len(twos)   > 0 else 0
    return dict(total=total, made=int(made), fg_pct=fg_pct,
                t3a=len(threes), t3_pct=t3_pct,
                t2a=len(twos),   t2_pct=t2_pct)

# ── Court drawing ──────────────────────────────────────────────
def add_court(fig):
    def line(x0, y0, x1, y1, w=1.5):
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=COURT_LINE, width=w))
    def rect(x0, y0, x1, y1):
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=COURT_LINE, width=1.5), fillcolor="rgba(0,0,0,0)")
    def circle(x0, y0, x1, y1, color=COURT_LINE):
        fig.add_shape(type="circle", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=color, width=1.5), fillcolor="rgba(0,0,0,0)")

    # Outer boundary
    rect(-250, -47.5, 250, 422.5)
    # Paint boxes
    rect(-80, -47.5, 80, 142.5)
    rect(-60, -47.5, 60, 142.5)
    # Free throw circle
    circle(-60, 82.5, 60, 202.5)
    # Restricted area
    fig.add_shape(type="path", path="M -40 0 A 40 40 0 0 1 40 0",
                  line=dict(color=COURT_LINE, width=1.5))
    # Hoop
    circle(-7.5, -7.5, 7.5, 7.5, color=HOOP_COL)
    # Backboard
    line(-30, -7.5, 30, -7.5, w=2.5)
    # Corner 3s
    line(-220, -47.5, -220, 92.5)
    line( 220, -47.5,  220, 92.5)
    # Three-point arc
    theta = np.linspace(np.radians(22), np.radians(158), 120)
    fig.add_trace(go.Scatter(
        x=237.5 * np.cos(theta),
        y=237.5 * np.sin(theta),
        mode='lines',
        line=dict(color=COURT_LINE, width=1.5),
        hoverinfo='none', showlegend=False
    ))
    return fig

# ── Build figure ───────────────────────────────────────────────
fig = go.Figure()
fig = add_court(fig)

# Dummy traces for make/miss legend
fig.add_trace(go.Scatter(
    x=[None], y=[None], mode='markers',
    marker=dict(size=8, color=MAKE_COL, symbol='circle'),
    name='Made', showlegend=True
))
fig.add_trace(go.Scatter(
    x=[None], y=[None], mode='markers',
    marker=dict(size=8, color=MISS_COL, symbol='circle'),
    name='Missed', showlegend=True
))

LEGEND_TRACES = 2  # arc + 2 legend dummies = indices 0,1,2; players start at 3

# Player shot traces
for player in player_names:
    player_df = chart[chart['PLAYER_NAME'] == player].copy()
    s = player_stats(chart, player)
    player_df['hover'] = (
        player_df['ACTION_TYPE'] + '<br>' +
        player_df['SHOT_TYPE'] + '<br>' +
        player_df['SHOT_DISTANCE'].astype(str) + ' ft<br>' +
        player_df['SHOT_MADE_FLAG'].map({1: '✓ Made', 0: '✗ Missed'})
    )
    fig.add_trace(go.Scatter(
        x=player_df['LOC_X'],
        y=player_df['LOC_Y'],
        mode='markers',
        marker=dict(
            color=player_df['SHOT_MADE_FLAG'].map({1: MAKE_COL, 0: MISS_COL}),
            size=5,
            opacity=0.65,
            line=dict(width=0)
        ),
        name=player,
        visible=False,
        hovertemplate='%{customdata}<extra></extra>',
        customdata=player_df['hover'],
        showlegend=False
    ))

# Make first player visible
fig.data[3].visible = True

# ── Buttons ────────────────────────────────────────────────────
N = len(player_names)
TOTAL_TRACES = 1 + LEGEND_TRACES + N  # arc + 2 legend + 7 players

fixed_layout = {
    'xaxis.range':     [-265, 265],
    'yaxis.range':     [-55,  400],
    'xaxis.autorange': False,
    'yaxis.autorange': False,
}

HEADER = (
    "<span style='font-size:22px;color:#ffffff;font-weight:bold;letter-spacing:2px'>"
    "SAN ANTONIO SPURS</span><br>"
    "<span style='font-size:12px;color:#888888;letter-spacing:3px'>"
    "2025–26 SHOT CHART</span><br>"
)

def make_title(player, s):
    return (
        HEADER +
        f"<span style='font-size:16px;color:{TEXT_COL};font-weight:bold'>{player}</span><br>"
        f"<span style='color:{ACC_COL};font-size:12px'>"
        f"FG {s['fg_pct']}%  ({s['made']}/{s['total']} FGA) &nbsp;|&nbsp; "
        f"2PT {s['t2_pct']}% ({s['t2a']} att) &nbsp;|&nbsp; "
        f"3PT {s['t3_pct']}% ({s['t3a']} att)</span>"
    )

buttons = []
for i, player in enumerate(player_names):
    s = player_stats(chart, player)
    visible = [True, True, True] + [j == i for j in range(N)]
    layout_update = {**fixed_layout, 'title.text': make_title(player, s)}
    buttons.append(dict(
        label=player,
        method='update',
        args=[{'visible': visible}, layout_update]
    ))

s0 = player_stats(chart, player_names[0])
init_title = make_title(player_names[0], s0)

fig.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        x=0.01, xanchor="left",
        y=1.13, yanchor="top",
        bgcolor="#2a2a2a",
        bordercolor=ACC_COL,
        borderwidth=1,
        font=dict(color=TEXT_COL, size=13),
        showactive=True,
        active=0,
    )],
    title=dict(
        text=init_title,
        x=0.5, xanchor='center',
        y=0.97, yanchor='top',
        font=dict(color=TEXT_COL)
    ),
    xaxis=dict(range=[-265, 265], showgrid=False, zeroline=False,
               visible=False, autorange=False),
    yaxis=dict(range=[-55, 400],  showgrid=False, zeroline=False,
               visible=False, autorange=False),
    plot_bgcolor=COURT_BG,
    paper_bgcolor=BG,
    margin=dict(l=20, r=20, t=175, b=20),
    width = 1400,
    height = 700,
    legend=dict(
        x=0.88, y=0.12,
        bgcolor="rgba(30,30,30,0.8)",
        bordercolor=ACC_COL,
        borderwidth=1,
        font=dict(color=TEXT_COL, size=12)
    ),
    font=dict(family="'Helvetica Neue', Arial, sans-serif", color=TEXT_COL)
)

fig.show()
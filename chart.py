import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp

chart = pd.read_csv("spurs_data.csv")

import plotly.graph_objects as go

def draw_nba_court(fig):
    # Hoop
    fig.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5,
                  line=dict(color="orange", width=2))
    # Backboard
    fig.add_shape(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5,
                  line=dict(color="black", width=2))
    # Paint - outer box
    fig.add_shape(type="rect", x0=-80, y0=-47.5, x1=80, y1=142.5,
                  line=dict(color="black", width=2))
    # Paint - inner box
    fig.add_shape(type="rect", x0=-60, y0=-47.5, x1=60, y1=142.5,
                  line=dict(color="black", width=2))
    # Free throw circle
    fig.add_shape(type="circle", x0=-60, y0=82.5, x1=60, y1=202.5,
                  line=dict(color="black", width=2))
    # Restricted area arc
    fig.add_shape(type="path",
                  path="M -40 0 A 40 40 0 0 1 40 0",
                  line=dict(color="black", width=2))
    # Three point line - left corner
    fig.add_shape(type="line", x0=-220, y0=-47.5, x1=-220, y1=92.5,
                  line=dict(color="black", width=2))
    # Three point line - right corner
    fig.add_shape(type="line", x0=220, y0=-47.5, x1=220, y1=92.5,
                  line=dict(color="black", width=2))
    # Three point arc
    theta = np.linspace(np.radians(22), np.radians(158), 100)
    arc_x = 237.5 * np.cos(theta)
    arc_y = 237.5 * np.sin(theta)
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode='lines',
        line=dict(color='black', width=2),
        hoverinfo='none',
        showlegend=False
    ))

    # Half court line
    fig.add_shape(type="line", x0=-250, y0=422.5, x1=250, y1=422.5,
                  line=dict(color="black", width=2))
    # Outer boundary
    fig.add_shape(type="rect", x0=-250, y0=-47.5, x1=250, y1=422.5,
                  line=dict(color="black", width=2))
    return fig

fig = go.Figure()
fig = draw_nba_court(fig)
fig.update_layout(
    autosize = True,
    xaxis=dict(range=[-300, 300], showgrid=False, zeroline=False, visible=False, autorange= False),
    yaxis=dict(range=[-50, 375], showgrid=False, zeroline=False, visible=False, autorange = False),
    plot_bgcolor="white",
    title="2025-26 San Antonio Spurs Shot Chart"
)

player_names = ["De'Aaron Fox","Stephon Castle", "Julian Champagnie","Devin Vassell","Victor Wembanyama","Keldon Johnson", "Dylan Harper"]

for player in player_names:
    player_df = chart[chart['PLAYER_NAME'] == player]
    
    fig.add_trace(go.Scatter(
        x=player_df['LOC_X'],
        y=player_df['LOC_Y'],
        mode='markers',
        marker=dict(
            color=player_df['SHOT_MADE_FLAG'].map({1: 'green', 0: 'red'}),
            size=5,
            opacity=0.6
        ),
        name=player,
        visible=False
    ))

fixed_layout = {
    'xaxis.range': [-300, 300],
    'yaxis.range': [-50, 375],
    'xaxis.autorange': False,
    'yaxis.autorange': False,
}

buttons = []
for i, player in enumerate(player_names):
    visible = [True] + [j == i for j in range(len(player_names))]
    buttons.append(dict(
        label=player,
        method='update',
        args=[
            {'visible': visible},
            fixed_layout
        ]
    ))

fig.update_layout(
    autosize = True,
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        x=0.9,
        y=1.1,
        showactive=True,
    )],
    xaxis=dict(range=[-300, 300], showgrid=False, zeroline=False, visible=False, autorange=False),
    yaxis=dict(range=[-50, 375], showgrid=False, zeroline=False, visible=False, autorange=False),
    plot_bgcolor="white"
)

fig.data[1].visible = True
fig.show()

fig.write_html('firstdraft.html')
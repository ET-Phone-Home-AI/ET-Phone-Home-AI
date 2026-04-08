"""
Artemis II Mission Dashboard
NASA's first crewed lunar flyby since Apollo 17 (1972)
Run: python artemis2.py  →  open http://127.0.0.1:8050
Requires: pip install dash plotly requests numpy
"""

import requests
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

NASA_API_KEY = "DEMO_KEY"   # Replace with your free key from https://api.nasa.gov

# ── Mission Data ─────────────────────────────────────────────────────────────
CREW = [
    {"name": "Reid Wiseman",   "role": "Commander",          "agency": "NASA",
     "bio": "Former ISS Commander · Naval aviator · 205 days in space"},
    {"name": "Victor Glover",  "role": "Pilot",              "agency": "NASA",
     "bio": "First Black astronaut on long-duration ISS mission · 167 days in space"},
    {"name": "Christina Koch", "role": "Mission Specialist", "agency": "NASA",
     "bio": "Longest spaceflight by a woman (328 days) · Spacewalk record holder"},
    {"name": "Jeremy Hansen",  "role": "Mission Specialist", "agency": "CSA",
     "bio": "First Canadian to travel to deep space · CF-18 fighter pilot"},
]

PHASES = [
    {"phase": "Launch & Ascent",        "start": 0.0,  "end": 0.08,  "color": "#ff7c00"},
    {"phase": "Earth Orbit / TLI",      "start": 0.08, "end": 1.0,   "color": "#ffaa00"},
    {"phase": "Translunar Coast",        "start": 1.0,  "end": 4.5,   "color": "#1a9eff"},
    {"phase": "Lunar Flyby",             "start": 4.5,  "end": 5.0,   "color": "#ff2244"},
    {"phase": "Transearth Coast",        "start": 5.0,  "end": 9.5,   "color": "#44dd88"},
    {"phase": "Reentry & Splashdown",   "start": 9.5,  "end": 10.0,  "color": "#ffff00"},
]

STATS = [
    {"label": "Mission Duration",   "value": "~10 Days"},
    {"label": "Max Distance",       "value": "~370,000 km"},
    {"label": "Reentry Speed",      "value": "~40,000 km/h"},
    {"label": "Heat Shield Temp",   "value": "2,760°C"},
    {"label": "SLS Thrust",         "value": "8.8M lbs"},
    {"label": "Crew",               "value": "4 Astronauts"},
]

# ── NASA API ──────────────────────────────────────────────────────────────────
def get_apod():
    try:
        r = requests.get(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": NASA_API_KEY}, timeout=10
        )
        return r.json() if r.ok else {}
    except Exception:
        return {}


def get_neos():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    try:
        r = requests.get(
            "https://api.nasa.gov/neo/rest/v1/feed",
            params={"start_date": today, "end_date": today, "api_key": NASA_API_KEY},
            timeout=10
        )
        if r.ok:
            return r.json()["near_earth_objects"].get(today, [])[:12]
    except Exception:
        pass
    return []


# ── Figures ───────────────────────────────────────────────────────────────────
DARK = "#0a0a1a"
PANEL = "#111130"
ACCENT = "#ff7c00"

def trajectory_fig():
    moon_x = 384_000
    a, b = 192_000, 75_000

    out_x = a + a * np.cos(np.linspace(np.pi, 0, 300))
    out_y = b * np.sin(np.linspace(np.pi, 0, 300))

    fly_t = np.linspace(np.pi, 2 * np.pi, 80)
    fly_x = moon_x + 14_000 * np.cos(fly_t)
    fly_y = 14_000 * np.sin(fly_t)

    ret_x = a + a * np.cos(np.linspace(0, np.pi, 300))
    ret_y = -b * np.sin(np.linspace(0, np.pi, 300))

    fig = go.Figure()

    # Glow rings for Earth
    for r, alpha in [(28000, 0.06), (20000, 0.12), (12000, 0.20)]:
        theta = np.linspace(0, 2*np.pi, 100)
        fig.add_trace(go.Scatter(
            x=r*np.cos(theta), y=r*np.sin(theta),
            mode="lines", line=dict(color=f"rgba(26,158,255,{alpha})", width=1),
            showlegend=False, hoverinfo="skip"
        ))

    fig.add_trace(go.Scatter(x=out_x, y=out_y, mode="lines",
        line=dict(color="#ff7c00", width=3), name="Outbound (TLI → Moon)"))
    fig.add_trace(go.Scatter(x=fly_x, y=fly_y, mode="lines",
        line=dict(color="#ff2244", width=3, dash="dot"), name="Lunar Flyby Arc"))
    fig.add_trace(go.Scatter(x=ret_x, y=ret_y, mode="lines",
        line=dict(color="#44dd88", width=3, dash="dash"), name="Return Coast"))

    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text",
        marker=dict(size=22, color="#1a9eff"), text=["🌍 Earth"],
        textposition="top center", name="Earth"))
    fig.add_trace(go.Scatter(x=[moon_x], y=[0], mode="markers+text",
        marker=dict(size=16, color="#cccccc"), text=["🌕 Moon"],
        textposition="top center", name="Moon"))
    fig.add_trace(go.Scatter(x=[0], y=[-9000], mode="markers+text",
        marker=dict(size=14, color="#ffff00", symbol="star"),
        text=["⭐ Splashdown"], textposition="bottom center", name="Splashdown"))

    fig.update_layout(
        title=dict(text="Artemis II Free-Return Trajectory", font=dict(size=18, color=ACCENT)),
        plot_bgcolor=DARK, paper_bgcolor=PANEL,
        font=dict(color="white"),
        legend=dict(bgcolor="#1a1a3a", bordercolor="#333366", font=dict(size=11)),
        xaxis=dict(gridcolor="#1a1a3a", zeroline=False, title="Distance (km)"),
        yaxis=dict(gridcolor="#1a1a3a", zeroline=False, title="Distance (km)",
                   scaleanchor="x", scaleratio=1),
        height=520, margin=dict(l=60, r=20, t=60, b=60),
    )
    return fig


def timeline_fig():
    fig = go.Figure()
    for p in PHASES:
        fig.add_trace(go.Bar(
            x=[p["end"] - p["start"]], y=[p["phase"]], base=[p["start"]],
            orientation="h", marker_color=p["color"], name=p["phase"],
            hovertemplate=f"<b>{p['phase']}</b><br>Day {p['start']} → {p['end']}<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text="Mission Phase Timeline (10-Day Journey)", font=dict(size=16, color=ACCENT)),
        plot_bgcolor=DARK, paper_bgcolor=PANEL, font=dict(color="white"),
        showlegend=False, barmode="overlay",
        xaxis=dict(gridcolor="#1a1a3a", title="Mission Elapsed Time (days)", range=[0, 10.5]),
        yaxis=dict(gridcolor="#1a1a3a"),
        height=340, margin=dict(l=180, r=20, t=50, b=50),
    )
    return fig


def distance_fig():
    days = np.linspace(0, 10, 600)
    peak_day, peak_dist = 4.5, 370_000
    dist = np.where(
        days <= peak_day,
        peak_dist * np.sin(np.pi * days / (2 * peak_day)) ** 1.4,
        peak_dist * np.sin(np.pi * (10 - days) / (2 * (10 - peak_day))) ** 1.4,
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=dist / 1000, mode="lines",
        line=dict(color="#1a9eff", width=3),
        fill="tozeroy", fillcolor="rgba(26,158,255,0.10)",
        hovertemplate="Day %{x:.2f}<br>Distance: %{y:,.0f} thousand km<extra></extra>",
    ))
    fig.add_vline(x=4.5, line_dash="dot", line_color="#ff2244", line_width=2,
                  annotation_text=" Lunar Flyby", annotation_font_color="#ff2244",
                  annotation_font_size=13)
    fig.update_layout(
        title=dict(text="Orion Distance from Earth", font=dict(size=16, color=ACCENT)),
        plot_bgcolor=DARK, paper_bgcolor=PANEL, font=dict(color="white"),
        xaxis=dict(gridcolor="#1a1a3a", title="Mission Elapsed Time (days)"),
        yaxis=dict(gridcolor="#1a1a3a", title="Distance (thousand km)"),
        height=340, margin=dict(l=70, r=20, t=50, b=50),
    )
    return fig


def neo_fig(neos):
    if not neos:
        fig = go.Figure()
        fig.add_annotation(text="No NEO data — check your NASA API key",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(color="white", size=15), showarrow=False)
        fig.update_layout(paper_bgcolor=PANEL, plot_bgcolor=DARK)
        return fig

    names = [n["name"].replace("(", "").replace(")", "") for n in neos]
    diams = [(n["estimated_diameter"]["kilometers"]["estimated_diameter_min"] +
              n["estimated_diameter"]["kilometers"]["estimated_diameter_max"]) / 2 for n in neos]
    hazard = [n["is_potentially_hazardous_asteroid"] for n in neos]
    colors = ["#ff2244" if h else "#44dd88" for h in hazard]

    fig = go.Figure(go.Bar(
        x=names, y=diams, marker_color=colors,
        hovertemplate="<b>%{x}</b><br>~%{y:.3f} km diameter<extra></extra>",
    ))
    fig.add_annotation(x=0.02, y=0.96, xref="paper", yref="paper", showarrow=False,
        text="🔴 Potentially hazardous   🟢 Safe", font=dict(color="white", size=12))
    fig.update_layout(
        title=dict(text="Today's Near-Earth Objects", font=dict(size=16, color=ACCENT)),
        plot_bgcolor=DARK, paper_bgcolor=PANEL, font=dict(color="white"),
        xaxis=dict(gridcolor="#1a1a3a", tickangle=40),
        yaxis=dict(gridcolor="#1a1a3a", title="Estimated Diameter (km)"),
        height=380, margin=dict(l=60, r=20, t=60, b=120),
    )
    return fig


# ── Layout ────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME],
    title="Artemis II Dashboard",
)

def stat_card(label, value):
    return dbc.Col(dbc.Card([
        dbc.CardBody([
            html.P(label, className="text-muted mb-1", style={"fontSize": "0.75rem", "textTransform": "uppercase"}),
            html.H5(value, style={"color": ACCENT, "fontWeight": "bold"}),
        ])
    ], style={"background": PANEL, "border": "1px solid #2a2a5a"}), width=2)


def crew_card(member):
    agency_color = "#1a9eff" if member["agency"] == "NASA" else "#ff2244"
    return dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H6(member["name"], style={"color": "white", "fontWeight": "bold"}),
            dbc.Badge(member["agency"], color="primary" if member["agency"] == "NASA" else "danger",
                      className="mb-2"),
            html.P(member["role"], style={"color": ACCENT, "fontSize": "0.85rem", "margin": 0}),
            html.P(member["bio"], className="text-muted mt-2", style={"fontSize": "0.78rem"}),
        ])
    ], style={"background": PANEL, "border": f"1px solid {agency_color}"}), width=3)


app.layout = dbc.Container(fluid=True, style={"background": "#06060f", "minHeight": "100vh", "padding": "24px"}, children=[

    # Header
    dbc.Row(dbc.Col(html.Div([
        html.H1("🚀 ARTEMIS II", style={"color": ACCENT, "letterSpacing": "4px", "fontWeight": "900", "margin": 0}),
        html.P("NASA's First Crewed Lunar Flyby Since Apollo 17 · Reid Wiseman · Victor Glover · Christina Koch · Jeremy Hansen",
               style={"color": "#8888aa", "fontSize": "0.9rem", "marginTop": "4px"}),
    ])), className="mb-4"),

    # Stat cards
    dbc.Row([stat_card(s["label"], s["value"]) for s in STATS], className="mb-4 g-3"),

    # Trajectory
    dbc.Row([
        dbc.Col(dcc.Graph(figure=trajectory_fig(), config={"displayModeBar": False}), width=8),
        dbc.Col([
            html.H5("Mission Phases", style={"color": ACCENT}),
            *[dbc.Row([
                dbc.Col(html.Div(style={"width": "12px", "height": "12px", "borderRadius": "50%",
                                        "background": p["color"], "marginTop": "5px"}), width="auto"),
                dbc.Col(html.Div([
                    html.Span(p["phase"], style={"color": "white", "fontSize": "0.85rem"}),
                    html.Br(),
                    html.Span(f"Day {p['start']} → {p['end']}", style={"color": "#8888aa", "fontSize": "0.75rem"}),
                ]))
            ], className="mb-2 align-items-start") for p in PHASES],
        ], width=4, style={"paddingTop": "60px"}),
    ], className="mb-4"),

    # Timeline + Distance
    dbc.Row([
        dbc.Col(dcc.Graph(figure=timeline_fig(), config={"displayModeBar": False}), width=6),
        dbc.Col(dcc.Graph(figure=distance_fig(), config={"displayModeBar": False}), width=6),
    ], className="mb-4"),

    # Crew
    html.H4("Mission Crew", style={"color": ACCENT, "marginBottom": "16px"}),
    dbc.Row([crew_card(m) for m in CREW], className="mb-4 g-3"),

    # NASA Live Data
    html.H4("NASA Live Data", style={"color": ACCENT, "marginBottom": "16px"}),
    dbc.Row([
        dbc.Col([
            dbc.Button("Load Astronomy Picture of the Day", id="apod-btn", color="warning",
                       outline=True, className="mb-3"),
            html.Div(id="apod-output"),
        ], width=5),
        dbc.Col([
            dbc.Button("Load Today's Near-Earth Objects", id="neo-btn", color="info",
                       outline=True, className="mb-3"),
            dcc.Graph(id="neo-chart", style={"display": "none"}, config={"displayModeBar": False}),
        ], width=7),
    ], className="mb-4"),

    html.P("Data sources: NASA Open APIs (api.nasa.gov) · Trajectory based on Artemis II mission profile",
           className="text-muted text-center", style={"fontSize": "0.75rem", "marginTop": "20px"}),
])


@callback(Output("apod-output", "children"), Input("apod-btn", "n_clicks"), prevent_initial_call=True)
def load_apod(_):
    data = get_apod()
    if not data or "error" in data:
        return html.P("Could not load APOD. Check your NASA API key.", style={"color": "#ff2244"})
    elements = [html.H6(f"{data.get('title', '')} ({data.get('date', '')})", style={"color": ACCENT})]
    if data.get("media_type") == "image":
        elements.append(html.Img(src=data.get("url", ""), style={"width": "100%", "borderRadius": "8px", "marginBottom": "10px"}))
    elements.append(html.P(data.get("explanation", "")[:400] + "...", style={"color": "#cccccc", "fontSize": "0.82rem"}))
    return elements


@callback(
    Output("neo-chart", "figure"),
    Output("neo-chart", "style"),
    Input("neo-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_neo(_):
    return neo_fig(get_neos()), {"display": "block"}


if __name__ == "__main__":
    app.run(debug=True)

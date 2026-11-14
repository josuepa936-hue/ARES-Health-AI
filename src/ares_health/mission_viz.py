"""Mission-style Plotly figures for *synthetic* health-signal exploration."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.ares_health.advanced_stats import SIGNALS, SignalSummary

SYSTEMS = ("Cardiovascular", "Sleep & Recovery", "Musculoskeletal")
HOTSPOTS = {
    "Cardiovascular": (-0.17, 5.13),
    "Sleep & Recovery": (0.0, 6.92),
    "Musculoskeletal": (0.22, 2.82),
}
SYSTEM_METRICS = {
    "Cardiovascular": "resting_hr_bpm",
    "Sleep & Recovery": "sleep_hours",
    "Musculoskeletal": "activity_minutes",
}


def make_signal_chart(
    frame: pd.DataFrame, metric: str, summary: SignalSummary | None = None,
) -> go.Figure:
    """Time series, optional rolling median and separate illustrative windows."""
    if metric not in SIGNALS:
        raise ValueError("Unsupported signal")
    label, unit, _, color = SIGNALS[metric]
    dates = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    vals = pd.to_numeric(frame[metric], errors="coerce")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=vals, mode="lines+markers", name="Observed (fictional)",
        line=dict(color=color, width=3), marker=dict(size=7),
        connectgaps=False,
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f} " + unit + "<extra></extra>",
    ))
    if summary is not None:
        smooth = vals.rolling(window=3, min_periods=3).median()
        fig.add_trace(go.Scatter(
            x=dates, y=smooth, mode="lines", name="3-day rolling median",
            line=dict(color="#F6C36B", width=2, dash="dot"),
            connectgaps=False,
        ))
        fig.add_hline(
            y=summary.baseline_mean, line=dict(color="#A9BCD0", width=1, dash="dash"),
            annotation_text="Illustrative reference mean",
            annotation_position="top left",
        )
    fig.update_layout(
        title=None,
        paper_bgcolor="#0C1528", plot_bgcolor="#0C1528",
        font=dict(color="#DFEAF5"),
        hovermode="x unified",
        margin=dict(l=26, r=22, t=28, b=28),
        height=380,
        xaxis=dict(title="UTC date", showgrid=False, zeroline=False),
        yaxis=dict(title=f"{label} ({unit})", gridcolor="#243551", zeroline=False),
        legend=dict(orientation="h", y=1.16, x=0),
    )
    return fig


def make_body_map(active_system: str = "Cardiovascular") -> go.Figure:
    """Original stylized vector silhouette with selectable system hotspots.

    The figure illustrates interface navigation, not human anatomy or diagnosis.
    """
    if active_system not in SYSTEMS:
        raise ValueError("Unsupported system")

    fig = go.Figure()
    shape = dict(fillcolor="rgba(75,143,207,0.13)", line=dict(color="#4C85B2", width=2))
    fig.add_shape(type="circle", x0=-0.39, y0=6.34, x1=0.39, y1=7.15, **shape)
    fig.add_shape(
        type="path",
        path="M -0.45,6.22 L 0.45,6.22 L 0.67,5.9 L 0.53,4.15 L 0.30,3.91 L -0.30,3.91 L -0.53,4.15 L -0.67,5.9 Z",
        **shape,
    )
    for x0, x1 in [(-0.53, -0.98), (0.53, 0.98)]:
        fig.add_shape(type="line", x0=x0, y0=5.78, x1=x1, y1=3.85,
                      line=dict(color="#4C85B2", width=20))
    for x0, x1 in [(-0.22, -0.42), (0.22, 0.42)]:
        fig.add_shape(type="line", x0=x0, y0=3.9, x1=x1, y1=1.35,
                      line=dict(color="#4C85B2", width=24))

    xs = [HOTSPOTS[s][0] for s in SYSTEMS]
    ys = [HOTSPOTS[s][1] for s in SYSTEMS]
    colors = [SIGNALS[SYSTEM_METRICS[s]][3] if s == active_system else "#405D7E" for s in SYSTEMS]
    size = [34 if s == active_system else 24 for s in SYSTEMS]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(color=colors, size=size, line=dict(color="#D5E9FA", width=2)),
        text=["H", "S", "M"], textposition="middle center",
        textfont=dict(color="#0A1426", size=12, family="Arial Black"),
        customdata=list(SYSTEMS), name="Body systems",
        hovertemplate="%{customdata}<extra></extra>",
        selected=dict(marker=dict(opacity=1)),
    ))
    fig.update_layout(
        height=500, margin=dict(l=5, r=5, t=10, b=10),
        paper_bgcolor="#0C1528", plot_bgcolor="#0C1528",
        font=dict(color="#DDEDF7"), showlegend=False,
        dragmode="select", clickmode="event+select",
        xaxis=dict(range=[-1.35, 1.35], visible=False, fixedrange=True),
        yaxis=dict(range=[0.9, 7.4], visible=False, fixedrange=True, scaleanchor="x"),
    )
    return fig

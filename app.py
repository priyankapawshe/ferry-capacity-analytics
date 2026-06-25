import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ferry Capacity Analytics",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #050a14 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #070d1a !important;
    border-right: 1px solid #1a2744 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b1223; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }

/* ── Main title area ── */
.dash-header {
    padding: 6px 0 16px;
    border-bottom: 1px solid #1a3050;
    margin-bottom: 18px;
}
.dash-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px; font-weight: 800;
    color: #e2e8f0; margin: 0 0 6px;
}
.dash-status {
    display: inline-flex; align-items: center; gap: 8px;
    background: #0f2b1a; border: 1px solid #166534;
    border-radius: 20px; padding: 3px 12px;
    font-size: 11px; font-weight: 600; color: #22c55e;
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #22c55e; animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
.dash-sub { font-size: 11px; color: #475569; letter-spacing: 1px; margin-left: 10px; }

/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(145deg, #0d1b2e, #0a1525);
    border: 1px solid #1a3050;
    border-radius: 14px; padding: 18px 16px;
    position: relative; overflow: hidden;
    transition: transform .2s, border-color .2s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-2px); border-color: #2a5080; }
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent); border-radius: 14px 14px 0 0;
}
.kpi-icon { font-size: 20px; margin-bottom: 8px; }
.kpi-title {
    font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
    text-transform: uppercase; color: #64748b; margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px; font-weight: 700;
    color: var(--accent); line-height: 1;
}
.kpi-sub { font-size: 11px; color: #475569; margin-top: 6px; }

/* ── Section headers ── */
.section-hdr {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; color: #38bdf8;
    padding-bottom: 8px; border-bottom: 1px solid #1a3050;
    margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}

/* ── Alert cards ── */
.alert-card {
    background: #0d1b2e;
    border-left: 3px solid var(--ac);
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin-bottom: 10px;
}
.alert-title { font-size: 12px; font-weight: 600; color: var(--ac); margin-bottom: 2px; }
.alert-body  { font-size: 11px; color: #94a3b8; }

/* ── Styled dataframe wrapper ── */
.styled-table-wrap {
    background: #0d1b2e; border: 1px solid #1a3050;
    border-radius: 12px; overflow: hidden; padding: 0;
}

/* ── Executive summary box ── */
.exec-card {
    background: linear-gradient(135deg, #0d1b2e, #071220);
    border: 1px solid #1a3050; border-radius: 14px;
    padding: 20px 22px;
}
.exec-card h4 {
    font-size: 12px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #38bdf8; margin-bottom: 10px;
}
.exec-card p { font-size: 13px; line-height: 1.8; color: #94a3b8; margin: 0; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-size: 12px !important;
    font-weight: 600 !important; padding: 8px 18px !important;
    letter-spacing: .4px !important; transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .82 !important; }

/* download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-size: 12px !important;
    font-weight: 600 !important; padding: 8px 18px !important;
}

/* ── Sidebar tweaks ── */
[data-testid="stSidebar"] .stRadio label { font-size: 12px !important; }
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { font-size: 12px !important; color: #94a3b8 !important; }

.sidebar-logo { text-align: center; padding: 12px 4px 18px; border-bottom: 1px solid #1a2744; margin-bottom: 14px; }
.sidebar-logo .s-title { font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700; color:#38bdf8; letter-spacing:1px; }
.sidebar-logo .s-sub   { font-size:9px; color:#475569; letter-spacing:2.5px; text-transform:uppercase; }
.sb-section { font-size:9px; font-weight:700; letter-spacing:1.5px; color:#475569; text-transform:uppercase; margin: 14px 0 6px; }

/* Plotly dark override inside cards */
.js-plotly-plot .plotly .bg { fill: #0d1b2e !important; }

div[data-testid="stHorizontalBlock"] { gap: 14px; }
</style>
""", unsafe_allow_html=True)


# ─── DATA ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("fairy_project_feature_engineering.csv.gz")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

df = load_data()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:30px;margin-bottom:4px">⛴️</div>
        <div class="s-title">TORONTO</div>
        <div class="s-sub">Island Ferry</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">📍 Control Center</div>', unsafe_allow_html=True)

    min_date = df["Timestamp"].min().date()
    max_date = df["Timestamp"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date))

    st.markdown('<div class="sb-section">🔧 Filters</div>', unsafe_allow_html=True)

    seasons = st.multiselect(
        "Season",
        options=df["season"].unique(),
        default=list(df["season"].unique()),
    )

    granularity = st.radio("Time Granularity", ["15-Minute", "Hourly", "Daily"], horizontal=True)

    threshold = st.slider("Congestion Limit (%)", 50, 100, 75)

    st.divider()
    apply_btn = st.button("✅  Apply Filters", use_container_width=True)

    st.markdown("""
    <div style="margin-top:16px">
        <div style="font-size:9px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:8px">Data Status</div>
        <div style="display:inline-flex;align-items:center;gap:7px;background:#0f2b1a;border:1px solid #166534;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:600;color:#22c55e">
            <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;display:inline-block"></span>
            All systems operational
        </div>
        <div style="font-size:10px;color:#475569;margin-top:8px">Last refresh: 2 min ago</div>
    </div>
    """, unsafe_allow_html=True)


# ─── FILTER ──────────────────────────────────────────────────────────────────
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df["Timestamp"].dt.date >= start_date) &
    (df["Timestamp"].dt.date <= end_date) &
    (df["season"].isin(seasons))
].copy()


# ─── KPI COMPUTATIONS ────────────────────────────────────────────────────────
kpi_capacity = filtered_df["capacity_utilization_ratio"].mean() * 100
kpi_pressure = filtered_df["redemption_pressure_ratio"].mean()
kpi_idle     = filtered_df["is_idle_period"].mean() * 100
kpi_peak     = filtered_df["congestion_streak_length"].max() * 15
kpi_var      = filtered_df["total_activity_load"].std() / max(filtered_df["total_activity_load"].mean(), 1)


# ─── HEADER ──────────────────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("""
    <div class="dash-header">
        <div class="dash-title">⛴️ Ferry Capacity Utilization &amp; Efficiency Analytics</div>
        <div style="display:flex;align-items:center;gap:10px;margin-top:6px">
            <div class="dash-status">
                <span class="status-dot"></span> SYSTEM STATUS: ACTIVE
            </div>
            <span class="dash-sub">TORONTO ISLAND DATASTREAM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    bc1, bc2 = st.columns(2)
    with bc1:
        st.button("📥 Export Report")
    with bc2:
        st.button("🔗 Share")


# ─── KPI CARDS ───────────────────────────────────────────────────────────────
kpi_data = [
    ("🎯", "Capacity Utilization", f"{kpi_capacity:.1f}%",  "Efficiency",       "#38bdf8"),
    ("🔥", "Congestion Pressure",  f"{kpi_pressure:.2f}",   "Pressure Index",   "#ef4444"),
    ("💤", "Idle Capacity",         f"{kpi_idle:.1f}%",      "Waste Ratio",      "#eab308"),
    ("⏱️", "Peak Strain Duration",  f"{kpi_peak:.0f} min",  "Peak Duration",    "#a855f7"),
    ("📉", "Operational Variability",f"{kpi_var:.2f}",       "Consistency Score","#22c55e"),
]

cols = st.columns(5)
for col, (icon, title, value, sub, accent) in zip(cols, kpi_data):
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

# ─── CHART HELPERS ───────────────────────────────────────────────────────────
CARD_BG  = "#0d1b2e"
GRID_COL = "#1a3050"
TEXT_COL = "#94a3b8"
CYAN     = "#38bdf8"
RED      = "#ef4444"

def base_layout(height=370):
    return dict(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(family="Inter", size=11, color=TEXT_COL),
        margin=dict(l=44, r=16, t=36, b=28),
        height=height,
        xaxis=dict(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL, tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COL, font=dict(size=10)),
        hoverlabel=dict(bgcolor="#0a1525", bordercolor=GRID_COL, font=dict(size=11)),
    )


# ─── ROW 2: TIMELINE + HEATMAP ───────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown('<div class="section-hdr">📈 CAPACITY UTILIZATION OVER TIME</div>', unsafe_allow_html=True)

    if granularity == "Hourly":
        chart_df = filtered_df.set_index("Timestamp").resample("H")["capacity_utilization_ratio"].mean().reset_index()
    elif granularity == "Daily":
        chart_df = filtered_df.set_index("Timestamp").resample("D")["capacity_utilization_ratio"].mean().reset_index()
    else:
        chart_df = filtered_df[["Timestamp", "capacity_utilization_ratio"]].copy()
        if len(chart_df) > 8000:
            chart_df = chart_df.iloc[::max(1, len(chart_df) // 8000)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_df["Timestamp"],
        y=chart_df["capacity_utilization_ratio"],
        fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
        line=dict(color=CYAN, width=1.4),
        name="Utilization",
        hovertemplate="%{x|%Y-%m-%d %H:%M}<br>%{y:.3f}<extra></extra>",
    ))
    fig.add_hline(
        y=threshold / 100,
        line=dict(color=RED, dash="dash", width=1.5),
        annotation_text=f"Congestion Limit ({threshold}%)",
        annotation_font=dict(color=RED, size=11),
    )
    fig.update_layout(**base_layout(370), yaxis_title="Utilization Ratio")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
   st.markdown(
    '<div class="section-hdr">🌡️ CONGESTION &amp; IDLE HEATMAP</div>',
    unsafe_allow_html=True
)

heat = filtered_df.pivot_table(
    index="hour",
    columns="day_of_week",
    values="capacity_utilization_ratio",
    aggfunc="mean"
)

day_labels = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun"
}

heat.columns = [day_labels.get(c, c) for c in heat.columns]

fig2 = go.Figure(
    go.Heatmap(
        z=heat.values,
        x=heat.columns.tolist(),
        y=[f"{h:02d}:00" for h in heat.index],
        colorscale=[
            [0.0, "#0d1b2e"],
            [0.3, "#312e81"],
            [0.6, "#b45309"],
            [0.85, "#ea580c"],
            [1.0, "#fbbf24"]
        ],
        hovertemplate=
        "Day: %{x}<br>Hour: %{y}<br>Utilization: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title=dict(
                text="Utilization %",
                font=dict(color=TEXT_COL, size=11)
            ),
            tickfont=dict(
                color=TEXT_COL,
                size=9
            ),
            bgcolor=CARD_BG,
            bordercolor=GRID_COL
        )
    )
)

fig2.update_layout(
    **base_layout(370),
    yaxis=dict(
        autorange="reversed",
        gridcolor=GRID_COL,
        tickfont=dict(size=9)
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True,
    config={"displayModeBar": False}
)

# ─── ROW 3: SEASONAL + RADAR ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-hdr">🍂 SEASONAL EFFICIENCY COMPARISON</div>', unsafe_allow_html=True)

    season_df = filtered_df.groupby("season").agg(
        capacity_utilization_ratio=("capacity_utilization_ratio", "mean"),
        redemption_pressure_ratio=("redemption_pressure_ratio", "mean"),
        is_idle_period=("is_idle_period", "mean"),
    ).reset_index()

    tab_eff, tab_pres, tab_idle = st.tabs(["Efficiency", "Pressure Index", "Idle Capacity"])

    season_colors = {
        "Summer (Peak)": "#ef4444",
        "Spring":        "#22c55e",
        "Fall":          "#f97316",
        "Winter":        "#38bdf8",
    }

    for tab, metric, ylabel in [
        (tab_eff,  "capacity_utilization_ratio", "Avg Utilization Ratio"),
        (tab_pres, "redemption_pressure_ratio",  "Avg Pressure Ratio"),
        (tab_idle, "is_idle_period",              "Idle Period Fraction"),
    ]:
        with tab:
            fig3 = go.Figure(go.Bar(
                x=season_df["season"],
                y=season_df[metric],
                marker_color=[season_colors.get(s, CYAN) for s in season_df["season"]],
                marker_line_width=0,
                text=[f"{v:.3f}" for v in season_df[metric]],
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate="%{x}<br>%{y:.4f}<extra></extra>",
            ))
            fig3.update_layout(**base_layout(310), yaxis_title=ylabel, bargap=0.38, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with col2:
    st.markdown('<div class="section-hdr">🎯 KPI SUMMARY RADAR</div>', unsafe_allow_html=True)

    radar_cats = ["Utilization", "Pressure", "Idle", "Peak Strain", "Variability"]
    radar_vals = [
        min(kpi_capacity, 100),
        min(kpi_pressure * 50, 100),
        min(kpi_idle, 100),
        min(kpi_peak / 5, 100),
        min(kpi_var * 100, 100),
    ]

    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=radar_vals + [radar_vals[0]],
        theta=radar_cats + [radar_cats[0]],
        fill="toself",
        fillcolor="rgba(56,189,248,0.15)",
        line=dict(color=CYAN, width=2),
        name="KPI Profile",
    ))
    radar.update_layout(
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID_COL,
                            tickfont=dict(size=8, color=TEXT_COL), linecolor=GRID_COL),
            angularaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL,
                             tickfont=dict(size=11, color=TEXT_COL)),
        ),
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_COL),
        height=400,
        margin=dict(l=50, r=50, t=40, b=40),
        showlegend=False,
    )
    st.plotly_chart(radar, use_container_width=True, config={"displayModeBar": False})


# ─── ROW 4: ALERTS ───────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">🚨 EFFICIENCY ALERTS</div>', unsafe_allow_html=True)

al1, al2, al3 = st.columns(3)

alerts = []
if (filtered_df["capacity_utilization_ratio"] > threshold / 100).sum() > 0:
    n = int((filtered_df["capacity_utilization_ratio"] > threshold / 100).sum())
    alerts.append(("#ef4444", "🔴 High Congestion Detected",
                   f"Utilization exceeded {threshold}% at {n:,} intervals"))

if kpi_peak > 120:
    alerts.append(("#eab308", "🟡 Sustained Peak Strain",
                   f"Peak congestion duration reached {kpi_peak:.0f} min"))

if kpi_idle > 20:
    alerts.append(("#38bdf8", "🔵 Idle Capacity Opportunity",
                   f"Idle periods account for {kpi_idle:.1f}% of intervals"))

if not alerts:
    alerts.append(("#22c55e", "✅ No Active Alerts", "All metrics within normal thresholds"))

for acol, (color, title, body) in zip([al1, al2, al3], (alerts + [None, None, None])[:3]):
    if alerts and (color := None) is None:
        pass
    with acol:
        if len(alerts) > 0:
            c, t, b = alerts[0] if acol == al1 else (alerts[1] if acol == al2 and len(alerts) > 1 else (alerts[2] if acol == al3 and len(alerts) > 2 else (None, None, None)))
            if c:
                st.markdown(f"""
                <div class="alert-card" style="--ac:{c}">
                    <div class="alert-title">{t}</div>
                    <div class="alert-body">{b}</div>
                </div>
                """, unsafe_allow_html=True)

# simpler reliable alert render
st.markdown("")
a_cols = st.columns(min(len(alerts), 3))
for i, (color, title, body) in enumerate(alerts[:3]):
    with a_cols[i]:
        st.markdown(f"""
        <div class="alert-card" style="--ac:{color}">
            <div class="alert-title">{title}</div>
            <div class="alert-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)


# ─── ROW 5: TABLES ───────────────────────────────────────────────────────────
t1, t2 = st.columns(2)

with t1:
    st.markdown('<div class="section-hdr">🔝 TOP 10 BUSIEST INTERVALS</div>', unsafe_allow_html=True)

    busy = (filtered_df
            .sort_values("total_activity_load", ascending=False)
            .head(10)[["Timestamp", "total_activity_load", "season", "time_band"]]
            .reset_index(drop=True))
    busy.index += 1
    busy["Timestamp"] = busy["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(
        busy,
        use_container_width=True,
        column_config={
            "total_activity_load": st.column_config.NumberColumn("Total Load", format="%d"),
        },
    )
    st.button("View All Busy Intervals")

with t2:
    st.markdown('<div class="section-hdr">💤 TOP 10 IDLE PERIODS</div>', unsafe_allow_html=True)

    idle = (filtered_df
            .sort_values("idle_streak_length", ascending=False)
            .head(10)[["Timestamp", "idle_streak_length", "season", "time_band"]]
            .reset_index(drop=True))
    idle.index += 1
    idle["Timestamp"] = idle["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(
        idle,
        use_container_width=True,
        column_config={
            "idle_streak_length": st.column_config.NumberColumn("Idle Streak", format="%d intervals"),
        },
    )
    st.button("View All Idle Periods")


# ─── ROW 6: EXECUTIVE SUMMARY ────────────────────────────────────────────────
es1, es2 = st.columns(2)

with es1:
    st.markdown(f"""
    <div class="exec-card">
        <h4>📋 Executive Summary</h4>
        <p>
        Ferry operations show <strong style="color:#38bdf8">{kpi_capacity:.1f}%</strong> average utilization
        across the selected period. Peak congestion duration reached
        <strong style="color:#ef4444">{kpi_peak:.0f} minutes</strong>, with an operational variability
        score of <strong style="color:#22c55e">{kpi_var:.2f}</strong>.
        Idle periods account for <strong style="color:#eab308">{kpi_idle:.1f}%</strong> of all intervals,
        presenting scheduling and capacity optimisation opportunities.
        </p>
    </div>
    """, unsafe_allow_html=True)

with es2:
    st.markdown(f"""
    <div class="exec-card" style="border-color:#166534">
        <h4 style="color:#22c55e">🎯 Recommendation</h4>
        <p>
        Consider deploying <strong style="color:#22c55e">additional ferry capacity</strong> during peak
        evening hours (6 PM – 10 PM) on weekends to relieve congestion pressure.
        Dynamic scheduling during idle morning slots can reduce operational waste.
        Target a congestion limit reduction to
        <strong style="color:#38bdf8">{max(threshold-5,50)}%</strong> through load redistribution.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin:18px 0 8px'></div>", unsafe_allow_html=True)

# ─── DOWNLOAD ────────────────────────────────────────────────────────────────
csv = filtered_df.to_csv(index=False)
st.download_button(
    "📥 Download Filtered Data",
    csv,
    file_name="filtered_ferry_data.csv",
    mime="text/csv",
    use_container_width=False,
)

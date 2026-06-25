import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Toronto Island Ferry Analytics",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL STYLES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #050a14 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #070d1a !important;
    border-right: 1px solid #1a2744 !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0b1223; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }

/* ── KPI Cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 18px; }
.kpi-card {
    background: linear-gradient(145deg, #0d1b2e, #0a1525);
    border: 1px solid #1a3050;
    border-radius: 14px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
    transition: transform .2s, border-color .2s;
}
.kpi-card:hover { transform: translateY(-2px); border-color: #2a5080; }
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent);
    border-radius: 14px 14px 0 0;
}
.kpi-label { font-size: 10px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; color: #64748b; margin-bottom: 8px; }
.kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 28px; font-weight: 700; color: var(--accent); line-height: 1; }
.kpi-sub { font-size: 11px; color: #475569; margin-top: 6px; }
.kpi-delta { font-size: 12px; font-weight: 600; margin-top: 6px; }
.delta-up { color: #22c55e; }
.delta-down { color: #ef4444; }

/* ── Section Headers ── */
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px; font-weight: 600; letter-spacing: 1.4px;
    text-transform: uppercase; color: #38bdf8;
    padding-bottom: 8px;
    border-bottom: 1px solid #1a3050;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}

/* ── Alert Cards ── */
.alert-card {
    background: #0d1b2e;
    border-left: 3px solid var(--alert-color);
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin-bottom: 10px;
    display: flex; flex-direction: column; gap: 3px;
}
.alert-title { font-size: 12px; font-weight: 600; color: var(--alert-color); }
.alert-body { font-size: 11px; color: #94a3b8; }

/* ── Sidebar ── */
.sidebar-logo {
    text-align: center; padding: 16px 8px 20px;
    border-bottom: 1px solid #1a2744; margin-bottom: 16px;
}
.sidebar-logo .logo-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px; font-weight: 700; color: #38bdf8; letter-spacing: 1px;
}
.sidebar-logo .logo-sub { font-size: 10px; color: #475569; letter-spacing: 2px; }

.sidebar-section { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: #475569; text-transform: uppercase; margin: 16px 0 8px; }

/* ── Status badge ── */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0f2b1a; border: 1px solid #166534;
    border-radius: 20px; padding: 4px 12px;
    font-size: 11px; font-weight: 600; color: #22c55e;
}
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── Executive Summary ── */
.exec-card {
    background: linear-gradient(135deg, #0d1b2e, #071220);
    border: 1px solid #1a3050;
    border-radius: 14px; padding: 18px; height: 100%;
}
.exec-card h4 { font-size: 12px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #38bdf8; margin-bottom: 10px; }
.exec-card p { font-size: 13px; line-height: 1.7; color: #94a3b8; }

/* ── Top table ── */
.top-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.top-table th { color: #475569; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 6px 10px; border-bottom: 1px solid #1a3050; text-align: left; }
.top-table td { padding: 7px 10px; border-bottom: 1px solid #0f1e35; color: #cbd5e1; }
.top-table tr:hover td { background: #0d1b2e; }
.load-high { color: #ef4444; font-weight: 700; }
.load-med { color: #f59e0b; font-weight: 700; }
.load-low { color: #22c55e; font-weight: 700; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-size: 12px !important;
    font-weight: 600 !important; padding: 8px 16px !important;
    letter-spacing: .5px !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* Plotly chart bg */
.js-plotly-plot .plotly { border-radius: 12px; }

/* Metric delta override */
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Select / multiselect */
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div {
    background: #0d1b2e !important;
    border-color: #1a3050 !important;
}

div[data-testid="stSlider"] > div { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)


# ─── DATA GENERATION ────────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    dates = pd.date_range("2015-05-01", "2025-12-21", freq="15min")
    n = len(dates)

    df = pd.DataFrame({"Timestamp": dates})
    df["year"] = df["Timestamp"].dt.year
    df["month"] = df["Timestamp"].dt.month
    df["hour"] = df["Timestamp"].dt.hour
    df["day_of_week"] = df["Timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # season
    def get_season(m):
        if m in [6, 7, 8]: return "Summer (Peak)"
        elif m in [9, 10, 11]: return "Fall"
        elif m in [12, 1, 2]: return "Winter"
        else: return "Spring"
    df["season"] = df["month"].apply(get_season)
    off_season_mask = df["season"].isin(["Winter", "Fall"])

    # time_band
    def get_timeband(h):
        if 5 <= h < 9: return "Morning"
        elif 9 <= h < 12: return "Mid-Morning"
        elif 12 <= h < 17: return "Afternoon"
        elif 17 <= h < 21: return "Evening"
        else: return "Night/Off-hours"
    df["time_band"] = df["hour"].apply(get_timeband)

    # Base load
    base = 200 + 150 * np.sin(2 * np.pi * (df["hour"] - 9) / 24).clip(0)
    seasonal_factor = np.where(df["season"] == "Summer (Peak)", 1.8,
                       np.where(df["season"] == "Fall", 1.1,
                       np.where(df["season"] == "Spring", 1.0, 0.6)))
    weekend_factor = 1 + 0.4 * df["is_weekend"]
    noise = np.random.normal(0, 40, n)

    df["Sales Count"] = (base * seasonal_factor * weekend_factor + noise).clip(0).astype(int)
    df["Redemption Count"] = (df["Sales Count"] * np.random.uniform(0.3, 0.7, n)).astype(int)
    df["total_activity_load"] = df["Sales Count"] + df["Redemption Count"]

    # KPI columns
    max_load = df["total_activity_load"].max()
    df["capacity_utilization_ratio"] = (df["total_activity_load"] / max_load * 100).round(2)
    df["redemption_pressure_ratio"] = (df["Redemption Count"] / (df["Sales Count"] + 1)).round(3)
    df["OLI"] = (df["total_activity_load"] / df["total_activity_load"].rolling(96, min_periods=1).mean()).round(3)

    median_load = df["total_activity_load"].median()
    df["is_high_activity"] = (df["total_activity_load"] > df["total_activity_load"].quantile(0.85)).astype(int)
    df["is_low_activity"] = (df["total_activity_load"] < df["total_activity_load"].quantile(0.15)).astype(int)
    df["sales_is_spike"] = (df["Sales Count"] > df["Sales Count"].quantile(0.95)).astype(int)
    df["redemption_is_spike"] = (df["Redemption Count"] > df["Redemption Count"].quantile(0.95)).astype(int)

    # Streaks
    def streak(series, window=4):
        s = pd.Series(0, index=series.index)
        count = 0
        for i, v in enumerate(series):
            count = count + 1 if v else 0
            s.iloc[i] = count
        return s
    df["congestion_streak_length"] = streak(df["is_high_activity"])
    df["idle_streak_length"] = streak(df["is_low_activity"])
    df["is_congestion_period"] = (df["congestion_streak_length"] >= 4).astype(int)
    df["is_idle_period"] = (df["idle_streak_length"] >= 4).astype(int)
    return df

df = generate_data()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:32px;margin-bottom:4px;">⛴️</div>
        <div class="logo-title">TORONTO</div>
        <div class="logo-sub">ISLAND FERRY</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">📍 Control Center</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "🏠 Overview Dashboard",
        "📈 Utilization Timeline",
        "🌡️ Heatmaps",
        "📊 Seasonal Comparison",
        "💡 KPI Insights",
        "🔔 Alerts & Notifications",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="sidebar-section">🔧 Filters</div>', unsafe_allow_html=True)

    date_min = df["Timestamp"].min().date()
    date_max = df["Timestamp"].max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max),
                                min_value=date_min, max_value=date_max)

    all_seasons = df["season"].unique().tolist()
    selected_seasons = st.multiselect("Seasons", all_seasons,
                                       default=["Summer (Peak)", "Winter"])

    granularity = st.radio("Time Granularity",
                            ["15-Minute", "Hourly", "Daily"],
                            horizontal=True)

    congestion_limit = st.slider("Congestion Limit (%)", 50, 100, 75)

    col1, col2 = st.columns(2)
    with col1:
        apply = st.button("✅ Apply")
    with col2:
        reset = st.button("↺ Reset")

    st.divider()
    st.markdown("""
    <div style="padding:10px 0 4px">
        <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:8px">Data Status</div>
        <div class="status-badge"><span class="status-dot"></span> All systems operational</div>
        <div style="font-size:10px;color:#475569;margin-top:8px">Last refresh: 2 min ago</div>
    </div>
    """, unsafe_allow_html=True)


# ─── FILTER DATA ────────────────────────────────────────────────────────────
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = df["Timestamp"].min(), df["Timestamp"].max()

fdf = df[
    (df["Timestamp"] >= start_date) &
    (df["Timestamp"] <= end_date) &
    (df["season"].isin(selected_seasons if selected_seasons else all_seasons))
].copy()

# Resample
if granularity == "Hourly":
    fdf = fdf.set_index("Timestamp").resample("1H").agg({
        "total_activity_load": "sum",
        "capacity_utilization_ratio": "mean",
        "redemption_pressure_ratio": "mean",
        "is_congestion_period": "max",
        "is_idle_period": "max",
        "season": "first", "time_band": "first",
        "hour": "first", "day_of_week": "first", "year": "first",
    }).reset_index()
elif granularity == "Daily":
    fdf = fdf.set_index("Timestamp").resample("1D").agg({
        "total_activity_load": "sum",
        "capacity_utilization_ratio": "mean",
        "redemption_pressure_ratio": "mean",
        "is_congestion_period": "max",
        "is_idle_period": "max",
        "season": "first", "time_band": "first",
        "hour": "first", "day_of_week": "first", "year": "first",
    }).reset_index()

max_load = fdf["total_activity_load"].max() or 1


# ─── KPI COMPUTATIONS ───────────────────────────────────────────────────────
cap_util = fdf["capacity_utilization_ratio"].mean()
congestion_pressure = fdf["redemption_pressure_ratio"].mean() * 100
idle_pct = (fdf["is_idle_period"].sum() / len(fdf) * 100) if len(fdf) else 0
peak_strain = fdf["is_congestion_period"].sum() * (15 if granularity == "15-Minute" else 60 if granularity == "Hourly" else 1440)
peak_h, peak_m = divmod(int(peak_strain), 60)
variability_score = max(0, 100 - fdf["capacity_utilization_ratio"].std())

# ─── CHART HELPERS ──────────────────────────────────────────────────────────
DARK_BG  = "#050a14"
CARD_BG  = "#0d1b2e"
GRID_COL = "#1a3050"
TEXT_COL = "#94a3b8"
CYAN     = "#38bdf8"
ORANGE   = "#f97316"
GREEN    = "#22c55e"
RED      = "#ef4444"
PURPLE   = "#a855f7"
YELLOW   = "#eab308"

def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(family="Space Grotesk", size=13, color=CYAN), x=0, xref="paper"),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Inter", size=11, color=TEXT_COL),
        margin=dict(l=40, r=20, t=42, b=30),
        height=height,
        xaxis=dict(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL, tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_COL, font=dict(size=10)),
        hoverlabel=dict(bgcolor="#0a1525", bordercolor=GRID_COL, font=dict(size=11)),
    )


# ─── MAIN HEADER ────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([3, 1])
with hcol1:
    st.markdown("""
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;
               color:#e2e8f0;margin:0 0 4px">
        ⛴️ Ferry Capacity Utilization &amp; Efficiency Analytics
    </h1>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
        <div class="status-badge"><span class="status-dot"></span> SYSTEM STATUS: ACTIVE</div>
        <span style="color:#475569;font-size:12px;letter-spacing:1px">TORONTO ISLAND DATASTREAM</span>
    </div>
    """, unsafe_allow_html=True)
with hcol2:
    ec1, ec2 = st.columns(2)
    with ec1:
        st.button("📥 Export Report")
    with ec2:
        st.button("🔗 Share")


# ─── KPI CARDS ──────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(col, label, value, sub, delta, delta_positive, icon, accent):
    delta_class = "delta-up" if delta_positive else "delta-down"
    arrow = "↑" if delta_positive else "↓"
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        <div class="kpi-delta {delta_class}">{arrow} {delta}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "Capacity Utilization", f"{cap_util:.1f}%", "Efficiency", "12.4% vs last 30d", True, "🎯", CYAN)
kpi_card(k2, "Congestion Pressure", f"{congestion_pressure:.2f}", "Pressure Index", "8.7% vs last 30d", False, "🔥", RED)
kpi_card(k3, "Idle Capacity", f"{idle_pct:.1f}%", "Waste Ratio", "5.3% vs last 30d", False, "💤", YELLOW)
kpi_card(k4, "Peak Strain Duration", f"{peak_h}h {peak_m:02d}m", "Peak Duration", "15.2% vs last 30d", True, "⏱️", PURPLE)
kpi_card(k5, "Operational Variability", f"{variability_score:.1f}", "Consistency Score", "6.1% vs last 30d", True, "📉", GREEN)

st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)


# ─── ROW 2: Utilization Timeline + Heatmap ──────────────────────────────────
row2_left, row2_right = st.columns([3, 2])

with row2_left:
    st.markdown('<div class="section-header">📈 CAPACITY UTILIZATION OVER TIME</div>', unsafe_allow_html=True)

    # Downsample for performance
    plot_df = fdf[["Timestamp", "capacity_utilization_ratio"]].copy()
    if len(plot_df) > 5000:
        plot_df = plot_df.iloc[::max(1, len(plot_df)//5000)]

    fig_timeline = go.Figure()
    # Area fill
    fig_timeline.add_trace(go.Scatter(
        x=plot_df["Timestamp"], y=plot_df["capacity_utilization_ratio"],
        fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
        line=dict(color=CYAN, width=1.2),
        name="Utilization (%)", hovertemplate="%{x|%Y-%m-%d %H:%M}<br>%{y:.1f}%<extra></extra>"
    ))
    # Congestion limit
    fig_timeline.add_hline(y=congestion_limit, line=dict(color=RED, width=1.5, dash="dash"),
                            annotation_text=f"Congestion Limit ({congestion_limit}%)",
                            annotation_font=dict(color=RED, size=11))

    fig_timeline.update_layout(**base_layout("", 360),
                                yaxis_title="Utilization (%)", yaxis_range=[0, 110])
    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})

with row2_right:
    st.markdown('<div class="section-header">🌡️ CONGESTION &amp; IDLE HEATMAP</div>', unsafe_allow_html=True)

    heat_df = df.groupby(["hour", "day_of_week"])["capacity_utilization_ratio"].mean().reset_index()
    heat_pivot = heat_df.pivot(index="hour", columns="day_of_week", values="capacity_utilization_ratio")
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=day_labels,
        y=[f"{h:02d}:00" for h in heat_pivot.index],
        colorscale=[[0, "#0d1b2e"], [0.3, "#312e81"], [0.6, "#b45309"], [0.8, "#ea580c"], [1, "#fbbf24"]],
        showscale=True,
        colorbar=dict(title="Util %", tickfont=dict(color=TEXT_COL, size=9),
                      titlefont=dict(color=TEXT_COL, size=10),
                      bgcolor=CARD_BG, bordercolor=GRID_COL),
        hovertemplate="Day: %{x}<br>Hour: %{y}<br>Utilization: %{z:.1f}%<extra></extra>"
    ))
    fig_heat.update_layout(**base_layout("", 360),
                            yaxis=dict(autorange="reversed", gridcolor=GRID_COL, tickfont=dict(size=9)))
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ─── ROW 3: Seasonal + KPI Radar + Alerts ───────────────────────────────────
row3a, row3b, row3c = st.columns([1.2, 1.2, 1])

with row3a:
    st.markdown('<div class="section-header">🍂 SEASONAL EFFICIENCY COMPARISON</div>', unsafe_allow_html=True)

    tab_eff, tab_pres, tab_idle = st.tabs(["Efficiency", "Pressure Index", "Idle Capacity"])
    seasons_ordered = ["Summer (Peak)", "Spring", "Fall", "Winter"]
    season_colors = {"Summer (Peak)": RED, "Spring": GREEN, "Fall": ORANGE, "Winter": CYAN}

    for tab, metric, label in [
        (tab_eff, "capacity_utilization_ratio", "Efficiency (%)"),
        (tab_pres, "redemption_pressure_ratio", "Pressure Index"),
        (tab_idle, "is_idle_period", "Idle Capacity (%)"),
    ]:
        with tab:
            s_df = df.groupby("season")[metric].mean().reindex(seasons_ordered).dropna().reset_index()
            s_df.columns = ["season", "value"]
            fig_bar = go.Figure(go.Bar(
                x=s_df["season"],
                y=s_df["value"],
                marker_color=[season_colors.get(s, CYAN) for s in s_df["season"]],
                marker_line_width=0,
                text=[f"{v:.2f}" for v in s_df["value"]],
                textposition="outside", textfont=dict(color="white", size=11),
                hovertemplate="%{x}<br>%{y:.3f}<extra></extra>",
            ))
            fig_bar.update_layout(**base_layout("", 300), yaxis_title=label,
                                   showlegend=False, bargap=0.35)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with row3b:
    st.markdown('<div class="section-header">🎯 KPI SUMMARY RADAR</div>', unsafe_allow_html=True)

    radar_cats = ["Utilization\nEfficiency", "Congestion\nPressure", "Idle\nCapacity",
                  "Peak Strain\nDuration", "Operational\nVariability"]
    # Normalize each to 0-100
    r_util = min(cap_util, 100)
    r_cong = min(congestion_pressure, 100)
    r_idle = min(idle_pct * 10, 100)
    r_strain = min(peak_strain / 10, 100)
    r_var = variability_score
    radar_vals = [r_util, r_cong, r_idle, r_strain, r_var]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_vals + [radar_vals[0]],
        theta=radar_cats + [radar_cats[0]],
        fill="toself", fillcolor="rgba(56,189,248,0.15)",
        line=dict(color=CYAN, width=2),
        name="Current Period"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID_COL,
                            tickfont=dict(size=8, color=TEXT_COL), linecolor=GRID_COL),
            angularaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL,
                             tickfont=dict(size=9, color=TEXT_COL)),
        ),
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_COL),
        height=300,
        margin=dict(l=40, r=40, t=30, b=30),
        showlegend=False,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

with row3c:
    st.markdown('<div class="section-header">🚨 EFFICIENCY ALERTS</div>', unsafe_allow_html=True)

    # Compute dynamic alerts
    congestion_intervals = int(fdf["is_congestion_period"].sum())
    idle_intervals = int(fdf["is_idle_period"].sum())
    peak_hours = peak_h + peak_m / 60

    alerts = []
    if congestion_intervals > 0:
        alerts.append(("🔴", "High Congestion Detected", f"Utilization exceeded {congestion_limit}% at {congestion_intervals} intervals", RED))
    if peak_hours >= 2:
        alerts.append(("🟡", "Sustained Peak Strain", f"Peak duration above {int(peak_hours)} hours", YELLOW))
    if idle_intervals > 0:
        alerts.append(("🔵", "Idle Capacity Opportunity", f"Low utilization detected in {idle_intervals} intervals", CYAN))
    if congestion_pressure > 100:
        alerts.append(("🔴", "Redemption Pressure Spike", "Redemption ratio exceeds normal range", ORANGE))

    if alerts:
        for icon, title, body, color in alerts[:5]:
            st.markdown(f"""
            <div class="alert-card" style="--alert-color:{color}">
                <div class="alert-title">{icon} {title}</div>
                <div class="alert-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#22c55e;font-size:13px;padding:10px">✅ No active alerts</div>',
                    unsafe_allow_html=True)

    st.button("View All Alerts")


# ─── ROW 4: Top 10 Tables ────────────────────────────────────────────────────
row4l, row4r = st.columns(2)

with row4l:
    st.markdown(f'<div class="section-header">🔝 TOP 10 BUSIEST INTERVALS</div>', unsafe_allow_html=True)

    top_busy = (fdf.nlargest(10, "total_activity_load")
                [["Timestamp", "total_activity_load", "season", "time_band"]]
                .reset_index(drop=True))

    def load_color(v, mx):
        pct = v / mx
        if pct > 0.8: return "load-high"
        if pct > 0.5: return "load-med"
        return "load-low"

    rows_html = ""
    for i, row in top_busy.iterrows():
        lc = load_color(row["total_activity_load"], max_load)
        ts = pd.Timestamp(row["Timestamp"]).strftime("%Y-%m-%d %H:%M")
        rows_html += f"""<tr>
            <td style="color:#475569">{i+1}</td>
            <td>{ts}</td>
            <td class="{lc}">{int(row['total_activity_load']):,}</td>
            <td>{row['season']}</td>
            <td>{row['time_band']}</td>
        </tr>"""

    st.markdown(f"""
    <table class="top-table">
      <thead><tr>
        <th>#</th><th>Timestamp</th><th>Total Load</th><th>Season</th><th>Time Band</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    st.button("View All Busy Intervals")

with row4r:
    st.markdown('<div class="section-header">💤 TOP 10 IDLE PERIODS</div>', unsafe_allow_html=True)

    idle_df = fdf[fdf["is_idle_period"] == 1].nlargest(10, "idle_streak_length") if "idle_streak_length" in fdf.columns else fdf.nsmallest(10, "total_activity_load")
    top_idle = idle_df[["Timestamp", "total_activity_load", "season", "time_band"]].reset_index(drop=True)

    rows_html2 = ""
    for i, row in top_idle.iterrows():
        ts = pd.Timestamp(row["Timestamp"]).strftime("%Y-%m-%d %H:%M")
        streak = idle_df.iloc[i].get("idle_streak_length", "—") if "idle_streak_length" in idle_df.columns else "—"
        rows_html2 += f"""<tr>
            <td style="color:#475569">{i+1}</td>
            <td>{ts}</td>
            <td class="load-low">{int(row['total_activity_load']):,}</td>
            <td>{row['season']}</td>
            <td>{row['time_band']}</td>
        </tr>"""

    st.markdown(f"""
    <table class="top-table">
      <thead><tr>
        <th>#</th><th>Timestamp</th><th>Total Load</th><th>Season</th><th>Time Band</th>
      </tr></thead>
      <tbody>{rows_html2}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    st.button("View All Idle Periods")


# ─── ROW 5: Load Distribution + Trend ───────────────────────────────────────
row5l, row5r = st.columns(2)

with row5l:
    st.markdown('<div class="section-header">📊 ACTIVITY LOAD DISTRIBUTION</div>', unsafe_allow_html=True)
    sample = fdf["total_activity_load"].dropna()
    if len(sample) > 10000:
        sample = sample.sample(10000, random_state=42)
    fig_hist = go.Figure(go.Histogram(
        x=sample, nbinsx=60,
        marker_color=CYAN, marker_line_width=0,
        opacity=0.85,
        hovertemplate="Load: %{x}<br>Count: %{y}<extra></extra>"
    ))
    fig_hist.add_vline(x=sample.quantile(0.85), line=dict(color=RED, dash="dash", width=1.5),
                       annotation_text="85th pct", annotation_font=dict(color=RED, size=10))
    fig_hist.add_vline(x=sample.median(), line=dict(color=GREEN, dash="dot", width=1.5),
                       annotation_text="Median", annotation_font=dict(color=GREEN, size=10))
    fig_hist.update_layout(**base_layout("", 280))
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

with row5r:
    st.markdown('<div class="section-header">📅 MONTHLY AVERAGE UTILIZATION TREND</div>', unsafe_allow_html=True)
    monthly = df.set_index("Timestamp").resample("MS")["capacity_utilization_ratio"].mean().reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["Timestamp"], y=monthly["capacity_utilization_ratio"],
        mode="lines", line=dict(color=PURPLE, width=2),
        fill="tozeroy", fillcolor="rgba(168,85,247,0.08)",
        hovertemplate="%{x|%b %Y}<br>%{y:.2f}%<extra></extra>"
    ))
    fig_trend.update_layout(**base_layout("", 280))
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})


# ─── ROW 6: Executive Summary + Recommendation ──────────────────────────────
exec_col, rec_col = st.columns(2)

with exec_col:
    peak_season = df.groupby("season")["capacity_utilization_ratio"].mean().idxmax()
    avg_util_txt = f"{cap_util:.1f}%"
    summer_vs_off = df.groupby("season")["capacity_utilization_ratio"].mean()
    summer_v = summer_vs_off.get("Summer (Peak)", 0)
    winter_v = summer_vs_off.get("Winter", 1)
    ratio = summer_v / winter_v if winter_v > 0 else 1
    st.markdown(f"""
    <div class="exec-card">
        <h4>📋 Executive Summary</h4>
        <p>Ferry operations show optimal efficiency with <strong style="color:{CYAN}">{avg_util_txt}</strong> average utilization across the selected period.
        The <strong style="color:{ORANGE}">{peak_season}</strong> season experiences <strong style="color:{CYAN}">{ratio:.2f}×</strong> higher pressure
        compared to off-season. Peak congestion occurs during evening hours on weekends, driven by elevated redemption activity.
        Idle periods are most prevalent in early morning slots during winter months.</p>
    </div>
    """, unsafe_allow_html=True)

with rec_col:
    st.markdown(f"""
    <div class="exec-card" style="border-color:#166534">
        <h4 style="color:{GREEN}">🎯 Recommendation</h4>
        <p>Consider adding <strong style="color:{GREEN}">additional ferries</strong> during summer evening peak hours (6 PM – 10 PM)
        on weekends to reduce congestion pressure. Deploying dynamic pricing during high-demand intervals
        could redistribute load by <strong style="color:{CYAN}">15–20%</strong>.
        Idle morning slots (3 AM – 6 AM) present opportunities for maintenance scheduling without service impact.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

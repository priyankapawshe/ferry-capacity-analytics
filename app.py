
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ferry Capacity Analytics", layout="wide")

# -------------------- DARK THEME --------------------
st.markdown("""
<style>
.stApp {background-color:#07111f;color:white;}
.kpi-card{
background:#0f1d31;padding:18px;border-radius:15px;
border:1px solid #1d3557;text-align:center;
}
.kpi-title{color:#7dd3fc;font-size:14px;}
.kpi-value{font-size:34px;font-weight:bold;color:white;}
.alert-box{
padding:10px;border-radius:10px;margin-bottom:8px;
background:#12243d;border-left:5px solid #ff4d4d;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("fairy_project_feature_engineering.csv.gz")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

df = load_data()

# -------------------- SIDEBAR --------------------
st.sidebar.title("🚢 Control Center")

min_date = df["Timestamp"].min().date()
max_date = df["Timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date)
)

seasons = st.sidebar.multiselect(
    "Season",
    options=df["season"].unique(),
    default=list(df["season"].unique())
)

granularity = st.sidebar.radio(
    "Granularity",
    ["15-Minute","Hourly","Daily"]
)

threshold = st.sidebar.slider(
    "Congestion Limit (%)",
    50,100,75
)

# -------------------- FILTER --------------------
if len(date_range)==2:
    start_date,end_date = date_range
else:
    start_date,end_date = min_date,max_date

filtered_df = df[
    (df["Timestamp"].dt.date >= start_date) &
    (df["Timestamp"].dt.date <= end_date) &
    (df["season"].isin(seasons))
].copy()

# -------------------- KPIs --------------------
kpi_capacity = filtered_df["capacity_utilization_ratio"].mean()*100
kpi_pressure = filtered_df["redemption_pressure_ratio"].mean()
kpi_idle = filtered_df["is_idle_period"].mean()*100
kpi_peak = filtered_df["congestion_streak_length"].max()*15
kpi_var = filtered_df["total_activity_load"].std()/max(filtered_df["total_activity_load"].mean(),1)

st.title("🚢 Ferry Capacity Utilization & Efficiency Analytics")
st.caption("Toronto Island Ferry Operations Dashboard")

c1,c2,c3,c4,c5 = st.columns(5)

cards = [
("Capacity Utilization",f"{kpi_capacity:.1f}%"),
("Congestion Pressure",f"{kpi_pressure:.2f}"),
("Idle Capacity",f"{kpi_idle:.1f}%"),
("Peak Strain",f"{kpi_peak:.0f} min"),
("Operational Variability",f"{kpi_var:.2f}")
]

for col,(title,val) in zip([c1,c2,c3,c4,c5],cards):
    col.markdown(f"""
    <div class='kpi-card'>
    <div class='kpi-title'>{title}</div>
    <div class='kpi-value'>{val}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------- TIMELINE --------------------
left,right = st.columns([2,1])

with left:
    st.subheader("Capacity Utilization Timeline")

    if granularity=="Hourly":
        chart_df = filtered_df.set_index("Timestamp").resample("H")["capacity_utilization_ratio"].mean().reset_index()
    elif granularity=="Daily":
        chart_df = filtered_df.set_index("Timestamp").resample("D")["capacity_utilization_ratio"].mean().reset_index()
    else:
        chart_df = filtered_df[["Timestamp","capacity_utilization_ratio"]]

    fig = px.line(
        chart_df,
        x="Timestamp",
        y="capacity_utilization_ratio",
        template="plotly_dark"
    )

    fig.add_hline(
        y=threshold/100,
        line_dash="dash",
        annotation_text=f"Congestion Limit {threshold}%"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Congestion Heatmap")

    heat = filtered_df.pivot_table(
        index="hour",
        columns="day_of_week",
        values="capacity_utilization_ratio",
        aggfunc="mean"
    )

    fig2 = px.imshow(
        heat,
        template="plotly_dark",
        color_continuous_scale="Turbo",
        aspect="auto"
    )

    st.plotly_chart(fig2, use_container_width=True)

# -------------------- SEASON COMPARISON --------------------
c1,c2 = st.columns(2)

with c1:
    st.subheader("Seasonal Efficiency Comparison")

    season_df = filtered_df.groupby("season").agg({
        "capacity_utilization_ratio":"mean",
        "redemption_pressure_ratio":"mean",
        "is_idle_period":"mean"
    }).reset_index()

    fig3 = px.bar(
        season_df,
        x="season",
        y="capacity_utilization_ratio",
        color="season",
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

with c2:
    st.subheader("KPI Radar View")

    radar = go.Figure()

    radar.add_trace(go.Scatterpolar(
        r=[
            min(kpi_capacity,100),
            min(kpi_pressure*50,100),
            min(kpi_idle,100),
            min(kpi_peak/5,100),
            min(kpi_var*100,100)
        ],
        theta=[
            "Utilization",
            "Pressure",
            "Idle",
            "Peak Strain",
            "Variability"
        ],
        fill="toself"
    ))

    radar.update_layout(template="plotly_dark")
    st.plotly_chart(radar,use_container_width=True)

# -------------------- ALERTS --------------------
st.subheader("🚨 Efficiency Alerts")

if (filtered_df["capacity_utilization_ratio"] > threshold/100).sum() > 0:
    st.markdown("<div class='alert-box'>High Congestion Detected</div>", unsafe_allow_html=True)

if kpi_peak > 120:
    st.markdown("<div class='alert-box'>Sustained Peak Strain</div>", unsafe_allow_html=True)

if kpi_idle > 20:
    st.markdown("<div class='alert-box'>Excess Idle Capacity</div>", unsafe_allow_html=True)

# -------------------- TABLES --------------------
a,b = st.columns(2)

with a:
    st.subheader("Top 10 Busiest Intervals")

    busy = filtered_df.sort_values(
        "total_activity_load",
        ascending=False
    ).head(10)

    st.dataframe(
        busy[[
            "Timestamp",
            "total_activity_load",
            "season",
            "time_band"
        ]],
        use_container_width=True
    )

with b:
    st.subheader("Top 10 Idle Periods")

    idle = filtered_df.sort_values(
        "idle_streak_length",
        ascending=False
    ).head(10)

    st.dataframe(
        idle[[
            "Timestamp",
            "idle_streak_length",
            "season",
            "time_band"
        ]],
        use_container_width=True
    )

# -------------------- SUMMARY --------------------
st.subheader("📋 Executive Summary")

st.info(
f"""
Average utilization is {kpi_capacity:.1f}%.
Peak congestion duration reached {kpi_peak:.0f} minutes.
Operational variability score is {kpi_var:.2f}.
"""
)

csv = filtered_df.to_csv(index=False)

st.download_button(
    "📥 Download Filtered Data",
    csv,
    file_name="filtered_ferry_data.csv",
    mime="text/csv"
)

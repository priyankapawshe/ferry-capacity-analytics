import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------
# PAGE SETUP - this just controls the browser tab title/layout
# -----------------------------------------------------------
st.set_page_config(page_title="Ferry Capacity Dashboard", layout="wide")


# -----------------------------------------------------------
# STEP 1: LOAD THE DATA
# -----------------------------------------------------------
# @st.cache_data means: "only reload the file if it actually
# changes" - this makes the app much faster when you click
# filters, because it won't re-read the CSV every single time.

@st.cache_data
def load_data():
    df = pd.read_csv("features_15min.csv")   # <- change path if needed
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

df = load_data()


# -----------------------------------------------------------
# STEP 2: SIDEBAR FILTERS
# -----------------------------------------------------------
# Everything in st.sidebar shows up in the left-side panel.

st.sidebar.title("Filters")

# Date range filter
min_date = df["Timestamp"].min().date()
max_date = df["Timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Season filter (multi-select checkboxes)
season_options = df["season"].unique().tolist()
selected_seasons = st.sidebar.multiselect(
    "Select season(s)",
    options=season_options,
    default=season_options   # default = all selected
)

# Granularity choice (15-min / hourly / daily)
granularity = st.sidebar.radio(
    "View data at this level:",
    ["15-Minute (raw)", "Hourly", "Daily"]
)


# -----------------------------------------------------------
# STEP 3: APPLY THE FILTERS
# -----------------------------------------------------------
# This is just narrowing df down to only the rows the user wants

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df["Timestamp"].dt.date >= start_date) &
    (df["Timestamp"].dt.date <= end_date) &
    (df["season"].isin(selected_seasons))
].copy()

if filtered_df.empty:
    st.warning("No data matches your filters. Try widening the date range.")
    st.stop()


# -----------------------------------------------------------
# STEP 4: RESAMPLE TO CHOSEN GRANULARITY
# -----------------------------------------------------------
# If the user picked "Hourly" or "Daily", we group the 15-min
# rows together using the same .resample() trick from Script 3.

if granularity == "Hourly":
    chart_df = filtered_df.set_index("Timestamp").resample("h")["total_activity_load"].sum().reset_index()
elif granularity == "Daily":
    chart_df = filtered_df.set_index("Timestamp").resample("D")["total_activity_load"].sum().reset_index()
else:
    chart_df = filtered_df[["Timestamp", "total_activity_load"]].copy()


# -----------------------------------------------------------
# STEP 5: TITLE + KPI CARDS AT THE TOP
# -----------------------------------------------------------
st.title("⛴️ Ferry Capacity Utilization & Operational Efficiency Dashboard")
st.caption("Jack Layton Ferry Terminal — Toronto Island Ferries")

# Calculate the same 5 KPIs from Script 3, but now on the FILTERED data
kpi_capacity = filtered_df["capacity_utilization_ratio"].mean()
kpi_congestion_pct = 100 * filtered_df["is_congestion_period"].sum() / len(filtered_df)
kpi_idle_pct = 100 * filtered_df["is_idle_period"].sum() / len(filtered_df)
kpi_peak_strain = filtered_df["congestion_streak_length"].max() * 15   # minutes
kpi_variability = filtered_df["total_activity_load"].std() / filtered_df["total_activity_load"].mean()

# st.columns() puts things side-by-side instead of stacked
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Capacity Utilization", f"{kpi_capacity:.1%}")
col2.metric("Congestion %", f"{kpi_congestion_pct:.2f}%")
col3.metric("Idle %", f"{kpi_idle_pct:.2f}%")
col4.metric("Peak Strain", f"{kpi_peak_strain:.0f} min")
col5.metric("Variability Score", f"{kpi_variability:.2f}")

st.divider()


# -----------------------------------------------------------
# STEP 6: TABS - lets us organize charts into separate pages
# -----------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Activity Timeline", "🔥 Heatmaps", "🌦️ Seasonal Comparison"])

# ---- TAB 1: TIMELINE CHART ----
with tab1:
    st.subheader("Total Activity Load Over Time")

    fig = px.line(chart_df, x="Timestamp", y="total_activity_load")
    fig.update_layout(height=450, xaxis_title="Time", yaxis_title="Sales + Redemptions")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Busiest Intervals (in current filter)")
    top_busy = filtered_df.sort_values("total_activity_load", ascending=False).head(10)
    st.dataframe(
        top_busy[["Timestamp", "total_activity_load", "season", "time_band"]],
        use_container_width=True
    )

    st.subheader("Top 10 Idle Periods (in current filter)")
    top_idle = filtered_df[filtered_df["is_idle_period"]].sort_values("idle_streak_length", ascending=False).head(10)
    st.dataframe(
        top_idle[["Timestamp", "total_activity_load", "idle_streak_length", "season", "time_band"]],
        use_container_width=True
    )

# ---- TAB 2: HEATMAPS ----
with tab2:
    st.subheader("Average Activity: Hour of Day vs Day of Week")

    heatmap_data = filtered_df.pivot_table(
        index="hour", columns="day_of_week", values="total_activity_load", aggfunc="mean"
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data = heatmap_data[[d for d in day_order if d in heatmap_data.columns]]

    fig2 = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(x="Day of Week", y="Hour", color="Avg Activity")
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---- TAB 3: SEASONAL COMPARISON ----
with tab3:
    st.subheader("Weekday vs Weekend")
    weekday_weekend = filtered_df.groupby("is_weekend")["total_activity_load"].mean().reset_index()
    weekday_weekend["is_weekend"] = weekday_weekend["is_weekend"].map({True: "Weekend", False: "Weekday"})
    fig3 = px.bar(weekday_weekend, x="is_weekend", y="total_activity_load", color="is_weekend")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Seasonal Comparison")
    seasonal = filtered_df.groupby("season")["total_activity_load"].mean().reset_index()
    fig4 = px.bar(seasonal, x="season", y="total_activity_load", color="season")
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Time of Day Comparison")
    time_band_order = ["Morning", "Afternoon", "Evening", "Night/Off-hours"]
    time_band = filtered_df.groupby("time_band")["total_activity_load"].mean().reindex(time_band_order).reset_index()
    fig5 = px.bar(time_band, x="time_band", y="total_activity_load", color="time_band")
    st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("Data: Toronto Island Ferry Ticket Counts (2015-2025) | Capacity assumption: 1,000 ticket events per 15-min interval (see research paper, Section 3.3)")

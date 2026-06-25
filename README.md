# Ferry Capacity Utilization & Operational Efficiency Analytics

An operational analytics project analyzing 10 years (2015–2025) of ticket sales
and redemption data from the Jack Layton Ferry Terminal (Toronto Island Ferries),
built during a Data Science & Analytics internship at Unified Mentor in
partnership with Toronto Government Parks, Forestry & Recreation.

![image alt](https://github.com/priyankapawshe/ferry-capacity-analytics/blob/7b9d9f49a45e32d1e95403bf67c71716f1cf713d/Screenshot%202026-06-25%20195707.png)

![image alt]()

![image alt]()


## 🔗 Live Dashboard

[View the live Streamlit dashboard](#) <!https://fairy-capacity-analytics.streamlit.app/>

## 📌 Project Overview

This project measures how efficiently ferry capacity is utilized — identifying
congestion-prone and idle-capacity periods — to support evidence-based
operational planning. It is intentionally focused on **operational efficiency**,
not demand forecasting.

## 📁 Files in this repo

| File | Description |
|---|---|
| `app.py` | Streamlit dashboard — interactive KPIs, timeline, heatmaps, seasonal comparison |
| `features_15min.csv` | Cleaned and feature-engineered dataset used by the dashboard |
| `requirements.txt` | Python packages needed to run the app |

## 📊 Key Findings

- **94.3%** of all sustained high-congestion events occur during summer months
  (June–September), despite summer making up only **34.6%** of all operating days
- The longest single sustained congestion event in 10 years lasted **~13 hours**,
  on Canada Day (July 1, 2018)
- Summer weekdays (52.9%) contribute slightly *more* high-congestion days than
  summer weekends (41.4%) — congestion is driven by season, not day of week
- Only **0.46%** of intervals show sustained idle capacity, suggesting limited
  over-provisioning during active service hours

## 🧮 Methodology Summary

1. **Data Cleaning** — timestamp parsing, duplicate/negative value checks,
   gap inspection within active service days
2. **Feature Engineering** — Total Activity Load, Redemption Pressure Ratio,
   Capacity Utilization Ratio, Operational Load Index (OLI), idle/congestion
   streak detection, calendar features (season, time-of-day band, weekday/weekend)
3. **KPIs** — Capacity Utilization Ratio, Congestion Pressure Index, Idle
   Capacity %, Peak Strain Duration, Operational Variability Score
4. **Dashboard** — interactive filters (date range, season, granularity) with
   live-updating KPIs and charts

> **Note:** Vessel-level capacity data was not available in the source dataset.
> An assumed capacity of 1,000 ticket events per 15-minute interval was used,
> calibrated against the 99th percentile of observed activity (962). See the
> full research paper for details.

## 🚀 Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📄 Related Deliverables

- Research Paper (EDA, methodology, findings, recommendations)
- Executive Summary (for government stakeholders)

## 👤 Author

Priyanka — Data Science & Analytics Intern, Unified Mentor

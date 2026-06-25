import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Toronto Ferry Analytics", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
.stApp{background:#08111f;color:white;}
section[data-testid="stSidebar"]{background:#111827;}
.card{
background:#10203a;
padding:18px;
border-radius:16px;
border:1px solid #1f3b63;
box-shadow:0 0 10px rgba(0,0,0,.3);
}
.kpi{
background:#10203a;
padding:20px;
border-radius:16px;
border-top:4px solid #29b6f6;
text-align:center;
height:140px;
}
.kpi h3{font-size:15px;color:#7dd3fc;}
.kpi h1{font-size:42px;color:white;}
.title{
font-size:52px;
font-weight:800;
}
.sub{
color:#94a3b8;
}
.alert{
background:#13253f;
padding:12px;
border-left:5px solid #ff5a5a;
border-radius:10px;
margin-bottom:10px;
}
.reco{
background:#0f2d28;
padding:15px;
border-radius:12px;
border-left:5px solid #10b981;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    df=pd.read_csv("fairy_project_feature_engineering.csv.gz")
    df["Timestamp"]=pd.to_datetime(df["Timestamp"])
    return df

df=load()

st.sidebar.markdown("# 🚢 Control Center")
d1=df["Timestamp"].min().date()
d2=df["Timestamp"].max().date()

dates=st.sidebar.date_input("Date Range",(d1,d2))
seasons=st.sidebar.multiselect("Seasons",df["season"].unique(),default=list(df["season"].unique()))
gran=st.sidebar.radio("Time Granularity",["15-Minute","Hourly","Daily"])
limit=st.sidebar.slider("Congestion Threshold (%)",50,100,75)

if len(dates)==2:
    s,e=dates
else:
    s,e=d1,d2

f=df[(df["Timestamp"].dt.date>=s)&(df["Timestamp"].dt.date<=e)&(df["season"].isin(seasons))].copy()

st.markdown('<div class="title">🚢 Ferry Capacity Utilization & Efficiency Analytics</div>',unsafe_allow_html=True)
st.markdown('<div class="sub">Real-time monitoring and analytics of Toronto Island Ferry operations</div><br>',unsafe_allow_html=True)

util=f["capacity_utilization_ratio"].mean()*100
pressure=f["redemption_pressure_ratio"].mean()
idle=f["is_idle_period"].mean()*100
peak=f["congestion_streak_length"].max()*15
var=f["total_activity_load"].std()/max(f["total_activity_load"].mean(),1)

c1,c2,c3,c4,c5=st.columns(5)
vals=[("CAPACITY UTILIZATION",f"{util:.1f}%"),
("CONGESTION PRESSURE",f"{pressure:.2f}"),
("IDLE CAPACITY",f"{idle:.1f}%"),
("PEAK STRAIN DURATION",f"{peak:.0f}m"),
("OPERATIONAL VARIABILITY",f"{var:.2f}")]

for c,v in zip([c1,c2,c3,c4,c5],vals):
    with c:
        st.markdown(f'<div class="kpi"><h3>{v[0]}</h3><h1>{v[1]}</h1></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

left,right=st.columns([2,1])

with left:
    st.markdown("## CAPACITY UTILIZATION OVER TIME")
    if gran=="Hourly":
        chart=f.set_index("Timestamp").resample("h")["capacity_utilization_ratio"].mean().reset_index()
    elif gran=="Daily":
        chart=f.set_index("Timestamp").resample("D")["capacity_utilization_ratio"].mean().reset_index()
    else:
        chart=f[["Timestamp","capacity_utilization_ratio"]]

    fig=px.line(chart,x="Timestamp",y="capacity_utilization_ratio",template="plotly_dark")
    fig.add_hline(y=limit/100,line_dash="dash",line_color="red")
    fig.update_layout(height=420,paper_bgcolor="#08111f",plot_bgcolor="#08111f")
    st.plotly_chart(fig,use_container_width=True)

with right:
    st.markdown("## CONGESTION HEATMAP")
    heat=f.pivot_table(index="hour",columns="day_of_week",values="capacity_utilization_ratio",aggfunc="mean")
    fig2=px.imshow(heat,color_continuous_scale="Plasma",template="plotly_dark",aspect="auto")
    fig2.update_layout(height=420,paper_bgcolor="#08111f",plot_bgcolor="#08111f")
    st.plotly_chart(fig2,use_container_width=True)

a,b,c=st.columns([1.2,1,1])

with a:
    st.markdown("## SEASONAL EFFICIENCY COMPARISON")
    season=f.groupby("season")["capacity_utilization_ratio"].mean().reset_index()
    fig3=px.bar(season,x="season",y="capacity_utilization_ratio",color="season",template="plotly_dark")
    st.plotly_chart(fig3,use_container_width=True)

with b:
    st.markdown("## KPI RADAR VIEW")
    radar=go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=[min(util,100),min(pressure*50,100),min(idle,100),min(peak/5,100),min(var*50,100)],
        theta=["Utilization","Pressure","Idle","Peak","Variability"],
        fill="toself"))
    radar.update_layout(template="plotly_dark",height=380,paper_bgcolor="#08111f")
    st.plotly_chart(radar,use_container_width=True)

with c:
    st.markdown("## EFFICIENCY ALERTS")
    if (f["capacity_utilization_ratio"]>limit/100).sum()>0:
        st.markdown('<div class="alert">🚨 High Congestion Detected</div>',unsafe_allow_html=True)
    if peak>120:
        st.markdown('<div class="alert">⚠ Sustained Peak Strain</div>',unsafe_allow_html=True)
    if idle>5:
        st.markdown('<div class="alert">ℹ Idle Capacity Opportunity</div>',unsafe_allow_html=True)

l,r=st.columns(2)

with l:
    st.markdown("## TOP 10 BUSIEST INTERVALS")
    busy=f.sort_values("total_activity_load",ascending=False).head(10)
    st.dataframe(busy[["Timestamp","total_activity_load","season","time_band"]],use_container_width=True)

with r:
    st.markdown("## TOP 10 IDLE PERIODS")
    idle_df=f.sort_values("idle_streak_length",ascending=False).head(10)
    st.dataframe(idle_df[["Timestamp","idle_streak_length","season","time_band"]],use_container_width=True)

x,y=st.columns([2,1])
with x:
    st.markdown("## EXECUTIVE SUMMARY")
    st.markdown(f'<div class="card">Average utilization is <b>{util:.1f}%</b>. Peak congestion duration reached <b>{peak:.0f} minutes</b>. Operational variability score is <b>{var:.2f}</b>.</div>',unsafe_allow_html=True)

with y:
    st.markdown("## RECOMMENDATION")
    st.markdown('<div class="reco">Consider additional ferry capacity during summer evening peaks and weekends to reduce congestion.</div>',unsafe_allow_html=True)

csv=f.to_csv(index=False)
st.download_button("📥 Export Report Data",csv,"ferry_report.csv","text/csv")

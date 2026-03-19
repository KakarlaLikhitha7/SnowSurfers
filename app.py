# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import streamlit as st
from snowflake.snowpark.context import get_active_session

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="CityRide Dashboard", layout="wide")

st.title("🚴 CityRide Smart Analytics Dashboard")

# Snowflake session
session = get_active_session()

# Helper function
def run_query(query):
    return session.sql(query).to_pandas()
# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

# KPI 1: Anomaly Rate
anomaly_df = run_query("SELECT anomaly_percentage FROM GOLD.anomaly_kpi")
col1.metric("⚠️ Anomaly Rate (%)", f"{anomaly_df.iloc[0,0]:.2f}%")

# KPI 2: Fleet Health
fleet_df = run_query("SELECT health_score FROM GOLD.fleet_health")
col2.metric("🔋 Fleet Health (%)", f"{fleet_df.iloc[0,0]:.2f}%")

# KPI 3: Engagement Ratio
eng_df = run_query("SELECT engagement_ratio FROM GOLD.active_riders")
col3.metric("👥 Engagement (%)", f"{eng_df.iloc[0,0]:.2f}%")

st.divider()

# -------------------------------------------------
# FILTER SECTION (SIDEBAR)
# -------------------------------------------------
st.sidebar.header("🎯 Filters")

channel = st.sidebar.selectbox(
    "Select Channel",
    ["All", "app", "kiosk", "corporate"]
)

# -------------------------------------------------
# REVENUE ANALYSIS
# -------------------------------------------------
st.subheader("💰 Revenue by Channel")

if channel == "All":
    revenue_query = "SELECT channel, avg_revenue FROM GOLD.revenue_kpi"
else:
    revenue_query = f"""
        SELECT channel, avg_revenue 
        FROM GOLD.revenue_kpi
        WHERE channel = '{channel}'
    """

revenue_df = run_query(revenue_query)

colA, colB = st.columns(2)

with colA:
    st.write("### 📊 Bar Chart")
    st.bar_chart(revenue_df, x="CHANNEL", y="AVG_REVENUE")

with colB:
    st.write("### 📈 Line Trend")
    st.line_chart(revenue_df.set_index("CHANNEL"))

st.divider()

# -------------------------------------------------
# STATION AVAILABILITY
# -------------------------------------------------
st.subheader("📍 Top Stations by Availability")

station_df = run_query("""
    SELECT station_id, availability_score
    FROM GOLD.station_availability
    ORDER BY availability_score DESC
    LIMIT 10
""")

colC, colD = st.columns(2)

with colC:
    st.bar_chart(station_df, x="STATION_ID", y="AVAILABILITY_SCORE")

with colD:
    st.dataframe(station_df, use_container_width=True)

st.divider()

# -------------------------------------------------
# KPI SUMMARY TABLE
# -------------------------------------------------
st.subheader("📈 KPI Summary Table")

kpi_df = run_query("SELECT * FROM GOLD.kpi_dashboard")
st.dataframe(kpi_df, use_container_width=True)

st.divider()

# -------------------------------------------------
# PIPELINE AUDIT
# -------------------------------------------------
st.subheader("🔍 Pipeline Audit Report")

audit_df = run_query("SELECT * FROM GOLD.pipeline_audit_report")

st.write("### 📊 Records Processed vs Failed")
st.bar_chart(audit_df, x="TABLE_NAME", y="ROW_COUNT")

st.dataframe(audit_df, use_container_width=True)

st.divider()

# -------------------------------------------------
# RENTALS FILTER DATA
# -------------------------------------------------
st.subheader("📦 Rental Records")

if channel == "All":
    query = "SELECT * FROM SILVER.rentals_silver LIMIT 100"
else:
    query = f"""
        SELECT * FROM SILVER.rentals_silver
        WHERE channel = '{channel}'
        LIMIT 100
    """

filtered_df = run_query(query)

st.dataframe(filtered_df, use_container_width=True)

st.divider()

# -------------------------------------------------
# USER ENGAGEMENT TREND (NEW 🔥)
# -------------------------------------------------
st.subheader("👥 Active Users Trend (Last 30 Days)")

users_df = run_query("""
    SELECT 
        DATE(start_time) AS ride_date, 
        COUNT(DISTINCT user_id) AS users
    FROM SILVER.rentals_silver
    WHERE start_time >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
    GROUP BY ride_date
    ORDER BY ride_date
""")

st.line_chart(users_df.set_index("RIDE_DATE"))

st.divider()

# -------------------------------------------------
# REFRESH BUTTON
# -------------------------------------------------
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
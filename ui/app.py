import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from src.config import PlantConfig, AdvancedConfig
from src.data_loader import DataLoader
from src.kpi_engine import KPIEngine
from src.aggregator import HistorianAggregator
from src.intelligence import ProcessIntelligence
from ui.components import render_sidebar_controls


# -------- SETUP & CONFIG --------

st.set_page_config(
    page_title="Project Sevs | Industrial Analytics",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# -------- DATA PIPELINE --------

@st.cache_data
def load_and_process():
    plant_config = PlantConfig()
    adv_config = AdvancedConfig()
    loader = DataLoader("data/mini_hercules_mock_data_hourly.csv")
    raw_df = loader.load_data()
    
    if raw_df is None or raw_df.empty:
        return None, []
        
    engine = KPIEngine(plant_config)
    enriched_df = engine.process(raw_df)
    
    intel = ProcessIntelligence(adv_config)
    intel_df = intel.detect_anomalies(enriched_df)
    alerts = intel.generate_alerts(intel_df)
    
    return intel_df, alerts


# -------- UI HELPERS --------

def create_kpi_card(title, value, unit, accent_class):
    return f"""
    <div class="kpi-card {accent_class}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value} <span class="kpi-unit">{unit}</span></div>
    </div>
    """


# -------- MAIN APPLICATION --------

def main():
    load_css()
    render_sidebar_controls()
    
    st.markdown("<h1 style='color: #E2E8F0; font-weight: 700; letter-spacing: 1px;'>💻 PROJECT SEVS <span style='color: #4A5568;'>// Operations Center</span></h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner("Initializing Pipeline..."):
        df, alerts = load_and_process()
        
    if df is None:
        st.error("System Error: Unable to connect to historian database.")
        return

    latest = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    status_text = "RUNNING" if latest['is_running'] else "IDLE"
    status_accent = "accent-green" if latest['is_running'] else "accent-red"
    
    with col1:
        st.markdown(create_kpi_card("System Status", status_text, "", status_accent), unsafe_allow_html=True)
    with col2:
        st.markdown(create_kpi_card("Throughput", f"{latest['throughput_kgph']:,.0f}", "kg/h", "accent-blue"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_kpi_card("Extraction Yield", f"{latest['extraction_yield_pct']:.1f}", "%", "accent-purple"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_kpi_card("Grinder Temp", f"{latest['grinder_temp_c']:.1f}", "°C", "accent-orange"), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_chart, col_alerts = st.columns([3, 1])
    
    with col_chart:
        st.markdown("<h3 style='color: #A0AEC0;'>Process Telemetry (72 Hrs)</h3>", unsafe_allow_html=True)
        fig = px.line(df, x='timestamp', y='throughput_kgph', template="plotly_dark", color_discrete_sequence=['#10B981'])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="Throughput (kg/h)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_alerts:
        st.markdown("<h3 style='color: #A0AEC0;'>System Alerts</h3>", unsafe_allow_html=True)
        if not alerts:
            st.success("No anomalies detected.")
        else:
            for alert in alerts[:4]:
                st.error(f"**{alert.timestamp.strftime('%H:%M')}**\n\n{alert.message}", icon="⚠️")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #A0AEC0;'>Dynamic Aggregation Report</h3>", unsafe_allow_html=True)
    
    col_freq, col_date = st.columns([1, 2])
    
    with col_freq:
        freq_label = st.selectbox("Aggregation Period", ["Daily", "Weekly", "Monthly"])
        freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
        selected_freq = freq_map[freq_label]
        
    with col_date:
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        date_range = st.date_input("Filter Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        mask = (df['timestamp'].dt.date >= date_range[0]) & (df['timestamp'].dt.date <= date_range[1])
        filtered_df = df.loc[mask].copy()
    elif len(date_range) == 1:
        mask = df['timestamp'].dt.date == date_range[0]
        filtered_df = df.loc[mask].copy()
    else:
        filtered_df = df.copy()

    plant_config = PlantConfig()
    aggregator = HistorianAggregator(plant_config)
    report_df = aggregator.aggregate(filtered_df, selected_freq)

    st.dataframe(report_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
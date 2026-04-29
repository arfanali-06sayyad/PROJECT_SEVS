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
    page_title="Project Sevs | Milling Intelligence Portal",
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
    
    if raw_df is None or raw_df.empty: return None, []
        
    engine = KPIEngine(plant_config)
    enriched_df = engine.process(raw_df)
    
    intel = ProcessIntelligence(adv_config)
    intel_df = intel.detect_anomalies(enriched_df)
    alerts = intel.generate_alerts(intel_df)
    
    return intel_df, alerts

# -------- UI HELPERS (HTML INJECTION) --------
def create_kpi_card(title, value, unit, status_text=None, status_type="neutral", is_main=False, fill_pct=None):
    badge_html = ""
    if status_text:
        badge_html = f'<div class="status-badge badge-{status_type}">{status_text}</div>'

    value_class = "kpi-value-main" if is_main else "kpi-value"
    
    fill_bar_html = ""
    if fill_pct is not None:
        safe_pct = max(0.0, min(100.0, float(fill_pct)))
        
        fill_bar_html = f'<div style="width: 100%; height: 6px; background-color: #e0e9f2; border-radius: 4px; margin-top: 24px; overflow: hidden;"><div style="width: {safe_pct}%; height: 100%; background-color: #003f87; transition: width 0.8s ease-in-out;"></div></div>'
    
    return f'<div class="kpi-card" style="justify-content: flex-start;"><div class="kpi-title">{title}</div><div class="{value_class}" style="margin-top: 12px; margin-bottom: 12px;">{value} <span class="kpi-unit">{unit}</span></div><div>{badge_html}</div>{fill_bar_html}</div>'

# -------- MAIN APPLICATION --------
def main():
    load_css()
    
    with st.spinner("Initializing Pipeline..."):
        df, alerts = load_and_process()
        
    if df is None:
        st.error("System Error: Unable to connect to historian database.")
        return

    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    nav_selection, global_date_range = render_sidebar_controls(min_date, max_date)

    if len(global_date_range) == 2:
        mask = (df['timestamp'].dt.date >= global_date_range[0]) & (df['timestamp'].dt.date <= global_date_range[1])
        filtered_df = df.loc[mask].copy()
    elif len(global_date_range) == 1:
        mask = df['timestamp'].dt.date == global_date_range[0]
        filtered_df = df.loc[mask].copy()
    else:
        filtered_df = df.copy()

    if filtered_df.empty:
        st.warning("No telemetry data available for the selected operating window.")
        return

    latest = filtered_df.iloc[-1]

    # -------- PAGE ROUTING: DASHBOARD --------
    if nav_selection == "Dashboard":
        st.markdown("<h2 style='color: #003f87; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;'>Milling Intelligence Portal</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #141d23; margin-top: -10px;'>KPI Dashboard</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if latest['machine_state'] == 'RUNNING': sys_badge = "ok"
        elif latest['machine_state'] == 'MAINTENANCE' or latest['machine_state'] == 'PLANNED STOPPAGE': sys_badge = "neutral"
        else: sys_badge = "alert"

        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(create_kpi_card(
                title="Overall Plant Efficiency (OPE)", 
                value=f"{latest['extraction_yield_pct']:.1f}", 
                unit="%", 
                status_text=latest['machine_state'], 
                status_type=sys_badge, 
                is_main=True,
                fill_pct=latest['extraction_yield_pct']
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Total Production", f"{latest['production_total_kg']:,.0f}", "kg", "ON TARGET", "neutral"), unsafe_allow_html=True)
        with col3:
            temp_status = "HIGH USAGE ALERT" if latest['grinder_temp_c'] > 60 else "TEMP NORMAL"
            temp_badge = "alert" if latest['grinder_temp_c'] > 60 else "ok"
            st.markdown(create_kpi_card("Grinder Temperature", f"{latest['grinder_temp_c']:.1f}", "°C", temp_status, temp_badge), unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        col_chart, col_alerts = st.columns([3, 1])
        
        with col_chart:
            st.markdown("<h4 style='color: #141d23; font-weight: 700;'>Process Telemetry</h4>", unsafe_allow_html=True)
            fig = px.line(filtered_df, x='timestamp', y='throughput_kgph', color_discrete_sequence=['#003f87'])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0), xaxis_title="", yaxis_title="Throughput (kg/h)")
            st.plotly_chart(fig, use_container_width=True)

        with col_alerts:
            st.markdown("<h4 style='color: #141d23; font-weight: 700;'>Active Alerts</h4>", unsafe_allow_html=True)
            
            if len(global_date_range) == 2:
                active_alerts = [a for a in alerts if global_date_range[0] <= a.timestamp.date() <= global_date_range[1]]
            elif len(global_date_range) == 1:
                active_alerts = [a for a in alerts if a.timestamp.date() == global_date_range[0]]
            else:
                active_alerts = alerts

            if not active_alerts:
                st.markdown('<div class="status-badge badge-ok" style="margin-top: 10px;">SYSTEM NORMAL</div>', unsafe_allow_html=True)
            else:
                for alert in active_alerts[:5]:
                    st.markdown(f"""
                    <div class="alert-box">
                        <span class="alert-time">{alert.timestamp.strftime('%H:%M')}</span>
                        <span class="alert-msg">{alert.message}</span>
                    </div>
                    """, unsafe_allow_html=True)

    # -------- PAGE ROUTING: REPORTS --------
    elif nav_selection == "Historical Reports":
        st.markdown("<h2 style='color: #003f87; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;'>Historical Reports</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #424752; font-size: 14px;'>Select Aggregation Period</h4>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 6])
        
        if 'agg_freq' not in st.session_state:
            st.session_state.agg_freq = "D"
            
        with col_btn1:
            if st.button("Daily Report", use_container_width=True): st.session_state.agg_freq = "D"
        with col_btn2:
            if st.button("Weekly Report", use_container_width=True): st.session_state.agg_freq = "W"
        with col_btn3:
            if st.button("Monthly Report", use_container_width=True): st.session_state.agg_freq = "ME"
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        plant_config = PlantConfig()
        aggregator = HistorianAggregator(plant_config)
        report_df = aggregator.aggregate(filtered_df, st.session_state.agg_freq)

        rename_map = {
            "timestamp": "Time Period",
            "feed_weight_kg_total": "Total Feed (kg)",
            "bag_count_total": "Total Bags Produced",
            "production_total_kg_total": "Total Output (kg)",
            "throughput_kgph_mean": "Throughput Avg (kg/h)",
            "grinder_temp_c_mean": "Grinder Temp Avg (°C)",
            "moisture_pct_mean": "Moisture Avg (%)",
            "extraction_yield_pct_mean": "Yield Avg (%)"
        }
        
        cols_to_rename = {k: v for k, v in rename_map.items() if k in report_df.columns}
        report_df = report_df.rename(columns=cols_to_rename)

        styled_df = report_df.style.set_properties(**{
            'background-color': '#ffffff',
            'color': '#141d23',
            'border-color': '#e0e9f2',
            'padding': '12px',
            'font-size': '14px'
        }).set_table_styles([{
            'selector': 'th',
            'props': [
                ('background-color', '#f6faff'),
                ('color', '#424752'),
                ('font-weight', 'bold'),
                ('text-transform', 'uppercase'),
                ('font-size', '12px'),
                ('padding', '12px')
            ]
        }])

        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

if __name__ == "__main__":
    main()
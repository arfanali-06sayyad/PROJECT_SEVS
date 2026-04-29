import streamlit as st
from pathlib import Path
import datetime

# -------- UI COMPONENTS --------

def render_sidebar_controls(df_min_date, df_max_date):
    logo_path = Path(__file__).parent / "logo.png"

    if logo_path.exists():
        st.sidebar.image(str(logo_path), width=180)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    st.sidebar.markdown("### Navigation")
    
    if 'nav_selection' not in st.session_state:
        st.session_state.nav_selection = "Dashboard"
        
    if st.sidebar.button("Dashboard", use_container_width=True):
        st.session_state.nav_selection = "Dashboard"
        
    if st.sidebar.button("Historical Reports", use_container_width=True):
        st.session_state.nav_selection = "Historical Reports"
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Global Filters")
    
    global_date_range = st.sidebar.date_input(
        "Operating Window", 
        [df_min_date, df_max_date], 
        min_value=df_min_date, 
        max_value=df_max_date
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("System Engine: Active\n\nModel: Sevs-Core v2.0")
    
    return st.session_state.nav_selection, global_date_range
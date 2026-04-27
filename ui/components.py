import streamlit as st
from pathlib import Path


# -------- UI COMPONENTS --------

def render_sidebar_controls():
    # Construct path to the new logo image relative to this script
    logo_path = Path(__file__).parent / "logo.png"

    # Strict existence check: Display logo only if the dependency file is present
    if logo_path.exists():
        # Display the custom logo with a custom width for premium visual impact
        st.sidebar.image(str(logo_path), width=180)
    else:
        # Prompt user to check the image's placement within the project directory
        st.sidebar.error("Logo file 'logo.png' not found. Ensure it sits in the 'ui/' folder.")

    # Apply same non-generic header divider and tight spacing used in the backend
    st.sidebar.markdown("## System Controls")
    st.sidebar.markdown("---")
    
    # Render user toggles and information panels
    auto_refresh = st.sidebar.checkbox("Auto-Refresh Data", value=True)
    show_raw_data = st.sidebar.checkbox("Show Raw Telemetry", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.info("System Engine: Active\n\nModel: Sevs-Core v1.0")
    
    return auto_refresh, show_raw_data
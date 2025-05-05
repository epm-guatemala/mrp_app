
import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Definitions 👋")

st.sidebar.success("Select the page")

st.markdown(
    """
    
    - MRP: Material Requirement planning
    - SKU: Stock keeping unit
    
    """
)


# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st

@st.cache_data
def load_data():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    return df

#%% Loading

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! (using st.cache_data)")

#%% Showing

st.header("Download all MRP Data")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_00 = convert_df(data)
st.download_button(
    "📥 Download purchase amount per company and year (.csv)",
    csv_00,
    "all_mrp.csv",
    "text/csv",
    key='download-csv-00'
)

#%%


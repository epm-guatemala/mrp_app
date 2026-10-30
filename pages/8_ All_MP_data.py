#%% Importing packages

import streamlit as st
import io
from datetime import datetime

#%% functions

@st.cache_data
def load_versions_mp():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT DISTINCT(version) AS version FROM clean_real_mp ORDER BY version DESC', ttl="10m")
    return df

@st.cache_data
def load_data_mp(version_list):
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Build query with placeholders
    query = "SELECT * FROM clean_real_mp WHERE version = ANY(:versions)"
    # Run query safely
    df = conn.query(query, params={"versions": version_list}, ttl="10m")
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Version selection

st.title('MP version')

data_load_state = st.text('Loading data...')
df_versions = load_versions_mp()
data_load_state.text("Done! (using st.cache_data)")

option = st.selectbox(
    "Select the year-week MP version you are interested in:",
    list(df_versions['version'])
    )
st.write("You selected:", option)

#%% Loading data

data_load_state = st.text('Loading MP...')
data = load_data_mp([option])
data_load_state.text("Done! (using st.cache_data)")

#%% website

st.header("Download all MP Data")

#date
dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_00 = convert_df(data)
st.download_button(
    "📥 Download all Material Planning data (.csv)",
    csv_00,
    f'{dt_now}_all_mrp.csv',
    "text/csv",
    key='download-csv-00'
)

#%% 



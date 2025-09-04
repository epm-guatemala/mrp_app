#%% Importing packages

import streamlit as st
import io
from datetime import datetime

#%% functions

@st.cache_data
def load_data():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query.
    df = conn.query('SELECT * FROM clean_mp;', ttl="10m")
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Loading

data_load_state = st.text('Loading data...')
data = load_data()
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


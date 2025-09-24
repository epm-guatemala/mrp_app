#%% Importing packages

import streamlit as st
import io
from datetime import datetime

import pandas as pd

#%% functions

@st.cache_data
def load_versions_mp():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT DISTINCT(version) AS version FROM clean_mp ORDER BY version DESC', ttl="10m")
    return df

@st.cache_data
def load_data_mp(version_list):
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Build query with placeholders
    query = "SELECT * FROM clean_mp WHERE version = ANY(:versions)"
    # Run query safely
    df = conn.query(query, params={"versions": version_list}, ttl="10m")
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')  # <-- BOM added here
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

#%% Main

st.title('SKU procurement')

# Selection of SKU of interest
option= st.selectbox(
    "Select SKU:",
    [""]+list(data['sku'].unique()))

if option:
    # Creating dictionaries
    dict_sku_description= dict(zip(data['sku'], data['sku_description']))
    dict_sku_family= dict(zip(data['sku'], data['sku_family']))
    
    df= data[data['sku'].isin([option])]
    
    cols=  ['sku',
            'inventory_purchase_eegsa',
            'purchase_type_eegsa',
            'inventory_purchase_eegsa_valuation',
            'inventory_purchase_trelec',
            'purchase_type_trelec',
            'inventory_purchase_trelec_valuation',
            'inventory_purchase_amesa',
            'purchase_type_amesa',
            'inventory_purchase_amesa_valuation',
            'inventory_purchase_energica',
            'purchase_type_energica',
            'inventory_purchase_energica_valuation',
            'year_month']
    
    df= df[cols]
    
    st.header("SKU basic information")
    
    st.write(f'SKU Description: {dict_sku_description[option]}')
    st.write(f'SKU family: {dict_sku_family[option]}')
    st.write('All currencies in GTQ')
    
    df= df.set_index('year_month')
    
    st.header("Procurement need per SKU")
    st.dataframe(df)
    
    #date
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    csv_00 = convert_df(df)
    st.download_button(
        "📥 Download purchase plan per sku and all companies (.csv)",
        csv_00,
        f'{dt_now}_pp_all.csv',
        "text/csv",
        key='download-csv-00'
    )

else:
    st.warning("Please make selection to continue.")

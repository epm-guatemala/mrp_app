# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mrp", type=GSheetsConnection)
    df = conn.read()
    return df

#%% Loading

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Done! (using st.cache_data)")


# Selection of SKU of interest
ls_skus= data['sku'].unique()
options = st.multiselect(
    "Select the companies you are interested in:",
    ls_skus,
    default=["42-3082"],
    max_selections=1
)

# Creating dictionaries
dict_sku_description= dict(zip(data['sku'], data['sku_description']))
dict_sku_family= dict(zip(data['sku'], data['sku_family']))

df= data[data['sku'].isin(options)]

cols=  ['sku',
        'inventory_purchase_eegsa',
        'purchase_type_eegsa',
        #'inventory_purchase_eegsa_valuation',
        'inventory_purchase_trelec',
        'purchase_type_trelec',
        #'inventory_purchase_trelec_valuation',
        'inventory_purchase_amesa',
        'purchase_type_amesa',
        #'inventory_purchase_amesa_valuation',
        'inventory_purchase_energica',
        'purchase_type_energica',
        #'inventory_purchase_energica_valuation',
        'year_month']

df= df[cols]

st.write(f'Description: {dict_sku_description[options[0]]} - Family: {dict_sku_family[options[0]]}')
st.write('All currencies in GTQ')

df= df.set_index('year_month')

st.header("Procurement need per SKU")
st.dataframe(df)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=True).encode('utf-8')

csv_00 = convert_df(df)
st.download_button(
    "📥 Download purchase plan per sku and companies (.csv)",
    csv_00,
    "purchase_plan_sku_companies.csv",
    "text/csv",
    key='download-csv-00'
)

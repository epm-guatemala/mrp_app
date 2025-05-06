# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
import pandas as pd

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
# ls_skus= data['sku'].unique()
# options = st.multiselect(
#     "Select the companies you are interested in:",
#     ls_skus,
#     default=["42-3082"],
#     max_selections=1
# )

# Creating dictionaries
dict_sku_description= dict(zip(data['sku'], data['sku_description']))
dict_sku_family= dict(zip(data['sku'], data['sku_family']))

cols=  [
       'inventory_purchase_eegsa_valuation',
       'inventory_purchase_trelec_valuation',
       'inventory_purchase_amesa_valuation',
       'inventory_purchase_energica_valuation',
       'year_month', 'year'
       ]

df= data[cols]

df_year= pd.pivot_table(df,
    index= 'year',
    values= ['inventory_purchase_eegsa_valuation',
    'inventory_purchase_trelec_valuation',
    'inventory_purchase_amesa_valuation',
    'inventory_purchase_energica_valuation'],
    aggfunc= 'sum'
    )

df_year= (df_year/1000000).round(2)
df_year["total"] = df_year.sum(axis= 1)

df_year= df_year[['inventory_purchase_eegsa_valuation',
'inventory_purchase_trelec_valuation',
'inventory_purchase_amesa_valuation',
'inventory_purchase_energica_valuation',
'total']]


#%% Showing

st.header("Purchase amount per company and year (MGTQ)")
st.dataframe(df_year)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=True).encode('utf-8')

csv_00 = convert_df(df_year)
st.download_button(
    "📥 Download purchase amount per company and year (.csv)",
    csv_00,
    "purchase_plan_sku_companies.csv",
    "text/csv",
    key='download-csv-00'
)
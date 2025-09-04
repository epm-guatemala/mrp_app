# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
from datetime import datetime
import io

import pandas as pd

#%% Functions

@st.cache_data
def load_data_mp():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query.
    df = conn.query('SELECT * FROM clean_mp;', ttl="10m")
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Downloading dataframe

data_load_state = st.text('Loading data...')
data = load_data_mp()
data_load_state.text("Done! (using st.cache_data)")

#%% Inventory simulation

cols = [
        'inventory_initial_new&ra_eegsa_valuation',
        'inventory_initial_new&ra_trelec_valuation',
        'inventory_initial_new&ra_amesa_valuation',
        'inventory_initial_new&ra_energica_valuation',
        'year_month']

cols_old_companies = cols[0:4]

cols_new_companies = [
    'eegsa',
    'trelec',
    'amesa',
    'energica'
    ]

df = data[cols]
     
cols_options = [
    'all',
    'eegsa',
    'eegsa_vad',
    'trelec',
    'amesa',
    'energica']

dict_values= dict(zip(cols_old_companies,cols_new_companies))
df= df.rename(columns= dict_values)

df_pivot= pd.pivot_table(df,
               index= 'year_month',
               values= cols_new_companies,
               aggfunc= 'sum')

df_pivot= (df_pivot/1000000).round(3)
df_pivot['all']=df_pivot.sum(axis= 1)

# adding vad eegsa regulatory limit
df_pivot['eegsa_vad']= 4.5/100*746*7.80

#%% Inventory visualization and its download

st.title('Inventory simulation & Purchase amount')

options = st.multiselect(
    "Select the companies you are interested in:",
    cols_options,
    default=["eegsa", "eegsa_vad"],
)
st.write("You selected:", options)

# Inventory simulation
st.header("Initial monthly inventory simulation")
st.write('For EEGSA the recognized regulatory inventory equals 4.5% of 746 MUSD or MGTQ 262')
df_pivot= df_pivot[options]
chart_data = pd.DataFrame(df_pivot, columns=cols_options)
st.line_chart(chart_data, y_label='MGTQ', x_label= 'year_month')

dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_00 = convert_df(df_pivot)
st.download_button(
   "📥 Download inventory simulation as (.csv)",
   csv_00,
   f'{dt_now}_is.csv',
   "text/csv",
   key='download-csv-00'
)

#%% Yearly purchases

# Creating dictionaries
dict_sku_description= dict(zip(data['sku'], data['sku_description']))
dict_sku_family= dict(zip(data['sku'], data['sku_family']))

cols_p=  [
       'inventory_purchase_eegsa_valuation',
       'inventory_purchase_trelec_valuation',
       'inventory_purchase_amesa_valuation',
       'inventory_purchase_energica_valuation',
       'year_month', 'year'
       ]

df_p= data[cols_p]

df_year= pd.pivot_table(df_p,
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

#%% #%% Yearly visualization and download

st.header("Purchase amount per company and year (MGTQ)")
st.dataframe(df_year)

csv_01 = convert_df(df_year)
st.download_button(
    "📥 Download purchase amount per company and year as (.csv)",
    csv_01,
    f'{dt_now}_purchaseplan.csv',
    "text/csv",
    key='download-csv-01'
)

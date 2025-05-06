# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
import pandas as pd

#%% Loading

@st.cache_data
def load_data_mrp():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mrp", type=GSheetsConnection)
    df = conn.read()
    return df


#%% Downloading dataframe

data_load_state = st.text('Loading data...')
data = load_data_mrp()
data_load_state.text("Done! (using st.cache_data)")

#columns

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

#%% Visualization

st.title('EPM Materiales Material Requirement Planning')

options = st.multiselect(
    "Select the companies you are interested in:",
    cols_options,
    default=['eegsa', 'eegsa_vad'],
)
st.write("You selected:", options)

# Inventory simulation
st.header("Initial monthly inventory simulation")
st.write('For EEGSA the recognized regulatory inventory equals 4.5% of 746 MUSD or MGTQ 262')
df_pivot= df_pivot[options]
chart_data = pd.DataFrame(df_pivot, columns=cols_options)
st.line_chart(chart_data, y_label='MGTQ', x_label= 'year_month')


#%% Download data

@st.cache_data
def convert_df(df):
   return df.to_csv(index=True).encode('utf-8')

csv = convert_df(df_pivot)
st.download_button(
   "📥 Download as comma-separated values (.csv)",
   csv,
   "inventory_simulation.csv",
   "text/csv",
   key='download-csv'
)

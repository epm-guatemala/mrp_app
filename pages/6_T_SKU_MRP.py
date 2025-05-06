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

# company selection
options_companies= [
    'eegsa',
    'trelec',
    'amesa',
    'energica',
    'all']

option_company= st.selectbox(
    "Select the company you are interested in:",
    options_companies)
option_company= options_companies[0] #TODO

# sku selection
option_sku= st.selectbox(
    "Select the sku you are interested in:",
    data['sku'].unique())
option_sku= 'TP-000075'

if 'all' not in option_company:
    cols= [elem for elem in data.columns if option_company in elem]
    cols= ['year', 'year_month', 'sku_family', 'sku', 'sku_description']+cols
else:
    cols = data.columns

df= data[cols]
df= df[df['sku'].isin([option_sku])]
    
st.header("Graphical MRP per SKU")
st.dataframe(df)
    
#%% Plotting results 

df.columns


npa_mrp= df.values
npa_mrp=np.transpose(npa_mrp)
npa_mrp.shape

# Connecting inventory within the month
for j in range(int_window-1):
    plt.plot([j,j], [npa_mrp[0,j], npa_mrp[6,j]], marker = '', color= 'royalblue', linestyle='--')

# Connecting inventory across the month
for j in range(int_window-1):
    plt.plot([j,j+1], [npa_mrp[6,j],npa_mrp[0,j+1]], marker = '', color= 'royalblue', linestyle='--')

plt.plot(npa_mrp[7,:], label= "RP", color= 'limegreen', linewidth= 0.9)
plt.plot(npa_mrp[8,:], label= "SS", color= 'red', linewidth= 0.6)
plt.xticks(np.arange(0, int_window, 1), ls_dates_df, fontsize= 5, rotation= 45)
plt.xlabel("Month")
plt.ylabel("Amount (#)")
plt.title(str_name)
plt.grid()
plt.legend()
plt.savefig(path_mrp_graph / filename_graph)
plt.show()
        

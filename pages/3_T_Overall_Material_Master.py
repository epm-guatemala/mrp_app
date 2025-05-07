# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
from datetime import datetime
import io

import pandas as pd
import numpy as np

#%% Functions

@st.cache_data
def load_data_mm():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mm", type=GSheetsConnection)
    df = conn.read()
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Loading material master

data_load_state = st.text('Loading Material Master data...')
df_mm= load_data_mm()
data_load_state.text("Done! (using st.cache_data)")

# dropping columns from main data frame
df_mm= df_mm.drop(['overall_classification'], axis=1)

# for complete master data download
df_mm_c= df_mm.copy()

# cleaning data
df_mm_clean= df_mm[((df_mm['mrp']=='si') | (df_mm['mto']=='si') | (df_mm['min_stock']=='si')) & (df_mm['obsoleto']=='no')]
df_mm_clean= df_mm_clean.drop_duplicates(subset= ['sap_codigo', 'sociedad'])

# all skus per company
df_sku_sociedad= pd.pivot_table(df_mm_clean,
               index= 'sociedad',
               values= 'sap_codigo',
               aggfunc= 'count')
df_sku_sociedad.index = df_sku_sociedad.index.str.lower()
df_sku_sociedad.columns= ['total_skus']

# binary and proportion matrix from skus and companies
df_binary = pd.DataFrame({'sap_codigo': df_mm_clean['sap_codigo'], 
                          'sociedad': df_mm_clean['sociedad']})
df_binary= df_binary.drop_duplicates()
binary_matrix = pd.crosstab(df_binary['sap_codigo'], df_binary['sociedad'])
shared_skus = binary_matrix.T.dot(binary_matrix)
shared_skus.index = shared_skus.index.str.lower()
shared_skus.columns = [elem.lower() for elem in shared_skus.columns]
proportion_df= shared_skus.div(np.diag(shared_skus), axis = 0).round(2)

# mrp mto and min skus
df_mm['sociedad']= df_mm['sociedad'].str.lower()
df_mm_unmelted= pd.melt(df_mm,
                        id_vars=['sap_codigo', 'sociedad'],
                        value_vars=['mrp','mto','min_stock'])
df_mm_unmelted['type']= df_mm_unmelted['variable']+'_'+df_mm_unmelted['value']

binary_matrix_mm= pd.crosstab(df_mm_unmelted['sociedad'], df_mm_unmelted['type'])
binary_matrix_mm= binary_matrix_mm[['min_stock_si','mrp_si','mto_si']]
binary_matrix_mm['total']=binary_matrix_mm.sum(axis=1)
binary_matrix_mm.loc['total']=binary_matrix_mm.sum()


#%% Visualization

st.title('Overall Material Master')
st.header("SKUS sharing between companies (unique count)")
st.dataframe(shared_skus)

st.header("SKUS sharing between companies (proportion from unique count)")
st.dataframe(proportion_df)

st.header("MRP-MTO-MIN SKU distribution (non-unique count)")
st.dataframe(binary_matrix_mm)

dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

st.header("Material Master Download - ⚠️ does not contain OBSOLETE SKUs")
csv_00 = convert_df(df_mm)
st.download_button(
   "📥 Download EPM GUA Material Master (.csv)",
   csv_00,
   f'{dt_now}_material_master_wo.csv',
   "text/csv",
   key='download-csv-00'
)

st.header("Material Master Download - complete")
csv_01 = convert_df(df_mm_c)
st.download_button(
   "📥 Download EPM GUA Material Master (.csv)",
   csv_01,
   f'{dt_now}_material_master_c.csv',
   "text/csv",
   key='download-csv-01'
)


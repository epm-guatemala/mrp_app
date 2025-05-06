# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
import pandas as pd
import numpy as np
import io

@st.cache_data
def load_data_mrp():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mrp", type=GSheetsConnection)
    df = conn.read()
    return df

@st.cache_data
def load_data_mm():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mm", type=GSheetsConnection)
    df = conn.read()
    return df

#%% Loading 

# Material master

data_load_state = st.text('Loading Material Master data...')
df_mm= load_data_mm()
data_load_state.text("Done! (using st.cache_data)")

# MRP
data_load_state = st.text('Loading MRP data...')
data = load_data_mrp()
data_load_state.text("Done! (using st.cache_data)")

#%% Cleaning material master

df_mm_clean= df_mm[((df_mm['mrp']=='si') | (df_mm['mto']=='si') | (df_mm['min_stock']=='si')) & (df_mm['obsoleto']=='no')]
df_mm_clean= df_mm_clean.drop_duplicates(subset= ['sap_codigo', 'sociedad'])

# all skus per company
df_sku_sociedad= pd.pivot_table(df_mm_clean,
               index= 'sociedad',
               values= 'sap_codigo',
               aggfunc= 'count')
df_sku_sociedad.index = df_sku_sociedad.index.str.lower()
df_sku_sociedad.columns= ['total_skus']

#%% Cleaning mrp

cols = [
        'sku_family',
        'sku',
        'sku_description',
        'year_month',
        'purchase_type_eegsa',
        'purchase_type_trelec',
        'purchase_type_amesa',
        'purchase_type_energica',
        ]

cols_analysis = [
    'purchase_type_eegsa',
    'purchase_type_trelec',
    'purchase_type_amesa',
    'purchase_type_energica'
    ]

df = data[cols]

dict_sku_description= dict(zip(df['sku'], df['sku_description']))
dict_sku_family= dict(zip(df['sku'], df['sku_family']))

# emergencies per sku x company

ls_sku= []
ls_sku_all_emerg= []

for str_sku in df['sku'].unique():
    
    df_elem= df[df['sku']==str_sku]
    
    ls_sku_emer= []
    
    for col in cols_analysis:
        if 'emergency' in df_elem[col].unique():
            ls_sku_emer.append('emergency')
        else:
            ls_sku_emer.append('no emergency')
            
    ls_sku.append(str_sku)
    ls_sku_all_emerg.append(ls_sku_emer)
            
# Creating dataframe
cols_analysis = ['eegsa', 'trelec', 'amesa', 'energica']
df_results= pd.DataFrame(np.array(ls_sku_all_emerg))
df_results.columns = cols_analysis
df_results['sku']= ls_sku
df_results['sku_description']= df_results['sku'].map(dict_sku_description)
df_results['sku_family']= df_results['sku'].map(dict_sku_family)

df_melted= pd.melt(df_results, 
                   id_vars=['sku', 'sku_description', 'sku_family'], 
                   value_vars=cols_analysis)

df_pivot= pd.pivot_table(df_melted,
               index= 'variable',
               columns= 'value',
               values= 'sku',
               aggfunc= 'count')

df_pivot= df_pivot['emergency'].sort_values(ascending=False)
df_pivot= pd.DataFrame(df_pivot)
df_pivot.columns= ['emergency_skus'] 

df_pivot= pd.concat([df_pivot, 
                     df_sku_sociedad], axis = 1)

df_pivot.loc['total'] = df_pivot.sum()
df_pivot['emergency_proportion']=(df_pivot['emergency_skus']/df_pivot['total_skus']).round(2)

#%% emergencies per unique sku

df_melted_sku_unique= pd.pivot_table(
    df_melted,
    index= 'sku',
    columns= 'value',
    values= 'variable',
    aggfunc= 'count'
    )

df_melted_sku_unique= df_melted_sku_unique[['emergency']]
df_melted_sku_unique= df_melted_sku_unique.dropna()
df_melted_sku_unique= df_melted_sku_unique.reset_index(drop= False)

df_melted_sku_unique['sku_description']= df_melted_sku_unique['sku'].map(dict_sku_description)
df_melted_sku_unique['sku_family']= df_melted_sku_unique['sku'].map(dict_sku_family)
df_melted_sku_unique= df_melted_sku_unique[['sku_family','sku', 'sku_description', 'emergency']]

df_melted_sku_unique= df_melted_sku_unique.sort_values('sku_family').reset_index(drop=True)
df_melted_sku_unique.index = range(1, df_melted_sku_unique.shape[0]+1)

#%% Download function

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Visualization

st.title('EPM SKU emergencies')
st.write('At a minimum, one delivery is required, and the known lead time exceeds the time remaining until the delivery date.')

st.header("SKUs in emergency state per company")
st.dataframe(df_pivot)

csv_00 = convert_df(df_melted)
st.download_button(
   "📥 Download sku companies emergencies comma-separated values (.csv)",
   csv_00,
   "sku_company_emergencies.csv",
   "text/csv",
   key='download-csv-00'
)

st.header("SKUs in emergency state")
int_rows= df_melted_sku_unique.shape[0]
st.write(f'Unique SKUs in emergency state: {int_rows}')
st.dataframe(df_melted_sku_unique)

csv_01 = convert_df(df_melted_sku_unique)
st.download_button(
   "📥 Download sku emergencies as comma-separated values (.csv)",
   csv_01,
   "sku_emergencies.csv.csv",
   "text/csv",
   key='download-csv-01'
)

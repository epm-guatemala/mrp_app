#%% Importing packages

import streamlit as st
from datetime import datetime
import io

import pandas as pd
import numpy as np

#%% Functions

@st.cache_data
def load_data_mm():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT * FROM raw_master_data', ttl="10m")
    return df

@st.cache_data
def load_versions_mp():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT DISTINCT(version) AS version FROM clean_real_mp ORDER BY version DESC', ttl="10m")
    return df

@st.cache_data
def load_alerts(version_list):
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Build query with placeholders
    query = """
        SELECT
        sku,
        -- eegsa --
        COUNT(*) FILTER (WHERE purchase_type_eegsa = 'no emergency') AS noemergency_count_eegsa,
        COUNT(*) FILTER (WHERE purchase_type_eegsa = 'emergency') AS emergency_count_eegsa,
        COUNT(*) FILTER (WHERE purchase_type_eegsa = 'near miss') AS nearmiss_count_eegsa,
        COUNT(*) FILTER (WHERE purchase_type_eegsa = 'stock out') AS stockout_count_eegsa,
        -- trelec --
        COUNT(*) FILTER (WHERE purchase_type_trelec = 'no emergency') AS noemergency_count_trelec,
        COUNT(*) FILTER (WHERE purchase_type_trelec = 'emergency') AS emergency_count_trelec,
        COUNT(*) FILTER (WHERE purchase_type_trelec = 'near miss') AS nearmiss_count_trelec,
        COUNT(*) FILTER (WHERE purchase_type_trelec = 'stock out') AS stockout_count_trelec,
        -- amesa --
    	COUNT(*) FILTER (WHERE purchase_type_amesa = 'no emergency') AS noemergency_count_amesa,
        COUNT(*) FILTER (WHERE purchase_type_amesa = 'emergency') AS emergency_count_amesa,
        COUNT(*) FILTER (WHERE purchase_type_amesa = 'near miss') AS nearmiss_count_amesa,
        COUNT(*) FILTER (WHERE purchase_type_amesa = 'stock out') AS stockout_count_amesa,
        -- energica --
        COUNT(*) FILTER (WHERE purchase_type_energica = 'no emergency') AS noemergency_count_energica,
        COUNT(*) FILTER (WHERE purchase_type_energica = 'emergency') AS emergency_count_energica,
        COUNT(*) FILTER (WHERE purchase_type_energica = 'near miss') AS nearmiss_count_energica,
        COUNT(*) FILTER (WHERE purchase_type_energica = 'stock out') AS stockout_count_energica
        FROM clean_real_mp
        where version =ANY(:versions)
        GROUP BY sku
        ORDER BY sku;"""    
        
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

# loading MP
data_load_state = st.text('Loading MP and material master data...')
data = load_alerts([option]).set_index('sku', drop= True)

# loading master data
df_mm= load_data_mm()
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
            
#%% Creating dataframe


# Unique SKU overall
pS_total_stockout= data['stockout_count_eegsa']+data['stockout_count_trelec']+data['stockout_count_amesa']+data['stockout_count_energica']
pS_total_near_miss= data['nearmiss_count_eegsa']+data['nearmiss_count_trelec']+data['nearmiss_count_amesa']+data['nearmiss_count_energica']
pS_total_emergency= data['emergency_count_eegsa']+data['emergency_count_trelec']+data['emergency_count_amesa']+data['emergency_count_energica']

df_sku_summary= pd.concat([pS_total_stockout, pS_total_near_miss, pS_total_emergency], axis= 1)
df_sku_summary.columns= ['stockout','nearmiss','emergency']
df_sku_summary= df_sku_summary/df_sku_summary

df_sku_summary['stockout']= np.where(df_sku_summary['stockout']>0, 'stockout','')
df_sku_summary['nearmiss']= np.where(df_sku_summary['nearmiss']>0, 'nearmiss','')
df_sku_summary['emergency']= np.where(df_sku_summary['emergency']>0, 'emergency','')
df_sku_summary['family']= df_sku_summary['stockout']+df_sku_summary['nearmiss']+df_sku_summary['emergency']



               
               

















df_pt_data= pd.DataFrame((data/data).sum(axis= 0))

df_titles= pd.DataFrame([str_title.split("_") for str_title in df_pt_data.index])
df_titles.columns= ['state', 'repeated', 'company']
df_titles['count']= df_pt_data.values


df_results= pd.pivot_table(df_titles, index='company', columns= 'state', 
         values='count', aggfunc= "sum")

df_results= df_results[['stockout','nearmiss','emergency','noemergency']]
df_results.loc['total']= df_results.sum(axis=0)
        









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


#%% website

st.title('SKUs emergencies')
st.write('At a minimum, one delivery is required and the known lead time exceeds \
         the time remaining until the required delivery date.')

st.header("SKUs in emergency state per company")
st.dataframe(df_pivot)

dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_00 = convert_df(df_melted)
st.download_button(
   "📥 Download companies SKUs emergencies as (.csv)",
   csv_00,
   f'{dt_now}_skus_company_emergencies.csv',
   "text/csv",
   key='download-csv-00'
)

st.header("SKUs in emergency state")
int_rows= df_melted_sku_unique.shape[0]
st.write(f'Unique SKUs in emergency state: {int_rows}')
st.dataframe(df_melted_sku_unique)

csv_01 = convert_df(df_melted_sku_unique)
st.download_button(
   "📥 Download SKU emergencies as (.csv)",
   csv_01,
   f'{dt_now}_sku_emergencies.csv',
   "text/csv",
   key='download-csv-01'
)



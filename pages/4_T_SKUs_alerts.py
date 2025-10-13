#%% Importing packages

import streamlit as st
from datetime import datetime
import io

import pandas as pd

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

# sku dictionry
dict_sku_description= dict(zip(df_mm['sap_codigo'], df_mm['sap_descripcion']))
dict_sku_family= dict(zip(df_mm['sap_codigo'], df_mm['familia_01']))

# all skus per company
df_sku_sociedad= pd.pivot_table(df_mm_clean,
               index= 'sociedad',
               values= 'sap_codigo',
               aggfunc= 'count')
df_sku_sociedad.index = df_sku_sociedad.index.str.lower()
df_sku_sociedad.columns= ['total_skus']

#%% dictionaries for state summarization

dict_variations ={
    (1,1,1):'stockouts',
    (1,0,1):'stockouts',
    (1,1,0):'stockouts',
    (0,1,1):'emergency',
    (1,0,0):'stockouts',
    (0,1,0):'near miss',
    (0,0,1):'emergency',
    (0,0,0):'no emergency'
    }

dict_all_variations ={
    (1,1,1):'stockouts',
    (1,0,1):'stockouts',
    (1,1,0):'emergency',
    (0,1,1):'stockouts',
    (1,0,0):'emergency',
    (0,1,0):'no emergency',
    (0,0,1):'stockouts',
    (0,0,0):'no emergency'
    }

#%% Overall state per company

ls_state_frames= []
ls_companies= ['eegsa', 'trelec', 'amesa', 'energica']

for str_company in ls_companies:

    # Unique SKU overall
    pS_total_stockout= data[f'stockout_count_{str_company}']
    pS_total_near_miss= data[f'nearmiss_count_{str_company}']
    pS_total_emergency= data[f'emergency_count_{str_company}']

    df_sku_summary= pd.DataFrame({
        'company': f'{str_company}',
        'stockouts': pS_total_stockout,
        'near miss': pS_total_stockout,
        'emergency': pS_total_emergency
        })

    ls_state_frames.append(df_sku_summary)
    

df_companies_state= pd.concat(ls_state_frames, axis= 0)
df_companies_state= df_companies_state.reset_index(drop=False).set_index(['sku','company'])

df_companies_state= (df_companies_state/df_companies_state).fillna(0)

ls_overall_final_state = []
for elem1, elem2, elem3 in zip(df_companies_state['stockouts'],
                               df_companies_state['near miss'],
                               df_companies_state['emergency']):
    ls_overall_final_state.append(dict_variations[(elem1, elem2, elem3)])

df_companies_state['final_state']= ls_overall_final_state
df_companies_state= df_companies_state.reset_index(drop= False)

df_companies_state['sku_description']= df_companies_state['sku'].map(dict_sku_description)
df_companies_state['sku_family']= df_companies_state['sku'].map(dict_sku_family)

df_companies_state= df_companies_state[['sku', 'sku_description', 'sku_family', 'company', 
                    'stockouts', 'near miss', 'emergency','final_state']]

df_summary= pd.pivot_table(df_companies_state, 
               index= 'company',
               columns= 'final_state',
               values= 'sku',
               aggfunc= 'count'
               )

df_summary= df_summary[['stockouts','emergency']]
df_summary= df_summary.sort_values('stockouts', ascending=False)


df_summary['total']= df_summary.sum(axis=1)
df_summary= df_summary[['stockouts','emergency','total']]

#%% Overall state for all companies

df_all_summary = pd.pivot_table(df_companies_state,
               columns= 'final_state',
               index= 'sku',
               values= 'company', 
               aggfunc='count')

df_companies_state['final_state'].unique()

df_all_summary= (df_all_summary/df_all_summary).fillna(0)

ls_overall_final_state = []
for elem1, elem2, elem3 in zip(df_all_summary['emergency'],
                               df_all_summary['no emergency'],
                               df_all_summary['stockouts']):
    ls_overall_final_state.append(dict_all_variations[(elem1, elem2, elem3)])

df_all_summary['final_state']= ls_overall_final_state
df_all_summary= df_all_summary.reset_index(drop=False)
df_all_summary['sku_description']= df_all_summary['sku'].map(dict_sku_description)
df_all_summary['sku_family']= df_all_summary['sku'].map(dict_sku_family)

df_all_summary= df_all_summary[['sku', 
                                'sku_description',
                                'sku_family',
                                'emergency', 
                                'no emergency', 
                                'stockouts', 
                                'final_state']]

df_meta= pd.pivot_table(df_all_summary,
               index= 'sku_family',
               columns= 'final_state',
               values= 'sku',
               aggfunc= 'count')

df_meta= df_meta.sort_values('stockouts', ascending=False)
df_meta.loc['total']= df_meta.sum(axis=0)
df_meta= df_meta[['stockouts','emergency','no emergency']]

df_meta_summary= df_meta.loc['total']

#%% Website

st.title('SKUs alerts for EPM GTM')
st.header("SKUs alerts")
st.dataframe(df_meta_summary)
st.header("SKU alerts per SKU-family")
st.dataframe(df_meta)

dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_00 = convert_df(df_all_summary)
st.download_button(
   "📥 Download SKUs alerts as (.csv)",
   csv_00,
   f'{dt_now}_skus_alerts.csv',
   "text/csv",
   key='download-csv-00'
)

st.header('SKUs per company and their alerts')
st.write('Stockouts, Near-misses, Emergencies per company and per SKU')

st.header("SKUs alerts per company")
st.dataframe(df_summary)

dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_01 = convert_df(df_companies_state)
st.download_button(
   "📥 Download companies SKUs alerts as (.csv)",
   csv_01,
   f'{dt_now}_skus_company_emergencies.csv',
   "text/csv",
   key='download-csv-01'
)
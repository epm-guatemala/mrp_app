#%% Importing packages

import streamlit as st
import io
from datetime import datetime

import pandas as pd

#%% functions

@st.cache_data
def load_data_mm():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mm", type=GSheetsConnection)
    df = conn.read()
    return df

@st.cache_data
def load_data_projects():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("projects", type=GSheetsConnection)
    df = conn.read()
    
    df_pC_v_max= pd.pivot_table(df,
                   index= 'project_id',
                   values= 'version_int',
                   aggfunc='max').reset_index(drop= False)

    df_pC_v_max['project_version']= df_pC_v_max['project_id']+'v'+df_pC_v_max['version_int'].astype(str)
    
    return df, df_pC_v_max

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Loading

data_load_state = st.text('Loading data...')
df_mm = load_data_mm()
df_projects, df_projects_max = load_data_projects()

data_load_state.text('Done! (using st.cache_data)')

st.title('SKU Projects - last version - all companies')

# Selection of SKU of interest

st.write('⚠️ Only non-recurrent projects with a defined timeline are shown.')
st.write('⚠️ If the SKU is not on the list, it means it was either not planned \
         in time or is part of a recurring project.')

option= st.selectbox(
    "Select SKU:",
    [""]+list(df_projects['sku'].unique()))

if option:
    
    # master data
    dict_sku_description= dict(zip(df_mm['sap_codigo'], df_mm['sap_descripcion']))
    dict_sku_family= dict(zip(df_mm['sap_codigo'], df_mm['familia_01']))
    
    # projects max version quantities for the sku
    df_projects_max_sku_quantities= df_projects[df_projects['project_version'].isin(set(df_projects_max['project_version'])) & df_projects['sku'].isin([option])]
    df_projects_max_sku_quantities= df_projects_max_sku_quantities.reset_index(drop= True)
    
    pt_projects_max_sku_quantities= pd.pivot_table(df_projects_max_sku_quantities,
                   index = 'year_month', 
                   columns= 'company',
                   values= 'qty',
                   aggfunc= 'sum')
    pt_projects_max_sku_quantities.index= pt_projects_max_sku_quantities.index.astype(str)
    pt_projects_max_sku_quantities['total']= pt_projects_max_sku_quantities.sum(axis=1)
    pt_projects_max_sku_quantities.loc['total']= pt_projects_max_sku_quantities.sum()
    
    # projects max version that include the SKU
    df_max_projects= pd.DataFrame()
    df_max_projects['project_version']= df_projects_max_sku_quantities['project_version'].unique()
    
    dict_project_description= dict(zip(df_projects_max_sku_quantities['project_version'], 
             df_projects_max_sku_quantities['project_description']))
    dict_project_company= dict(zip(df_projects_max_sku_quantities['project_version'], 
             df_projects_max_sku_quantities['company']))
    
    
    df_max_projects['project_description']= df_max_projects['project_version'].map(dict_project_description)
    df_max_projects['company']= df_max_projects['project_version'].map(dict_project_company)
    
    # date
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    #%% website
    
    st.header("SKU basic information")
    
    st.write(f'SKU Description: {dict_sku_description[option]}')
    st.write(f'SKU family: {dict_sku_family[option]}')
    
    st.header("Procurement need - non recurrent projects per SKU")
    st.dataframe(pt_projects_max_sku_quantities)
    
    csv_00 = convert_df(pt_projects_max_sku_quantities)
    st.download_button(
        "📥 Download non recurrent projects purchase plan per sku and all companies (.csv)",
        csv_00,
        f'{dt_now}_nrp_pp_sku_allc.csv',
        "text/csv",
        key='download-csv-00'
    )
    
    st.header("Project latest version and company that include this SKU")
    st.dataframe(df_max_projects)
    
    csv_01 = convert_df(df_max_projects)
    st.download_button(
        "📥 Download non recurrent projects latest version that include the SKU (.csv)",
        csv_01,
        f'{dt_now}_nrp_sku_allc.csv',
        "text/csv",
        key='download-csv-01'
    )
    
    st.header("All project SKU data")
    st.dataframe(df_projects_max_sku_quantities)
    
    csv_02 = convert_df(df_projects_max_sku_quantities)
    st.download_button(
        "📥 Download all non recurrent projects and SKU data (.csv)",
        csv_02,
        f'{dt_now}_nrp_sku_allc_detail.csv',
        "text/csv",
        key='download-csv-02'
    )
    
else:
    st.warning("Please make selection to continue.")

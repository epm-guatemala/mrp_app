#%% Importing packages

import streamlit as st
import io
from datetime import datetime

import pandas as pd
import numpy as np

#%% functions

@st.cache_data
def load_data_mm():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT * FROM raw_master_data', ttl="10m")
    return df

@st.cache_data
def load_data_projects():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT * FROM clean_company_projects', ttl="10m")
    return df

@st.cache_data
def load_data_projects_consumption():
    # Initialize connection.
    conn = st.connection("postgresql", type="sql")
    # Perform query
    df = conn.query('SELECT * FROM clean_company_projects_consumption', ttl="10m")
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

#%% Loading

data_load_state = st.text('Loading data...')

df_mm = load_data_mm()
df_projects = load_data_projects()
df_projects_consumption = load_data_projects_consumption()

data_load_state.text('Done! (using st.cache_data)')

#%% Master data

# proyect dictionary
dict_proyects = {}

for elem1, elem2, elem3, elem4, elem5 in zip(
        df_projects['project_version'],
        df_projects['project_description'],
        df_projects['version_int'],
        df_projects['pep'],
        df_projects['company']):
    
    dict_proyects[elem1]={}
    dict_proyects[elem1]['project_description']=elem2
    dict_proyects[elem1]['version_int']=elem3
    dict_proyects[elem1]['pep_project']=elem4
    dict_proyects[elem1]['company']=elem5


dict_mm= dict(zip(df_mm['sap_codigo'],df_mm['sap_descripcion']))

#%% Cleaning datasets

# project plan
df_projects= df_projects[['project_version',
             'sku',
             'year_month',
             'qty']]

df_projects['sku_description']= df_projects['sku'].map(dict_mm)
df_projects['val_type']=np.nan
df_projects['center']=np.nan
df_projects['warehouse']=np.nan
df_projects['year']=df_projects['year_month'].apply(lambda x: x[0:4])
df_projects['material_document']=np.nan
df_projects['pep_project']=[dict_proyects[elem]['pep_project'] for elem in df_projects['project_version']]
df_projects['type']= 'plan'
          
# project consumption 
df_projects_consumption= df_projects_consumption[['project_version',
                         'sku',
                         'sku_description',
                         'val_type',
                         'center',
                         'warehouse',
                         'year',
                         'year_month',
                         'qty',
                         'material_document',
                         'pep_project']]
df_projects_consumption['type']= 'real'

df= pd.concat([df_projects, df_projects_consumption], axis=0)

for str_col in ['project_description', 'version_int', 'pep_project', 'company']:
    df[str_col]= [dict_proyects[elem][str_col] for elem in df['project_version']]

# final dataframe
df= df[['project_version', 
        'version_int',
        'project_description', 
        'pep_project',
        'company',
        'sku', 
        'sku_description',
        'qty', 
        'year_month',
        'year',
        'val_type', 
        'center', 
        'warehouse',
        'material_document',
        'type']]

#%% Website

# Project search
st.title('Project search')
st.write('⚠️ Only non-recurrent projects with a defined timeline are shown together with MTO only SKUs in recurrent projects.')

str_selection= st.selectbox(
    "Select project version ~ project description:",
    [""]+list((df['project_version']+'~'+df['project_description']).unique()))
         
if str_selection:
    
    str_project_id= str_selection.split("~")[0]
    str_project_description= str_selection.split("~")[1]
    
    df_project= df[(df['project_version']==str_project_id) | (df['project_description']==str_project_description)]
    
    pt_df_project= pd.pivot_table(df_project,
                                  index= ['sku', 'sku_description'],
                                  columns='type',
                                  values= 'qty',
                                  aggfunc= 'sum')
    
    if 'real' in pt_df_project.columns:
        pt_df_project['planvsreal']=pt_df_project['plan']+pt_df_project['real']
        
    else:
        pt_df_project['real']=0
        pt_df_project['planvsreal']=pt_df_project['plan']+pt_df_project['real']
        
    pt_df_project= pt_df_project.sort_index(ascending=True)
    
    # render result
    st.dataframe(pt_df_project)
    
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    csv_00 = convert_df(df_project)
    st.download_button(
        "📥 Download non recurrent project (.csv)",
        csv_00,
        f'{dt_now}_project_info.csv',
        "text/csv",
        key='download-csv-00'
    )
    
else:
    st.warning("Please make selection to continue.")
    
# SKU search
st.title('SKU search')
st.write('⚠️ Only non-recurrent projects with a defined timeline are shown and only MTO SKUs in recurrent projects.')

str_sku_description= st.selectbox(
    "Select SKU ~ SKU description:",
    [""]+list((df['sku']+'~'+df['sku_description']).unique()))
         
if str_sku_description:
    
    str_sku= str_sku_description.split("~")[0]
    str_description= str_sku_description.split("~")[1]
    
    df_sku= df[(df['sku']==str_sku) | (df['sku_description']==str_description)]
    
    pt_df_sku= pd.pivot_table(df_sku,
                                  index= ['project_version',
                                          'version_int',
                                          'project_description',
                                          'pep_project',
                                          'company'],
                                  columns= ['type'],
                                  values= 'qty',
                                  aggfunc= 'sum')
    
    if 'real' in pt_df_sku.columns:
        pt_df_sku['planvsreal']=pt_df_sku['plan']+pt_df_sku['real']
        
    else:
        pt_df_sku['real']=0
        pt_df_sku['planvsreal']=pt_df_sku['plan']+pt_df_sku['real']
        
    pt_df_sku= pt_df_sku.sort_values('project_version',ascending=True)
    
    st.dataframe(pt_df_sku)
    
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    csv_01 = convert_df(df_sku)
    st.download_button(
        "📥 Download non recurrent projects purchase plan per sku and all companies (.csv)",
        csv_01,
        f'{dt_now}_sku_info.csv',
        "text/csv",
        key='download-csv-01'
    )
    
else:
    st.warning("Please make selection to continue.")
    
# SKU search
st.title('All project data')
st.write('All non recurrent project data and MTO only SKUs in recurrent projects')
    
dt_now= datetime.now()
dt_now= dt_now.strftime('%Y%m%d')

csv_02 = convert_df(df)
st.download_button(
    "📥 Download all non recurrent projects SKUs and only MTO SKUs data (.csv)",
    csv_02,
    f'{dt_now}_all_nrprojects_MTO_only.csv',
    "text/csv",
    key='download-csv-02'
)

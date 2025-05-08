#%% Importing packages

import streamlit as st
import io
from datetime import datetime

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% functions

@st.cache_data
def load_data():
    # Create a connection object.
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("mrp", type=GSheetsConnection)
    df = conn.read()
    return df

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

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

st.title('SKUs emergencies')

option_company= st.selectbox(
    "Select the company or all:",
    [""]+options_companies)

option_sku= st.selectbox(
    "Select SKU:",
    [""]+list(data['sku'].unique()))

if option_company and option_sku:
    st.success(f"You selected company: {option_company} and SKU: {option_sku}")
    
    # subsetting dataframe only for that sku
    data= data[data['sku']==option_sku]
    
    str_sku_description= data['sku_description'].unique()[0]
    str_sku_family= data['sku_family'].unique()[0]
    
    st.header("SKU basic information")
    
    st.write(f'SKU: {option_sku}')
    st.write(f'SKU Description: {str_sku_description}')
    st.write(f'SKU family: {str_sku_family}')
    
    #%% shifting company name to the end of each string
    
    companies = ['eegsa', 'trelec', 'amesa', 'energica']
    
    # Standardize columns
    def move_company_to_end(col, company_names):
        for company in company_names:
            if company in col:
                # Remove the company from wherever it is
                col_cleaned = re.sub(rf'[_&]?{company}', '', col)
                # Append it to the end with an underscore
                return f"{col_cleaned}_{company}"
        return col  # return original if no company name found
    
    # Apply to all column names in the data
    data.columns = [move_company_to_end(col, companies) for col in data.columns]
    
    #%% Column types: selected company columns, base company columns and all columns
    
    #selected company columns
    cols= [elem for elem in data.columns if option_company in elem]
    ls_selected_company_cols= cols
    
    #base company columns
    str_base_company= 'eegsa'
    cols= [elem for elem in data.columns if str_base_company in elem]
    ls_base_company_cols= cols
    
    ls_base_company_cols_sanitized= []
    for elem in ls_base_company_cols:
        if ('year' not in elem) and ('sku' not in elem):
            pattern = re.escape(str_base_company) + r'.*'
            ls_base_company_cols_sanitized.append(re.sub(pattern, '', elem))
        else:
            ls_base_company_cols_sanitized.append(elem)
    
    #all companies columns
    ls_all_cols = data.columns
    
    #%% Determining groups of columns and adding the cluster to a new cluster
    
    if 'all' == option_company:
        ls_cols= ls_all_cols
    else:
        ls_cols= ls_selected_company_cols
        
    ls_col_groups= []
    for str_base in ls_base_company_cols_sanitized:
        pattern = re.compile(rf"^{re.escape(str_base)}({'|'.join(companies)})$")
        matching_cols = [col for col in ls_cols if pattern.match(col)]
        ls_col_groups.append(matching_cols)
        
    
    df_final= pd.DataFrame()
    for ls_base, ls_group in zip(ls_base_company_cols_sanitized, ls_col_groups):
        try:
            df_final[ls_base.rstrip('_')]= data[ls_group].copy().sum(axis=1)
        except:
            pass
        
    df_final['year_month'] = data['year_month']    
    df_final= df_final.set_index(['year_month'])
    
    #%% Plotting results 
    
    #creating dataframe dictionary
    col_index_dict = {col: idx for idx, col in enumerate(df_final.columns)}
    npa_mrp=np.transpose(df_final.values)
    
    int_window= npa_mrp.shape[1]
    
    # MRP graph
    fig_mrp, ax = plt.subplots()
    
    # Connecting inventory within the month
    for j in range(int_window-1):
        plt.plot([j,j], [npa_mrp[col_index_dict['inventory_initial_new&ra'],j], 
                         npa_mrp[col_index_dict['inventory_final_new&ra'],j]], 
                 marker = '', 
                 color= 'royalblue', 
                 linewidth= 1,
                 linestyle='--')
    
    # Connecting inventory across the months
    for j in range(int_window-1):
        plt.plot([j,j+1], [npa_mrp[col_index_dict['inventory_final_new&ra'],j],
                           npa_mrp[col_index_dict['inventory_initial_new&ra'],j+1]], 
                 marker = '', 
                 color= 'royalblue',
                 linewidth= 1,
                 linestyle='--')
        
    plt.plot(npa_mrp[col_index_dict['rp_inventory'],:], 
                     label= "reorder point",
                     color= 'limegreen',
                     linewidth= 0.7)
    plt.plot(npa_mrp[col_index_dict['ss_inventory'],:], 
                     label= "safety stock",
                     color= 'red',
                     linewidth= 0.7)
    plt.plot(npa_mrp[col_index_dict['demand_min_stock'],:], 
                     label= "min_stock",
                     color= 'magenta',
                     linewidth= 0.7)
    plt.xticks(np.arange(0, int_window, 1), 
               df_final.index, 
               fontsize= 4, 
               rotation= 45)
    plt.xlabel('year_month')
    plt.ylabel('Inventory (#)')
    plt.title(f'MP for {option_sku}')
    plt.grid(color='lightgrey')
    plt.legend()
    #plt.savefig(path_mrp_graph / filename_graph)
    #plt.show()
    
    # Purchases graph
    fig_purchases, ax = plt.subplots()
    ax.bar(df_final.index, 
           df_final['inventory_purchase'])
    plt.xticks(np.arange(0, int_window, 1), 
               df_final.index, 
               fontsize= 4, 
               rotation= 45)
    plt.grid(color='lightgrey', axis='y')
    plt.title(f'Purchase Amounts for {option_sku}')
    plt.xlabel('year_month')
    plt.ylabel('Total Purchase Amount (#)')
    #plt.tight_layout()
    
    #%% website
    
    #showing graph
    st.header("Graphical Material Planning for {option_company.upper()}")
    st.pyplot(fig_mrp)
    
    # Save plot to BytesIO buffer
    buf = io.BytesIO()
    fig_mrp.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    #date
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    # Streamlit download button
    st.download_button(
        label="📥 Download graphical material planning (.png)",
        data=buf,
        file_name=f'{dt_now}_gmp_{option_company}_{option_sku}.png',
        mime="image/png"
    )
    
    st.header("Graphical required purchases for {option_company.upper()}")
    st.pyplot(fig_purchases)
    
    # Save plot to BytesIO buffer
    buf = io.BytesIO()
    fig_purchases.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Streamlit download button
    st.download_button(
        label="📥 Download graphical purchase plan (.png)",
        data=buf,
        file_name=f'{dt_now}_gpp_{option_company}_{option_sku}.png',
        mime="image/png"
    )
    
    #showing tabular data
    st.header(f'Tabular Material Planning per SKU for {option_company.upper()}')
    st.dataframe(df_final.T)
    
    csv_00 = convert_df(df_final)
    st.download_button(
       "📥 Download tabular material planning (.csv)",
       csv_00,
       f'{dt_now}_tmp_{option_company}_{option_sku}.csv',
       "text/csv",
       key='download-csv-00'
    )
    
else:
    st.warning("Please make selection to continue.")


# -*- coding: utf-8 -*-

#%% Importing packages

import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import io

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

# sku selection
option_sku= st.selectbox(
    "Select the sku you are interested in:",
    data['sku'].unique())

# option_company= 'eegsa' #TODO
# option_sku= '42-3082' #TODO

# option_company= 'trelec' #TODO
# option_sku= '78-0832' #TODO

# option_company= 'trelec' #TODO
# option_sku= '38-0757' #TODO

# subsetting dataframe only for that sku
data= data[data['sku']==option_sku]

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
           fontsize= 4, rotation= 45)
plt.grid(color='lightgrey', axis='y')
plt.title(f'Purchase Amounts for {option_sku}')
plt.xlabel('year_month')
plt.ylabel('Total Purchase Amount (#)')
#plt.tight_layout()

#%% Showing results in the app

#showing graph
st.header("Graphical MP per sku")
st.pyplot(fig_mrp)

# Save plot to BytesIO buffer
buf = io.BytesIO()
fig_mrp.savefig(buf, format="png", dpi=300, bbox_inches='tight')
buf.seek(0)

# Streamlit download button
st.download_button(
    label="📥 Download material planning as PNG",
    data=buf,
    file_name=f'mp_{option_sku}.png',
    mime="image/png"
)

st.header("Required purchases")
st.pyplot(fig_purchases)

# Save plot to BytesIO buffer
buf = io.BytesIO()
fig_purchases.savefig(buf, format="png", dpi=300, bbox_inches='tight')
buf.seek(0)

# Streamlit download button
st.download_button(
    label="📥 Download purchases as PNG",
    data=buf,
    file_name=f'p_{option_sku}.png',
    mime="image/png"
)

#showing tabular data
st.header("Tabular MP per sku")
st.dataframe(df_final.T)

@st.cache_data
def convert_df(df):
    # Convert DataFrame to CSV in memory with UTF-8 BOM encoding
    output = io.BytesIO()
    df.to_csv(output, index=True, encoding='utf-8-sig')  # <-- BOM added here
    return output.getvalue()

csv_00 = convert_df(df_final)
st.download_button(
   "📥 Download dataframe (.csv)",
   csv_00,
   f'dataframe_{option_sku}.csv',
   "text/csv",
   key='download-csv-00'
)




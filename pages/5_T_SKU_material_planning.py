#%% Importing packages

import streamlit as st
import io
from datetime import datetime

import re
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

st.title('SKUs emergencies')

# Company and sku selection

# company selection
options_companies= [
    'eegsa',
    'trelec',
    'amesa',
    'energica',
    'all']

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
    
    # Define colors (contrast-friendly)
    colors = {
        'reorder': '#2ca02c',     # green
        'safety': '#d62728',      # red
        'min_stock': '#9467bd',   # purple
        'inventory_line': '#1f77b4',  # blue
    }
    
    grid_color = '#f0f0f0'
    plotly_template = 'plotly_dark'
    text_color = 'black'

    #%% Interactive MRP plot with Plotly
    
    # ---- MRP Plot ----
    fig_mrp = go.Figure()
    
    # Inventory within month
    for j in range(int_window - 1):
        if j == 0:
          fig_mrp.add_trace(go.Scatter(
              x=[j, j],
              y=[npa_mrp[col_index_dict['inventory_initial_new&ra'], j],
                 npa_mrp[col_index_dict['inventory_final_new&ra'], j]],
              mode='lines',
              line=dict(color=colors["inventory_line"], dash='dash', width=1),
              name="Inventory Flow",  # <-- Legend label
              showlegend=True         # <-- Show legend
              ))
        else:        
             fig_mrp.add_trace(go.Scatter(
                x=[j, j],
                y=[npa_mrp[col_index_dict['inventory_initial_new&ra'], j],
                   npa_mrp[col_index_dict['inventory_final_new&ra'], j]],
                mode='lines',
                line=dict(color=colors["inventory_line"], dash='dash', width=1),
                showlegend=False
            ))
    
    # Inventory across months
    for j in range(int_window - 1):
        fig_mrp.add_trace(go.Scatter(
            x=[j, j + 1],
            y=[npa_mrp[col_index_dict['inventory_final_new&ra'], j],
               npa_mrp[col_index_dict['inventory_initial_new&ra'], j + 1]],
            mode='lines',
            line=dict(color=colors["inventory_line"], dash='dash', width=1),
            showlegend=False
        ))
    
    # RP, SS, Min stock
    fig_mrp.add_trace(go.Scatter(
        y=npa_mrp[col_index_dict['rp_inventory'], :],
        x=np.arange(int_window),
        name='Reorder Point',
        line=dict(color=colors["reorder"], width=2)
    ))
    
    fig_mrp.add_trace(go.Scatter(
        y=npa_mrp[col_index_dict['ss_inventory'], :],
        x=np.arange(int_window),
        name='Safety Stock',
        line=dict(color=colors["safety"], width=2)
    ))
    
    fig_mrp.add_trace(go.Scatter(
        y=npa_mrp[col_index_dict['demand_min_stock'], :],
        x=np.arange(int_window),
        name='Min Stock',
        line=dict(color=colors["min_stock"], width=2)
    ))
    
    # Layout
    
    fig_mrp.update_layout(
        title=dict(text=f'MRP for {option_sku}', font=dict(color=text_color)),
        paper_bgcolor='white',  # Full background
        plot_bgcolor='white',   # Plot area
        # legend=dict(
        #     font=dict(
        #         color='black'
        #         )
        #     ),
        
        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color=text_color)
            ),
        xaxis=dict(
            tickmode='array',
            tickvals=np.arange(int_window),
            ticktext=df_final.index.tolist(),
            tickangle=45,
            tickfont=dict(size=8, color=text_color),
            title=dict(text='year_month', font=dict(color=text_color)),
            range=[-0.5, int_window - 1 + 0.5],
            showgrid=True,
            gridcolor=grid_color,   # Dynamic grid color based on theme
            gridwidth=1
        ),
        yaxis=dict(
            title=dict(text='Inventory (#)', font=dict(color=text_color)),
            tickfont=dict(size=8, color=text_color),
            showgrid=True,
            gridcolor=grid_color,   # Dynamic grid color based on theme
            gridwidth=1
        ),
        template=plotly_template,  # Dynamic Plotly template based on theme
        height=500,
        margin=dict(l=60, r=40, b=80, t=60)
    )
    
#%%
    # ---- Purchases Plot ----
    fig_purchases = go.Figure()

    # Purchases bar plot
    fig_purchases.add_trace(go.Bar(
        x=df_final.index,
        y=df_final['inventory_purchase'],
        marker=dict(
        color='lightblue',
        line=dict(width=0)  # Removes the black border
        ),
        name="Purchases"
    ))
    
    # Layout for purchases plot with dynamic theme and grid color
    fig_purchases.update_layout(
        title=dict(text=f'Purchase Amounts for {option_sku}', font=dict(color=text_color)),
        paper_bgcolor='white',  # Full background
        plot_bgcolor='white',   # Plot area
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=8, color=text_color),
            title=dict(text='year_month', font=dict(color=text_color)),
            range=[-0.5, int_window - 1 + 0.5],
            tickmode='array',
            tickvals=list(range(len(df_final.index))),
            ticktext=df_final.index.tolist(),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            #rangeslider=dict(visible=True),  # Add zoom/scroll
            type='category'  # Ensures discrete ticks
            ),
        yaxis=dict(
            title=dict(text='Total Purchase Amount (#)', font=dict(color=text_color)),
            tickfont=dict(size=8, color=text_color),
            showgrid=True,
            gridcolor=grid_color,   # Dynamic grid color based on theme
            gridwidth=1
            ),
        template=plotly_template,  # Dynamic Plotly template based on theme
        height=400,
        margin=dict(l=60, r=40, b=80, t=60)
    )
    
    #%% website
    
    # Display the MRP plot in Streamlit
    st.header(f'Graphical Material Planning for {option_company.upper()}')
    st.plotly_chart(fig_mrp, use_container_width=True)
    
    #date
    dt_now= datetime.now()
    dt_now= dt_now.strftime('%Y%m%d')
    
    st.header(f'Graphical required purchases for {option_company.upper()}')
    # Display the Purchases plot in Streamlit
    st.plotly_chart(fig_purchases, use_container_width=True)
    
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
    

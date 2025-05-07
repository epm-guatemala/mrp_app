#%% importing packages
import streamlit as st

#%% website content

st.title('Definitions')

st.markdown(
    """
    
    - demand min stock: Minimum required stock (if SKU is classified as MIN Stock) 
    [quantity]
    
    - demand project consumption: Deterministic quantity that the set of non-recurrent 
    projects will consume in a specific month [quantity/month]
    
    - demand recurrent consumption: Average historic consumption; its calculation period is company-dependent
    [quantity/month]
    
    - demand sales: Quantity requested from customers or sales channels during a given period
    [quantity/month]
    
    - inventory final new&ra: Final inventory including both new and refurbished materials
    (MAT-NUEVO + MAT-USADO) [quantity]
    
    - inventory initial new: New initial inventory (MAT-NUEVO) 
    [quantity]
    
    - inventory initial new&ra: New and refurbished initial inventory (MAT-NUEVO + MAT-USADO) 
    [quantity]
    
    - inventory initial ra: Refurbished initial inventory (MAT-USADO)
     [quantity]
    
    - inventory purchase: Quantity of inventory purchased during a period 
    [quantity/month]
    
    - inventory transit extern: Inventory in transit from external suppliers 
    [quantity]
    
    - inventory transit intern: Inventory in transit from internal suppliers 
    (intercompany) [quantity]
    
    - ltd inventory: Quantity of inventory that will be consumed during the 
    deterministic lead time, with historic consumption [quantity]
    
    - lt: Lead Time — the time between placing an order and receiving the goods 
    [time, months]
    
    - MRP: Material Requirements Planning — a system to calculate material needs 
    based on demand and supply planning [process/tool]
    
    - purchase type: Categorization of purchases based on origin, urgency, or type 
    (e.g., not emergency, emergency) [category]
    
    - rp inventory: Reorder Point inventory — the level at which new stock should 
    be ordered to avoid stockouts [quantity]
    
    - SKU: Stock Keeping Unit — a unique identifier for each distinct product 
    and service that can be purchased [identifier]
    
    - ss inventory: Safety Stock inventory — extra inventory held to mitigate risk of 
    stockouts caused by demand or supply variability [quantity]
    
    """
)



import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Bienvenido al MRP EPM Guatemala! 👋")

st.sidebar.success("Select a page")

st.markdown(
    """
    
    MP (Material planning - Quantity&Moment) EPM Guatemala es el proceso de cálculo periódico 
    (al menos mensual) mediante el cual se cuantifican y unifican las necesidades de adquisición de 
    material para todas las filiales del grupo EPM en Guatemala:
    
    - EEGSA
    - TRELEC
    - AMESA
    - Enérgica
    
    Cada material determinado como almacenable, puede tener cinco (5) formas
    excluyentes de aprovisionamiento (ninguna otra combinación es posible o permitida):
       
    - MTO
    - MRP + MTO
    - MRP
    - MIN
    - MIN + MTO
    
    Las cuales se basan de tres (3) métodos unitarios de planificación:
        
    - MTO (Make to Order): El área operativa planifica al menos el SKU, mes/año y 
    cantidad requerida en el proyecto, se adquieren solo esas cantidades.
    - MRP (Material Requirement Planning): El consumo esperado (-> promedio), variación del consumo (-> desviación 
    estándar), lead time esperado (-> promedio), variación del lead time (-> desviación 
    estándar) y un nivel de servicio (-> pdf Normal 95...99%) determinan la magnitud 
    del inventario de seguridad (ss), punto de reorden (rp) y la adquisición
    requerida en el tiempo.
    - MIN (Minimum inventory): En cualquier momento esta cantidad debería estar
    disponible en inventario.
    
    El MP de EPM Guatemala determina por material las cantidades y momentos
    de abastecimiento. Para ello tiene input y output variables, que abajo se 
    detallan:
        
    ### Input variables
    #### Inventory
    - initial (new & reconditioned)
    - transit (intercompany & providers)
    
    #### Demand
    - historic (-> expected value and variance)
    - project driven (-> deterministic demand)
    - sales (intercompany)
    
    #### System
    - Historic lead times (-> expected value and variance)
    - Service level (95% -> 99%)
    - Safety Stock
    - Reorder point
    - Lead time demand
    
    ### Output variables
    - Material purchases (quantities and moments)
    - Material purchase type (emergency / no emergency)
    - Monthly inventory (quantities and amount-GTQ)
    
"""
)


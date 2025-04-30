
import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Bienvenido al MRP EPM Guatemala! 👋")

st.sidebar.success("Select the page")

st.markdown(
    """
    MRP EPM Guatemala es el proceso de cálculo que unifica para EEGSA, TRELEC,
    AMESA y ENERGICA sus consumos recurrentes, consumos derivados de proyectos, 
    inventarios iniciales, inventarios en tránsito (externos y compraventas), 
    determinando las necesidades de abastecimiento de materiales (cantidades y momentos) 
    y simulando los inventarios finales en cantidades y monto monetario.
        
    ### Variables contenidas
    #### Inventario
    - inicial (nuevo)
    - inicial (reacondicionado)
    - inicial total (nuevo + reacondicionado)
    - en tránsito (externo y de fuente otras filiales)
    - en tránsito (externo y de fuente otras filiales)
    - compras de material (cantidades y momentos)
    - tipo de compra de material (emergencia o no emergencia)
    
    #### Demanda
    - recurrente
    - proyectos
    - ventas (externas y a otras filiales)
    
    #### Sistema
    - Tiempos de entrega (lead times)
    - Nivel de servicio (95%)
    - Inventario de seguridad (safety stock)
    - Consumo durante el tiemp de entrega (lead time demand)
    - Puntos de reorden (reorder point) 
"""
)



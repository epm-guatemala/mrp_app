
import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Bienvenido al MRP EPM Guatemala! 👋")

st.sidebar.success("Select the page")

st.markdown(
    """
    
    MP (Material planning - Quantity&Moment) EPM Guatemala es el proceso de cálculo periódico 
    (al menos mensual) mediante el cual se unifican las necesidades de adquisición de 
    material para todas las filiales del grupo EPM en Guatemala:
    
    - EEGSA
    - TRELEC
    - AMESA
    - Enérgica
    
    Cada material determinado como almacenable, puede tener cinco (5) formas
    excluyentes de aprovisionamiento (ninguna otra combinación es permitida):
       
    - MTO
    - MRP + MTO
    - MRP
    - MIN
    - MIN + MTO
    
    Las cuales se componen de tres (3) formas basales de aprovisionamiento:
        
    - MTO (Make to Order): El área operativa planifica al menos el SKU, mes/año y 
    cantidad requerida, se adquiere solo esas cantidades.
    - MRP (Material Requirement planning): El consumo esperado (-> promedio), variación del consumo (-> desviación 
    estándar), lead time esperado (-> promedio), variación del lead time (-> desviación 
    estándar) y un nivel de servicio (-> pdf Normal 95...99%) determinan la magnitud 
    del inventario de seguridad (ss), punto de reorden (rp) y la adquisición
    requerida.
    - MIN (Minimum inventory): En cualquier momento esta cantidad debería estar
    disponible en inventario.
    
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


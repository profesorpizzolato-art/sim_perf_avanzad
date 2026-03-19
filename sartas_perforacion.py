import streamlit as st

def modulo_sartas_api():
    st.title("🔩 CONFIGURACIÓN DE SARTA (API 5DP)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Especificaciones de Tubería")
        od_pipe = st.selectbox("OD Drill Pipe (in)", [3.5, 4.0, 4.5, 5.0, 5.5], index=3)
        grado = st.selectbox("Grado de Acero API", ["E-75", "X-95", "G-105", "S-135"])
        peso_nom = st.number_input("Peso Nominal (lb/ft)", value=19.5)

    # Base de datos de Fluencia (Yield Strength) por Grado
    yield_map = {"E-75": 75000, "X-95": 95000, "G-105": 105000, "S-135": 135000}
    
    # Cálculo de Tensión de Fluencia del Cuerpo (Body Yield)
    # Área aproximada para 5" 19.5 lb/ft es ~5.27 in2
    area_aprox = 5.27 
    tension_max = yield_map[grado] * area_aprox
    
    with col2:
        st.subheader("Límites de Diseño")
        st.metric("Resistencia a la Fluencia", f"{yield_map[grado]} psi")
        st.metric("Carga de Tensión Máxima", f"{int(tension_max)} lbs")
        
        sf = st.slider("Factor de Diseño (Safety Factor)", 1.0, 2.0, 1.1)
        st.info(f"Carga de Trabajo Permitida: {int(tension_max / sf)} lbs")

    st.divider()
    st.write("**Nota técnica:** Según API, el grado S-135 es el estándar para secciones horizontales en Vaca Muerta debido a su alta resistencia.")

import streamlit as st

def configuracion_ui():
    """
    Panel de configuración para el Instructor (Grado, Peso y OD).
    """
    st.subheader("⚙️ Configuración de Sarta (API 5DP)")
    
    col1, col2 = st.columns(2)
    with col1:
        # Se guarda en session_state para que persista durante la sesión de entrenamiento
        st.session_state.od_pipe = st.selectbox("OD Drill Pipe (in)", [3.5, 4.0, 4.5, 5.0, 5.5], index=3)
        st.session_state.grado_acero = st.selectbox("Grado de Acero API", ["E-75", "X-95", "G-105", "S-135"], index=3)
        st.session_state.peso_nom = st.number_input("Peso Nominal (lb/ft)", value=19.5)
    
    with col2:
        st.info("**Nota para Vaca Muerta:** El grado S-135 es el estándar para secciones horizontales debido a su alta resistencia.")

def modulo_sartas_api(piz):
    """
    Cálculo en tiempo real del Hook Load y límites de tensión.
    """
    # 1. Parámetros Técnicos (API 5DP)
    yield_map = {"E-75": 75000, "X-95": 95000, "G-105": 105000, "S-135": 135000}
    
    # Área de sección transversal para 5" 19.5 lb/ft (aprox 5.27 in2)
    # En versiones futuras podemos calcularla dinámicamente según el OD
    area_aprox = 5.27  
    
    grado = st.session_state.get("grado_acero", "S-135")
    peso_nom = st.session_state.get("peso_nom", 19.5)
    
    # 2. Resistencia Máxima (Cuerpo de la tubería)
    tension_max = yield_map[grado] * area_aprox
    
    # 3. Cálculo de Hook Load Dinámico
    # Profundidad de metros a pies
    prof_ft = piz.get("profundidad_actual", 0) * 3.28084
    
    # Factor de Flotabilidad (BF)
    # Basado en densidad del acero (65.5 ppg)
    densidad_lodo = piz.get("densidad_lodo", 9.5)
    buoyancy_factor = (65.5 - densidad_lodo) / 65.5
    
    # Peso en el gancho = (Profundidad * Peso Nominal) * BF
    peso_aire = prof_ft * peso_nom
    hook_load_real = peso_aire * buoyancy_factor
    
    return {
        "max_yield": tension_max,
        "hook_load": hook_load_real,
        "margen": tension_max - hook_load_real
    }

import streamlit as st

def render_bop_ui(pizarra):
    st.header("🛡️ Unidad de Control de Surgencias")
    
    # Estado dinámico
    es_cerrado = pizarra.get("bop_cerrado", False)
    estado_txt = "CERRADO" if es_cerrado else "ABIERTO (FLUYENDO)"
    color_bg = "#FF4B4B" if es_cerrado else "#28a745"
    
    st.markdown(f"""
        <div style="background-color:{color_bg}; padding:15px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">ESTADO DEL POZO: {estado_txt}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Mandos de Presión
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔴 CIERRE ANULAR", use_container_width=True, key="btn_anular"):
            pizarra["bop_cerrado"] = True
            st.rerun()
    with c2:
        if st.button("🔴 CIERRE RAMS", use_container_width=True, key="btn_rams"):
            pizarra["bop_cerrado"] = True
            st.rerun()
    with c3:
        if st.button("🟢 ABRIR POZO", use_container_width=True, key="btn_abrir"):
            pizarra["bop_cerrado"] = False
            st.rerun()

    # --- SECCIÓN TÉCNICA DE CONTROL (Ingeniería) ---
    if es_cerrado:
        st.divider()
        st.subheader("📋 Parámetros de Ahogo")
        
        col_ing1, col_ing2 = st.columns(2)
        
        with col_ing1:
            st.markdown("### 1. Registro de Presiones")
            # El alumno debe ingresar las presiones estabilizadas
            sidpp = st.number_input("SIDPP (Presión de Cierre TP) [psi]", 0, 3000, 500)
            sicp = st.number_input("SICP (Presión de Cierre TR) [psi]", 0, 3000, 800)
            st.caption("SIDPP: Shut-In Drill Pipe Pressure")
        
        with col_ing2:
            st.markdown("### 2. Cálculo de Ingeniería")
            # Fórmula de Control de Pozos
            tvd_ft = pizarra["profundidad_actual"] * 3.2808  # Convertimos a pies para la fórmula estándar
            mw_actual = pizarra["densidad_lodo"]
            
            # Cálculo del Lodo de Ahogo (Kill Mud Weight)
            kmw = mw_actual + (sidpp / (0.052 * tvd_ft))
            
            st.metric("Lodo de Ahogo Requerido (KMW)", f"{round(kmw, 2)} ppg", 
                      delta=f"{round(kmw - mw_actual, 2)} ppg extra")
            
        st.divider()
        st.subheader("⚙️ Método de Control Seleccionado")
        metodo = st.radio("Procedimiento:", 
                         ["Método del Perforador", "Esperar y Pesar"], 
                         horizontal=True)
        
        if st.button("🚀 INICIAR OPERACIÓN DE AHOGO", type="primary", use_container_width=True):
            st.warning(f"Iniciando {metodo}... Bombeando {round(kmw, 2)} ppg a emboladas constantes.")
            # Actualizamos la densidad en la pizarra
            pizarra["densidad_lodo"] = round(kmw, 2)
            pizarra["evento_activo"] = None # El pozo se estabiliza
            st.success("Presiones niveladas. Sistema normalizado.")

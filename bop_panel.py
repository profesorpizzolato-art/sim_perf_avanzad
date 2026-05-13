import streamlit as st

def render_bop_ui(pizarra):
    st.header("🛡️ Unidad de Control de Surgencias")
    
    # --- ESTADO FÍSICO DEL BOP ---
    estado = "CERRADO" if pizarra["bop_cerrado"] else "ABIERTO"
    color = "#FF4B4B" if pizarra["bop_cerrado"] else "#28a745"
    
    st.markdown(f"""
        <div style="background-color:{color}; padding:10px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">ESTADO DEL POZO: {estado}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- MANDOS DE CIERRE ---
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔴 CIERRE ANULAR", use_container_width=True):
            pizarra["bop_cerrado"] = True
            st.toast("Cerrando Anular...")
    with c2:
        if st.button("🔴 CIERRE RAMS", use_container_width=True):
            pizarra["bop_cerrado"] = True
            st.toast("Cerrando Rams...")
    with c3:
        if st.button("🟢 ABRIR POZO", use_container_width=True):
            pizarra["bop_cerrado"] = False
            st.success("Pozo Abierto - Monitorear flujo")

    # --- LÓGICA DE CONTROL DE POZOS (Solo si está cerrado) ---
    if pizarra["bop_cerrado"]:
        st.divider()
        st.subheader("📝 Protocolo de Control de Pozos")
        
        metodo = st.selectbox("Seleccione Método de Control", 
                             ["Seleccionar...", "Método del Perforador (Driller's Method)", "Esperar y Pesar (Wait & Weight)"])
        
        if metodo != "Seleccionar...":
            col_inf1, col_inf2 = st.columns(2)
            
            with col_inf1:
                st.info(f"**Estrategia:** {metodo}")
                sidpp = st.number_input("SIDPP (psi)", 0, 2000, 500)
                sicp = st.number_input("SICP (psi)", 0, 2000, 750)
                
            with col_inf2:
                # Cálculo dinámico de la nueva densidad de lodo (KMW)
                prof_vert = pizarra["profundidad_actual"] * 3.28084 # Convertir a pies para la fórmula estándar
                dens_actual = pizarra["densidad_lodo"]
                kmw = dens_actual + (sidpp / (0.052 * prof_vert))
                
                st.metric("Lodo de Ahogo (KMW)", f"{round(kmw, 2)} ppg")
                st.caption("Fórmula: MW + (SIDPP / (0.052 * TVD))")

            # Botón para iniciar la circulación de ahogo
            if st.button("🚀 Iniciar Circulación de Ahogo", type="primary"):
                st.warning("Iniciando bombeo de lodo pesado... Mantenga presión en el casing.")
                pizarra["densidad_lodo"] = round(kmw, 2)
                pizarra["evento_activo"] = None # Normaliza el sistema al terminar

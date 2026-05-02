import streamlit as st

def panel_instructor(piz):
    st.title("👨‍🏫 Mando Central de Instructor - MENFA 3.0")
    
    # SECCIÓN DE ÓRDENES TÉCNICAS
    st.subheader("📝 Órdenes Operativas")
    with st.container():
        orden = st.text_area("Dictar orden de perforación (ej: 'Mantener WOB en 35 klbs y observar torque'):")
        col_ord1, col_ord2 = st.columns(2)
        if col_ord1.button("🚀 ENVIAR ORDEN A CABINAS"):
            piz["mensaje_profesor"] = orden
            st.success("Orden transmitida.")
        if col_ord2.button("🧹 LIMPIAR RADIO"):
            piz["mensaje_profesor"] = ""

    st.divider()

    # GENERADOR DE FALLAS Y EVENTOS (Material Técnico)
    st.subheader("⚠️ Simulación de Eventos Críticos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.write("**Control de Presiones**")
        if st.button("🚨 ACTIVAR KICK", type="primary"):
            piz["evento_activo"] = "KICK"
            piz["alarma"] = True
            piz["mensaje_evento"] = "¡SURGENCIA! Ganancia en piletas detectada."
            
    with c2:
        st.write("**Fallas Mecánicas**")
        if st.button("⚙️ FALLA DE TREPANO"):
            piz["evento_activo"] = "BIT_WEAR"
            piz["factor_desgaste"] = 0.3 # Reduce el ROP drásticamente
            
    with c3:
        st.write("**Geología**")
        if st.button("📉 PÉRDIDA DE CIRC."):
            piz["evento_activo"] = "LOST_CIRC"
            piz["alarma"] = True

    st.divider()
    
    # CONTROL DE FORMACIÓN
    st.subheader("🌍 Configuración de Formación")
    piz["litologia"] = st.selectbox("Cambiar Capa Litológica:", 
                                   ["Areniscas Consolidadas", "Arcillas Plásticas", "Tobas y Cenizas", "Vaca Muerta (Shale)"])
    piz["gradiente"] = st.slider("Gradiente de Presión (psi/ft):", 0.40, 0.90, float(piz.get("gradiente", 0.44)))

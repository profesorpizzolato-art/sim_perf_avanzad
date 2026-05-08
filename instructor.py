import streamlit as st

def render_instructor_ui(piz):
    st.title("👨‍🏫 Consola de Control - Instructor")
    
    col_ctrl, col_fail = st.columns([1, 1])
    
    with col_ctrl:
        st.subheader("Controles de Perforación")
        piz["wob_maestro"] = st.slider("Ajustar WOB (klbs)", 0.0, 50.0, piz["wob_maestro"])
        piz["rpm_maestro"] = st.slider("Ajustar RPM", 0, 160, piz["rpm_maestro"])
        piz["caudal_maestro"] = st.slider("Caudal Bombas (GPM)", 0, 1200, piz["caudal_maestro"])
    
    with col_fail:
        st.subheader("Inyectar Fallas Técnicas")
        if st.button("🚨 DISPARAR KICK (Surgencia)", use_container_width=True):
            piz["evento_activo"] = "KICK"
            piz["alarma_activa"] = True
            
        if st.button("📉 PÉRDIDA DE RETORNO", use_container_width=True):
            piz["evento_activo"] = "PERDIDA"
            piz["alarma_activa"] = True
            
        if st.button("✅ NORMALIZAR SISTEMA", use_container_width=True, type="primary"):
            piz["evento_activo"] = None
            piz["alarma_activa"] = False
            piz["presion_base"] = 1200.0
            piz["nivel_tanques"] = 80.0

    if st.button("Cerrar Sesión Instructor"):
        st.session_state.autenticado = False
        st.rerun()

import streamlit as st
import time


def render_bop_ui(pizarra):  # <-- Asegurate que se llame así, todo en minúsculas
    st.write("### Consola de Control de Surgencias")

def bop_panel_module():
    st.title("🛡️ UNIDAD DE CIERRE - PANEL BOP")
    st.image("logo_menfa.png", width=100)
    
    presion_koomey = st.sidebar.slider("Presión Acumulador (psi)", 0, 3000, 2800)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CERRAR ANULAR", type="primary"):
            with st.status("Cerrando..."):
                time.sleep(2)
                st.success("✅ ANULAR SELLADO")
    with col2:
        if st.button("CERRAR PIPE RAMS"):
            st.warning("⚠️ RAMS TRABADOS")

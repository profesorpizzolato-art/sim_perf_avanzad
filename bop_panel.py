import streamlit as st

def render_bop_ui(pizarra):
    st.header("Panel de Control de Reventones")
    
    # Estado del pozo
    estado = "CERRADO" if pizarra["bop_cerrado"] else "ABIERTO (FLUYENDO)"
    color = "red" if pizarra["bop_cerrado"] else "green"
    st.markdown(f"### ESTADO DEL POZO: <span style='color:{color}'>{estado}</span>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔴 CERRAR ANULAR", use_container_width=True):
            pizarra["bop_cerrado"] = True
            st.toast("Cerrando BOP Anular...")
    with c2:
        if st.button("🔴 CERRAR RAMS", use_container_width=True):
            pizarra["bop_cerrado"] = True
    with c3:
        if st.button("🟢 ABRIR POZO", use_container_width=True):
            pizarra["bop_cerrado"] = False
            st.toast("Abriendo pozo...")
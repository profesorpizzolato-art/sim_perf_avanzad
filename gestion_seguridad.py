import streamlit as st
import base64
import os

def disparar_alarma_sonora():
    ruta_audio = "assets/alarma.mp3" 
    if os.path.exists(ruta_audio):
        with open(ruta_audio, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            html_audio = f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.components.v1.html(html_audio, height=0, width=0)

def render_bop_ui(piz):
    st.markdown("### 🛡️ CONTROL DE SURGENCIAS")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 CERRAR ANULAR", use_container_width=True):
            piz["bop_cerrado"] = True
            piz["alarma_activa"] = False
            piz["mensaje_evento"] = "POZO CERRADO SEGURO"
            st.rerun()
    with col2:
        if st.button("✅ ABRIR POZO", use_container_width=True):
            piz["bop_cerrado"] = False
            piz["mensaje_evento"] = "Operación Normal"
            st.rerun()

def aplicar_estilo_emergencia(piz):
    if piz.get("alarma_activa"):
        st.markdown("<style>.stApp {background-color: #440000 !important;}</style>", unsafe_allow_html=True)
        disparar_alarma_sonora()

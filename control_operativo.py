import streamlit as st

def panel_instructor(piz):
    st.title("👨‍🏫 Panel del Instructor - Clase Virtual MENFA")
    
    # Chat / Instrucciones
    st.subheader("📢 Comunicación en Vivo")
    msg = st.text_input("Enviar instrucción técnica a los alumnos:")
    if st.button("Transmitir"):
        piz["mensaje_profesor"] = msg
        st.success("Mensaje enviado a las cabinas.")

    st.divider()

    # Generador de Eventos
    st.subheader("⚠️ Disparador de Crisis")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚨 ACTIVAR KICK", type="primary"):
            piz["evento_activo"] = "KICK"
            piz["alarma"] = True
    with col2:
        if st.button("📉 PÉRDIDA TOTAL"):
            piz["evento_activo"] = "PERDIDA"
    with col3:
        if st.button("✅ NORMALIZAR"):
            piz["evento_activo"] = None
            piz["alarma"] = False

    st.divider()
    # Control de Geología en tiempo real
    piz["litologia_actual"] = st.selectbox("Cambiar Formación:", ["Arcillosa", "Arenisca", "Vaca Muerta (Shale)"])

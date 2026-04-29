import streamlit as st

def panel_instructor(piz):
    st.title("👨‍🏫 Panel de Control del Instructor (MENFA)")
    
    st.info("Desde aquí controlás los eventos que los alumnos verán en sus cabinas.")

    # --- ESTADO DEL SISTEMA ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Alumnos Conectados", len(piz.get("alumnos_activos", {})))
    with col2:
        st.metric("Estado del Pozo", "PELIGRO" if piz.get("evento_activo") else "NORMAL")
    with col3:
        st.metric("BOP", "CERRADO" if piz.get("bop_cerrado") else "ABIERTO")

    st.divider()

    # --- DISPARADOR DE EVENTOS ---
    st.subheader("⚠️ Simulación de Fallas y Surgencias")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("🚨 ACTIVAR KICK (SURGENCIA)", use_container_width=True):
            piz["evento_activo"] = "KICK"
            piz["mensaje_evento"] = "¡ALERTA! Aumento de presión en fondo detectado."
            piz["alarma"] = True
            st.warning("Kick activado. Los alumnos verán un aumento en el nivel de tanques.")

        if st.button("📉 ACTIVAR PÉRDIDA DE CIRCULACIÓN", use_container_width=True):
            piz["evento_activo"] = "PERDIDA"
            piz["mensaje_evento"] = "¡ALERTA! Caída de presión y pérdida de retorno."
            st.error("Pérdida de circulación activada.")

    with c2:
        if st.button("✅ NORMALIZAR POZO", use_container_width=True):
            piz["evento_activo"] = None
            piz["mensaje_evento"] = "Operación Normal"
            piz["alarma"] = False
            st.success("Pozo estabilizado.")

    st.divider()

    # --- CONTROL DE SEGURIDAD ---
    st.subheader("🛡️ Control de BOP (Solo Instructor)")
    if piz.get("bop_cerrado"):
        if st.button("ABRIR BOP", type="primary"):
            piz["bop_cerrado"] = False
            st.rerun()
    else:
        if st.button("CERRAR BOP (Shut-In)", type="secondary"):
            piz["bop_cerrado"] = True
            st.rerun()

    # --- MENSAJES A LOS ALUMNOS ---
    st.subheader("💬 Mensaje a la Cabina")
    mensaje = st.text_input("Enviar instrucción técnica:")
    if st.button("Enviar"):
        piz["mensaje_profesor"] = mensaje
        st.success("Mensaje enviado.")

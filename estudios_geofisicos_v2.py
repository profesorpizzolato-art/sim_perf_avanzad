def modulo_geofisica_lwd():
    st.title("🧪 EVALUACIÓN GEOFÍSICA LWD")
    
    tipo_lodo = st.radio("Fluido de Perforación:", ["Base Agua (WBM)", "Base Aceite (OBM)"])
    
    st.write("### Lecturas de Registros Eléctricos")
    
    if tipo_lodo == "Base Aceite (OBM)":
        st.info("💡 Nota: En lodos OBM se requieren herramientas de inducción magnética ya que el lodo no es conductor.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Resistividad Somera", "15.4 Ohm-m")
    with c2:
        st.metric("Resistividad Profunda", "120.2 Ohm-m")
        st.success("🎯 Hidrocarburo Detectado (Alta Resistividad)")

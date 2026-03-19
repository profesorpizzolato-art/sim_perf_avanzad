def modulo_well_control_api():
    st.title("🛡️ CONTROL DE POZOS - NORMATIVA API S53")
    
    metodo = st.selectbox("Método de Matanza:", ["Método del Perforador", "Esperar y Pesar (Engineer's Method)"])
    
    st.write("### Hoja de Matanza (Kill Sheet)")
    col1, col2 = st.columns(2)
    with col1:
        sidpp = st.number_input("SIDPP (psi)", 0, 2000, 500)
        sicp = st.number_input("SICP (psi)", 0, 2000, 750)
    with col2:
        st.metric("Presión de Fondo (BHP)", f"{sidpp + 1500} psi")
        st.metric("Máxima Presión Anular", "2500 psi")

    if sicp > 2000:
        st.error("🚨 RIESGO DE FRACTURA EN EL ZAPATO (Shoe Failure)")

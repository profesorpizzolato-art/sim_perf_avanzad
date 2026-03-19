def calcular_riesgo_kick(depth, mud_weight, gradiente_yac):
    st.title("🛡️ MONITOREO DE WELL CONTROL (API S53)")
    
    # Presión de Formación vs Presión Hidrostática
    presion_formacion = depth * 3.28 * gradiente_yac
    presion_hidrostatica = depth * 3.28 * 0.052 * mud_weight
    
    overbalance = presion_hidrostatica - presion_formacion
    
    st.write(f"### Balance de Presiones a {depth} m")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Presión de Formación", f"{int(presion_formacion)} psi")
    with col2:
        st.metric("Presión Hidrostática", f"{int(presion_hidrostatica)} psi", 
                  delta=f"{int(overbalance)} psi", delta_color="normal")

    if overbalance < 200:
        st.error("🚨 MARGEN DE SEGURIDAD BAJO: Riesgo de influjo (Kick). Aumentar densidad de lodo.")
    elif overbalance > 1000:
        st.warning("⚠️ SOBREPRESIÓN: Riesgo de pérdida de circulación por fractura.")
    else:
        st.success("✅ POZO BALANCEADO: Operación segura.")

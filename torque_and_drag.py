def modulo_torque_drag(depth, incl, mud_weight):
    st.title("🏗️ ANÁLISIS DE TORQUE & DRAG (API RP 7G)")
    
    # Constantes de Tubería (DP 5" S-135)
    tensile_yield = 560000 # lbs (Límite elástico)
    makeup_torque = 28000  # ft-lb
    
    # Cálculo simplificado de fricción
    factor_friccion = 0.25 # Lodo base agua
    hook_load_estatico = (depth * 22) * (1 - (mud_weight/65.5))
    drag_subida = hook_load_estatico * (1 + factor_friccion * np.sin(np.radians(incl)))
    
    st.subheader("Límites de Operación")
    c1, c2 = st.columns(2)
    c1.metric("Hook Load Esperado", f"{int(drag_subida)} lbs")
    c2.metric("Margen de Tensión", f"{int(tensile_yield - drag_subida)} lbs")
    
    if drag_subida > (tensile_yield * 0.8):
        st.error("🚨 ALERTA: Superando el 80% del límite elástico de la sarta.")
    else:
        st.success("✅ Cargas dentro de diseño API.")

def modulo_torque_drag_avanzado(depth, inc):
    st.title("🎢 TORQUE & DRAG - MECÁNICA AVANZADA")
    
    st.markdown("### Análisis de Pandeo (Buckling)")
    
    # Simulación de carga axial
    carga_axial = st.slider("Carga de Compresión (lbs)", 0, 50000, 15000)
    
    # Límite de Pandeo Sinusoidal (Simplificado)
    limite_buckling = 25000 
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if carga_axial > limite_buckling:
            st.error("🚨 CRÍTICO: PANDEO SINUSOIDAL DETECTADO")
            st.write("Riesgo de pegadura de tubería y falla de fatiga.")
        else:
            st.success("✅ Sarta en estabilidad elástica.")

    with col_b:
        # Gráfico de Torque vs Profundidad
        depths = np.linspace(0, depth, 20)
        torque_line = depths * 1.5 * np.sin(np.radians(inc))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=torque_line, y=depths, name="Torque Proyectado", line=dict(color='orange')))
        fig.update_layout(title="Perfil de Torque", yaxis=dict(autorange="reversed"), template="plotly_dark")
        st.plotly_chart(fig)

def modulo_geofisica():
    st.title("🧪 EVALUACIÓN GEOFÍSICA (Logging)")
    
    st.info("Simulación de perfiles eléctricos de pozo abierto.")
    
    depths = np.linspace(2800, 2900, 100)
    resistividad = 10**(np.random.normal(1, 0.5, 100)) # Escala logarítmica
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=resistividad, y=depths, name="Resistividad (Ohm-m)"))
    fig.update_xaxes(type="log")
    fig.update_layout(title="Perfil de Resistividad (Inducción)", yaxis=dict(autorange="reversed"))
    
    st.plotly_chart(fig)
    st.write("**Interpretación:** Resistividades > 20 Ohm-m indican presencia de Hidrocarburos.")

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
import plotly.graph_objects as go
import numpy as np

def calcular_curvas_esfuerzo(wob, rpm):
    # Simulación de límites de la sarta (Grado S-135)
    torque_limite = 35.0  # kft-lb
    tension_limite = 450.0 # klbs
    
    # El torque real sube con el WOB y las RPM
    torque_real = (wob * 0.4) + (rpm * 0.05) + 5.0
    
    # Crear gráfico de Dona o Indicador de Esfuerzo
    fig = go.Figure()
    
    # Añadimos una línea de tendencia de torque vs profundidad simulada
    profundidades = np.linspace(0, 4000, 20)
    torque_puntos = (profundidades * 0.005) + torque_real
    
    fig.add_trace(go.Scatter(
        x=torque_puntos, y=profundidades,
        mode='lines+markers',
        name='Torque Actual',
        line=dict(color='#ffcc00', width=3)
    ))
    
    # Línea de límite de seguridad
    fig.add_vline(x=torque_limite, line_dash="dash", line_color="red", annotation_text="Límite Sarta")

    fig.update_layout(
        title="⚙️ Análisis de Torque & Drag",
        xaxis=dict(title="Torque (kft-lb)", range=[0, 45]),
        yaxis=dict(title="Profundidad (m)", autorange="reversed"),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Simulación de trayectoria vertical y luego curva
    z = np.linspace(0, profundidad_actual, 100)
    x = np.where(z < 1500, 0, (z - 1500)**1.5 / 500) # Empieza a desviarse a los 1500m
    
    fig = go.Figure()
    # Línea de diseño (Target)
    fig.add_trace(go.Scatter(x=x*1.1, y=z, name="Target Plan", line=dict(color='gray', dash='dash')))
    # Línea real
    fig.add_trace(go.Scatter(x=x, y=z, name="Bit Position", line=dict(color='yellow', width=4)))
    
    fig.update_layout(
        title="Navegación en Tiempo Real",
        yaxis=dict(autorange="reversed", title="Profundidad (m)"),
        xaxis=dict(title="Desplazamiento Horizontal (m)"),
        template="plotly_dark",
        height=500
    )
    return fig
    
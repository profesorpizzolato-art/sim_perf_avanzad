import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Simulación de trayectoria: Vertical hasta 2500m, luego curva hacia horizontal
    z = np.linspace(0, profundidad_actual, 100)
    # --- CORRECCIÓN MATEMÁTICA PARA EVITAR EL WARNING ---
# Usamos np.maximum para asegurarnos de que el número nunca sea menor a 0 antes de elevarlo
diferencia = np.maximum(0, z - 2500)
x = diferencia**1.5 / 50  # Ahora ya no dará error con valores menores a 2500
    
    fig = go.Figure()
    
    # Dibujar el pozo
    fig.add_trace(go.Scatter(
        x=x, y=z, 
        mode='lines', 
        name='Trayectoria Real',
        line=dict(color='#00ff00', width=4)
    ))
    
    # Formateo del gráfico para que parezca una consola de perforación
    fig.update_layout(
        title="🛰️ Monitoreo de Geonavegación (LWD)",
        xaxis=dict(title="Desplazamiento Lateral (m)", gridcolor='gray'),
        yaxis=dict(title="Profundidad (m)", autorange="reversed", gridcolor='gray'),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

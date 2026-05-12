import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Generamos 100 puntos desde la superficie hasta la profundidad actual
    z = np.linspace(0, profundidad_actual, 100)
    
    # CORRECCIÓN MATEMÁTICA: 
    # Usamos np.maximum para que cualquier valor menor a 1500 sea 0.
    # Así evitamos elevar números negativos a la 1.5.
    delta_z = np.maximum(0, z - 1500)
    x = (delta_z**1.5) / 500 
    
    fig = go.Figure()
    
    # Línea de diseño (Target Plan) - Una referencia visual del objetivo
    fig.add_trace(go.Scatter(
        x=x*1.1, 
        y=z, 
        name="Trayectoria Planificada", 
        line=dict(color='rgba(150, 150, 150, 0.5)', dash='dash')
    ))
    
    # Línea real (Bit Position)
    fig.add_trace(go.Scatter(
        x=x, 
        y=z, 
        name="Posición del Trépano", 
        line=dict(color='#FFD700', width=4) # Amarillo dorado para visibilidad
    ))
    
    fig.update_layout(
        title="🛰️ Monitoreo de Geonavegación (KOP @ 1500m)",
        yaxis=dict(
            autorange="reversed", 
            title="Profundidad Vertical (TVD) [m]",
            gridcolor='dimgray'
        ),
        xaxis=dict(
            title="Desplazamiento Lateral [m]",
            gridcolor='dimgray',
            zeroline=True,
            zerolinecolor='white'
        ),
        template="plotly_dark",
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

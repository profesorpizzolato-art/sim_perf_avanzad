import plotly.graph_objects as go
import numpy as np

def generar_grafico_trayectoria(profundidad_actual):
    # Profundidad total del diseño del pozo (Target Final)
    profundidad_total_diseno = 3500.0
    
    # 1. TRAYECTORIA PLANIFICADA (Fija hasta el fondo para referencia del alumno)
    z_plan = np.linspace(0, profundidad_total_diseno, 200)
    delta_z_plan = np.maximum(0, z_plan - 1500)
    x_plan = (delta_z_plan**1.5) / 500
    
    # 2. TRAYECTORIA REAL (Se va dibujando dinámicamente hasta donde está el trépano)
    # Usamos un paso fijo (cada 10 metros) para evitar deformaciones de curva
    pasos = int(max(10, profundidad_actual / 10))
    z_real = np.linspace(0, profundidad_actual, pasos)
    delta_z_real = np.maximum(0, z_real - 1500)
    x_real = (delta_z_real**1.5) / 500 

    fig = go.Figure()
    
    # Línea de diseño (Target Plan) - Estática y referencial
    fig.add_trace(go.Scatter(
        x=x_plan * 1.1, 
        y=z_plan, 
        name="Trayectoria Planificada (Target)", 
        line=dict(color='rgba(150, 150, 150, 0.4)', dash='dash', width=2)
    ))
    
    # Línea real (Bit Position) - Se desplaza en vivo
    fig.add_trace(go.Scatter(
        x=x_real, 
        y=z_real, 
        name="Posición Real del Trépano", 
        line=dict(color='#FFD700', width=4) # Amarillo dorado
    ))
    
    # Marcador del Trépano (Un punto gordo al final de la línea real)
    if len(x_real) > 0:
        fig.add_trace(go.Scatter(
            x=[x_real[-1]], 
            y=[z_real[-1]], 
            name="Trépano / BHA",
            mode="markers",
            marker=dict(color='red', size=10, symbol='triangle-down')
        ))
    
    fig.update_layout(
        title="🛰️ Monitoreo de Geonavegación en Tiempo Real (KOP @ 1500m)",
        yaxis=dict(
            autorange="reversed", 
            title="Profundidad Vertical (TVD) [m]",
            gridcolor='dimgray',
            range=[profundidad_total_diseno + 100, 0] # Mantiene la escala visual fija
        ),
        xaxis=dict(
            title="Desplazamiento Lateral [m]",
            gridcolor='dimgray',
            zeroline=True,
            zerolinecolor='white',
            range=[-50, max(x_plan) * 1.3] # Mantiene la escala horizontal estable
        ),
        template="plotly_dark",
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

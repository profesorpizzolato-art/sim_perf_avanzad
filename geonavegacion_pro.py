import plotly.graph_objects as go
import numpy as np
import streamlit as st

def generar_grafico_trayectoria(profundidad_actual):
    # Profundidad total del diseño del pozo (Target Final)
    profundidad_total_diseno = 3500.0
    
    # 1. TRAYECTORIA PLANIFICADA (Fija hasta el fondo para referencia del alumno)
    z_plan = np.linspace(0, profundidad_total_diseno, 200)
    delta_z_plan = np.maximum(0, z_plan - 1500)
    x_plan = (delta_z_plan**1.5) / 500
    
    # 2. TRAYECTORIA REAL CALCULADA (Física Cognitiva)
    # En lugar de calcar la teórica, reconstruimos la curva real basada en el historial de navegación
    z_real = []
    x_real = []
    
    if "historial_gamma" in st.session_state and len(st.session_state.historial_gamma) > 0:
        # Extraemos los datos registrados por el alumno en la simulación
        # Cada registro contiene: (profundidad, gamma, inclinacion)
        datos = sorted(st.session_state.historial_gamma, key=lambda x: x[0])
        
        # Punto inicial en la superficie (0,0) con el pozo vertical
        z_acum = 0.0
        x_acum = 0.0
        z_real.append(z_acum)
        x_real.append(x_acum)
        
        for i in range(1, len(datos)):
            md_anterior, _, inc_anterior = datos[i-1]
            md_actual, _, inc_actual = datos[i]
            
            delta_md = md_actual - md_anterior
            if delta_md <= 0:
                continue
                
            # Promedio angular para el paso de cálculo (Base matemática de agrimensura)
            ang_promedio = np.radians((inc_anterior + inc_actual) / 2.0)
            
            # Si la profundidad es menor al KOP (1500m), forzamos que caiga vertical directo
            if md_actual < 1500:
                z_acum += delta_md
                x_acum += 0.0
            else:
                # Ecuaciones trigonométricas de descomposición de vectores
                # Inclinación 90° = Perforación puramente horizontal
                z_acum += delta_md * np.cos(ang_promedio)
                x_acum += delta_md * np.sin(ang_promedio)
                
            z_real.append(z_acum)
            x_real.append(x_acum)
    else:
        # Resguardo analítico por si el historial no se ha inicializado todavía
        pasos = int(max(10, profundidad_actual / 10))
        z_real = list(np.linspace(0, profundidad_actual, pasos))
        delta_z_real = np.maximum(0, np.array(z_real) - 1500)
        x_real = list((delta_z_real**1.5) / 500)

    fig = go.Figure()
    
    # Línea de diseño (Target Plan) - Estática y referencial
    fig.add_trace(go.Scatter(
        x=x_plan, 
        y=z_plan, 
        name="Trayectoria Planificada (Target)", 
        line=dict(color='rgba(150, 150, 150, 0.4)', dash='dash', width=2)
    ))
    
    # Línea real (Bit Position) - Refleja si el alumno se desvió del target o no
    fig.add_trace(go.Scatter(
        x=x_real, 
        y=z_real, 
        name="Trayectoria Real Ejecutada", 
        line=dict(color='#FFD700', width=4) # Amarillo dorado corporativo
    ))
    
    # Marcador del Trépano (Un punto gordo al final de la línea real)
    if len(x_real) > 0:
        fig.add_trace(go.Scatter(
            x=[x_real[-1]], 
            y=[z_real[-1]], 
            name="Trépano / BHA Activo",
            mode="markers",
            marker=dict(color='red', size=12, symbol='triangle-down')
        ))
    
    fig.update_layout(
        title="🛰️ Monitoreo de Geonavegación Dinámica (KOP @ 1500m)",
        yaxis=dict(
            autorange="reversed", 
            title="Profundidad Vertical Verdadera (TVD) [m]",
            gridcolor='dimgray',
            range=[profundidad_total_diseno + 100, 0] # Escala fija anti-deformación
        ),
        xaxis=dict(
            title="Desplazamiento Horizontal Calculado [m]",
            gridcolor='dimgray',
            zeroline=True,
            zerolinecolor='white',
            range=[-50, max(x_plan) * 1.3] # Mantiene la perspectiva estable
        ),
        template="plotly_dark",
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

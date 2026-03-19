import streamlit as st
import numpy as np
import plotly.graph_objects as go

def modulo_geonavegacion():
    st.title("📡 GEOSTEERING & CORRELACIÓN LWD")
    
    # Parámetros de formación (Vaca Muerta)
    target_depth = 2850 # TVD metros
    espesor_capa = 15    # Ventana de navegación
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Lecturas de Fondo")
        gr = st.slider("Gamma Ray (API)", 0, 250, 145)
        inc = st.number_input("Inclinación MWD (°)", 0.0, 110.0, 89.5)
        
        # Lógica de Alarma API
        if gr > 120:
            st.success("🎯 DENTRO DE PAY-ZONE (Shale Rico)")
        elif gr < 80:
            st.error("⚠️ SALIDA POR TECHO (Caliza/Siltstone)")
        else:
            st.warning("⚖️ ZONA DE TRANSICIÓN")

    with col2:
        # Gráfico de Correlación
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[80, 80, 180, 180, 80], y=[2840, 2860, 2860, 2840, 2840], 
                                 fill="toself", name="Target Window", line_color='green', opacity=0.3))
        fig.add_trace(go.Scatter(x=[gr], y=[target_depth], mode='markers+text', 
                                 text=["TRÉPANO"], textposition="top center", marker=dict(size=15, color='red')))
        fig.update_layout(title="Posición en Reservorio", xaxis_title="Gamma Ray", yaxis_title="TVD", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig)

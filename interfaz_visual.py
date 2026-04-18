import streamlit as st
import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"<b>{titulo}</b><br>{unidad}"},
        gauge={'axis': {'range': [0, max_val]}, 'bar': {'color': color}}
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

def render_manual_menfa():
    with st.expander("📖 MANUAL DEL SISTEMA V3.0"):
        st.write("""
        **Bienvenido al Simulador IPCL MENFA**
        - El instructor controla los parámetros globales.
        - Ante una alarma sonora (Kick), debe cerrar el BOP inmediatamente.
        - Al finalizar, genere su reporte PDF en el botón lateral.
        """)

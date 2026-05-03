import streamlit as st
import pandas as pd
import numpy as np
import time
import base64
import os
import sys
from datetime import datetime
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero) ---
st.set_page_config(page_title="MENFA 3.0 - Mendoza Oil Industry", layout="wide", page_icon="🏗️")

# --- 2. MEMORIA COMPARTIDA (PIZARRA MAESTRA) ---
@st.cache_resource
def conectar_pizarra_maestra():
    return {
        "profundidad_actual": 2500.0,
        "caudal_maestro": 500.0,
        "wob_maestro": 0.0,
        "rpm_maestro": 0.0,
        "torque_maestro": 0.0,
        "presion_base": 1200.0,
        "densidad_maestra": 10.2,
        "piletas_nivel": 450.0,
        "evento_activo": None,
        "alarma_activa": False,
        "bop_cerrado": False,
        "mensaje_evento": "Operación Normal",
        "alumnos_activos": {}
    }

piz = conectar_pizarra_maestra()

# --- 3. LÓGICA DE AUTENTICACIÓN ---
PASSWORD_ALUMNO = "alumno2026"
USUARIOS_ALUMNOS = ["Usubiaga", "Flores", "Moya", "Perez", "Paredes", "Casanueva", "Pizzolato", "Villalba", "Invitado"]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # ... (Aquí va tu código de Login con las pestañas Alumno/Instructor)
    st.stop()

# --- 4. SISTEMA DE LATIDO (AUTOREFRESH) ---
nombre_usuario = st.session_state.get("usuario", "anonimo")
st_autorefresh(interval=2000, key=f"latido_{nombre_usuario}")

# --- 5. FUNCIONES DE INTERFAZ (Gauges) ---
def crear_manometro(valor, titulo, unidad, max_val, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"<b>{titulo}</b><br><span style='font-size:0.8em'>{unidad}</span>"},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ]
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

# --- 6. PANEL DE CONTROL (SIDEBAR) ---
with st.sidebar:
    st.image("logo.menfa.png", use_container_width=True)
    st.title(f"👤 {st.session_state.usuario}")
    
    if st.session_state.rol == "instructor":
        st.header("👨‍🏫 Controles de Instructor")
        piz["caudal_maestro"] = st.slider("Caudal (GPM)", 0, 1200, int(piz["caudal_maestro"]))
        piz["rpm_maestro"] = st.slider("RPM", 0, 200, int(piz["rpm_maestro"]))
        piz["wob_maestro"] = st.slider("WOB (klbs)", 0, 100, int(piz["wob_maestro"]))
        
        if st.button("🚨 ACTIVAR KICK"):
            piz["alarma_activa"] = True
            piz["evento_activo"] = "KICK"
            piz["mensaje_evento"] = "¡SURGENCIA DETECTADA!"
            st.rerun()

# --- 7. CUERPO PRINCIPAL (TABS) ---
st.title("📟 Consola de Perforación Avanzada")

# Cálculos rápidos de física
hhp = (piz["presion_base"] * piz["caudal_maestro"]) / 1714

tab1, tab2, tab3, tab4 = st.tabs(["🎮 Consola", "🛡️ BOP", "🧪 Lodos", "🛰️ Geo"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(crear_manometro(piz["presion_base"], "Presión SPP", "PSI", 5000, "red"), key="main_spp")
    with col2:
        st.plotly_chart(crear_manometro(hhp, "Potencia", "HHP", 2000, "purple"), key="main_hhp")
    with col3:
        st.plotly_chart(crear_manometro(piz["rpm_maestro"], "Rotación", "RPM", 200, "green"), key="main_rpm")

# --- 8. SISTEMA DE ALARMA SONORA ---
if piz.get("alarma_activa"):
    st.error(f"🚨 {piz['mensaje_evento']}")
    # Inyectar audio HTML (debe estar en assets/alarma.mp3)

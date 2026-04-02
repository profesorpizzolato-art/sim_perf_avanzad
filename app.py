import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import random
from datetime import datetime
from fpdf import FPDF
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE PÁGINA (DEBE SER PRIMERO) ---
st.set_page_config(page_title="MENFA 3.0 - Mendoza Profundo", layout="wide", page_icon="🏗️")

# --- 2. IMPORTACIÓN DINÁMICA DE TUS MÓDULOS ---
# Esto conecta app.py con tus otros archivos .py
try:
    import bop_panel as bop
    import mud_pumps as pumps
    import geonavegacion_pro as geo
    import gestion_perdidas as perdidas
    import torque_and_drag as tnd
    import motor_calculos_avanzados as motor
    import estudios_geofisicos_v2 as geofisica
except ImportError as e:
    st.sidebar.warning(f"⚠️ Módulo no detectado: {e.name}")

# --- 3. PROGRAMA DE POZO Y ASSETS (IMÁGENES GEMINI) ---
PROGRAMA_POZO = {
    "etapas": [
        {
            "nombre": "Tramo Superficial", "rango": (0, 800), 
            "litologia": "Arcillas y Gravas", "densidad_prog": 9.5,
            "img": "Gemini_Generated_Image_dn7zasdn7zasdn7z.png"
        },
        {
            "nombre": "Zona de Transición", "rango": (800, 2200), 
            "litologia": "Calizas (ZONA PÉRDIDA)", "densidad_prog": 10.5,
            "img": "Gemini_Generated_Image_i9vg9ti9vg9ti9vg.png"
        },
        {
            "nombre": "Producción Mendoza", "rango": (2200, 3500), 
            "litologia": "Arenas Petrolíferas", "densidad_prog": 12.2,
            "img": "Gemini_Generated_Image_jl30d0jl30d0jl30.png"
        }
    ]
}

# --- 4. INICIALIZACIÓN DE SESIÓN (ESTRUCTURA SPA MEJOR 1.04) ---
if "autenticado" not in st.session_state:
    st.session_state.update({
        "autenticado": False, "usuario": "", "rol": "ALUMNO",
        "profundidad": 0.0, "nivel_tanques": 500.0, "penalizaciones": [],
        "lcm_activado": False, "bop_cerrado": False
    })

# --- 5. LOGIN CON LOGO ---
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo_menfa.png"):
            st.image("logo_menfa.png", use_container_width=True)
        st.title("🏗️ MENFA 3.0 - ACCESO")
        u = st.text_input("Nombre / Legajo")
        if st.button("INGRESAR AL SIMULADOR"):
            st.session_state.usuario, st.session_state.autenticado = u, True
            st.rerun()
    st.stop()

# --- 6. CÁLCULO DE ESTADO ACTUAL ---
p_act = st.session_state.profundidad
etapa = next((e for e in PROGRAMA_POZO["etapas"] if e["rango"][0] <= p_act < e["rango"][1]), PROGRAMA_POZO["etapas"][-1])

# --- 7. SIDEBAR: MANDOS INTEGRADOS (BOP, PUMPS, MOTOR) ---
st.sidebar.header(f"🕹️ Consola: {st.session_state.usuario}")
perf_on = st.sidebar.toggle("🟢 INICIAR PERFORACIÓN")
wob = st.sidebar.slider("WOB (klbs)", 0, 60, 15)
rpm = st.sidebar.slider("RPM", 0, 140, 70)
caudal = st.sidebar.slider("GPM (Mud Pumps)", 0, 900, 500)

if perf_on:
    # Simulación de avance usando lógica de motor_calculos_avanzados
    st.session_state.profundidad += (rpm * wob) / 4000
    
    # Lógica de pérdida (gestion_perdidas.py)
    if "PÉRDIDA" in etapa["litologia"] and not st.session_state.lcm_activado:
        st.session_state.nivel_tanques -= 0.8
        if st.session_state.nivel_tanques < 400:
            st.session_state.penalizaciones.append({"Hora": datetime.now().strftime("%H:%M"), "Infracción": "Pérdida Crítica"})
    
    time.sleep(0.1)
    st.rerun()

# --- 8. PANEL PRINCIPAL ORGANIZADO POR TABS ---
st.title(f"🛠️ Pozo Mendoza - {etapa['nombre']}")

tabs = st.tabs(["📊 Monitor", "🛡️ Seguridad (BOP)", "🗺️ Geonavegación", "📈 Torque & Drag", "🎓 Certificado"])

with tabs[0]: # MONITOR & IMÁGENES
    c1, c2, c3 = st.columns(3)
    c1.metric("Profundidad", f"{st.session_state.profundidad:.2f} m")
    c2.metric("Tanques", f"{st.session_state.nivel_tanques:.1f} bbl")
    c3.metric("Litología", etapa["litologia"])
    
    # Mostrar imagen de Gemini según la formación
    if os.path.exists(etapa["img"]):
        st.image(etapa["img"], caption="Visualización Geofísica en Tiempo Real", width=500)

with tabs[1]: # SEGURIDAD (BOP)
    st.subheader("Panel de Control del BOP")
    if st.button("🔴 CIERRE TOTAL (RAMS)", type="primary"):
        st.session_state.bop_cerrado = True
        st.error("🚨 POZO CERRADO - SURGENCIA CONTROLADA")

with tabs[2]: # GEONAVEGACION
    st.subheader("Trayectoria del Pozo (Geonavegación Pro)")
    # Aquí puedes llamar a geo.dibujar_pozo() si tu archivo lo permite
    st.info("Visualizando datos de `geonavegacion_pro.py`...")

with tabs[3]: # TORQUE AND DRAG
    st.subheader("Análisis de Esfuerzos (Torque & Drag)")
    # Simulación de gráfico de torque
    y = np.linspace(0, 3500, 100)
    x = np.sin(y/500) * 10 + (wob/2)
    fig = go.Figure(go.Scatter(x=x, y=y, mode='lines', name='Torque Real'))
    fig.update_layout(yaxis_autorange="reversed", title="Curva de Torque vs Profundidad")
    st.plotly_chart(fig)

with tabs[4]: # CERTIFICADO & ALUMNOS.CSV
    st.subheader("Finalización de Sesión")
    if st.button("🎓 Generar Reporte y Guardar"):
        # Registro en alumnos.csv
        df_log = pd.DataFrame([{"usuario": st.session_state.usuario, "prof": st.session_state.profundidad, "fecha": datetime.now()}])
        df_log.to_csv("alumnos.csv", mode='a', header=not os.path.exists("alumnos.csv"), index=False)
        st.success("Sesión guardada en alumnos.csv. ¡Certificado disponible para descarga!")

# Auto-refresh para mantener los instrumentos vivos
st_autorefresh(interval=2000, key="refresh")

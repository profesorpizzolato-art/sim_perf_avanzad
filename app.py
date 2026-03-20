import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import os
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="SIMULADOR MENFA V7.5 - ESTRENO", layout="wide")

# --- 2. INICIALIZACIÓN DE SESIÓN (ESTO EVITA EL ERROR 219) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "usuario" not in st.session_state: st.session_state.usuario = ""
if "legajo" not in st.session_state: st.session_state.legajo = ""
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "ROP": 0.0, "GR": 110, "TANQUES": 1200
    }])

# --- 3. PANTALLA DE ACCESO (REGISTRO AUTOMÁTICO) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #003366;'>🛡️ BIENVENIDOS AL IPCL MENFA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Simulador de Perforación - Estreno Cursada 2026</h3>", unsafe_allow_html=True)
    
    with st.container():
        c1, c2, c3 = st.columns([1,1.5,1])
        with c2:
            st.info("Complete sus datos para habilitar el examen y la certificación.")
            nombre_reg = st.text_input("Nombre y Apellido del Alumno:")
            dni_reg = st.text_input("DNI o Legajo Provisional:")
            
            if st.button("INGRESAR A CABINA", use_container_width=True):
                if nombre_reg and dni_reg:
                    st.session_state.usuario = nombre_reg
                    st.session_state.legajo = dni_reg
                    st.session_state.auth = True
                    st.success("Acceso concedido. Cargando parámetros de pozo...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Debe completar los datos para el registro de asistencia.")
    st.stop() # Bloquea el resto del código hasta que se registren

# --- 4. CUERPO DEL SIMULADOR (INTERFAZ SCADA) ---
curr = st.session_state.history.iloc[-1]

st.sidebar.image("https://img.icons8.com/color/96/oil-rig.png", width=80)
st.sidebar.title("CONTROLES")
st.sidebar.write(f"👤 **Op:** {st.session_state.usuario}")
st.sidebar.divider()

wob = st.sidebar.slider("WOB (klbs)", 0, 60, 20)
rpm = st.sidebar.slider("RPM", 0, 150, 80)

if st.sidebar.button("⏩ PERFORAR 300 METROS"):
    # Lógica de perforación simple
    n_prof = curr['DEPTH'] + 1.0
    nueva_fila = {
        "DEPTH": n_prof, "WOB": wob, "RPM": rpm,
        "ROP": (wob * rpm) / 500,
        "GR": random.randint(80, 120),
        "TANQUES": 1200 + (40 if random.random() < 0.05 else 0)
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
    st.rerun()

# --- TABS DE TRABAJO ---
tabs = st.tabs(["📊 SCADA", "🧪 LODOS", "🛡️ WELL CONTROL", "📖 EVALUACIÓN"])

with tabs[0]:
    st.subheader("Instrumentos de Perforación")
    col1, col2, col3 = st.columns(3)
    col1.metric("Profundidad", f"{curr['DEPTH']} m")
    col2.metric("WOB Actual", f"{curr['WOB']} klbs")
    col3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    
    # Gráfica de Perforación
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history['GR'], y=st.session_state.history['DEPTH'], mode='lines'))
    fig.update_layout(yaxis=dict(autorange="reversed", title="Profundidad (m)"), xaxis=dict(title="Gamma Ray"))
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.header("Cierre de Evaluación")
    if st.button("🏁 FINALIZAR TURNO Y GUARDAR"):
        # Guardado local
        if not os.path.exists("EXAMENES_MENFA"): os.makedirs("EXAMENES_MENFA")
        filename = f"EXAMENES_MENFA/Examen_{st.session_state.legajo}.csv"
        st.session_state.history.to_csv(filename, index=False)
        st.success(f"Archivo {filename} generado en el servidor local.")
        st.balloons()

# --- PANEL DEL INSTRUCTOR (FABRICIO) ---
with st.expander("🔐 PANEL DE INSTRUCTOR (FABRICIO)"):
    pass_doc = st.text_input("Clave Docente:", type="password")
    if pass_doc == "menfa2026":
        st.write("### Reportes de la Sesión")
        if os.path.exists("EXAMENES_MENFA"):
            archivos = os.listdir("EXAMENES_MENFA")
            st.write(f"Archivos recibidos: {len(archivos)}")
            st.write(archivos)

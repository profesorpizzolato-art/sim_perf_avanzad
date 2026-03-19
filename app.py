import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="SIMULADOR MENFA V5 - IPCL", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS: Fondo Sepia, Alarmas y Tipografía Industrial
st.markdown("""
    <style>
    .stApp {
        background-color: #f4ecd8; /* Estética Retro/Industrial */
        color: #5d4037;
    }
    @keyframes blinker { 50% { opacity: 0; } }
    .alarm-kick {
        background-color: #d32f2f;
        padding: 20px;
        border-radius: 10px;
        border: 5px solid #fff;
        text-align: center;
        animation: blinker 1s linear infinite;
        color: white;
        margin-bottom: 20px;
    }
    .warning-pesca {
        background-color: #610000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: #ffaa00;
        font-weight: bold;
    }
    .target-reached {
        background-color: #2e7d32;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        border: 4px double #ffd700;
    }
    .manual-box {
        background-color: #eaddca;
        padding: 15px;
        border-left: 5px solid #8b4513;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "target_met" not in st.session_state: st.session_state.target_met = False
if "kicks_recibidos" not in st.session_state: st.session_state.kicks_recibidos = 0

TARGET_DEPTH = 3000.0

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 8000, 
        "SPP": 2800, "ROP": 12.0, "GR": 110, "TANQUES": 1200
    }])

# --- 3. LÓGICA DE LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🛡️ IPCL MENFA - MENDOZA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>SIMULADOR TÉCNICO DE PERFORACIÓN V5.0</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login"):
            u = st.text_input("Nombre del Operador:")
            l = st.text_input("Legajo / Matrícula:")
            if st.form_submit_button("INICIAR TURNO"):
                if u and l:
                    st.session_state.usuario = u
                    st.session_state.auth = True
                    st.rerun()
    st.stop()

# --- 4. CÁLCULOS Y SIMULACIÓN (SIDEBAR) ---
curr = st.session_state.history.iloc[-1]

with st.sidebar:
    st.title("🕹️ COMANDOS")
    wob_in = st.slider("WOB (Peso - klbs)", 0, 60, int(curr['WOB']))
    rpm_in = st.slider("RPM (Giro)", 0, 180, int(curr['RPM']))
    
    st.divider()
    
    if st.button("⏩ AVANZAR 1 METRO", use_container_width=True):
        if not st.session_state.pesca_activa and not st.session_state.target_met:
            # Desgaste de herramienta
            st.session_state.vida_sarta -= (wob_in * 0.18)
            if st.session_state.vida_sarta <= 0:
                st.session_state.pesca_activa = True
                st.session_state.vida_sarta = 0
            
            # Profundidad
            nueva_p = curr['DEPTH'] + 1.0
            if nueva_p >= TARGET_DEPTH: st.session_state.target_met = True
            
            # Geología Dinámica (Zona de reservorio 2850-2950)
            gr_val = random.randint(25, 45) if 2850 < nueva_p < 2950 else random.randint(85, 125)
            
            # Evento de Kick (5% probabilidad)
            vol_tanque = curr['TANQUES']
            if random.random() < 0.05 and not st.session_state.kick_alert:
                st.session_state.kick_alert = True
                st.session_state.kicks_recibidos += 1
                vol_tanque += 35 
            
            # Registro
            nueva_fila = {
                "DEPTH": nueva_p, "WOB": wob_in, "RPM": rpm_in,
                "TORQUE": (wob_in * 310) + random.randint(-40, 40),
                "SPP": 2850 + random.randint(-15, 15),
                "ROP": (wob_in * rpm_in) / 480,
                "GR": gr_val, "TANQUES": vol_tanque
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

# --- 5. INTERFAZ MULTI-PESTAÑA ---

# Alertas Críticas siempre visibles arriba
if st.session_state.kick_alert:
    st.markdown('<div class="alarm-kick"><h1>🚨 ¡KICK! SURGENCIA EN TANQUES</h1><p>CIERRE BOP ANULAR DE INMEDIATO</p></div>', unsafe_allow_html=True)
if st.session_state.pesca_activa:
    st.markdown('<div class="warning-pesca">⚠️ HERRAMIENTA CORTADA (FISURA POR WOB). OPERACIÓN DE PESCA REQUERIDA.</div>', unsafe_allow_html=True)
if st.session_state.target_met:
    st.markdown('<div class="target-reached"><h1>🎯 OBJETIVO ALCANZADO</h1><p>Profundidad Final Lograda. Genere su reporte.</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 SCADA", "🔩 SARTA & PESCA", "🛡️ CONTROL DE POZO", "📈 GEOLOGÍA", "📖 MANUAL & EVALUACIÓN"])

with tabs[0]: # SCADA
    st.title("Monitor en Tiempo Real")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PROFUNDIDAD", f"{curr['DEPTH']} m")
    c2.metric("WOB", f"{curr['WOB']} klbs")
    c3.metric("ROP", f"{round(curr['ROP'], 1)} m/h")
    c4.metric("GAMMA RAY", f"{curr['GR']} API")
    
    st.subheader("Historial de Operación")
    st.dataframe(st.session_state.history.tail(8), use_container_width=True)

with tabs[1]: # SARTA & PESCA
    st.title("Mantenimiento de Sarta")
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Integridad del BHA")
        st.progress(st.session_state.vida_sarta / 100)

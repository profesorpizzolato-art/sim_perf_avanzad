import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import time

# --- IMPORTACIÓN DE TUS MÓDULOS ---
try:
    from motor_calculos_avanzados import calcular_presiones_fondo
    from bop_panel import bop_panel_ui
    from mud_pumps import calcular_caudal_real, mud_pumps_panel
    from torque_drag_pro import calcular_tension_sarta
    from gestion_perdidas import verificar_estabilidad
except ImportWarning:
    st.error("⚠️ Algunos módulos de ingeniería no se encontraron. Verifica los nombres de archivos.")

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="MENFA SIMULADOR PRO", layout="wide", page_icon="🛢️")

def init_state():
    if "auth" not in st.session_state:
        st.session_state.update({
            "auth": False, "nombre": "", "legajo": "",
            "depth": 2500.0, "bit_health": 100, "kick": False, "loss": False,
            "pit_vol": 500.0, "gas": 0.0, "sidpp": 0, "sicp": 0,
            "bop_cerrado": False, "choke": 100, "wob": 25, "rpm": 100, "flow": 600,
            "history": pd.DataFrame(columns=["Depth", "WOB", "RPM", "SPP", "ROP"])
        })

init_state()

# 2. LOGIN
if not st.session_state.auth:
    st.title("🔐 ACCESO SISTEMA MENFA")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.session_state.nombre = st.text_input("Operador / Alumno")
        st.session_state.legajo = st.text_input("Legajo ID")
        if st.button("Ingresar al Simulador"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. BARRA LATERAL (CONTROLES DE CABINA)
with st.sidebar:
    st.image("logo_menfa.png", width=150) if "logo_menfa.png" else st.title("MENFA")
    st.subheader(f"👤 {st.session_state.nombre}")
    
    st.divider()
    # Sliders de Control Directo
    wob = st.slider("WOB (klbs)", 0, 60, st.session_state.wob, key="wob_slider")
    rpm = st.slider("RPM", 0, 180, st.session_state.rpm, key="rpm_slider")
    flow = st.slider("Flow (GPM)", 0, 1200, st.session_state.flow, key="flow_slider")
    
    st.divider()
    # Panel de Instructor (Oculto)
    with st.expander("🔐 PANEL INSTRUCTOR"):
        clave = st.text_input("Password", type="password")
        if clave == "menfa2026":
            if st.button("🔴 ACTIVAR KICK"): st.session_state.kick = True
            if st.button("🟡 ACTIVAR PÉRDIDA"): st.session_state.loss = True
            if st.button("🔄 RESET SIM"): st.session_state.clear(); st.rerun()

# 4. MOTOR DE CÁLCULO INTEGRADO
# Aquí es donde tus archivos .py hacen el trabajo sucio
def procesar_ingenieria():
    # Torque desde tu módulo torque_drag_pro
    torque = (wob * 0.45) + (rpm * 0.08) # Simulación fallback
    
    # SPP desde mud_pumps
    spp_base = (flow * 3.2) + 200
    if st.session_state.loss: spp_base *= 0.6
    
    # ROP desde motor_calculos_avanzados
    rop = (wob * rpm) / 450
    if st.session_state.bit_health < 30: rop *= 0.5
    
    # ECD (Densidad Equivalente)
    ecd = 10.5 + (spp_base / 10000)
    
    return round(torque, 1), round(spp_base, 0), round(rop, 1), round(ecd, 2)

torque, spp, rop, ecd = procesar_ingenieria()

# 5. UI PRINCIPAL - CABINA PRO
st.title("🕹️ CONSOLA DE PERFORACIÓN EN TIEMPO REAL")

# Gauges de Visualización Superior
def draw_gauge(val, label, max_v, unit):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val, title={'text': f"{label} ({unit})"},
        gauge={'axis': {'range': [0, max_v]}, 'bar': {'color': "#00ffcc"}}
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="#0e1117", font={'color': "white"})
    return fig

row_g1 = st.columns(3)
row_g1[0].plotly_chart(draw_gauge(st.session_state.depth, "DEPTH", 5000, "m"), use_container_width=True)
row_g1[1].plotly_chart(draw_gauge(torque, "TORQUE", 100, "%"), use_container_width=True)
row_g1[2].plotly_chart(draw_gauge(spp, "SPP", 5000, "psi"), use_container_width=True)

# 6. PANELES INTERACTIVOS (TUS MÓDULOS)
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["💧 SISTEMA DE LODO", "🛡️ WELL CONTROL", "📉 SCADA", "⚙️ MECÁNICA"])

with tab1:
    col_mud1, col_mud2 = st.columns([1, 2])
    with col_mud1:
        st.metric("Pit Volume", f"{st.session_state.pit_vol} bbl", delta=round(st.session_state.pit_vol - 500, 2))
        st.metric("ECD", f"{ecd} ppg")
    with col_mud2:
        # Aquí llamas a la función visual de mud_pumps.py
        st.info("Visualización del Sistema de Bombas")
        # mud_pumps_panel() 

with tab2:
    st.subheader("Panel de Control de Surgencias")
    col_bop1, col_bop2 = st.columns(2)
    with col_bop1:
        st.metric("SICP (Casing)", f"{st.session_state.sicp} psi", "RED")
        st.metric("SIDPP (Pipe)", f"{st.session_state.sidpp} psi")
    with col_bop2:
        # Integración de bop_panel.py
        if st.button("🚨 CERRAR ANULAR", use_container_width=True):
            st.session_state.bop_cerrado = True
            st.success("BOP CERRADO - Pozo Asegurado")
        st.session_state.choke = st.slider("Apertura de Choke %", 0, 100, st.session_state.choke)

with tab3:
    if not st.session_state.history.empty:
        st.line_chart(st.session_state.history.set_index("Depth")[["ROP", "SPP"]])

# 7. BOTÓN DE ACCIÓN: PERFORAR
st.divider()
if st.button("⛏️ PERFORAR TRAMO (10m)", type="primary", use_container_width=True):
    # Lógica de avance
    st.session_state.depth += 10
    st.session_state.bit_health -= (wob * 0.02)
    
    # Simulación de Ganancia/Pérdida en Pits
    if st.session_state.kick:
        st.session_state.pit_vol += random.uniform(5, 12)
        st.session_state.gas += 0.5
    if st.session_state.loss:
        st.session_state.pit_vol -= random.uniform(8, 15)
    
    # Guardar en Historial
    new_data = pd.DataFrame([{
        "Depth": st.session_state.depth, "WOB": wob, 
        "RPM": rpm, "SPP": spp, "ROP": rop
    }])
    st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
    
    # Efecto visual de carga
    with st.spinner('Perforando...'):
        time.sleep(0.5)
    st.rerun()

# 8. ALERTAS CRÍTICAS
if st.session_state.kick:
    st.error(f"🚨 ALERTA: KICK DETECTADO. Gas en superficie: {st.session_state.gas}%")
if st.session_state.pit_vol > 530:
    st.warning("⚠️ REBALSE DE PILETAS INMINENTE")

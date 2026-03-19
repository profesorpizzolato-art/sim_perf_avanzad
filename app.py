import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SIMULADOR MENFA V5", layout="wide", initial_sidebar_state="collapsed")

# --- 2. FUNCIONES DE INTERFAZ ---
def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)

# --- 3. ESTADO DEL SISTEMA ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "GR": 120, "TANQUES": 1000
    }])

curr = st.session_state.history.iloc[-1]

# --- 4. DEFINICIÓN DE MÓDULOS ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("SISTEMA DE ENTRENAMIENTO PETROLERO")
    st.subheader("IPCL MENFA - MENDOZA")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("acceso_operador"):
        nombre = st.text_input("Operador:")
        legajo = st.text_input("Legajo:")
        yacimiento = st.selectbox("Yacimiento:", ["Barrancas", "Vizcacheral", "Malargüe", "Puesto Pozo Cercado"])
        if st.form_submit_button("INGRESAR A CABINA"):
            if nombre:
                st.session_state.usuario = nombre
                st.session_state.legajo = legajo
                st.session_state.yacimiento = yacimiento
                st.session_state.auth = True
                st.rerun()

def render_home():
    st.title(f"🕹️ CONTROL DE OPERACIONES - {st.session_state.yacimiento}")
    st.write(f"Operador: {st.session_state.usuario} | Legajo: {st.session_state.legajo}")
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        if st.button("🛡️ PANEL BOP", use_container_width=True): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        if st.button("📡 GEONAVEGACIÓN LWD", use_container_width=True): st.session_state.menu = "LWD"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🧪 CÁLCULO DE LODOS", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5:
        if st.button("🔩 DISEÑO DE SARTA", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    with c6:
        if st.button("🏆 REPORTE FINAL", use_container_width=True): st.session_state.menu = "REPORTE"; st.rerun()

def vista_scada():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.header("MONITOR DE PERFORACIÓN (REAL TIME)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Profundidad (m)", f"{curr['DEPTH']}")
    m2.metric("WOB (klbs)", f"{curr['WOB']}")
    m3.metric("RPM", f"{curr['RPM']}")
    m4.metric("MSE (kpsi)", f"{curr['MSE']}")
    fig = go.Figure(go.Scatter(y=st.session_state.history['SPP'], name="SPP", line=dict(color='#00ff00')))
    fig.update_layout(template="plotly_dark", title="Presión de Bomba (PSI)")
    st.plotly_chart(fig, use_container_width=True)

def panel_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("SISTEMA DE SEGURIDAD BOP")
    mostrar_imagen("bop_panel.png", ancho=500)
    if st.button("CIERRE HIDRÁULICO DE EMERGENCIA", type="primary"):
        st.error("¡RAMS CERRADOS - POZO SEGURO!")

def render_lwd():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 GEONAVEGACIÓN LWD / MWD")
    st.write(f"Lectura Gamma Ray: {curr['GR']} API")
    z = np.linspace(0, curr['DEPTH'], 50)
    fig = go.Figure(data=[go.Scatter(x=np.random.randn(50)+curr['GR'], y=z, name="GR Log")])
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_dark", title="Registro de Formación")
    st.plotly_chart(fig, use_container_width=True)

def modulo_lodos():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🧪 INGENIERÍA DE LODOS (0.052)")
    col_a, col_b = st.columns(2)
    with col_a:
        densidad = st.number_input("Densidad (ppg):", value=9.5)
        tvd = curr['DEPTH'] * 3.28
        presion = 0.052 * densidad * tvd
        st.metric("Presión Hidrostática", f"{round(presion, 2)} psi")
    with col_b:
        st.write("Fórmula: Ph = 0.052 * δ * TVD")
        st.info("Cálculo basado en estándares de la industria petrolera.")

def modulo_sartas():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🔩 DISEÑO Y TENSIÓN DE SARTA")
    st.write(f"Peso en Gancho Estimado: {round(curr['DEPTH'] * 15 / 1000, 2)} klbs")
    st.info("Módulo para cálculo de Margen de Overpull y Torque máximo.")

def generar_reporte():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🏆 REPORTE FINAL DE GUARDIA")
    st.write(f"Operador: {st.session_state.usuario}")
    st.write(f"Yacimiento: {st.session_state.yacimiento}")
    st.table(st.session_state.history.tail(10))
    csv = st.session_state.history.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR REPORTE .CSV", csv, f"Reporte_{st.session_state.usuario}.csv", "text/csv")

# --- 5. LÓGICA DE NAVEGACIÓN ---

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.write(f"Operador: {st.session_state.usuario}")
        st.divider()
        wob = st.slider("Ajustar WOB (klbs)", 0, 50, int(curr['WOB']))
        rpm = st.slider("Ajustar RPM", 0, 180, int(curr['RPM']))
        
        if st.button("AVANZAR PERFORACIÓN"):
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, 
                "TORQUE": wob * 320, "SPP": 2800 + (curr['DEPTH'] * 0.02),
                "ROP

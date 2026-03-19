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
        "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "TANQUES": 1000
    }])

curr = st.session_state.history.iloc[-1]

# --- 4. MÓDULOS MENFA ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("SISTEMA DE ENTRENAMIENTO PETROLERO")
    st.subheader("IPCL MENFA - MENDOZA")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("acceso_operador"):
        nombre = st.text_input("Operador:")
        yacimiento = st.selectbox("Yacimiento:", ["Barrancas", "Vizcacheral", "Malargüe", "Puesto Pozo Cercado"])
        if st.form_submit_button("INGRESAR A CABINA"):
            if nombre:
                st.session_state.usuario = nombre
                st.session_state.yacimiento = yacimiento
                st.session_state.auth = True
                st.rerun()

def panel_control():
    st.title(f"🕹️ CONTROL DE OPERACIONES - {st.session_state.yacimiento}")
    st.write(f"Operador: {st.session_state.usuario}")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 MONITOR SCADA", use_container_width=True): 
            st.session_state.menu = "SCADA"; st.rerun()
    with col2:
        if st.button("🛡️ PANEL BOP", use_container_width=True): 
            st.session_state.menu = "BOP"; st.rerun()
    with col3:
        if st.button("📉 PÉRDIDAS", use_container_width=True): 
            st.session_state.menu = "PERDIDA"; st.rerun()

def vista_scada():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.header("MONITOR DE PERFORACIÓN EN TIEMPO REAL")
    
    # Métricas principales
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Profundidad (m)", f"{curr['DEPTH']}")
    m2.metric("WOB (klbs)", f"{curr['WOB']}")
    m3.metric("RPM", f"{curr['RPM']}")
    m4.metric("MSE (kpsi)", f"{curr['MSE']}")
    
    # Gráfico de Presión
    fig = go.Figure(go.Scatter(y=st.session_state.history['SPP'], name="SPP", line=dict(color='#00ff00')))
    fig.update_layout(template="plotly_dark", title="Presión de Bomba (PSI)")
    st.plotly_chart(fig, use_container_width=True)

def panel_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("SISTEMA DE SEGURIDAD BOP")
    mostrar_imagen("bop_panel.png", ancho=500)
    if st.button("CIERRE HIDRÁULICO DE EMERGENCIA", type="primary"):
        st.error("¡RAMS CERRADOS - POZO SEGURO!")

# --- 5. LÓGICA DE NAVEGACIÓN ---

if not st.session_state.auth:
    login_menfa()
else:
    # Sidebar Instructor
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.write(f"Operador: {st.session_state.usuario}")
        st.divider()
        wob = st.slider("WOB", 0, 50, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
        
        if st.button("PERFORAR 1M"):
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, 
                "TORQUE": wob * 300, "SPP": 2800 + (curr['DEPTH'] * 0.02),
                "ROP": (rpm * 0.1), "MSE": 30.0, "TANQUES": curr['TANQUES']
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()
            
        if st.button("CERRAR GUARDIA"):
            st.session_state.auth = False
            st.rerun()

    # Ruteo de pantallas
    if st.session_state.menu == "HOME": panel_control()
    elif st.session_state.menu == "SCADA": vista_scada()
    elif st.session_state.menu == "BOP": panel_bop()

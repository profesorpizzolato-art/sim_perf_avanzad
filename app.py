import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN E IDENTIDAD MENFA ---
st.set_page_config(page_title="SIMULADOR PROFESIONAL MENFA V5", layout="wide", initial_sidebar_state="collapsed")

def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)

# --- 2. ESTADO DEL SISTEMA (LOGICA DE INGENIERÍA) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "MSE": 30.0, "GR": 120, "TANQUES": 1000, "GPM": 500
    }])

curr = st.session_state.history.iloc[-1]

# --- 3. MÓDULOS RECUPERADOS Y NORMADOS ---

def render_home():
    if st.session_state.kick_alert:
        st.error("⚠️ ALERTA API S53: FLUJO POSITIVO EN TANQUES. ¡PROCEDER A CIERRE!")
    
    st.title(f"🕹️ CENTRAL DE OPERACIONES - {st.session_state.yacimiento}")
    st.subheader(f"OPERADOR: {st.session_state.usuario} | NORMATIVA API ACTIVA")
    st.divider()
    
    # Fila 1: Operaciones Principales
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 MONITOR SCADA (RT)", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2:
        tipo = "primary" if st.session_state.kick_alert else "secondary"
        if st.button("🛡️ PANEL BOP (API S53)", use_container_width=True, type=tipo): st.session_state.menu = "BOP"; st.rerun()
    with c3:
        if st.button("📡 GEONAVEGACIÓN LWD", use_container_width=True): st.session_state.menu = "LWD"; st.rerun()
    
    # Fila 2: Ingeniería y Fluidos
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🧪 FLUIDOS (API RP 13B)", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5:
        if st.button("🔩 TORQUE, DRAG & FATIGA", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    with c6:
        if st.button("⚙️ HIDRÁULICA Y BOMBAS", use_container_width=True): st.session_state.menu = "BOMBAS"; st.rerun()

    # Fila 3: Finalización
    st.write("")
    if st.button("🏆 REPORTE FINAL DE GUARDIA", use_container_width=True): st.session_state.menu = "REPORTE"; st.rerun()

def modulo_bombas():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("⚙️ HIDRÁULICA DE PERFORACIÓN")
    st.info("Cálculo de Potencia y Caudal según requerimientos de limpieza de pozo.")
    
    gpm = st.number_input("Caudal (GPM):", value=float(curr['GPM']))
    presion = curr['SPP']
    hhp = (gpm * presion) / 1714  # Fórmula de Potencia Hidráulica
    
    st.metric("Potencia Hidráulica (HHP)", f"{round(hhp, 2)} HP")
    st.write("Fórmula API: HHP = (GPM * PSI) / 1714")

def render_lwd():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📡 MÓDULO LWD (LOGGING WHILE DRILLING)")
    st.subheader("Registro de Rayos Gamma en Tiempo Real")
    
    # Generar registro visual del pozo
    z = np.linspace(curr['DEPTH']-100, curr['DEPTH'], 20)
    gr_values = st.session_state.history['GR'].tail(20).values
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gr_values, y=z, name="Gamma Ray (API Units)", line=dict(color='yellow')))
    fig.update_layout(yaxis=dict(autorange="reversed", title="Profundidad (m)"), 
                      xaxis=dict(title="API Units", range=[0, 200]),
                      template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

def modulo_sartas():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🔩 MECÁNICA DE SARTAS (API 5DP)")
    
    f_flot = 1 - (9.5 / 65.5)
    hook_load = (curr['DEPTH'] * 15 * f_flot) + (curr['WOB'] * 1000)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hook Load (Peso Flotado)", f"{int(hook_load)} lbs")
        st.metric("Torque de Rotación", f"{int(curr['TORQUE'])} ft-lb")
    with col2:
        st.subheader("Vida Útil de Tubería (API RP 7G)")
        st.progress(st.session_state.vida_sarta / 100)
        if st.session_state.vida_sarta < 20: st.error("¡REEMPLAZO INMEDIATO REQUERIDO!")

def panel_bop():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("🛡️ PANEL DE CONTROL DE SURGENCIAS (API S53)")
    mostrar_imagen("bop_panel.png", ancho=600)
    if st.button("CIERRE DE EMERGENCIA (FULL SHUT-IN)", type="primary"):
        st.session_state.kick_alert = False
        st.success("POZO ASEGURADO BAJO NORMA API S53")

# --- 4. LÓGICA DE PERFORACIÓN ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("IPCL MENFA - MENDOZA")
    st.subheader("SIMULADOR TÉCNICO PROFESIONAL")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Operador:")
        l = st.text_input("Legajo:")
        y = st.selectbox("Yacimiento:", ["Barrancas", "Vizcacheral", "Malargüe"])
        if st.form_submit_button("CONECTAR SISTEMA"):
            st.session_state.usuario, st.session_state.legajo, st.session_state.yacimiento, st.session_state.auth = u, l, y, True
            st.rerun()

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.divider()
        wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
        
        if st.button("AVANZAR PERFORACIÓN"):
            # Lógica de Fatiga y Kick
            st.session_state.vida_sarta -= (wob * 0.02) + (rpm * 0.005)
            kick = random.randint(10, 30) if random.random() < 0.08 else 0
            if kick > 0: st.session_state.kick_alert = True
            
            nueva_fila = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, 
                "TORQUE": (wob * 380) + (curr['DEPTH'] * 0.12), 
                "SPP": 2800 + (curr['DEPTH'] * 0.02),
                "ROP": (rpm * 0.12) + (wob * 0.04), "MSE": 32.0, 
                "GR": random.randint(60, 140), "TANQUES": curr['TANQUES'] + kick, "GPM": 500
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

    # Ruteador Final
    if st.session_state.menu == "HOME": render_home()
    elif st.session_state.menu == "SCADA":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.header("MONITOR SCADA")
        st.metric("Profundidad", f"{curr['DEPTH']} m")
        st.metric("Presión SPP", f"{int(curr['SPP'])} psi")
    elif st.session_state.menu == "BOP": panel_bop()
    elif st.session_state.menu == "LWD": render_lwd()
    elif st.session_state.menu == "LODOS":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.title("🧪 FLUIDOS (API 0.052)")
        dens = st.number_input("Densidad (ppg):", 9.5)
        st.metric("Presión Hidrostática", f"{round(0.052 * dens * curr['DEPTH'] * 3.28, 2)} psi")
    elif st.session_state.menu == "SARTAS": modulo_sartas()
    elif st.session_state.menu == "BOMBAS": modulo_bombas()
    elif st.session_state.menu == "REPORTE":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.write("REPORTE DE GUARDIA API")
        st.dataframe(st.session_state.history.tail(20))

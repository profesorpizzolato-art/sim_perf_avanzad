import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
import os
import time

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO SEPIA) ---
st.set_page_config(page_title="SIMULADOR MENFA V5", layout="wide", initial_sidebar_state="collapsed")

# Inyección de CSS para fondo Sepia y Alarmas
st.markdown("""
    <style>
    .stApp {
        background-color: #f4ecd8; /* Tono Sepia Suave */
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
    }
    .target-reached {
        background-color: #2e7d32;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        border: 4px double #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)

def mostrar_imagen(archivo, ancho=None):
    if os.path.exists(archivo):
        st.image(archivo, width=ancho)
    else:
        st.warning(f"Cargue {archivo} para ver el logo institucional.")

# --- 2. ESTADO DEL SISTEMA ---
if "auth" not in st.session_state: st.session_state.auth = False
if "menu" not in st.session_state: st.session_state.menu = "HOME"
if "kick_alert" not in st.session_state: st.session_state.kick_alert = False
if "time_kick" not in st.session_state: st.session_state.time_kick = 0
if "reaccion_sec" not in st.session_state: st.session_state.reaccion_sec = 0
if "vida_sarta" not in st.session_state: st.session_state.vida_sarta = 100.0 
if "pesca_activa" not in st.session_state: st.session_state.pesca_activa = False
if "target_met" not in st.session_state: st.session_state.target_met = False

TARGET_DEPTH = 3000.0 # Objetivo final de la perforación

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([{
        "DEPTH": 2500.0, "WOB": 20.0, "RPM": 100, "TORQUE": 15000, 
        "SPP": 2800, "ROP": 10.0, "GR": 120, "TANQUES": 1000, "GPM": 500
    }])

curr = st.session_state.history.iloc[-1]

# --- 3. MÓDULOS ---

def login_menfa():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    mostrar_imagen("logo_menfa.png", ancho=300)
    st.title("SISTEMA DE ENTRENAMIENTO - IPCL MENFA")
    st.subheader("INGRESO DE OPERADOR")
    st.markdown('</div>', unsafe_allow_html=True)
    with st.form("acceso"):
        nombre = st.text_input("Nombre y Apellido:")
        legajo = st.text_input("Número de Legajo:")
        if st.form_submit_button("CONECTAR A CABINA"):
            if nombre and legajo:
                st.session_state.usuario, st.session_state.legajo = nombre, legajo
                st.session_state.yacimiento, st.session_state.auth = "OPERACIÓN MENDOZA", True
                st.rerun()

def render_home():
    # Alarmas Visuales
    if st.session_state.kick_alert:
        st.markdown('<div class="alarm-kick"><h1>🚨 ¡KICK DETECTADO! 🚨</h1><p>CIERRE BOP INMEDIATO</p></div>', unsafe_allow_html=True)
    
    if st.session_state.target_met:
        st.markdown(f'<div class="target-reached"><h1>🎯 OBJETIVO ALCANZADO: {TARGET_DEPTH}m</h1><p>Guardia completada con éxito. Descargue su reporte.</p></div>', unsafe_allow_html=True)

    st.title(f"🕹️ CENTRAL MENFA - {st.session_state.yacimiento}")
    st.write(f"Operador: **{st.session_state.usuario}** | Integridad Sarta: **{round(st.session_state.vida_sarta, 1)}%**")
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("📊 MONITOR SCADA", use_container_width=True): st.session_state.menu = "SCADA"; st.rerun()
    with c2: 
        tipo = "primary" if st.session_state.kick_alert else "secondary"
        if st.button("🛡️ PANEL BOP", use_container_width=True, type=tipo): st.session_state.menu = "BOP"; st.rerun()
    with c3: 
        if st.button("🔩 SARTA / PESCA", use_container_width=True): st.session_state.menu = "SARTAS"; st.rerun()
    
    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("🧪 FLUIDOS", use_container_width=True): st.session_state.menu = "LODOS"; st.rerun()
    with c5: 
        if st.button("📈 AVANCE GRÁFICO", use_container_width=True): st.session_state.menu = "PERFIL"; st.rerun()
    with c6: 
        if st.button("🏆 REPORTE FINAL", use_container_width=True): st.session_state.menu = "EXAMEN"; st.rerun()

    st.divider()
    if st.button("📖 MANUAL DE USUARIO API", use_container_width=True): st.session_state.menu = "MANUAL"; st.rerun()

def render_perfil_grafico():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    st.title("📈 PERFIL DE PERFORACIÓN")
    df = st.session_state.history
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0]*len(df), y=df['DEPTH'], mode='lines', line=dict(color='white', width=5)))
    fig.add_hline(y=TARGET_DEPTH, line_dash="dash", line_color="lime", annotation_text="TARGET")
    fig.update_layout(yaxis=dict(title="Profundidad (m)", autorange="reversed"), template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

def render_manual():
    st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
    t1, t2, t3, t4 = st.tabs(["🚀 Operación", "🛡️ Control", "🔩 Pesca", "📚 Glosario"])
    with t1: st.write("Controle WOB/RPM. Objetivo final: 3000m.")
    with t2: st.write("Ante alarma roja parpadeante, cierre la BOP.")
    with t3: st.write("Si la sarta falla, use Overshot con 180+ klbs.")
    with t4: st.write("**WOB:** Peso sobre trépano. **Kick:** Ingreso de fluido.")

# --- 4. LÓGICA DE CONTROL ---

if not st.session_state.auth:
    login_menfa()
else:
    with st.sidebar:
        mostrar_imagen("logo_menfa.png", ancho=150)
        st.divider()
        wob = st.slider("WOB (klbs)", 0, 60, int(curr['WOB']))
        rpm = st.slider("RPM", 0, 180, int(curr['RPM']))
        if st.button("AVANZAR 1m") and not st.session_state.pesca_activa and not st.session_state.target_met:
            st.session_state.vida_sarta -= (wob * 0.05)
            if curr['DEPTH'] + 1 >= TARGET_DEPTH: st.session_state.target_met = True
            
            kick = 20 if (random.random() < 0.05 and not st.session_state.kick_alert) else 0
            if kick > 0: 
                st.session_state.kick_alert = True
                st.session_state.time_kick = time.time()
            
            nueva = {
                "DEPTH": curr['DEPTH'] + 1.0, "WOB": wob, "RPM": rpm, "TORQUE": (wob * 400),
                "SPP": 2800, "ROP": 10.0, "GR": random.randint(60, 140), 
                "TANQUES": curr['TANQUES'] + kick, "GPM": 500
            }
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([nueva])], ignore_index=True)
            st.rerun()

    # Ruteador
    m = st.session_state.menu
    if m == "HOME": render_home()
    elif m == "PERFIL": render_perfil_grafico()
    elif m == "MANUAL": render_manual()
    elif m == "BOP":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        if st.button("ACTIVAR CIERRE", type="primary"):
            if st.session_state.kick_alert:
                st.session_state.reaccion_sec = int(time.time() - st.session_state.time_kick)
                st.session_state.kick_alert = False
                st.success(f"POZO SEGURO. Reacción: {st.session_state.reaccion_sec}s")
    elif m == "EXAMEN":
        st.button("🔙 VOLVER", on_click=lambda: st.session_state.update({"menu": "HOME"}))
        st.download_button("📥 DESCARGAR REPORTE MENFA", st.session_state.history.to_csv(), "reporte_guardia.csv")

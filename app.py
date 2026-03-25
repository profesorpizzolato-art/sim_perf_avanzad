import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CONFIGURACIÓN DE PANTALLA INDUSTRIAL ---
st.set_page_config(page_title="MENFA CYBERBASE V16", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070a; color: #00ffcc; }
    .stMetric { background-color: #10141b; border: 2px solid #1f2937; border-radius: 10px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff; font-family: 'Segment7', 'Courier New'; font-size: 2.5rem; }
    .stSlider { color: #00ffcc; }
    .stButton>button { background: linear-gradient(135deg, #00ffcc 0%, #008b8b 100%); color: black; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO (FÍSICA DE PERFORACIÓN) ---
def simular_parametros(wob, rpm, flow, mw, depth):
    # Relaciones matemáticas reales (Torque, Drag, ROP)
    torque = (wob * 0.15) + (rpm * 0.05) + (depth * 0.001)
    drag = depth * 0.02 # Arrastre por fricción
    hook_load = 250 - drag - wob
    spp = (flow**1.8) * 0.02 # Stand Pipe Pressure (psi)
    rop = (wob * rpm) / 400
    return hook_load, torque, spp, rop

# --- ESTADO INICIAL ---
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["MD", "HKLD", "TORQUE", "SPP", "ROP"])

# --- INTERFAZ: CABINA DEL PERFORADOR ---
st.title("📟 PANEL DE CONTROL INTEGRAL - IPCL MENFA")

# FILA 1: INDICADORES ANÁLOGOS (Gauges estilo Martin-Decker)
col_g1, col_g2, col_g3 = st.columns(3)

# Inputs de control (Sliders simulando palancas de la cabina)
with st.sidebar:
    st.header("🎛️ MANDOS DE LA TORRE")
    wob_in = st.slider("WOB (klbs) - Peso sobre trépano", 0, 80, 25)
    rpm_in = st.slider("RPM - Mesa Rotaria / Top Drive", 0, 200, 100)
    st.divider()
    st.header("💧 CONTROL DE LODOS")
    flow_in = st.slider("GPM - Caudal de Bombas", 200, 1200, 600)
    mw_in = st.number_input("MW (ppg) - Densidad", 8.3, 18.0, 10.5)
    
    st.divider()
    if st.button("🚀 INICIAR PERFORACIÓN (TRAMO 30m)"):
        st.toast("Perforando... monitorear presiones.")

# Lógica de cálculo
hkld, torq, spp, rop = simular_parametros(wob_in, rpm_in, flow_in, mw_in, 3200)

with col_g1:
    fig_hkld = go.Figure(go.Indicator(
        mode = "gauge+number", value = hkld,
        title = {'text': "HOOK LOAD (klbs)", 'font': {'size': 20, 'color': "#00ffcc"}},
        gauge = {'axis': {'range': [0, 300], 'tickwidth': 2}, 'bar': {'color': "#00ffcc"},
                 'steps': [{'range': [0, 50], 'color': "red"}, {'range': [250, 300], 'color': "red"}]}
    ))
    fig_hkld.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_hkld, use_container_width=True)

with col_g2:
    fig_torq = go.Figure(go.Indicator(
        mode = "gauge+number", value = torq,
        title = {'text': "TORQUE (ft-lb)", 'font': {'size': 20, 'color': "#ffff00"}},
        gauge = {'axis': {'range': [0, 50], 'tickwidth': 2}, 'bar': {'color': "#ffff00"},
                 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 45}}
    ))
    fig_torq.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_torq, use_container_width=True)

with col_g3:
    fig_spp = go.Figure(go.Indicator(
        mode = "gauge+number", value = spp,
        title = {'text': "SPP (psi) - Bombas", 'font': {'size': 20, 'color': "#00ffff"}},
        gauge = {'axis': {'range': [0, 5000], 'tickwidth': 2}, 'bar': {'color': "#00ffff"}}
    ))
    fig_spp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
    st.plotly_chart(fig_spp, use_container_width=True)

# FILA 2: MÉTRICAS DIGITALES Y GEONAVEGACIÓN
st.divider()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROP (m/h)", f"{rop:.1f}")
c2.metric("BIT DEPTH (m)", "3240.5")
c3.metric("TVD (m)", "3180.2")
c4.metric("D-EXPONENT", "1.24")
c5.metric("PUMP STROKES", f"{flow_in/8:.0f} SPM")

# FILA 3: GEOLOGÍA Y CONTROL DE POZOS
col_l, col_r = st.columns([2, 1])

with col_l:
    st.subheader("📈 Registros de Perforación (Real-Time Logs)")
    # Simulación de curvas geofísicas
    t = np.linspace(3200, 3240, 40)
    gr = 100 + np.random.randn(40) * 10
    res = 10** (np.random.rand(40) * 2)
    
    fig_logs = make_subplots(rows=1, cols=2, shared_yaxes=True)
    fig_logs.add_trace(go.Scatter(x=gr, y=t, name="Gamma Ray", line=dict(color="green")), 1, 1)
    fig_logs.add_trace(go.Scatter(x=res, y=t, name="Resistividad", line=dict(color="red")), 1, 2)
    fig_logs.update_yaxes(autorange="reversed")
    fig_logs.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)')
    st.plotly_chart(fig_logs, use_container_width=True)

with col_r:
    st.subheader("🚨 Panel de Seguridad")
    st.error("Nivel de Tanques: +5 bbl (Alerta)")
    if st.button("🔴 EMERGENCY SHUT DOWN"):
        st.warning("BOP Cerrado. Sistema Bloqueado.")
    
    with st.expander("🛠️ Detalles de la Sarta"):
        st.write("- **Trépano:** PDC 8-1/2' (Mendoza High-Impact)")
        st.write("- **BHA:** Motor de Fondo + MWD + LWD")
        st.write("- **Portamechas:** 6-1/4' x 90m")

# PIE DE PÁGINA PROFESIONAL
st.markdown("---")
st.caption("IPCL MENFA - Entrenamiento Técnico en Petróleo | UTN Mendoza 2026")

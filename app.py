import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import random
from motor_calculos_avanzados import *
from bop_panel import *
from mud_pumps import *
from torque_drag_pro import *
from gestion_perdidas import *
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}
.stMetric {
    background-color: #111827;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="MENFA SIMULADOR PRO", layout="wide")

# -----------------------------------
# SESSION STATE
# -----------------------------------
def init_state():
    defaults = {
        "auth": False,
        "nombre": "",
        "legajo": "",
        "depth": 2500,
        "bit_health": 100,
        "kick": False,
        "loss": False,
        "formacion": "normal",
        "pit_vol": 500,
        "gas": 0,
        "sidpp": 0,
        "sicp": 0,
        "bop_cerrado": False,
        "choke": 50,
        "history": pd.DataFrame(columns=["Depth","WOB","RPM","SPP","ROP"])
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -----------------------------------
# LOGIN
# -----------------------------------
if not st.session_state.auth:
    st.title("🔐 MENFA LOGIN")

    nombre = st.text_input("Nombre")
    legajo = st.text_input("Legajo")

    if st.button("Ingresar", key="login_btn"):
        st.session_state.auth = True
        st.session_state.nombre = nombre
        st.session_state.legajo = legajo
        st.rerun()

    st.stop()

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.markdown("### 🎮 CONTROL CABINA")

col_j1, col_j2 = st.columns(2)

with col_j1:
    if st.button("⬆️ SUBIR WOB", key="wob_up"):
        st.session_state.wob += 2
    if st.button("⬇️ BAJAR WOB", key="wob_down"):
        st.session_state.wob -= 2

with col_j2:
    if st.button("⏩ +RPM", key="rpm_up"):
        st.session_state.rpm += 10
    if st.button("⏪ -RPM", key="rpm_down"):
        st.session_state.rpm -= 10
st.markdown("## 🖥️ CABINA DEL PERFORADOR MENFA")

# GRID tipo cabina
row1 = st.columns(3)
row2 = st.columns(3)

# ------------------------
# FILA 1 (instrumentos)
# ------------------------
row1[0].plotly_chart(gauge(st.session_state.depth, "DEPTH", 4000))
row1[1].plotly_chart(gauge(st.session_state.torque, "TORQUE", 100))
row1[2].plotly_chart(gauge(st.session_state.spp, "SPP", 5000))

# ------------------------
# FILA 2 (lodo + control)
# ------------------------
row2[0].metric("MW", st.session_state.mw)
row2[1].metric("PIT VOL", st.session_state.pit_vol)
row2[2].metric("ECD", st.session_state.ecd)
st.sidebar.title(f"👷 {st.session_state.nombre}")

wob = st.sidebar.slider("WOB", 0, 60, 25, key="wob")
rpm = st.sidebar.slider("RPM", 0, 180, 100, key="rpm")
flow = st.sidebar.slider("FLOW", 200, 1200, 600, key="flow")

# LODO
st.sidebar.subheader("🛢️ LODO")
mw = st.sidebar.slider("MW", 8.0, 15.0, 10.0, key="mw")
pv = st.sidebar.slider("PV", 5, 50, 20, key="pv")
yp = st.sidebar.slider("YP", 5, 40, 15, key="yp")
with st.container():
    st.subheader("🛢️ SISTEMA DE LODO")
    # llamar tu módulo
    mud_pumps_panel()  # o la función que tengas
with st.container():
    st.subheader("🛡️ PANEL BOP")
    bop_panel()  # tu módulo
    
# CHOKE
st.sidebar.subheader("🛡️ CHOKE")
st.session_state.choke = st.sidebar.slider(
    "Choke %", 0, 100, st.session_state.choke, key="choke_slider"
)

# INSTRUCTOR
with st.sidebar.expander("🔐 INSTRUCTOR"):
    clave = st.text_input("Clave", type="password", key="clave_instr")

    if clave == "menfa2026":
        if st.button("KICK", key="kick_btn"):
            st.session_state.kick = True
        if st.button("LOSS", key="loss_btn"):
            st.session_state.loss = True
        if st.button("FORMACIÓN DURA", key="form_dura"):
            st.session_state.formacion = "dura"

# -----------------------------------
# MOTOR DE CÁLCULO
# -----------------------------------
def calcular():

    factor = 1
    if st.session_state.formacion == "dura":
        factor = 0.5

    torque = wob * 0.4 + rpm * 0.1

    spp = flow * 3 + (pv * 10) + (yp * 5)

    eficiencia = yp / pv
    rop = (wob * rpm / 500) * factor * eficiencia

    # ECD
    ecd = mw + (spp / 10000)

    # efecto gas
    mw_ef = mw - (st.session_state.gas * 0.2)

    # pérdida
    if st.session_state.loss:
        spp *= 0.6

    # well control
    if st.session_state.bop_cerrado:
        spp *= (st.session_state.choke / 100)

    if st.session_state.bit_health <= 0:
        rop = 0

    return torque, spp, rop, ecd, mw_ef

torque, spp, rop, ecd, mw_ef = calcular()
st.session_state.torque, st.session_state.spp, st.session_state.rop, st.session_state.ecd = calcular()

# -----------------------------------
# CABINA
# -----------------------------------
st.title("🖥️ CABINA MENFA PRO")

def gauge(val, title, maxv):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={'text': title},
        gauge={'axis': {'range': [0, maxv]}}
    ))

c1, c2, c3 = st.columns(3)
c1.plotly_chart(gauge(st.session_state.depth, "DEPTH", 4000), use_container_width=True)
c2.plotly_chart(gauge(torque, "TORQUE", 100), use_container_width=True)
c3.plotly_chart(gauge(spp, "SPP", 5000), use_container_width=True)
if st.button("⛏️ PERFORAR", key="main_drill"):

    st.session_state.depth += 10

    # dinámica real
    actualizar_pits()
    actualizar_gas()
    actualizar_well_control()
# -----------------------------------
# MÉTRICAS
# -----------------------------------
c4, c5, c6 = st.columns(3)
c4.metric("ROP", round(rop,1))
c5.metric("MW", mw)
c6.metric("ECD", round(ecd,2))

c7, c8, c9 = st.columns(3)
c7.metric("PIT VOL", round(st.session_state.pit_vol,1))
c8.metric("GAS", round(st.session_state.gas,2))
c9.metric("CHOKE", st.session_state.choke)

# -----------------------------------
# ALERTAS
# -----------------------------------
if st.session_state.kick:
    st.error("🚨 KICK")

if st.session_state.loss:
    st.warning("⚠️ LOSS")

if st.session_state.pit_vol > 520:
    st.error("🚨 PIT GAIN")

if st.session_state.pit_vol < 480:
    st.warning("⚠️ PIT LOSS")

# -----------------------------------
# DIAGNÓSTICO
# -----------------------------------
st.subheader("🧠 Diagnóstico MENFA")

if st.session_state.kick and not st.session_state.bop_cerrado:
    st.error("🔴 Cerrar BOP YA")

elif st.session_state.bop_cerrado and st.session_state.choke < 30:
    st.success("🟢 Pozo controlado")

elif ecd > 14:
    st.warning("🟠 Riesgo fractura")

elif yp / pv < 0.5:
    st.info("🔵 Limpieza deficiente")

else:
    st.success("🟢 Operación óptima")

# -----------------------------------
# PERFORAR
# -----------------------------------
if st.button("⛏️ PERFORAR 10m", key="perforar_main"):

    st.session_state.depth += 10
    st.session_state.bit_health -= wob * 0.05

    # pits
    entrada = flow / 10
    salida = flow / 10

    if st.session_state.kick:
        entrada += random.uniform(5, 15)

    if st.session_state.loss:
        salida += random.uniform(5, 15)

    st.session_state.pit_vol += (entrada - salida)

    # gas
    if st.session_state.kick:
        st.session_state.gas += random.uniform(0.1, 0.5)

    # presiones
    if st.session_state.kick and not st.session_state.bop_cerrado:
        st.session_state.sidpp = random.randint(300, 800)
        st.session_state.sicp = random.randint(500, 1200)

    fila = {
        "Depth": st.session_state.depth,
        "WOB": wob,
        "RPM": rpm,
        "SPP": spp,
        "ROP": rop
    }

    st.session_state.history = pd.concat(
        [st.session_state.history, pd.DataFrame([fila])],
        ignore_index=True
    )

# -----------------------------------
# WELL CONTROL
# -----------------------------------
st.subheader("🛡️ WELL CONTROL PRO")

c1, c2, c3 = st.columns(3)
c1.metric("SIDPP", st.session_state.sidpp)
c2.metric("SICP", st.session_state.sicp)
c3.metric("KMW", round(mw + st.session_state.sidpp / 1000,2))

if st.session_state.kick and not st.session_state.bop_cerrado:
    if st.button("🔒 CERRAR BOP", key="bop_main"):
        st.session_state.bop_cerrado = True
        st.success("Pozo cerrado")

# -----------------------------------
# SCADA
# -----------------------------------
st.subheader("📊 SCADA")

if len(st.session_state.history) > 1:
    df = st.session_state.history.copy()
    df["TIME"] = range(len(df))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["TIME"], y=df["SPP"], name="SPP"))
    fig.add_trace(go.Scatter(x=df["TIME"], y=df["ROP"], name="ROP"))

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# CERTIFICACIÓN
# -----------------------------------
st.subheader("🎓 Certificación")

if len(st.session_state.history) > 10:
    st.success("APROBADO")

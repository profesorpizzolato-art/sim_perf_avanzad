import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import random

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="MENFA SIMULADOR PRO", layout="wide")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "nombre" not in st.session_state: st.session_state.nombre = ""
if "legajo" not in st.session_state: st.session_state.legajo = ""

if "depth" not in st.session_state: st.session_state.depth = 2500
if "bit_health" not in st.session_state: st.session_state.bit_health = 100
if "kick" not in st.session_state: st.session_state.kick = False
if "loss" not in st.session_state: st.session_state.loss = False
if "formacion" not in st.session_state: st.session_state.formacion = "normal"

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Depth","WOB","RPM","SPP","ROP"])

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
usuarios_validos = {
    "admin": "1234",
    "alumno1": "1111"
}

if nombre in usuarios_validos and legajo == usuarios_validos[nombre]:
    st.session_state.auth = True
# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title(f"👷 {st.session_state.nombre}")

wob = st.sidebar.slider("WOB", 0, 60, 25, key="wob_slider")
rpm = st.sidebar.slider("RPM", 0, 180, 100, key="rpm_slider")
flow = st.sidebar.slider("FLOW", 200, 1200, 600, key="flow_slider")

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
# MOTOR
# -----------------------------------
def calcular():
    factor = 1
    if st.session_state.formacion == "dura":
        factor = 0.5

    torque = wob * 0.4 + rpm * 0.1
    spp = flow * 3
    rop = (wob * rpm / 500) * factor

    if st.session_state.loss:
        spp *= 0.5

    if st.session_state.bit_health <= 0:
        rop = 0

    return torque, spp, rop

torque, spp, rop = calcular()

# -----------------------------------
# CABINA
# -----------------------------------
st.title("🖥️ CABINA MENFA")

def gauge(val, title, maxv, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={'text': title},
        gauge={'axis': {'range': [0, maxv]}, 'bar': {'color': color}}
    ))
    return fig

c1, c2, c3 = st.columns(3)
c1.plotly_chart(gauge(st.session_state.depth, "DEPTH", 4000, "cyan"), use_container_width=True)
c2.plotly_chart(gauge(torque, "TORQUE", 100, "yellow"), use_container_width=True)
c3.plotly_chart(gauge(spp, "SPP", 5000, "green"), use_container_width=True)

# -----------------------------------
# ALERTAS
# -----------------------------------
if st.session_state.kick:
    st.error("🚨 KICK ACTIVO")

if st.session_state.loss:
    st.warning("⚠️ LOSS")

if st.session_state.bit_health <= 0:
    st.error("🔩 SARTA ROTA")

# -----------------------------------
# BOTÓN PRINCIPAL (ÚNICO)
# -----------------------------------
if st.button("⛏️ PERFORAR 10m", key="btn_perforar_main"):

    st.session_state.depth += 10
    st.session_state.bit_health -= wob * 0.05

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

    # guardar
    if not os.path.exists("data"):
        os.makedirs("data")

    st.session_state.history.to_csv(
        f"data/{st.session_state.legajo}.csv",
        index=False
    )

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
# WELL CONTROL
# -----------------------------------
st.subheader("🛡️ WELL CONTROL")

if st.session_state.kick:
    if st.button("🔒 CERRAR BOP", key="btn_bop"):
        st.session_state.kick = False
        st.success("Pozo controlado")

# -----------------------------------
# RANKING
# -----------------------------------
st.subheader("🏆 Ranking")

def ranking():
    if not os.path.exists("data"):
        return pd.DataFrame()

    res = []
    for f in os.listdir("data"):
        df = pd.read_csv(f"data/{f}")
        res.append({
            "Alumno": f,
            "Prof": df["Depth"].max(),
            "ROP": df["ROP"].mean()
        })

    return pd.DataFrame(res)

df_rank = ranking()
if not df_rank.empty:
    st.dataframe(df_rank)

# -----------------------------------
# CERTIFICADO
# -----------------------------------
st.subheader("🎓 Certificación")

if len(st.session_state.history) > 10:
    st.success("APROBADO")

# -----------------------------------
# PANEL DOCENTE
# -----------------------------------
with st.expander("🔐 DOCENTE"):
    clave = st.text_input("Clave docente", type="password", key="clave_doc")

    if clave == "menfa_pro":
        st.success("Panel activo")

        if not df_rank.empty:
            st.dataframe(df_rank)

        if st.button("RESET", key="reset_btn"):
            import shutil
            shutil.rmtree("data", ignore_errors=True)
            st.warning("Datos borrados")

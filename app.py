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
if "pit_vol" not in st.session_state:
    st.session_state.pit_vol = 500  # bbl

if "gas" not in st.session_state:
    st.session_state.gas = 0
# -----------------------------------
# LOGIN
# -----------------------------------
# --- 1. Definición de usuarios (Base de datos simple) ---
usuarios_validos = {
    "Fabricio": "1234",
    "Johana": "5678",
    "Alumno": "2026"
}

# --- 2. Interfaz de Login ---
st.title("🔐 Acceso IPCL MENFA")

# Inicializamos las variables vacías para que no den NameError
nombre = st.text_input("Ingrese su Nombre completo:", key="login_nom")
legajo = st.text_input("Ingrese su DNI o Legajo:", key="login_leg")

if st.button("Ingresar al Simulador", key="btn_login"):
    # REGLA DE ORO: Validamos solo si el usuario escribió algo
    if nombre in usuarios_validos and legajo == usuarios_validos[nombre]:
        st.session_state.auth = True
        st.session_state.nombre = nombre
        st.session_state.legajo = legajo
        st.success(f"Bienvenido {nombre}. Cargando parámetros de perforación...")
        st.rerun()
    else:
        st.error("Credenciales incorrectas. Verifique los datos.")
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
# LODOS
# -----------------------------------
st.sidebar.subheader("🛢️ LODO")

mw = st.sidebar.slider("Mud Weight (ppg)", 8.0, 15.0, 10.0, key="mw")
pv = st.sidebar.slider("Plastic Viscosity (cP)", 5, 50, 20, key="pv")
yp = st.sidebar.slider("Yield Point", 5, 40, 15, key="yp")
gel = st.sidebar.slider("Gel Strength", 5, 30, 10, key="gel")
# -----------------------------------
# MOTOR
# -----------------------------------
def calcular():

    factor_formacion = 1
    if st.session_state.formacion == "dura":
        factor_formacion = 0.5

    # BASE
    torque = wob * 0.4 + rpm * 0.1

    # EFECTO LODO EN PRESIÓN
    spp = flow * 3 + (pv * 15) + (yp * 10)

    # EFECTO LODO EN ROP
    eficiencia_limpieza = (yp / pv)

    rop = (wob * rpm / 500) * factor_formacion * eficiencia_limpieza

    # CONTROL DE KICK POR MW
    if mw < 9:
        if random.random() < 0.1:
            st.session_state.kick = True

    # PÉRDIDAS POR MW ALTO
    if mw > 13:
        st.session_state.loss = True

    # EFECTO LOSS
    if st.session_state.loss:
        spp *= 0.6

    # SARTA ROTA
    if st.session_state.bit_health <= 0:
        rop = 0

    return torque, spp, rop
ecd = mw + (spp / 10000)
return torque, spp, rop, ecd
torque, spp, rop, ecd = calcular()
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
# MÉTRICAS OPERATIVAS + LODO
# -----------------------------------
c4, c5, c6 = st.columns(3)

c4.metric("ROP", round(rop,1))
c5.metric("MW", mw)
c6.metric("PV/YP", f"{pv}/{yp}")
# -----------------------------------
# DINÁMICA DE PITS
# -----------------------------------

# flujo base
entrada = flow / 10
salida = flow / 10

# KICK → entra fluido
if st.session_state.kick:
    entrada += random.uniform(5, 15)

# LOSS → se pierde
if st.session_state.loss:
    salida += random.uniform(5, 15)

# actualizar volumen
st.session_state.pit_vol += (entrada - salida)
# generación de gas
if st.session_state.kick:
    st.session_state.gas += random.uniform(0.1, 1)

# efecto gas
mw_efectivo = mw - (st.session_state.gas * 0.2)
# -----------------------------------
# DETECCIÓN AUTOMÁTICA
# -----------------------------------

if st.session_state.pit_vol > 520:
    st.error("🚨 PIT GAIN → POSIBLE KICK")

if st.session_state.pit_vol < 480:
    st.warning("⚠️ PIT LOSS → POSIBLE PÉRDIDA")
c7, c8, c9 = st.columns(3)

c7.metric("PIT VOL", round(st.session_state.pit_vol,1))
c8.metric("ECD", round(ecd,2))
c9.metric("GAS %", round(st.session_state.gas,2))

# -----------------------------------
# ALERTAS
# -----------------------------------
if st.session_state.kick:
    st.error("🚨 KICK ACTIVO")

if st.session_state.loss:
    st.warning("⚠️ LOSS")

if st.session_state.bit_health <= 0:
    st.error("🔩 SARTA ROTA")
if mw < 9:
    st.warning("⚠️ MW BAJO → Riesgo de KICK")

if mw > 13:
    st.warning("⚠️ MW ALTO → Riesgo de pérdidas")

if yp / pv < 0.5:
    st.warning("⚠️ Mala limpieza de pozo")
if ecd > 14:
    st.error("🚨 ECD ALTO → riesgo de fractura")

if st.session_state.gas > 5:
    st.error("🚨 GAS ALTO → riesgo de blowout")

if st.session_state.pit_vol > 520:
    st.error("🚨 GANANCIA DE VOLUMEN")

if st.session_state.pit_vol < 480:
    st.warning("⚠️ PÉRDIDA DE LODO")
    
    # -----------------------------------
# DIAGNÓSTICO INTELIGENTE
# -----------------------------------
st.subheader("🧠 Diagnóstico MENFA")

if st.session_state.kick:
    st.error("🔴 KICK → Aumentar MW y cerrar BOP")

elif mw < 9:
    st.warning("🟠 MW bajo → riesgo de ingreso de fluido")

elif mw > 13:
    st.warning("🟠 MW alto → riesgo de pérdidas")

elif yp / pv < 0.5:
    st.info("🔵 Limpieza deficiente → ajustar YP/PV")

elif rop < 5:
    st.info("🔵 Baja ROP → revisar WOB/RPM o formación")

else:
    st.success("🟢 Operación óptima")
    st.subheader("🧠 Diagnóstico Hidráulico MENFA")

if st.session_state.pit_vol > 520 and st.session_state.gas > 2:
    st.error("🔴 KICK CONFIRMADO → cerrar BOP y circular")

elif st.session_state.pit_vol < 480:
    st.warning("🟠 PÉRDIDAS → reducir MW y caudal")

elif ecd > 14:
    st.warning("🟠 FRACTURA → bajar presión")

elif st.session_state.gas > 3:
    st.info("🔵 GAS EN LODO → monitorear separador")

else:
    st.success("🟢 Sistema hidráulico estable")
# -----------------------------------
# BOTÓN PRINCIPAL (ÚNICO)
# -----------------------------------
if st.button("⛏️ PERFORAR 100m", key="btn_perforar_main"):

    st.session_state.depth += 100
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

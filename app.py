import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import time
if "loss" not in st.session_state:
    st.session_state.loss = False

if "formacion" not in st.session_state:
    st.session_state.formacion = "normal"
# -----------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------
st.set_page_config(page_title="MENFA SIMULADOR PRO", layout="wide")

# -----------------------------------
# ESTILO MENFA
# -----------------------------------
st.markdown("""
<style>
.stApp { background-color: #05070a; color: #00ffcc; }
.stButton>button { background: linear-gradient(135deg, #00ffcc, #008b8b); color: black; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# PRESENTACIÓN INICIAL
# -----------------------------------
if "inicio" not in st.session_state:
    st.session_state.inicio = False

if not st.session_state.inicio:
    st.title("🛢️ MENFA - Simulador de Perforación Profesional")
    st.subheader("Entrenamiento Técnico en Tiempo Real")

    st.markdown("""
    ### 🔹 ¿Qué incluye este simulador?
    - Cabina del perforador tipo Cyberbase
    - Control de pozo (Well Control)
    - Geonavegación
    - Eventos reales (Kick, pesca, desgaste)
    - Evaluación certificada

    ### 🔹 Objetivo:
    Formar operadores con criterio operativo real.
    """)

    if st.button("🚀 INGRESAR AL SIMULADOR"):
        st.session_state.inicio = True
        st.rerun()

    st.stop()

# -----------------------------------
# LOGIN
# -----------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Operador MENFA")

    nombre = st.text_input("Nombre")
    legajo = st.text_input("Legajo")

    if st.button("Ingresar"):
        if nombre:
            st.session_state.auth = True
            st.session_state.nombre = nombre
            st.session_state.legajo = legajo
            st.rerun()
    st.stop()
# -----------------------------------
# MODO ACADEMIA - REGISTRO
# -----------------------------------
import os

if "curso" not in st.session_state:
    st.session_state.curso = "Perforación MENFA"

def guardar_alumno(nombre, legajo):
    archivo = "alumnos_menfa.csv"

    existe = os.path.isfile(archivo)

    with open(archivo, "a", newline="", encoding="utf-8") as f:
        import csv
        writer = csv.writer(f)

        if not existe:
            writer.writerow(["Nombre", "Legajo", "Curso"])

        writer.writerow([nombre, legajo, st.session_state.curso])

guardar_alumno(st.session_state.nombre, st.session_state.legajo)
def guardar_sesion(df, nombre, legajo):

    carpeta = "SESIONES_MENFA"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    archivo = f"{carpeta}/{legajo}_{nombre}.csv"
    df.to_csv(archivo, index=False)
   guardar_sesion(st.session_state.history, st.session_state.nombre, st.session_state.legajo)

# -----------------------------------
# VARIABLES
# -----------------------------------
if "depth" not in st.session_state:
    st.session_state.depth = 2500

if "bit_health" not in st.session_state:
    st.session_state.bit_health = 100

if "kick" not in st.session_state:
    st.session_state.kick = False

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Depth","WOB","RPM","SPP","ROP"])
# impacto pérdida
if st.session_state.loss:
    spp *= 0.5

# desgaste extremo
if st.session_state.bit_health <= 0:
    rop = 0
# -----------------------------------
# SIDEBAR (MANDOS)
# -----------------------------------
st.sidebar.title(f"👷 {st.session_state.nombre}")

wob = st.sidebar.slider("WOB", 0, 60, 25)
rpm = st.sidebar.slider("RPM", 0, 180, 100)
flow = st.sidebar.slider("Flow", 200, 1200, 600)
mw = st.sidebar.slider("Mud Weight", 8.5, 15.0, 10.0)
# -----------------------------------
# MODO INSTRUCTOR (OCULTO)
# -----------------------------------
if "modo_instructor" not in st.session_state:
    st.session_state.modo_instructor = False

with st.sidebar.expander("🔐 PANEL INSTRUCTOR"):
    clave = st.text_input("Clave", type="password")

    if clave == "menfa2026":
        st.session_state.modo_instructor = True
        st.success("Modo instructor activo")

        st.markdown("### 🎮 CONTROL DE EVENTOS")

        if st.button("🚨 GENERAR KICK"):
            st.session_state.kick = True

        if st.button("💧 PÉRDIDA DE CIRCULACIÓN"):
            st.session_state.loss = True

        if st.button("🔩 ROMPER SARTA"):
            st.session_state.bit_health = 0

        if st.button("🪨 FORMACIÓN DURA"):
            st.session_state.formacion = "dura"

        if st.button("🟢 FORMACIÓN BLANDA"):
            st.session_state.formacion = "blanda"
# -----------------------------------
# MOTOR DE CÁLCULO
# -----------------------------------


def calcular(wob, rpm, flow, depth):

    factor_formacion = 1

    if st.session_state.formacion == "dura":
        factor_formacion = 0.5
    elif st.session_state.formacion == "blanda":
        factor_formacion = 1.5

    torque = wob * 0.4 + rpm * 0.1
    spp = flow * 3

    rop = ((wob * rpm) / 500) * factor_formacion

    return torque, spp, rop

# -----------------------------------
# EVENTOS
# -----------------------------------
if random.random() < 0.05:
    st.session_state.kick = True

# desgaste
st.session_state.bit_health -= (wob * 0.05)

# -----------------------------------
# CABINA DEL PERFORADOR
# -----------------------------------
st.title("📟 CABINA DEL PERFORADOR - MENFA")

col1, col2, col3 = st.columns(3)

def gauge(valor, titulo, maximo, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': titulo},
        gauge={'axis': {'range': [0, maximo]},
               'bar': {'color': color}}
    ))
    return fig

col1.plotly_chart(gauge(st.session_state.depth, "DEPTH", 4000, "#00ffcc"), use_container_width=True)
col2.plotly_chart(gauge(torque, "TORQUE", 100, "yellow"), use_container_width=True)
col3.plotly_chart(gauge(spp, "SPP", 5000, "cyan"), use_container_width=True)

# -----------------------------------
# MÉTRICAS
# -----------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("ROP", round(rop,1))
c2.metric("BIT HEALTH", round(st.session_state.bit_health,1))
c3.metric("MW", mw)
# -----------------------------------
# EVENTOS VISUALES
# -----------------------------------
if st.session_state.kick:
    st.error("🚨 KICK ACTIVO → CERRAR BOP INMEDIATAMENTE")

if st.session_state.loss:
    st.warning("⚠️ PÉRDIDA DE CIRCULACIÓN → BAJA SPP")

if st.session_state.bit_health <= 0:
    st.error("🔩 SARTA ROTA → INICIAR PESCA")
# -----------------------------------
# ALERTAS
# -----------------------------------
if st.session_state.kick:
    st.error("🚨 KICK DETECTADO - CERRAR BOP")

# -----------------------------------
# AVANCE
# -----------------------------------
if st.button("⛏️ PERFORAR 10m"):
    st.session_state.depth += 10

    nueva_fila = {
        "Depth": st.session_state.depth,
        "WOB": wob,
        "RPM": rpm,
        "SPP": spp,
        "ROP": rop
    }

    st.session_state.history = pd.concat(
        [st.session_state.history, pd.DataFrame([nueva_fila])],
        ignore_index=True
    )
# -----------------------------------
# CABINA MENFA - NIVEL EMPRESA
# -----------------------------------
st.subheader("🖥️ MENFA CYBERBASE - CABINA PROFESIONAL")

df = st.session_state.history.copy()

if len(df) > 5:

    df["TIME"] = range(len(df))
    df["TORQUE"] = df["WOB"] * 0.4 + np.random.randn(len(df)) * 2
    df["HKLD"] = 220 - df["WOB"] * 1.2 + np.random.randn(len(df)) * 2

    # -----------------------------
    # LÓGICA DE ALARMAS INTELIGENTES
    # -----------------------------
    torque_alert = df["TORQUE"].iloc[-1] > 45
    spp_alert = df["SPP"].iloc[-1] > 4000
    rop_drop = df["ROP"].iloc[-1] < 5

    if torque_alert:
        st.error("⚠️ TORQUE ALTO → Posible pega o vibración")

    if spp_alert:
        st.warning("⚠️ SPP ALTO → Restricción hidráulica")

    if rop_drop:
        st.info("⚠️ BAJA ROP → Cambio de formación o desgaste")

    # -----------------------------
    # PANTALLA 1: HOOKLOAD / TORQUE
    # -----------------------------
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df["TIME"], y=df["HKLD"],
        name="Hook Load",
        line=dict(color="lime", width=3)
    ))

    fig1.add_trace(go.Scatter(
        x=df["TIME"], y=df["TORQUE"],
        name="Torque",
        line=dict(color="yellow", width=2)
    ))

    fig1.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1)
    fig1.add_hrect(y0=50, y1=70, fillcolor="yellow", opacity=0.1)
    fig1.add_hrect(y0=70, y1=120, fillcolor="red", opacity=0.1)

    fig1.update_layout(template="plotly_dark", height=300, title="HOOKLOAD / TORQUE")

    # -----------------------------
    # PANTALLA 2: SPP
    # -----------------------------
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df["TIME"], y=df["SPP"],
        name="SPP",
        line=dict(color="cyan", width=3)
    ))

    fig2.add_hrect(y0=0, y1=3000, fillcolor="green", opacity=0.1)
    fig2.add_hrect(y0=3000, y1=4000, fillcolor="yellow", opacity=0.1)
    fig2.add_hrect(y0=4000, y1=6000, fillcolor="red", opacity=0.1)

    fig2.update_layout(template="plotly_dark", height=300, title="STAND PIPE PRESSURE")

    # -----------------------------
    # PANTALLA 3: ROP vs DEPTH
    # -----------------------------
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df["ROP"], y=df["Depth"],
        name="ROP",
        line=dict(color="orange", width=3)
    ))

    fig3.update_layout(
        template="plotly_dark",
        yaxis=dict(autorange="reversed"),
        height=300,
        title="ROP vs DEPTH"
    )

    # -----------------------------
    # PANTALLA 4: CORRELACIÓN OPERATIVA
    # -----------------------------
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=df["WOB"], y=df["ROP"],
        mode='markers',
        name="Eficiencia",
        marker=dict(color="white")
    ))

    fig4.update_layout(
        template="plotly_dark",
        height=300,
        title="WOB vs ROP (Eficiencia de perforación)"
    )

    # -----------------------------
    # GRID CABINA REAL
    # -----------------------------
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(fig3, use_container_width=True)
    col4.plotly_chart(fig4, use_container_width=True)

    # -----------------------------
    # DIAGNÓSTICO AUTOMÁTICO (CLAVE COMERCIAL)
    # -----------------------------
    st.divider()
    st.subheader("🧠 Diagnóstico Automático MENFA")

    if torque_alert and rop_drop:
        st.error("🔴 POSIBLE PEGA DE TUBERÍA → Reducir WOB y circular")

    elif spp_alert:
        st.warning("🟠 POSIBLE OBSTRUCCIÓN → Revisar boquillas o sólidos")

    elif rop_drop:
        st.info("🔵 FORMACIÓN MÁS DURA → Ajustar parámetros")

    else:
        st.success("🟢 PERFORACIÓN ÓPTIMA")

else:
    st.info("Iniciá perforación para activar cabina profesional.")
# -----------------------------------
# WELL CONTROL
# -----------------------------------
st.subheader("🛡️ WELL CONTROL")

if st.session_state.kick:
    if st.button("🔒 CERRAR BOP"):
        st.session_state.kick = False
        st.success("Pozo controlado")
if st.session_state.kick:
    if st.button("🔒 CERRAR BOP"):
        st.session_state.kick = False
        st.success("Pozo controlado correctamente")
# -----------------------------------
# EVALUACIÓN
# -----------------------------------
st.subheader("🏁 EVALUACIÓN")

score = 100

if st.session_state.kick:
    score -= 30

if st.session_state.loss:
    score -= 20

if st.session_state.bit_health <= 0:
    score -= 25

st.metric("PUNTAJE OPERADOR", score)
st.divider()
st.subheader("🏆 Ranking MENFA (Tiempo Real)")

def generar_ranking():

    carpeta = "SESIONES_MENFA"
    if not os.path.exists(carpeta):
        return pd.DataFrame()

    archivos = os.listdir(carpeta)

    ranking = []

    for arc in archivos:
        try:
            df = pd.read_csv(os.path.join(carpeta, arc))

            nombre = arc.split("_")[1].replace(".csv","")

            rop_prom = df["ROP"].mean()
            prof = df["Depth"].max()

            score = (rop_prom * 2) + (prof / 100)

            ranking.append({
                "Alumno": nombre,
                "ROP Prom": round(rop_prom,2),
                "Profundidad": prof,
                "Score": round(score,2)
            })

        except:
            pass

    return pd.DataFrame(ranking).sort_values(by="Score", ascending=False)

df_rank = generar_ranking()

if not df_rank.empty:
    st.dataframe(df_rank, use_container_width=True)
else:
    st.info("Sin datos aún.")
    with st.expander("🔐 PANEL DOCENTE MENFA"):

    clave = st.text_input("Clave docente", type="password")

    if clave == "menfa_pro":

        st.success("Acceso docente habilitado")

        df_rank = generar_ranking()

        if not df_rank.empty:
            st.dataframe(df_rank)

            st.download_button(
                "📥 Descargar Ranking",
                df_rank.to_csv(index=False),
                "ranking_menfa.csv"
            )

        # RESET CURSO
        if st.button("🧹 Reiniciar curso"):
            import shutil
            if os.path.exists("SESIONES_MENFA"):
                shutil.rmtree("SESIONES_MENFA")
                st.warning("Datos reiniciados")

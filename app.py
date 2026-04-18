import streamlit as st
from streamlit_autorefresh import st_autorefresh
import motor_fisico as motor
import gestion_seguridad as seg
import interfaz_visual as ui
import generador_reportes as rep
import geonavegacion_pro as geo # Tu archivo original

# --- MEMORIA COMPARTIDA ---
@st.cache_resource
def conectar_pizarra():
    return {
        "profundidad_actual": 2500.0, "caudal_maestro": 500.0,
        "wob_maestro": 0.0, "rpm_maestro": 0.0, "torque_maestro": 15.0,
        "presion_base": 1200.0, "alarma_activa": False,
        "mensaje_evento": "Operación Normal", "bop_cerrado": False
    }

piz = conectar_pizarra()

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    u = st.text_input("Usuario")
    c = st.text_input("Clave", type="password")
    if st.button("Ingresar"):
        if c == "menfa2026":
            st.session_state.update({"autenticado": True, "usuario": "Fabricio", "rol": "instructor"})
            st.rerun()
        elif c == "alumno2026":
            st.session_state.update({"autenticado": True, "usuario": u, "rol": "alumno"})
            st.rerun()
    st.stop()

# --- INTERFAZ Y REFRESH ---
st_autorefresh(interval=2000, key=f"ref_{st.session_state.usuario}")
seg.aplicar_estilo_emergencia(piz)
st.title("🏗️ Simulador MENFA 3.0")
ui.render_manual_menfa()

# --- LÓGICA DE CÁLCULO ---
res = motor.calcular_fisica_perforacion(piz["wob_maestro"], piz["rpm_maestro"], piz["torque_maestro"], piz["profundidad_actual"], piz["caudal_maestro"])

# --- PANEL LATERAL ---
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.session_state.rol == "instructor":
        piz["caudal_maestro"] = st.slider("Caudal", 0, 1200, int(piz["caudal_maestro"]))
        piz["rpm_maestro"] = st.slider("RPM", 0, 200, int(piz["rpm_maestro"]))
        if st.button("🚨 ACTIVAR KICK"):
            piz["alarma_activa"] = True
            piz["mensaje_evento"] = "¡KICK DETECTADO!"
            st.rerun()
    
    st.divider()
    if st.button("📊 GENERAR REPORTE PDF"):
        bytes_pdf = rep.generar_pdf(piz, st.session_state.usuario)
        st.download_button("📥 Descargar PDF", bytes_pdf, f"Reporte_{st.session_state.usuario}.pdf")

# --- CUERPO PRINCIPAL ---
t1, t2, t3 = st.tabs(["📊 Consola", "🛡️ BOP", "🛰️ Trayectoria"])

with t1:
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(ui.crear_manometro(piz["presion_base"], "Presión", "PSI", 5000, "red"), use_container_width=True)
    c2.plotly_chart(ui.crear_manometro(res["ROP"], "ROP", "m/h", 60, "lime"), use_container_width=True)
    c3.plotly_chart(ui.crear_manometro(res["HOOK_LOAD"], "Peso Gancho", "klbs", 600, "white"), use_container_width=True)

with t2:
    seg.render_bop_ui(piz)

with t3:
    st.plotly_chart(geo.generar_grafico_trayectoria(piz["profundidad_actual"]))

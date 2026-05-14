import streamlit as st
import pandas as pd
import datetime
import base64  
from streamlit_autorefresh import st_autorefresh
import auth
import ui_components
import logic_events
import generador_reportes
import motor_calculos_avanzados as motor
import bop_panel
import geonavegacion_pro
import manual_tecnico_maestro
import sartas_perforacion as modulo_sartas

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="MENFA 3.0 - Simulador Pro", layout="wide")

st.title("🏗️ Room de Operaciones MENFA")
st.info("Bienvenido al simulador. Asegúrese de tener su Manual Maestro a mano y registrar sus parámetros cada 15 minutos.")

@st.cache_resource
def conectar_pizarra():
    return {
        "profundidad_actual": 2500.0, 
        "caudal_maestro": 500.0,
        "wob_maestro": 12.0, 
        "rpm_maestro": 70.0, 
        "torque_maestro": 3200.0,
        "presion_base": 1200.0, 
        "nivel_tanques": 80.0,
        "densidad_lodo": 10.5,
        "evento_activo": None, 
        "alarma_activa": False, 
        "bop_cerrado": False,
        "toolface": 0,
        "dls_set": 3.0,
        "historial": pd.DataFrame(columns=["Tiempo", "ROP", "WOB", "SPP"])
    }

piz = conectar_pizarra()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

# 2. SISTEMA DE LOGIN DUAL
if not st.session_state.autenticado:
    st.title("🛡️ Sistema de Simulación MENFA")
    col_log, _ = st.columns([1, 2])
    with col_log:
        u = st.text_input("Usuario (Apellido)")
        c = st.text_input("Clave de Acceso", type="password")
        if st.button("Ingresar al Sistema"):
            if u.lower() == "instructor" and c == "menfa2026":
                st.session_state.autenticado = True
                st.session_state.rol = "instructor"
                st.rerun()
            elif auth.validar_acceso(u, c, "alumno"):
                st.session_state.autenticado = True
                st.session_state.rol = "alumno"
                st.session_state.usuario = u
                st.rerun()
            else:
                st.error("Credenciales inválidas")
    st.stop()

# 3. INTERFAZ DEL INSTRUCTOR
if st.session_state.rol == "instructor":
    st.title("👨‍🏫 Consola de Control - Instructor")
    st_autorefresh(interval=2000, key="ref_ins")
    
    with st.expander("🏗️ Configuración Técnica de la Sarta", expanded=False):
        modulo_sartas.configuracion_ui() 
    
    st.divider()
    col_ctrl, col_fail = st.columns([1, 1])
    
    with col_ctrl:
        st.subheader("Controles de Perforación")
        piz["wob_maestro"] = st.slider("Ajustar WOB (klbs)", 0.0, 50.0, float(piz["wob_maestro"]))
        piz["rpm_maestro"] = st.slider("Ajustar RPM", 0, 160, int(piz["rpm_maestro"]))
        piz["caudal_maestro"] = st.slider("Caudal Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]))
        piz["densidad_lodo"] = st.slider("Densidad Lodo (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1)
    
    with col_fail:
        st.subheader("Inyectar Fallas Técnicas")
        if st.button("🚨 DISPARAR KICK (Surgencia)", use_container_width=True):
            piz["evento_activo"] = "KICK"
            piz["alarma_activa"] = True
        if st.button("📉 PÉRDIDA DE RETORNO", use_container_width=True):
            piz["evento_activo"] = "PERDIDA"
            piz["alarma_activa"] = True
        if st.button("✅ NORMALIZAR SISTEMA", use_container_width=True, type="primary"):
            piz["evento_activo"] = None
            piz["alarma_activa"] = False
            piz["presion_base"] = 1200.0
            piz["nivel_tanques"] = 80.0

    st.divider()
    if st.button("Cerrar Sesión Instructor", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# 4. INTERFAZ DEL ALUMNO
else:
    st_autorefresh(interval=2000, key="ref_alu")
    
    if "log_eventos" not in st.session_state:
        st.session_state.log_eventos = []
    if "strokes_totales" not in st.session_state:
        st.session_state.strokes_totales = 0

    # SONIDO DE ALARMA
    if piz.get("alarma_activa", False):
        try:
            with open("assets/alarma.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                st.markdown(f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except: pass

    # CÁLCULOS TÉCNICOS (SARTA Y ECD)
    datos_sarta = modulo_sartas.modulo_sartas_api(piz)
    piz["hook_load"] = datos_sarta["hook_load"]
    piz["tension_max"] = datos_sarta["max_yield"]
    piz["margen_overpull"] = datos_sarta["margen"]

    friccion_anular = (piz["caudal_maestro"] / 1200) * 0.4
    piz["ecd"] = round(piz["densidad_lodo"] + friccion_anular, 2)

    # LÓGICA DE INFLUJO (KICK)
    if piz.get("evento_activo") == "KICK":
        if not piz.get("bop_cerrado", False):
            piz["nivel_tanques"] += 0.5 
        else:
            if piz.get("choke_pos", 0) > 10:
                piz["nivel_tanques"] += 0.1

    # FÍSICA Y AVANCE
    logic_events.gestionar_fallas(piz)
    res = motor.calcular_fisica_perforacion(
        float(piz["wob_maestro"]), float(piz["rpm_maestro"]), 
        float(piz["torque_maestro"]), float(piz["profundidad_actual"]), 
        float(piz["caudal_maestro"]), float(piz["densidad_lodo"])
    )

    if not piz.get("bop_cerrado", False) and piz["rpm_maestro"] > 0 and piz["caudal_maestro"] > 400:
        incremento = (res["ROP"] / 3600) * 2
        piz["profundidad_actual"] = round(piz["profundidad_actual"] + incremento, 4)
        piz["nivel_tanques"] -= 0.005 # Trip Tank
        piz["formacion"] = "🏜️ Perforando"
    else:
        piz["formacion"] = "⏸️ Detenida"

    # SIDEBAR INTEGRAL (MANDOS + NAVEGACIÓN)
    with st.sidebar:
        try: st.image("logo_menfa.png", width=150)
        except: st.title("MENFA 3.0")
        st.header(f"👤 Operador: {st.session_state.get('usuario', 'Invitado')}")
        
        if not piz.get("bop_cerrado", False):
            with st.expander("🕹️ Consola de Mando", expanded=True):
                piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]), key="sld_c")
                piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]), key="sld_r")
                piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), key="num_w")
                piz["densidad_lodo"] = st.slider("Densidad (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1)

            with st.expander("🛰️ Control Direccional (MWD)", expanded=True):
                piz["toolface"] = st.slider("Toolface (TF)", 0, 360, int(piz["toolface"]), 5)
                piz["dls_set"] = st.slider("DLS (Agresividad)", 0.0, 10.0, float(piz["dls_set"]), 0.5)
                st.divider()
                c_inc, c_azi = st.columns(2)
                c_inc.metric("INC", f"{round(res.get('inclinacion', 89.2), 1)}°")
                c_azi.metric("AZI", f"{round(res.get('azimut', 120.5), 1)}°")
                target_tvd = st.number_input("Target TVD (m)", 1500.0, 5000.0, 2750.0, key="tgt_alu")
                st.info(f"Faltan: {round(target_tvd - piz['profundidad_actual'], 2)} m")
        else:
            st.warning("⚠️ Pozo Cerrado")
             with st.expander("📖 Manual Técnico Maestro", expanded=False):
            st.write("Consulta de Procedimientos:")
            # Aquí llamamos a la función de tu módulo manual_tecnico_maestro
            try:
                manual_tecnico_maestro.mostrar_manual_sidebar()
            except:
                st.info("Manual cargado en la base de datos técnica.")
                if st.button("Ver Protocolos de Intervención"):
                    st.info("Protocolos: Verificar presiones antes de abrir BOP.")

        st.divider()

        
        if st.button("🛑 STOP TOTAL", type="primary", use_container_width=True):
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
            st.rerun()

    # TABS
    tab1, tab2, tab_geo, tab_analisis, tab3, tab4 = st.tabs([
        "🎮 Panel Central", "🛡️ Control de Pozos", "🛰️ Geonavegación", "📈 Análisis", "🏆 Ranking", "📜 Certificado"
    ])
    
    with tab1:
        st.subheader(f"Estado: {piz['formacion']}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Densidad (MW/ECD)", f"{piz['densidad_lodo']} / {piz['ecd']} ppg")
        presion_fondo = round(res.get('PH', 0) + (piz['ecd'] - piz['densidad_lodo']) * 0.052 * piz['profundidad_actual'], 1)
        m2.metric("P. Fondo (BHP)", f"{presion_fondo} psi")
        m3.metric("Hook Load", f"{int(piz['hook_load'] / 1000)} klbs", delta=f"{int(piz['margen_overpull'] / 1000)} MOP")
        m4.metric("Nivel Tanques", f"{round(piz['nivel_tanques'], 1)} %", delta=f"{piz['profundidad_actual']} m")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(ui_components.crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True)
        with c2: st.plotly_chart(ui_components.crear_manometro(piz["wob_maestro"], "WOB", "klbs", 50, "orange"), use_container_width=True)
        with c3: st.plotly_chart(ui_components.crear_manometro(piz["rpm_maestro"], "RPM", "rpm", 150, "skyblue"), use_container_width=True)

    with tab2:
        try: bop_panel.render_bop_ui(piz) 
        except: st.error("Error en BOP")

    with tab_geo:
        st.plotly_chart(geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"]), use_container_width=True)

    with tab_analisis:
        if not piz["historial"].empty:
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "SPP"]])
            st.code("\n".join(reversed(st.session_state.log_eventos[-10:])))

    with tab3:
        st.table(pd.DataFrame({"Operador": [st.session_state.get('usuario')], "Profundidad": [piz["profundidad_actual"]]}))

    with tab4:
        if st.button("Finalizar y Generar PDF", type="primary"):
            st.balloons()
            pdf = generador_reportes.crear_certificado_pdf(st.session_state.get('usuario'), 95, piz["profundidad_actual"])
            st.download_button("📥 Descargar", data=pdf, file_name="Certificado.pdf", mime="application/pdf")

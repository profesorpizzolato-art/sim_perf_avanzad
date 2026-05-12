import streamlit as st
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
import auth, ui_components, logic_events, generador_reportes
import motor_calculos_avanzados as motor 
import bop_panel, geonavegacion_pro 
import manual_tecnico_maestro
 
# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="MENFA 3.0 - Simulador Pro", layout="wide")

st.title("🏗️ Room de Operaciones MENFA")
st.info("Bienvenido al simulador. Asegúrese de tener su Manual Maestro a mano y registrar sus parámetros cada 15 minutos de simulación.")

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
        # AGREGADO: Memoria para gráficas
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
    
    col_ctrl, col_fail = st.columns([1, 1])
    
    with col_ctrl:
        st.subheader("Controles de Perforación")
        wob_val = float(piz.get("wob_maestro", 12.0))
        piz["wob_maestro"] = st.slider("Ajustar WOB (klbs)", 0.0, 50.0, wob_val)
        
        valor_seguro_rpm = int(piz.get("rpm_maestro", 70))
        valor_seguro_rpm = max(0, min(160, valor_seguro_rpm))
        piz["rpm_maestro"] = st.slider("Ajustar RPM", 0, 160, valor_seguro_rpm)
        
        caudal_val = int(piz.get("caudal_maestro", 500))
        piz["caudal_maestro"] = st.slider("Caudal Bombas (GPM)", 0, 1200, caudal_val)
        
        dens_val = float(piz.get("densidad_lodo", 10.5))
        piz["densidad_lodo"] = st.slider("Densidad Lodo (ppg)", 8.3, 19.0, dens_val, step=0.1)
    
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

    if st.button("Cerrar Sesión Instructor"):
        st.session_state.autenticado = False
        st.rerun()

# 4. INTERFAZ DEL ALUMNO
else:
    st_autorefresh(interval=2000, key="ref_alu")
    logic_events.gestionar_fallas(piz)
    
    # Cálculos físicos (Motor de simulación)
    res = motor.calcular_fisica_perforacion(
        piz["wob_maestro"], piz["rpm_maestro"], piz["torque_maestro"], 
        piz["profundidad_actual"], piz["caudal_maestro"], piz["densidad_lodo"]
    )

    # --- LÓGICA DE AVANCE Y GEOLOGÍA ---
    if not piz.get("bop_cerrado", False) and piz["rpm_maestro"] > 0 and piz["caudal_maestro"] > 400:
        # Avance real basado en ROP (m/h) convertido a incremento por ciclo (2 seg)
        incremento = (res["ROP"] / 3600) * 2
        piz["profundidad_actual"] = round(piz["profundidad_actual"] + incremento, 4)
        
        # Cambio de Formación Dinámico
        if piz["profundidad_actual"] < 2550:
            piz["formacion"] = "🏜️ Arcilla Blanda (Alta ROP)"
        elif 2550 <= piz["profundidad_actual"] < 2800:
            piz["formacion"] = "🪨 Caliza Compacta (Dureza Media)"
            res["ROP"] *= 0.7  
        else:
            piz["formacion"] = "💎 Basalto/Granito (Dureza Extrema)"
            res["ROP"] *= 0.4  
    else:
        piz["formacion"] = "⏸️ Perforación Detenida"

    # --- LÓGICA DE SEGURIDAD (KICK) ---
    UMBRAL_KICK = 5.0 
    pit_gain = max(0.0, piz["nivel_tanques"] - 80.0)

    if pit_gain >= UMBRAL_KICK and not piz.get("bop_cerrado", False):
        st.markdown("""<style>.stApp {background-color: #4b0000; transition: 0.5s;}</style>""", unsafe_allow_html=True)
        st.error(f"🚨 ¡KICK DETECTADO! Ganancia: {round(pit_gain, 1)} bbl")

    if not piz.get("bop_cerrado", False):
        if st.button("🔴 ACTIVAR CIERRE (SHUT-IN)", width="stretch", type="primary"):
            tvd_ft = piz["profundidad_actual"] * 3.28
            ph = 0.052 * piz["densidad_lodo"] * tvd_ft
            pres_formacion = ph + 300 
            piz["sidpp"] = round(pres_formacion - ph, 2)
            piz["sicp"] = round(piz["sidpp"] + (0.052 * piz["densidad_lodo"] - 0.1) * (pit_gain / 0.0459), 2)
            piz["kmw"] = round((piz["sidpp"] / (0.052 * tvd_ft)) + piz["densidad_lodo"], 2)
            piz["bop_cerrado"] = True
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
            st.rerun()

    # --- ACTUALIZACIÓN DE HISTORIAL ---
    nuevo_punto = {
        "Tiempo": datetime.datetime.now().strftime("%H:%M:%S"),
        "ROP": res["ROP"], "WOB": piz["wob_maestro"], "SPP": piz["presion_base"]
    }
    piz["historial"] = pd.concat([piz["historial"], pd.DataFrame([nuevo_punto])]).tail(20)

    # --- SIDEBAR (CONTROLES OPERATIVOS Y MATERIAL) ---
    with st.sidebar:
        try: st.image("logo_menfa.png", width=150)
        except: st.title("MENFA 3.0")
        
        st.header(f"👤 Alumno: {st.session_state.get('usuario', 'Invitado')}")
        st.divider()

        if not piz.get("bop_cerrado", False):
            st.subheader("🕹️ Consola de Mando")
            piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]))
            piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]))
            piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), step=0.5)
            piz["densidad_lodo"] = st.slider("Densidad (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1)
        else:
            st.warning("⚠️ Controles bloqueados (Pozo Cerrado)")

        if st.button("🛑 STOP TOTAL", width="stretch", type="primary"):
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
            st.rerun()

        st.divider()
        st.subheader("📚 Biblioteca Técnica")
        try:
            pdf_content = manual_tecnico_maestro.generar_manual_completo()
            # Asegurar formato bytes para evitar AttributeError
            pdf_data = bytes(pdf_content) if isinstance(pdf_content, (bytearray, memoryview)) else pdf_content
            
            st.download_button(
                label="📥 Manual Maestro 3.0",
                data=pdf_data, 
                file_name="Manual_MENFA_V3.pdf",
                mime="application/pdf",
                width="stretch"
            )
            st.success("Manual listo")
        except Exception as e:
            st.error(f"Error en manual: {e}")

    # --- CUERPO PRINCIPAL (TABS) ---
    if piz.get("bop_cerrado"):
        with st.expander("📋 HOJA DE MATAR (KILL SHEET)", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("SIDPP", f"{piz['sidpp']} psi")
            col2.metric("SICP", f"{piz['sicp']} psi")
            col3.metric("KMW", f"{piz['kmw']} ppg")
            if piz["densidad_lodo"] >= piz["kmw"]:
                if st.button("🔄 Abrir Pozo (BOP Open)", width="stretch"):
                    piz["bop_cerrado"] = False
                    piz["nivel_tanques"] = 80.0
                    st.rerun()

    tab1, tab2, tab_geo, tab_analisis, tab3, tab4 = st.tabs([
        "🎮 Panel Central", "🛡️ Control de Pozos", "🛰️ Geonavegación", 
        "📈 Análisis", "🏆 Ranking", "📜 Certificado"
    ])
    
    with tab1:
        st.subheader(f"Capa Geológica: {piz.get('formacion', 'Analizando...')}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Densidad Lodo", f"{piz['densidad_lodo']} ppg")
        m2.metric("P. Hidrostática", f"{res.get('PH', 0)} psi")
        m3.metric("Fondo (TVD)", f"{piz['profundidad_actual']} m", delta=f"{round(res['ROP'], 2)} m/h")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(ui_components.crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), width="stretch", key="m_rop")
        with c2: st.plotly_chart(ui_components.crear_manometro(piz["wob_maestro"], "WOB", "klbs", 50, "orange"), width="stretch", key="m_wob")
        with c3: st.plotly_chart(ui_components.crear_manometro(piz["rpm_maestro"], "RPM", "rpm", 150, "skyblue"), width="stretch", key="m_rpm")
        
        c4, c5, c6 = st.columns(3)
        with c4: st.plotly_chart(ui_components.crear_manometro(piz["presion_base"], "Presión SPP", "PSI", 5000, "red"), width="stretch", key="m_spp")
        with c5: st.plotly_chart(ui_components.crear_manometro(res["HOOK_LOAD"], "Hook Load", "klbs", 350, "white"), width="stretch", key="m_hook")
        with c6: st.plotly_chart(ui_components.crear_manometro(piz["nivel_tanques"], "Tanques", "%", 100, "yellow"), width="stretch", key="m_tanques")

    with tab2:
        bop_panel.render_bop_ui(piz)

    with tab_geo:
        st.subheader("Visualización de Trayectoria y Geonavegación")
        fig_geo = geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"])
        st.plotly_chart(fig_geo, width="stretch")
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1: st.metric("Inclinación", f"{round(res.get('inclinacion', 89.2), 1)}°")
        with col_g2: st.metric("Azimut", f"{round(res.get('azimut', 120.5), 1)}°")
        with col_g3: st.info("🎯 Objetivo: Mantener TVD dentro del target.")

    with tab_analisis:
        st.subheader("📈 Monitor de Tendencias Críticas")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write("**Eficiencia: ROP vs WOB**")
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "WOB"]])
        with col_c2:
            st.write("**Circulación: Presión SPP (psi)**")
            st.area_chart(piz["historial"].set_index("Tiempo")["SPP"])

    with tab3:
        st.header("🏆 Ranking de Operadores")
        try:
            df = pd.read_csv("alumnos_ranking.csv")
            st.dataframe(df.sort_values("Puntaje", ascending=False), width="stretch")
        except: st.info("Sin datos registrados.")

    with tab4:
        st.header("📜 Emisión de Certificado")
        if st.button("Finalizar y Generar PDF", type="primary"):
            st.balloons()
            pdf_cert = generador_reportes.crear_certificado_pdf(
                st.session_state.usuario, 95, piz["profundidad_actual"]
            )
            # Asegurar formato bytes para descarga limpia
            pdf_cert_data = bytes(pdf_cert) if isinstance(pdf_cert, (bytearray, memoryview)) else pdf_cert
            
            st.download_button(
                label="📥 Descargar mi Certificado PDF",
                data=pdf_cert_data,
                file_name=f"Certificado_MENFA_{st.session_state.usuario}.pdf",
                mime="application/pdf",
                width="stretch"
            )

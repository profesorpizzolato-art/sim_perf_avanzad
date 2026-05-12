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
        piz["profundidad_actual"], piz["caudal_maestro"]
    )

    # --- [NUEVO] LÓGICA DE SEGURIDAD Y CONTROL DE POZOS ---
    UMBRAL_KICK = 5.0  # Barriles
    # Calculamos la ganancia comparando el nivel actual contra el inicial (80%)
    pit_gain = max(0.0, piz["nivel_tanques"] - 80.0)

    # 1. Alarma de Kick (Cambio de color de fondo)
    if pit_gain >= UMBRAL_KICK and not piz.get("bop_cerrado", False):
        st.markdown(
            """<style>.stApp {background-color: #4b0000; transition: 0.5s;}</style>""", 
            unsafe_allow_html=True
        )
        st.error(f"🚨 ¡KICK DETECTADO! Ganancia en piletas: {round(pit_gain, 1)} bbl")
        st.toast("¡PELIGRO! Cierre el pozo inmediatamente", icon="⚠️")

    # 2. Lógica de Cierre y Cálculos de Presión
    if not piz.get("bop_cerrado", False):
        if st.button("🔴 ACTIVAR CIERRE (SHUT-IN)", use_container_width=True, type="primary"):
            tvd_ft = piz["profundidad_actual"] * 3.28
            ph = 0.052 * piz["densidad_lodo"] * tvd_ft
            pres_formacion = ph + 300  # Simulamos desequilibrio
            
            # Guardamos en la pizarra para que persista
            piz["sidpp"] = round(pres_formacion - ph, 2)
            piz["sicp"] = round(piz["sidpp"] + (0.052 * piz["densidad_lodo"] - 0.1) * (pit_gain / 0.0459), 2)
            piz["kmw"] = round((piz["sidpp"] / (0.052 * tvd_ft)) + piz["densidad_lodo"], 2)
            
            piz["bop_cerrado"] = True
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
            st.rerun()

    # --- ACTUALIZACIÓN DE HISTORIAL PARA GRÁFICAS ---
    nuevo_punto = {
        "Tiempo": datetime.datetime.now().strftime("%H:%M:%S"),
        "ROP": res["ROP"],
        "WOB": piz["wob_maestro"],
        "SPP": piz["presion_base"]
    }
    piz["historial"] = pd.concat([piz["historial"], pd.DataFrame([nuevo_punto])]).tail(20)

    # --- BARRA LATERAL (Controles del Perforador) ---
    with st.sidebar:
        try: st.image("logo_menfa.png", width=150)
        except: st.title("MENFA 3.0")
        
        st.header(f"👤 Alumno: {st.session_state.get('usuario', 'Invitado')}")
        st.divider()

        st.subheader("🕹️ Consola de Mando")
        if not piz["bop_cerrado"]:
            piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]))
            piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]))
            piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), step=0.5)
        else:
            st.warning("⚠️ Controles bloqueados por BOP")

        st.divider()
        if st.button("🛑 STOP", use_container_width=True, type="primary"):
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
        
        if piz["bop_cerrado"]: st.error("🚫 POZO CERRADO")
        else: st.success("✅ FLUJO ABIERTO")

    # --- CUERPO PRINCIPAL ---
    st.title("Simulador de Perforación Avanzado")
    
    # 3. Mostrar Kill Sheet si el pozo está cerrado
    if piz.get("bop_cerrado"):
        st.warning("🔒 PROTOCOLO DE CONTROL DE POZO ACTIVADO")
        with st.expander("📋 HOJA DE MATAR (KILL SHEET) - DATOS DE CIERRE", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("SIDPP", f"{piz['sidpp']} psi")
            c2.metric("SICP", f"{piz['sicp']} psi")
            c3.metric("KMW (Lodo de Matar)", f"{piz['kmw']} ppg")
            st.info(f"Instrucción: Incrementar densidad a {piz['kmw']} ppg.")
            if st.button("🔄 Abrir Pozo (BOP Open)"):
                piz["bop_cerrado"] = False
                piz["nivel_tanques"] = 80.0
                st.rerun()

    # AGREGADA PESTAÑA DE ANÁLISIS
    tab1, tab2, tab_geo, tab_analisis, tab3, tab4 = st.tabs([
        "🎮 Panel Central", 
        "🛡️ Control de Pozos", 
        "🛰️ Geonavegación", 
        "📈 Análisis de Tendencias",
        "🏆 Ranking", 
        "📜 Certificado"
    ])
    
    with tab1:
        m1, m2, m3 = st.columns(3)
        m1.metric("Densidad Lodo", f"{piz['densidad_lodo']} ppg")
        presion_h = round(0.052 * piz['densidad_lodo'] * piz['profundidad_actual'] * 3.28, 0)
        m2.metric("Presión Hidrostática", f"{presion_h} psi")
        m3.metric("Fondo de Pozo (TVD)", f"{piz['profundidad_actual']} m")
        st.divider()
        
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(ui_components.crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True)
        with c2: st.plotly_chart(ui_components.crear_manometro(piz["wob_maestro"], "WOB", "klbs", 50, "orange"), use_container_width=True)
        with c3: st.plotly_chart(ui_components.crear_manometro(piz["rpm_maestro"], "RPM", "rpm", 150, "skyblue"), use_container_width=True)
        
        c4, c5, c6 = st.columns(3)
        with c4: st.plotly_chart(ui_components.crear_manometro(piz["presion_base"], "Presión SPP", "PSI", 5000, "red"), use_container_width=True)
        with c5: st.plotly_chart(ui_components.crear_manometro(res["HOOK_LOAD"], "Hook Load", "klbs", 350, "white"), use_container_width=True)
        with c6: st.plotly_chart(ui_components.crear_manometro(piz["nivel_tanques"], "Tanques", "%", 100, "yellow"), use_container_width=True)

    with tab2:
        bop_panel.render_bop_ui(piz)

    with tab_geo:
        st.subheader("Visualización de Trayectoria y Geonavegación")
        fig_geo = geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"])
        st.plotly_chart(fig_geo, use_container_width=True)
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1: st.metric("Inclinación", f"{round(res.get('inclinacion', 89.2), 1)}°")
        with col_g2: st.metric("Azimut", f"{round(res.get('azimut', 120.5), 1)}°")
        with col_g3: st.info("🎯 Objetivo: Mantener TVD dentro del target.")

    # CONTENIDO DE LA NUEVA PESTAÑA DE ANÁLISIS
    with tab_analisis:
        st.subheader("📈 Monitor de Tendencias Críticas")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.write("**Eficiencia: ROP vs WOB**")
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "WOB"]])
        with col_c2:
            st.write("**Circulación: Presión SPP (psi)**")
            st.area_chart(piz["historial"].set_index("Tiempo")["SPP"])
        st.info("💡 Estas gráficas te permiten detectar cambios de formación y fallas mecánicas antes que los manómetros.")

    with tab3:
        st.header("🏆 Ranking de Operadores")
        try:
            df = pd.read_csv("alumnos_ranking.csv")
            st.dataframe(df.sort_values("Puntaje", ascending=False), use_container_width=True)
        except: st.info("Sin datos registrados.")

    with tab4:
        st.header("📜 Emisión de Certificado")
        if st.button("Finalizar y Generar PDF"):
            st.balloons()
            pdf = generador_reportes.crear_certificado_pdf(st.session_state.usuario, 95, piz["profundidad_actual"])
            st.download_button("📥 Descargar PDF", data=pdf, file_name=f"Certificado_{st.session_state.usuario}.pdf")

with st.sidebar: 
    st.subheader("📚 Material de Referencia Oficial")
    st.write("Descarga el material técnico actualizado de MENFA.")
    
    # Generamos el contenido una sola vez para que el botón esté siempre listo
    # No te preocupes por el rendimiento, FPDF es muy rápido.
    try:
        pdf_content = manual_tecnico_maestro.generar_manual_completo()
        
        st.download_button(
            label="📥 Descargar Manual Maestro 3.0",
            data=pdf_content,
            file_name="Manual_Maestro_MENFA_3.pdf",
            mime="application/pdf",
            width="stretch"  # Esto elimina la advertencia de logs
        )
        st.success("Manual listo para descarga")
    except Exception as e:
        st.error(f"Error al preparar el manual: {e}")

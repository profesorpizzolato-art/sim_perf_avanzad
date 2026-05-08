import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import auth, ui_components, logic_events, generador_reportes
import motor_calculos_avanzados as motor 
import bop_panel, geonavegacion_pro 
import manual_tecnico_maestro
 
st.title("🏗️ Room de Operaciones MENFA")
st.info("Bienvenido al simulador. Asegúrese de tener su Manual Maestro a mano y registrar sus parámetros cada 15 minutos de simulación.")
# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="MENFA 3.0 - Simulador Pro", layout="wide")

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
        "densidad_lodo": 10.5, # Densidad inicial en ppg
        "evento_activo": None, 
        "alarma_activa": False, 
        "bop_cerrado": False
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
        piz["wob_maestro"] = st.slider("Ajustar WOB (klbs)", 0.0, 50.0, piz["wob_maestro"])
        piz["rpm_maestro"] = st.slider("Ajustar RPM", 0, 160, piz["rpm_maestro"])
        piz["caudal_maestro"] = st.slider("Caudal Bombas (GPM)", 0, 1200, piz["caudal_maestro"])
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

    # --- BARRA LATERAL (Controles del Perforador) ---
    with st.sidebar:
        try: st.image("logo_menfa.png", width=150)
        except: st.title("MENFA 3.0")
        
        st.header(f"👤 Alumno: {st.session_state.get('usuario', 'Invitado')}")
        st.divider()

        # Mandos Operativos Estándar
        st.subheader("🕹️ Consola de Mando")
        piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]))
        piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]))
        piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), step=0.5)
        piz["densidad_lodo"] = st.slider("Densidad (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1)

        st.divider()
        
        # Mandos de Geonavegación (Nuevos)
        st.subheader("🛰️ Control Direccional")
        col_dir1, col_dir2 = st.columns(2)
        with col_dir1:
            if st.button("🔼 Subir", help="Corregir hacia arriba", use_container_width=True):
                piz["inc_target"] = piz.get("inc_target", 90.0) + 0.5
        with col_dir2:
            if st.button("🔽 Bajar", help="Corregir hacia abajo", use_container_width=True):
                piz["inc_target"] = piz.get("inc_target", 90.0) - 0.5

        st.divider()
        if st.button("🛑 STOP", use_container_width=True, type="primary"):
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
        
        if piz["bop_cerrado"]: st.error("🚫 POZO CERRADO")
        else: st.success("✅ FLUJO ABIERTO")

    # --- CUERPO PRINCIPAL ---
    st.title("Simulador de Perforación Avanzado")
    if piz["alarma_activa"]:
        st.error(f"🚨 ALERTA: {piz['evento_activo']}")

    # Definición de Pestañas Únicas
    tab1, tab2, tab_geo, tab3, tab4 = st.tabs([
        "🎮 Panel Central", 
        "🛡️ Control de Pozos", 
        "🛰️ Geonavegación", 
        "🏆 Ranking", 
        "📜 Certificado"
    ])
    
    with tab1:
        # Métricas Rápidas
        m1, m2, m3 = st.columns(3)
        m1.metric("Densidad Lodo", f"{piz['densidad_lodo']} ppg")
        presion_h = round(0.052 * piz['densidad_lodo'] * piz['profundidad_actual'] * 3.28, 0)
        m2.metric("Presión Hidrostática", f"{presion_h} psi")
        m3.metric("Fondo de Pozo (TVD)", f"{piz['profundidad_actual']} m")
        st.divider()
        
        # Manómetros
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
        # El gráfico reacciona a la profundidad y correcciones del alumno
        fig_geo = geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"])
        st.plotly_chart(fig_geo, use_container_width=True)
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1: st.metric("Inclinación", f"{round(res.get('inclinacion', 89.2), 1)}°")
        with col_g2: st.metric("Azimut", f"{round(res.get('azimut', 120.5), 1)}°")
        with col_g3: st.info("🎯 Objetivo: Mantener TVD dentro del target.")

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
    with st.sidebar: # Línea 194
         st.subheader("📚 Material de Referencia Oficial") # Línea 195 (CON ESPACIOS)
         st.write("Aquí van los manuales de MENFA") # También con espacios
        with st.spinner("Compilando manual..."):
            pdf_content = manual_tecnico_maestro.generar_manual_completo()
            st.download_button(
                label="📥 Descargar Manual Completo (PDF)",
                data=pdf_content,
                file_name="Manual_Maestro_MENFA_3.pdf",
                mime="application/pdf"
            )

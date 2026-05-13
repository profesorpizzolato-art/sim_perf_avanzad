import streamlit as st
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
import auth
import ui_components
import logic_events
import generador_reportes
import motor_calculos_avanzados as motor
import bop_panel
import geonavegacion_pro
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
    
    # --- [NUEVO] CONFIGURACIÓN DE SARTA PARA EL INSTRUCTOR ---
    with st.expander("🏗️ Configuración Técnica de la Sarta", expanded=False):
        modulo_sartas.configuracion_ui() 
    
    st.divider()

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

    st.divider()
    if st.button("Cerrar Sesión Instructor", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
# 4. INTERFAZ DEL ALUMNO (Versión Unificada con Control de Pozos)
else:
    st_autorefresh(interval=2000, key="ref_alu")
    
    # --- [A] INICIALIZACIÓN DE SISTEMAS DE SEGUIMIENTO ---
    if "log_eventos" not in st.session_state:
        st.session_state.log_eventos = []
    if "strokes_totales" not in st.session_state:
        st.session_state.strokes_totales = 0

    # --- [NUEVA INTEGRACIÓN] CÁLCULO DE SARTA API 5DP ---
    datos_sarta = modulo_sartas.modulo_sartas_api(piz)
    piz["hook_load"] = datos_sarta["hook_load"]
    piz["tension_max"] = datos_sarta["max_yield"]
    piz["margen_overpull"] = datos_sarta["margen"]

    # Alerta de seguridad por tensión en Bitácora
    if piz["hook_load"] > piz["tension_max"] * 0.9:
        if not st.session_state.log_eventos or "⚠️ TENSIÓN" not in st.session_state.log_eventos[-1]:
            hora = datetime.datetime.now().strftime('%H:%M:%S')
            st.session_state.log_eventos.append(f"[{hora}] ⚠️ ALTA TENSIÓN: Sarta cerca del límite de fluencia.")

    # --- [B] LÓGICA DE INFLUJO DINÁMICO ---
    if piz.get("evento_activo") == "KICK":
        if not piz.get("bop_cerrado", False):
            piz["nivel_tanques"] += 0.5 
        else:
            if piz.get("choke_pos", 0) > 10:
                piz["nivel_tanques"] += 0.1
                if not st.session_state.log_eventos or "⚠️ Fuga" not in st.session_state.log_eventos[-1]:
                    hora = datetime.datetime.now().strftime('%H:%M:%S')
                    st.session_state.log_eventos.append(f"[{hora}] ⚠️ Fuga detectada: Presión insuficiente por Choke abierto.")

    # --- [C] CONTADOR DE STROKES (BOMBAS) ---
    if piz["caudal_maestro"] > 0:
        spm_simulado = piz["caudal_maestro"] / 8
        st.session_state.strokes_totales += (spm_simulado * 0.033)

    # --- [D] PROCESAMIENTO DE FALLAS Y FÍSICA ---
    logic_events.gestionar_fallas(piz)
    
    res = motor.calcular_fisica_perforacion(
        float(piz["wob_maestro"]), 
        float(piz["rpm_maestro"]), 
        float(piz["torque_maestro"]), 
        float(piz["profundidad_actual"]), 
        float(piz["caudal_maestro"]), 
        float(piz["densidad_lodo"])
    )

    # --- [E] LÓGICA DE AVANCE Y GEOLOGÍA ---
    if not piz.get("bop_cerrado", False) and piz["rpm_maestro"] > 0 and piz["caudal_maestro"] > 400:
        incremento = (res["ROP"] / 3600) * 2
        piz["profundidad_actual"] = round(piz["profundidad_actual"] + incremento, 4)
        
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

    # --- ACTUALIZACIÓN DE HISTORIAL ---
    try:
        nuevo_punto = pd.DataFrame([{
            "Tiempo": datetime.datetime.now().strftime("%H:%M:%S"),
            "ROP": res["ROP"], 
            "WOB": piz["wob_maestro"], 
            "SPP": piz["presion_base"]
        }])
        piz["historial"] = pd.concat([piz["historial"], nuevo_punto], ignore_index=True).tail(20)
    except Exception as e:
        st.error(f"Error en historial: {e}")

    # --- SIDEBAR (CONTROLES Y GEONAVEGACIÓN) ---
    with st.sidebar:
        try: st.image("logo_menfa.png", width=150)
        except: st.title("MENFA 3.0")
        
        st.header(f"👤 Alumno: {st.session_state.get('usuario', 'Invitado')}")
        st.divider()

        if not piz.get("bop_cerrado", False):
            with st.expander("🕹️ Consola de Mando", expanded=True):
                piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]), key="sld_caudal_alu")
                piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]), key="sld_rpm_alu")
                piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), step=0.5, key="num_wob_alu")
                piz["densidad_lodo"] = st.slider("Densidad (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1, key="sld_dens_alu")
            
            st.divider()
            with st.expander("🛰️ Geonavegación", expanded=True):
                col_s1, col_s2 = st.columns(2)
                col_s1.metric("INC", f"{round(res.get('inclinacion', 89.2), 1)}°")
                col_s2.metric("AZI", f"{round(res.get('azimut', 120.5), 1)}°")
                target_tvd = st.number_input("Target TVD (m)", 1500.0, 5000.0, 2750.0, step=10.0, key="num_target_alu")
                st.info(f"Distancia: {round(target_tvd - piz['profundidad_actual'], 2)} m")
        else:
            st.warning("⚠️ Controles bloqueados (Pozo Cerrado)")

        if st.button("🛑 STOP TOTAL", width="stretch", type="primary", key="btn_stop_alu"):
            piz["rpm_maestro"], piz["caudal_maestro"] = 0, 0
            st.rerun()

    # --- TABS PRINCIPALES (MANTENIENDO TODO) ---
    tab1, tab2, tab_geo, tab_analisis, tab3, tab4 = st.tabs([
        "🎮 Panel Central", "🛡️ Control de Pozos", "🛰️ Geonavegación", 
        "📈 Análisis", "🏆 Ranking", "📜 Certificado"
    ])
    
    # TAB 1: PANEL CENTRAL (Con nueva métrica de Hook Load)
    with tab1:
        st.subheader(f"Capa Geológica: {piz.get('formacion', 'Analizando...')}")
        m1, m2, m3, m4 = st.columns(4) # Expandido a 4 para incluir Hook Load
        m1.metric("Densidad Lodo", f"{piz['densidad_lodo']} ppg")
        m2.metric("P. Hidrostática", f"{round(res.get('PH', 0), 2)} psi")
        m3.metric("Hook Load", f"{int(piz['hook_load'] / 1000)} klbs", delta=f"{int(piz['margen_overpull'] / 1000)} MOP")
        m4.metric("Fondo (TVD)", f"{piz['profundidad_actual']} m", delta=f"{round(res['ROP'], 2)} m/h")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(ui_components.crear_manometro(res["ROP"], "ROP", "m/hr", 60, "lime"), use_container_width=True, key="gau_rop_alu")
        with c2: st.plotly_chart(ui_components.crear_manometro(piz["wob_maestro"], "WOB", "klbs", 50, "orange"), use_container_width=True, key="gau_wob_alu")
        with c3: st.plotly_chart(ui_components.crear_manometro(piz["rpm_maestro"], "RPM", "rpm", 150, "skyblue"), use_container_width=True, key="gau_rpm_alu")

    # TAB 2: CONTROL DE POZOS
    with tab2:
        try: bop_panel.render_bop_ui(piz) 
        except Exception as e: st.error(f"Error técnico: {e}")

    # TAB GEO: GEONAVEGACIÓN (Se mantiene intacto)
    with tab_geo:
        st.subheader("🛰️ Geonavegación en Tiempo Real")
        fig_geo = geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"])
        st.plotly_chart(fig_geo, use_container_width=True, key="chart_geo_alu")

    # TAB ANÁLISIS: GRÁFICOS (Se mantiene intacto)
    with tab_analisis:
        st.subheader("📈 Análisis de Tendencias Técnicas")
        if not piz["historial"].empty:
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "SPP"]], height=250)
            st.divider()
            st.subheader("📜 Bitácora Reciente")
            st.code("\n".join(reversed(st.session_state.log_eventos[-10:])))
        else:
            st.info("Esperando datos...")

    # TAB 3 y 4 (Se mantienen Ranking y Certificado igual que antes)
    with tab3:
        st.subheader("🏆 Cuadro de Mérito - MENFA")
        ranking_data = pd.DataFrame({
            "Operador": [st.session_state.get('usuario', 'Alumno'), "Operador Master", "Guardia A"],
            "Profundidad": [piz["profundidad_actual"], 5200.0, 4800.0],
            "Estado": ["En Proceso", "Completado", "Completado"]
        }).sort_values(by="Profundidad", ascending=False)
        st.table(ranking_data)

    with tab4:
        st.header("📜 Emisión de Certificado")
        if st.button("Finalizar y Generar PDF", type="primary", key="btn_cert_alu"):
            st.balloons()
            pdf_cert = generador_reportes.crear_certificado_pdf(st.session_state.get('usuario', 'Alumno'), 95, piz["profundidad_actual"])
            st.download_button(
                label="📥 Descargar Certificado",
                data=pdf_cert,
                file_name=f"Certificado_MENFA_{st.session_state.get('usuario', 'Alumno')}.pdf",
                mime="application/pdf",
                key="btn_dl_cert_alu"
            )
   
# ... (Tu código de certificado)

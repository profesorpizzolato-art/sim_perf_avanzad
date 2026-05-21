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
        "choke_pos": 0,
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

   # --- SIDEBAR FINAL (CORREGIDO SIN ERRORES DE INDENTACIÓN) ---
    with st.sidebar:
        try:
            st.image("logo_menfa.png", width=150)
        except:
            st.title("MENFA 3.0")
        
        st.header(f"👤 Operador: {st.session_state.get('usuario', 'Invitado')}")
        st.divider()

        # 1. CONTROLES OPERATIVOS
        if not piz.get("bop_cerrado", False):
            with st.expander("🕹️ Consola de Mando", expanded=True):
                piz["caudal_maestro"] = st.slider("Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]), key="sld_c_f")
                piz["rpm_maestro"] = st.slider("Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]), key="sld_r_f")
                piz["wob_maestro"] = st.number_input("WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), key="num_w_f")
                piz["densidad_lodo"] = st.slider("Densidad (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1, key="sld_den_f")

            with st.expander("🛰️ Control Direccional (MWD)", expanded=True):
                piz["toolface"] = st.slider("Toolface (TF)", 0, 360, int(piz.get("toolface", 0)), 5)
                piz["dls_set"] = st.slider("DLS (Agresividad)", 0.0, 10.0, float(piz.get("dls_set", 3.0)), 0.5)
                st.divider()
                st.metric("INC / AZI", f"{round(res.get('inclinacion', 89.2), 1)}° / {round(res.get('azimut', 120.5), 1)}°")
        else:
            st.warning("⚠️ Pozo Cerrado - Controles Bloqueados")

        st.divider()

    # --- BLOQUE DEL MANUAL (Asegúrate de que este 'with' esté bien alineado) ---
        with st.sidebar.expander("📖 Manual Técnico Maestro", expanded=False):
            try:
                # 1. Mostramos la interfaz
                manual_tecnico_maestro.mostrar_manual_sidebar()
                
                st.divider()
                
                # 2. Botón de generación (usando el nuevo estándar width='stretch')
                if st.button("🚀 Generar PDF del Manual", width='stretch'):
                    with st.spinner("Compilando material..."):
                        # Llamamos a tu función de manual_tecnico_maestro
                        pdf_data = manual_tecnico_maestro.generar_manual_completo()
                        
                        st.download_button(
                            label="📥 Descargar Copia", 
                            data=pdf_data,
                            file_name="Manual_Maestro_MENFA_3.0.pdf",
                            mime="application/pdf",
                            width='stretch'
                        )
            except Exception as e:
                st.error(f"Error al cargar el manual: {e}")

        # 3. BOTÓN DE EMERGENCIA
        if st.button("🛑 STOP TOTAL", type="primary", use_container_width=True, key="btn_final_stop"):
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
        st.subheader("🛡️ Sistema de Control de Superficie")
        
        # Intentamos renderizar la interfaz visual del BOP
        try: 
            bop_panel.render_bop_ui(piz) 
        except: 
            st.error("Error al cargar los controles visuales del BOP")

        st.divider()
        
        # --- LÓGICA DE CONTROL OPERATIVO ---
        col_bop1, col_bop2 = st.columns(2)
        
        with col_bop1:
            st.write("🔧 **Accionamiento de Seguridad**")
            # El botón cambia su etiqueta y color según el estado
            if not piz.get("bop_cerrado", False):
                if st.button("🔴 CERRAR POZO (Shut-In)", use_container_width=True, type="primary"):
                    piz["bop_cerrado"] = True
                    piz["rpm_maestro"] = 0  # Seguridad: No se puede rotar con BOP cerrado
                    piz["alarma_activa"] = False # Apagamos la alarma sonora al tomar acción
                    st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ POZO CERRADO: Protocolo de seguridad activado.")
                    st.rerun()
            else:
                if st.button("🟢 ABRIR POZO (Open BOP)", use_container_width=True):
                    piz["bop_cerrado"] = False
                    st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 POZO ABIERTO: Reinicio de operaciones.")
                    st.rerun()

        with col_bop2:
            st.write("🔌 **Control de Presiones**")
            
            # 1. Definición estricta de las opciones del Choke Manifold
            opciones_choke = [0, 10, 25, 50, 75, 100]
            
            # 2. Rescate y sanitización segura del valor en memoria
            try:
                choke_actual = int(piz.get("choke_pos", 0))
            except:
                choke_actual = 0
                
            # Forzamos que esté dentro de las opciones válidas para evitar el ValueError
            if choke_actual not in opciones_choke:
                choke_actual = 0
            
            # 3. Renderizado seguro con clave única
            piz["choke_pos"] = st.select_slider(
                "Apertura de Choke (%)",
                options=opciones_choke,
                value=choke_actual,
                key="choke_control_secure_slider",
                help="Controla la contrapresión para circular el kick."
            )
            
            # Cálculo de contrapresión dinámica (Backpressure)
            if piz.get("bop_cerrado", False):
                # Si el choke está muy cerrado, la presión sube
                backpressure = (100 - piz["choke_pos"]) * 5.5
                piz["presion_base"] = 1200 + backpressure 
                st.metric("Contrapresión (Backpressure)", f"{int(backpressure)} psi")
            else:
                piz["presion_base"] = 1200 # Presión normal de circulación

        # --- INFO DE SEGURIDAD ---
        if piz.get("evento_activo") == "KICK" and piz.get("bop_cerrado"):
            st.success("✅ Influjo contenido. Proceda a circular con el Método del Perforador.")
        elif piz.get("evento_activo") == "KICK" and not piz.get("bop_cerrado"):
            st.warning("⚠️ ¡ALERTA! El pozo fluye. Cierre el BOP inmediatamente.")

    with tab_geo:
        st.plotly_chart(geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"]), use_container_width=True)

    with tab_analisis:
        st.subheader("📈 Tendencias en Tiempo Real")
        
        if not piz["historial"].empty:
            # Graficamos ROP y SPP para ver el comportamiento del pozo
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "SPP"]], height=300)
            
            st.divider()
            st.subheader("📜 Bitácora de Operaciones")
            # Mostramos los últimos 10 eventos registrados
            if st.session_state.log_eventos:
                log_texto = "\n".join(reversed(st.session_state.log_eventos[-10:]))
                st.code(log_texto, language="bash")
            else:
                st.info("No hay eventos registrados en la bitácora aún.")
        else:
            st.warning("📊 Esperando la recolección de datos... Perfore unos metros para ver las tendencias.")

    with tab3:
        st.table(pd.DataFrame({"Operador": [st.session_state.get('usuario')], "Profundidad": [piz["profundidad_actual"]]}))

    with tab4:
        if st.button("Finalizar y Generar PDF", type="primary"):
            st.balloons()
            pdf = generador_reportes.crear_certificado_pdf(st.session_state.get('usuario'), 95, piz["profundidad_actual"])
            st.download_button("📥 Descargar", data=pdf, file_name="Certificado.pdf", mime="application/pdf")

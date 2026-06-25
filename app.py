import streamlit as st
import pandas as pd
from datetime import datetime
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
import fluidos_y_sincronia as modulo_fluidos 
# --- IMPORTACIÓN DEL NUEVO MÓDULO DE CONTROL OPERATIVO DINÁMICO ---
import control_operativo as modulo_operativo

# 1. CONFIGURACIÓN E INICIALIZACIÓN ABSOLUTA
st.set_page_config(page_title="MENFA 3.0 - Simulador Pro", layout="wide", page_icon="🏗️")

# Inyección de estilo CSS para mejorar la UI oscura de la cabina
st.markdown("""
    <style>
    .metric-box { background-color: #1e2430; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ Room de Operaciones MENFA")

# NUEVO REQUISITO OPERATIVO DE 1 MINUTO
st.error("⏱️ **CONTROL OPERATIVO ESTRICTO: REGISTRAR PARÁMETROS CADA 1 MINUTO**")
with st.expander("📋 HOJA DE RUTA EXPRESA PARA EL OPERADOR (EXXONMOBIL TOP 40 COMPLIANT)", expanded=True):
    st.markdown("""
    * **Densidad (ECD):** Monitorear que flote entre **9.8 ppg** (riesgo de brote) y **15.5 ppg** (riesgo de fractura).
    * **Limpieza Anular (Pozos >40°):** Es mandatorio mantener las RPM y revoques firmes. Las píldoras de limpieza (*sweeps*) no reemplazan la reología base.
    * **Maniobras de Sacada (POOH):** Si el sobrepulso (*overpull*) supera las **30,000 lbs**, ¡no jale! Conecte Top Drive y recircule (*MR MC*).
    * **Optimización Fast Drill:** Ante vibraciones de *Stick-Slip*, ajuste las RPM inmediatamente entre 60 y 80 RPM y optimice WOB.
    """)

# ==============================================================================
# 🛡️ PERSISTENCIA INDIVIDUAL: LA PIZARRA VIVE EN EL SESSION STATE DE CADA ALUMNO
# ==============================================================================
if "pizarra" not in st.session_state:
    st.session_state.pizarra = {
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
        "historial": pd.DataFrame(columns=["Tiempo", "ROP", "WOB", "SPP"]),
        
        # Variables de inicialización para el módulo de fluidos
        "ecd": 10.5,
        "eficiencia_limpieza": 100.0,
        "mse": 0,
        
        # 🔧 SOLUCIÓN PARA TELEMETRÍA BOP UI
        "total_strokes": 0,       
        "bop_annular": False,     
        "bop_pipe": False,        
        "presion_acumulador": 3000.0,  
        "presion_manifold": 1500.0,    

        # ⚙️ VARIABLES DE CONTROL OPERATIVO AVANZADO Y DINÁMICO
        "vida_trepano": 100.0,       
        "contaminacion_lodo": 0.0,   
        "geo_actual": "Cacheuta",  
        "geo_desc": "Formación compacta lutítica. Monitorear torque por riesgo de aprisionamiento.",
        "bit_balling_activo": False,
        "rop_consigna": 0.0,

        # 🚀 INTEGRACIÓN EXXONMOBIL TOP 40: NUEVAS LLAVES LÓGICAS
        "angulo_pozo": 45.0,              # Activador de pozo inclinado (>40°)
        "sobrepulso_real": 12000.0,       # lbs de Overpull simulado en viajes
        "npt_overpull_atascado": False,   # Estado de pega mecánica
        "stick_slip_activo": False,        # Vibración torsional destructiva
        "whirl_activo": False             # Vibración severa del BHA
    }

if "log_eventos" not in st.session_state:
    st.session_state.log_eventos = []

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

piz = st.session_state.pizarra

# 2. SISTEMA DE LOGIN DUAL
if not st.session_state.autenticado:
    st.title("🛡️ Sistema de Simulación MENFA")
    col_log, _ = st.columns([1, 2])
    with col_log:
        u = st.text_input("Usuario (Apellido)")
        c = st.text_input("Clave de Acceso", type="password")
        if st.button("Ingresar al Sistema", use_container_width=True):
            if u.lower() == "instructor" and c == "menfa2026":
                st.session_state.autenticado = True
                st.session_state.rol = "instructor"
                st.rerun()
            elif u.strip() != "" and c == "alumno2026":
                st.session_state.autenticado = True
                st.session_state.rol = "alumno"
                st.session_state.usuario = u.strip().capitalize()
                st.rerun()
            else:
                st.error("Credenciales inválidas. Verifique el usuario o la clave.")
    st.stop()

# 3. INTERFAZ DEL INSTRUCTOR
if st.session_state.rol == "instructor":
    st.title("👨‍🏫 Consola de Control - Instructor")
    st_autorefresh(interval=2000, key="ref_ins")
    
    with st.expander("🏗️ Configuración Técnica de la Sarta y Pozo", expanded=False):
        modulo_sartas.configuracion_ui() 
        # 🚀 INTEGRACIÓN EXXONMOBIL: Setear ángulo para activar lógicas críticas de limpieza
        piz["angulo_pozo"] = st.slider("Ángulo de Inclinación del Pozo (°)", 0.0, 90.0, float(piz["angulo_pozo"]))
    
    st.divider()
    col_ctrl, col_fail = st.columns([1, 1])
    
    with col_ctrl:
        st.subheader("Controles de Perforación")
        piz["wob_maestro"] = st.slider("Ajustar WOB (klbs)", 0.0, 50.0, float(piz["wob_maestro"]))
        piz["rpm_maestro"] = st.slider("Ajustar RPM", 0, 160, int(piz["rpm_maestro"]))
        piz["caudal_maestro"] = st.slider("Caudal Bombas (GPM)", 0, 1200, int(piz["caudal_maestro"]))
        piz["densidad_lodo"] = st.slider("Densidad Lodo (ppg)", 8.3, 19.0, float(piz["densidad_lodo"]), step=0.1)
    
    with col_fail:
        st.subheader("Inyectar Fallas Técnicas (ExxonMobil Lógicas)")
        if st.button("🚨 DISPARAR KICK (Surgencia)", use_container_width=True):
            piz["evento_activo"] = "KICK"
            piz["alarma_activa"] = True
        if st.button("📉 PÉRDIDA DE RETORNO", use_container_width=True):
            piz["evento_activo"] = "PERDIDA"
            piz["alarma_activa"] = True
            
        # 🚀 INTEGRACIÓN EXXONMOBIL: Inyectores específicos del Top 40
        if st.button("⛓️ INYECTAR EXCESO DE ARRASTRE (>30,000 lbs POOH)", use_container_width=True):
            piz["sobrepulso_real"] = 35000.0
            st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] [INST] Inyección de alto arrastre en sarta.")
        if st.button("🌀 INYECTAR VIBRACIÓN STICK-SLIP", use_container_width=True):
            piz["stick_slip_activo"] = True
            piz["alarma_activa"] = True
            
        if st.button("✅ NORMALIZAR SISTEMA", use_container_width=True, type="primary"):
            piz["evento_activo"] = None
            piz["alarma_activa"] = False
            piz["presion_base"] = 1200.0
            piz["nivel_tanques"] = 80.0
            piz["vida_trepano"] = 100.0
            piz["contaminacion_lodo"] = 0.0
            piz["bit_balling_activo"] = False
            piz["sobrepulso_real"] = 12000.0
            piz["npt_overpull_atascado"] = False
            piz["stick_slip_activo"] = False
            piz["whirl_activo"] = False

    st.divider()
    if st.button("Cerrar Sesión Instructor", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# 4. INTERFAZ DEL ALUMNO
else:
    st_autorefresh(interval=2000, key="ref_alu")

    # SONIDO DE ALARMA
    if piz.get("alarma_activa", False):
        try:
            with open("assets/alarma.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                st.markdown(f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except: 
            pass

    # CÁLCULOS TÉCNICOS (SARTA)
    datos_sarta = modulo_sartas.modulo_sartas_api(piz)
    piz["hook_load"] = datos_sarta["hook_load"]
    piz["tension_max"] = datos_sarta["max_yield"]
    piz["margen_overpull"] = datos_sarta["margen"]

    # LÓGICA DE INFLUJO ACTIVO
    if piz.get("evento_activo") == "KICK":
        if not piz.get("bop_cerrado", False):
            piz["nivel_tanques"] += 0.6  
        else:
            if piz.get("choke_pos", 0) > 15:
                piz["nivel_tanques"] += 0.1  

    logic_events.gestionar_fallas(piz)
    
    if "profundidad_dinamica" not in st.session_state:
        st.session_state["profundidad_dinamica"] = float(piz["profundidad_actual"])

    # EJECUCIÓN DEL MOTOR DE FÍSICA DE FONDO
    res = motor.calcular_fisica_perforacion(
        float(piz["wob_maestro"]), 
        float(piz["rpm_maestro"]), 
        float(piz["torque_maestro"]), 
        float(st.session_state["profundidad_dinamica"]), 
        float(piz["caudal_maestro"]), 
        float(piz["densidad_lodo"])
    )

    bop_abierto = not piz.get("bop_cerrado", False)
    rotaria_activa = int(piz["rpm_maestro"]) > 0
    bombas_ok = int(piz["caudal_maestro"]) > 400

    # 🔄 ACUMULACIÓN REAL DE STROKES
    if int(piz["caudal_maestro"]) > 0:
        emboladas_ciclo = (int(piz["caudal_maestro"]) / 60) * 2 * 0.95
        piz["total_strokes"] += int(max(emboladas_ciclo, 1))

    # --- LÓGICA INTEGRADORA DEL CONTROL DE ROP (AUTO-DRILLER) ---
    if bop_abierto and rotaria_activa and bombas_ok and not piz.get("npt_overpull_atascado", False):
        # Determinar ROP base según el switch de cabina
        if piz.get("rop_consigna", 0.0) > 0.0:
            rop_base = float(piz["rop_consigna"])
        else:
            rop_base = float(res.get("ROP", 0))

        # Degradación del trépano
        factor_desgaste = (piz["wob_maestro"] * piz["rpm_maestro"]) * 0.00005
        piz["vida_trepano"] = max(piz["vida_trepano"] - factor_desgaste, 0.0)
        
        # Penalización por desgaste y arcillas embozadas
        rop_real = rop_base * (piz["vida_trepano"] / 100.0)
        if piz.get("bit_balling_activo", False):
            rop_real *= 0.15  
            
        # 🚀 INTEGRACIÓN EXXONMOBIL: Penalización por Vibración Torsional (Stick-Slip)
        if piz.get("stick_slip_activo", False):
            rop_real *= 0.4
            piz["vida_trepano"] = max(piz["vida_trepano"] - 0.1, 0.0) # Desgaste severo acelerado
            
        # Integración de profundidad en tiempo real
        factor_tiempo = 2 / 3600 
        incremento = rop_real * factor_tiempo * 2 
        
        st.session_state["profundidad_dinamica"] += incremento
        piz["profundidad_actual"] = round(st.session_state["profundidad_dinamica"], 4)
        piz["nivel_tanques"] -= 0.003  
        
        if piz.get("bit_balling_activo", False):
            piz["formacion"] = "🚨 EMBOZADO (Bit Balling)"
        elif piz.get("stick_slip_activo", False):
            piz["formacion"] = "🌀 ALERTA: Vibración Stick-Slip Detectada"
        else:
            piz["formacion"] = f"🏜️ Perforando Tramo {piz.get('geo_actual', 'Cacheuta')}"
        
        # Registro en la base histórica temporal
        nuevo_registro = pd.DataFrame([{
            "Tiempo": datetime.now().strftime("%H:%M:%S"),
            "ROP": round(rop_real, 2),
            "WOB": round(float(piz["wob_maestro"]), 2),
            "SPP": round(float(piz["presion_base"]), 2)
        }])
        piz["historial"] = pd.concat([piz["historial"], nuevo_registro], ignore_index=True).tail(30)
    else:
        rop_real = 0.0
        piz["profundidad_actual"] = round(st.session_state["profundidad_dinamica"], 4)
        if piz.get("npt_overpull_atascado", False):
            piz["formacion"] = "❌ NPT CRÍTICO: Sarta Atascada Mecánicamente por jalar >30 klbs"
        else:
            piz["formacion"] = "⏸️ Operación Detenida / Fuera de Parámetros"

    # EVALUACIÓN HIDRÁULICA DE FLUIDOS Y SINCRONÍA
    analisis_fluido = modulo_fluidos.evaluar_sincronia_operativa(
        caudal_gpm=float(piz["caudal_maestro"]),
        densidad_lodo=float(piz["densidad_lodo"]),
        presion_standpipe=float(piz["presion_base"]),
        rpm=float(piz["rpm_maestro"]),
        wob=float(piz["wob_maestro"]),
        rop_actual=rop_real,
        profundidad_m=float(piz["profundidad_actual"])
    )
    
    piz["ecd"] = analisis_fluido["ecd"]
    piz["eficiencia_limpieza"] = analisis_fluido["eficiencia_limpieza"]
    
    # 🚀 INTEGRACIÓN EXXONMOBIL: Si el pozo supera los 40°, se castiga automáticamente la limpieza 
    # si las RPM o el caudal no acompañan la remoción de lechos de recortes
    if piz["angulo_pozo"] > 40.0:
        if piz["rpm_maestro"] < 80 or piz["caudal_maestro"] < 600:
            piz["eficiencia_limpieza"] = max(piz["eficiencia_limpieza"] - 25.0, 30.0)
            if "Riesgo de embachamiento por ángulo de inclinación >40°" not in [a["msg"] for a in analisis_fluido["alertas"]]:
                analisis_fluido["alertas"].append({"tipo": "WARN", "msg": "Riesgo de embachamiento por ángulo de inclinación >40° (Top 40 Rule)"})

    piz["mse"] = analisis_fluido["mse"]
    piz["torque_maestro"] = analisis_fluido["torque"]
        
    # --- CONSTRUCCIÓN DEL SIDEBAR DE MANDOS ---
    with st.sidebar:
        try:
            st.image("logo_menfa.png", width=160)
        except:
            st.title("🏗️ MENFA PRO")
        
        st.subheader(f"👤 Operador: {st.session_state.get('usuario', 'Invitado')}")
        st.markdown(f"**Estatus:** Cabina Activa")
        st.divider()

        if not piz.get("bop_closed_master", False):
            with st.sidebar.expander("🕹️ Consola de Mando de Cabina", expanded=True):
                # CONTROL DE MODO DE ROP (ADDS DEL DASHBOARD)
                modo_perforacion = st.radio(
                    "Modo de Avance del Freno:",
                    ["Manual (Setear WOB)", "Automático (Gobernar ROP)"],
                    index=0,
                    key="modo_perf_selector"
                )
                
                st.divider()
                piz["caudal_maestro"] = st.slider("Bombas de Lodo (GPM)", 0, 1200, int(piz["caudal_maestro"]), key="sld_c_f")
                piz["rpm_maestro"] = st.slider("Mesa Rotaria (RPM)", 0, 160, int(piz["rpm_maestro"]), key="sld_r_f")
                
                # 🚀 INTEGRACIÓN EXXONMOBIL: Acción correctiva para mitigar Stick-Slip
                if piz.get("stick_slip_activo", False) and 60 <= piz["rpm_maestro"] <= 80 and piz["wob_maestro"] > 15:
                    piz["stick_slip_activo"] = False
                    piz["alarma_activa"] = False
                    st.toast("✅ ¡Práctica Correctiva ExxonMobil! Vibración Stick-slip mitigada por ajuste de RPM/WOB.")

                if modo_perforacion == "Manual (Setear WOB)":
                    piz["wob_maestro"] = st.number_input("Peso sobre Trépano - WOB (klbs)", 0.0, 60.0, float(piz["wob_maestro"]), step=1.0, key="num_w_f")
                    piz["rop_consigna"] = 0.0  
                else:
                    piz["rop_consigna"] = st.slider("Consigna ROP Destacada (m/hr)", 0.0, 45.0, float(piz.get("rop_consigna", 15.0)), step=0.5, key="sld_rop_ctrl")
                    factor_wob_reactivo = (piz["rop_consigna"] * 1.4) / max(piz["rpm_maestro"] / 70, 0.4)
                    piz["wob_maestro"] = round(min(factor_wob_reactivo, 45.0), 1)
                    st.caption(f"🤖 Peso regulado automáticamente: **{piz['wob_maestro']} klbs**")

            with st.expander("🛰️ Control Direccional (MWD)", expanded=False):
                piz["toolface"] = st.slider("Orientación Toolface (TF)", 0, 360, int(piz.get("toolface", 0)), 5)
                piz["dls_set"] = st.slider("Agresividad Dogleg Severity", 0.0, 10.0, float(piz.get("dls_set", 3.0)), 0.5)
                st.divider()
                st.metric("Inclinación / Azimut", f"{round(res.get('inclinacion', 89.2), 1)}° / {round(res.get('azimut', 120.5), 1)}°")
        else:
            st.warning("⚠️ Controles de perforación bloqueados por Cierre de Pozo.")

        st.divider()
        with st.sidebar.expander("📖 Manual de Consulta Técnica", expanded=False):
            try:
                manual_tecnico_maestro.mostrar_manual_sidebar()
            except:
                st.error("Manual no disponible en este bloque.")

        if st.button("🛑 PARADA DE EMERGENCIA", type="primary", use_container_width=True):
            piz["rpm_maestro"], piz["caudal_maestro"], piz["wob_maestro"], piz["rop_consigna"] = 0, 0, 0.0, 0.0
            st.rerun()

    # --- DISEÑO DEL CUERPO CENTRAL DE TRABAJO (TABS) ---
    tab_central, tab_bop, tab_geo, tab_graficos, tab_ranking, tab_cierre = st.tabs([
        "🎮 Panel Central", "🛡️ Control de Pozos & BOP", "🛰️ Geonavegación", "📈 Análisis de Tendencias", "🏆 Ranking", "📜 Certificación"
    ])
    
    with tab_central:
        # Fila de Alertas y Notificaciones del Sistema de Seguridad
        for alerta in analisis_fluido["alertas"]:
            if alerta["tipo"] == "ERROR":
                st.error(f"🚨 CRÍTICO: {alerta['msg']}")
                if f"⚠️ {alerta['msg']}" not in st.session_state.log_eventos:
                    st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] {alerta['msg']}")
            else:
                st.warning(f"⚠️ ADVERTENCIA: {alerta['msg']}")

        if piz.get("bit_balling_activo", False):
            st.error("💩 **ALERTA MECÁNICA:** Trépano embozado por arcillas reactivas. ROP severamente penalizada.")

        # 🚀 INTEGRACIÓN EXXONMOBIL: Alertas de Interfaz del Top 40
        if piz.get("sobrepulso_real", 0.0) > 30000.0:
            st.error(f"⚠️ **ALERTA DE SEGURIDAD (ARRASTRE):** Sobrepulso actual de {piz['sobrepulso_real']:,} lbs supera el límite de 30k lbs.")
            col_exxon1, col_exxon2 = st.columns(2)
            with col_exxon1:
                if st.button("🚨 SEGUIR JALANDO SARTA", use_container_width=True, type="primary"):
                    piz["npt_overpull_atascado"] = True
                    piz["alarma_activa"] = True
                    st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ERROR OPERATIVO: Sarta rota/atascada por exceso de tensión.")
            with col_exxon2:
                if st.button("🔄 APLICAR MR MC (Bajar y rotar/circular)", use_container_width=True):
                    piz["sobrepulso_real"] = 12000.0
                    piz["npt_overpull_atascado"] = False
                    st.success("Sarta liberada siguiendo protocolo ExxonMobil.")
                    st.rerun()

        # Panel de Telemetría Principal (KPIs)
        st.markdown("### 📊 Telemetría de Fondo en Tiempo Real")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Profundidad de Fondo", f"{piz['profundidad_actual']:,} m")
        m2.metric("Densidad MW / ECD", f"{piz['densidad_lodo']} / {piz['ecd']:.2f} ppg")
        
        presion_fondo = round(res.get('PH', 0) + (piz['ecd'] - piz['densidad_lodo']) * 0.052 * piz['profundidad_actual'], 1)
        m3.metric("Presión de Fondo (BHP)", f"{presion_fondo:,} psi")
        m4.metric("Limpieza Anular", f"{piz['eficiencia_limpieza']:.1f} %")

        # Fila de Instrumentos Gráficos Dinámicos
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(ui_components.crear_manometro(rop_real, "ROP (Velocidad de Avance)", "m/hr", 60, "lime"), use_container_width=True)
        with c2: st.plotly_chart(ui_components.crear_manometro(piz["wob_maestro"], "WOB (Peso Real)", "klbs", 50, "orange"), use_container_width=True)
        with c3: st.plotly_chart(ui_components.crear_manometro(piz["rpm_maestro"], "RPM (Rotación)", "rpm", 150, "skyblue"), use_container_width=True)

        st.divider()
        st.markdown("### 🧪 Laboratorio Mecánico y Control de Fluidos")
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        
        with col_acc1:
            st.info(f"**Formación Activa:** {piz['geo_actual']}\n\n*Detalle:* {piz['geo_desc']}\n\n*Ángulo del Pozo:* {piz['angulo_pozo']}°")
        with col_acc2:
            st.metric("Contaminación del Fluido", f"{piz['contaminacion_lodo']:.1f} %")
            if st.button("🧪 Dosificar Químicos / Filtrar Lodo", use_container_width=True):
                piz["contaminacion_lodo"] = max(piz["contaminacion_lodo"] - 30.0, 0.0)
                piz["bit_balling_activo"] = False
                st.rerun()
        with col_acc3:
            st.metric("Estado del Trépano", f"{piz['vida_trepano']:.1f} %")
            if st.button("🔧 Realizar Maniobra y Cambiar Trépano", use_container_width=True, type="primary" if piz['vida_trepano'] < 40 else "secondary"):
                piz["vida_trepano"] = 100.0
                piz["rpm_maestro"], piz["caudal_maestro"], piz["wob_maestro"], piz["rop_consigna"] = 0, 0, 0.0, 0.0
                st.rerun()

    with tab_bop:
        st.subheader("🛡️ Consola de Control de Presiones Superficiales")
        col_str, col_btn_rst = st.columns([2, 1])
        with col_str:
            st.metric(label="Contador de Emboladas (Total Strokes)", value=f"{piz.get('total_strokes', 0):,}")
        with col_btn_rst:
            st.write("")  
            if st.button("🔄 Reiniciar Contador de Emboladas", use_container_width=True):
                piz["total_strokes"] = 0
                st.rerun()
                
        st.divider()
        try: 
            bop_panel.render_bop_ui(piz) 
        except Exception as e: 
            st.error(f"⚠️ Error de variables en Interfaz BOP: {e}")

        st.divider()
        col_bop1, col_bop2 = st.columns(2)
        with col_bop1:
            st.markdown("**Accionamiento Hidráulico (Válvulas)**")
            if not piz.get("bop_cerrado", False):
                if st.button("🔴 EJECUTAR SHUT-IN (Cerrar Pozo)", use_container_width=True, type="primary"):
                    piz["bop_cerrado"] = True
                    piz["rpm_maestro"], piz["rop_consigna"] = 0, 0.0
                    piz["alarma_activa"] = False 
                    piz["bop_annular"] = True
                    piz["bop_pipe"] = True
                    st.session_state.log_eventos.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ POZO CERRADO.")
                    st.rerun()
            else:
                if st.button("🟢 REAPERTURA DE BOP (Open Well)", use_container_width=True):
                    piz["bop_cerrado"] = False
                    piz["bop_annular"] = False
                    piz["bop_pipe"] = False
                    st.rerun()

        with col_bop2:
            st.markdown("**Control de Contrapresión (Choke Manifold)**")
            opciones_choke = [0, 10, 25, 50, 75, 100]
            choke_actual = int(piz.get("choke_pos", 0)) if piz.get("choke_pos", 0) in opciones_choke else 0
            
            piz["choke_pos"] = st.select_slider("Apertura Choke (%)", options=opciones_choke, value=choke_actual, key="choke_ctrl")
            
            if piz.get("bop_cerrado", False):
                backpressure = (100 - piz["choke_pos"]) * 6.2
                piz["presion_base"] = 1200 + backpressure 
                st.metric("Contrapresión Aplicada", f"{int(backpressure)} psi")
            else:
                piz["presion_base"] = 1200 

    with tab_geo:
        st.subheader("🛰️ Monitoreo de Trayectoria Direccional")
        st.plotly_chart(geonavegacion_pro.generar_grafico_trayectoria(piz["profundidad_actual"]), use_container_width=True)

    with tab_graficos:
        st.subheader("📈 Tendencias y Registro Histórico")
        if not piz["historial"].empty:
            st.line_chart(piz["historial"].set_index("Tiempo")[["ROP", "SPP"]], height=300)
            st.divider()
            st.markdown("### 📜 Bitácora de Eventos Recientes")
            if st.session_state.log_eventos:
                st.code("\n".join(reversed(st.session_state.log_eventos[-12:])), language="bash")
        else:
            st.warning("📊 Esperando adquisición de datos mecánicos.")

    with tab_ranking:
        st.subheader("🏆 Tabla de Desempeño en Tiempo Real")
        st.table(pd.DataFrame({
            "Operador en Cabina": [st.session_state.get('usuario', 'Invitado')], 
            "Metros Perforados Totales": [piz["profundidad_actual"]],
            "Eficiencia Hidráulica": [f"{piz['eficiencia_limpieza']:.1f} %"]
        }))

    with tab_cierre:
        st.subheader("📜 Cierre de Guardia y Certificación")
        if st.button("🏁 Finalizar Simulación y Generar Reporte", type="primary", use_container_width=True):
            st.balloons()
            pdf = generador_reportes.crear_certificado_pdf(st.session_state.get('usuario', 'Invitado'), 95, piz["profundidad_actual"])
            st.download_button("📥 Descargar Certificado MENFA (.pdf)", data=pdf, file_name=f"Certificado_MENFA_{st.session_state.get('usuario')}.pdf", mime="application/pdf", use_container_width=True)

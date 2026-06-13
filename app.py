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

st.title("🏗️ Room de Operaciones MENFA")

# NUEVO REQUISITO OPERATIVO DE 1 MINUTO
st.error("⏱️ **CONTROL OPERATIVO ESTRICTO: REGISTRAR PARÁMETROS CADA 1 MINUTO**")
with st.expander("📋 HOJA DE RUTA EXPRESA PARA EL OPERADOR", expanded=True):
    st.markdown("""
    * **Densidad (ECD):** Monitorear que flote entre **9.8 ppg** (riesgo de brote) y **15.5 ppg** (riesgo de fractura).
    * **Limpieza Anular:** Mantener la eficiencia por encima del **70%** para evitar el asentamiento de ripio y pegas de sarta.
    * **Torque y MSE:** Vigilar las fluctuaciones continuas. Cambios bruscos indican desgaste de trépano o nueva formación.
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
        
        # 🔧 INICIALIZACIÓN DE VARIABLES PARA CONTROL DE POZOS Y BOP UI
        "total_strokes": 0,       # Contador físico de emboladas acumuladas
        "bop_annular": "Abierto",  # Estado del preventor anular
        "bop_pipe": "Abierto",      # Estado del preventor de arietes

        # ⚙️ VARIABLES DE CONTROL OPERATIVO AVANZADO Y DINÁMICO
        "vida_trepano": 100.0,       # Estado de los cortadores (%)
        "contaminacion_lodo": 0.0,   # Sólidos incorporados (%)
        "geo_actual": "Superficie",  # Nombre de la formación geológica
        "geo_desc": "Iniciando tramo de perforación.",
        "bit_balling_activo": False  # Alerta de trépano embozado
    }

if "log_eventos" not in st.session_state:
    st.session_state.log_eventos = []

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

# Variable de referencia directa para simplificar la escritura en los módulos
piz = st.session_state.pizarra

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
            # Reset de fallas operativas mecánicas
            piz["vida_trepano"] = 100.0
            piz["contaminacion_lodo"] = 0.0
            piz["bit_balling_activo"] = False

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
    piz

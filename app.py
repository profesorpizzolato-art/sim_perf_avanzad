import streamlit as st
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis
import sarta_pro as sarta

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", page_icon="assets/logo_menfa.png")

# 2. CONSTANTES DE SEGURIDAD
CLAVE_ALUMNO = "menfa2026"
CLAVE_INSTRUCTOR = "admin_mza"

# 3. SISTEMA DE SEGURIDAD
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None
    st.session_state.usuario = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO AL RIG</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        input_pass = st.text_input("Código de Seguridad:", type="password")
        if st.button("CONECTAR CON LA CABINA", use_container_width=True):
            if input_pass == CLAVE_INSTRUCTOR:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "instructor", "Fabricio Pizzolato"
                st.rerun()
            elif input_pass == CLAVE_ALUMNO:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "alumno", "Operador en Evaluación"
                st.rerun()
            else:
                st.error("Código inválido.")
    st.stop()

# --- 4. FILTRO DE CONFIGURACIÓN (Forzado para Well Control) ---
if not piz.get("configurado"):
    st.warning("⚠️ Configuración inicial pendiente.")
    
    # Este botón va a forzar el inicio si el selector falla
    if st.button("🚀 FORZAR ARRANQUE DEL RIG"):
        piz["configurado"] = True
        piz["tvd_target"] = 3500.0 # Valor estándar Vaca Muerta
        piz["profundidad_actual"] = 1200.0 # Empezamos ya perforando
        pm.actualizar_fichero(piz)
        st.rerun()

    pm.selector_yacimiento_mendoza(piz)
    
    if st.session_state.rol == "alumno":
        st.info("Esperando que el instructor configure el pozo...")
        st.stop()
# --- 5. FILTRO DE CONFIGURACIÓN ---
if not piz.get("configurado"):
    st.warning("⚠️ El sistema requiere configuración inicial del yacimiento.")
    pm.selector_yacimiento_mendoza(piz)
    if st.session_state.rol == "alumno":
        st.info("Esperando que el instructor configure el pozo...")
        st.stop()

# 6. PROCESAMIENTO TÉCNICO Y SARTAS (API 5DP)
datos_fisica = motor.calcular_todo(piz)
resistencia = sarta.modulo_sartas_api(piz) 
datos_fisica["hook_load"] = resistencia.get("hook_load", 0)
datos_fisica["max_yield"] = resistencia.get("max_yield", 0)

# --- 7. MOTOR DE AVANCE Y GEONAVEGACIÓN ---
if not piz.get("bop_cerrado"):
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        avance = (rop_actual / 3600) * 15 # Factor de simulación
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4) 
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
        piz["tvd"] = datos_fisica.get("TVD", piz.get("tvd", 0))
    
    influjo_rate = piz.get("influjo_instructor", 0) 
    piz["volumen_piletas"] += (influjo_rate * 0.1)
    datos_fisica["Influjo"] = influjo_rate 

# --- 8. GUARDAR Y RENDERIZAR ---
pm.actualizar_fichero(piz) 

st.sidebar.title(f"👤 {st.session_state.usuario}")

# Fix ZeroDivisionError
meta = piz.get("tvd_target", 2500.0)
meta = 2500.0 if meta <= 0 else meta
prof_actual = piz.get("profundidad_actual", 0.0)
st.progress(min(prof_actual / meta, 1.0), text=f"Progreso: {prof_actual:.2f} m / {meta} m")

if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica)
elif st.session_state.rol == "instructor":
    tab1, tab2 = st.tabs(["🎮 Control de Pozo", "🔩 Configuración de Sarta"])
    with tab1:
        control.panel_instructor(piz)
    with tab2:
        sarta.configuracion_ui()

# --- 9. ALERTAS Y CIERRE ---
if datos_fisica["max_yield"] > 0 and datos_fisica["hook_load"] > (datos_fisica["max_yield"] * 0.9):
    st.warning("⚠️ TENSIÓN EN SARTA PRÓXIMA AL LÍMITE DE FLUENCIA")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

time.sleep(0.5)
st.rerun()

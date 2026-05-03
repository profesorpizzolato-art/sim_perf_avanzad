import streamlit as st
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", page_icon="assets/logo_menfa.png")

# --- 2. SISTEMA DE CLAVES ---
CLAVE_ALUMNO = "menfa2026"
CLAVE_INSTRUCTOR = "admin_mza"

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO</h1>", unsafe_allow_html=True)
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
            else: st.error("Código inválido.")
    st.stop()

# --- 3. CONEXIÓN A PIZARRA Y VARIABLES ---
piz = pm.conectar_pizarra()
if "profundidad_actual" not in piz: piz["profundidad_actual"] = 0.0
if "volumen_piletas" not in piz: piz["volumen_piletas"] = 1200.0

# 4. FILTRO DE CONFIGURACIÓN
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 5. PROCESAMIENTO TÉCNICO (Física Base)
datos_fisica = motor.calcular_todo(piz)

# --- 6. EL MOTOR INTEGRAL (Avance + GeoNav + Control) ---
if not piz.get("bop_cerrado"):
    # A. Avance de Profundidad
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_avance = 15 
        avance = (rop_actual / 3600) * factor_avance
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
        
        # B. GEONAVEGACIÓN (Vaca Muerta Activa)
        # Sincronizamos la trayectoria con los cálculos del motor
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
        piz["tvd"] = datos_fisica.get("TVD", piz.get("tvd", 0))
    
    # C. CONTROL DE POZO (Well Control)
    # Reacción del volumen de piletas ante influjos o pérdidas
    influjo_rate = datos_fisica.get("Influjo", 0)
    piz["volumen_piletas"] += (influjo_rate * 0.1)
else:
    # Si el BOP está cerrado, la profundidad no se mueve pero las presiones sí
    st.sidebar.warning("⚠️ POZO CERRADO (SHUT-IN)")

# --- 7. INTERFAZ Y RENDERIZADO ---
st.sidebar.title(f"👤 {st.session_state.usuario}")

# Barra de progreso visual para el avance
meta = 2500.0 # O la que definas en el yacimiento
progreso = min(piz["profundidad_actual"] / meta, 1.0)
st.progress(progreso, text=f"Progreso: {piz['profundidad_actual']:.2f} m / {meta} m")

if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica)
elif st.session_state.rol == "instructor":
    control.panel_instructor(piz)

if st.sidebar.button("Log Out"):
    st.session_state.auth = False
    st.rerun()

# 8. ALERTAS CRÍTICAS
if datos_fisica.get("Influjo", 0) > 1.0:
    st.toast("🚨 ¡KICK DETECTADO! REVISAR PILETAS", icon="🔥")

# 9. LATIDO
time.sleep(0.5)
st.rerun()

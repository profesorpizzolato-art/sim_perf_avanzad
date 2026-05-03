import streamlit as st
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN TÉCNICA (Identidad IPCL MENFA)
st.set_page_config(
    layout="wide", 
    page_title="MENFA Drilling Sim 3.0", 
    page_icon="🏗️"
)

# --- 2. SISTEMA DE CLAVES DE ACCESO ---
CLAVE_ALUMNO = "menfa2026"      # Entregas esta al inicio de la clase
CLAVE_INSTRUCTOR = "admin_mza"  # Solo para vos (Fabricio)

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None

# Muro de Seguridad Inicial
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO AL RIG</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.info("Identifíquese para activar los sistemas del pozo.")
        input_pass = st.text_input("Código de Seguridad:", type="password")
        
        if st.button("CONECTAR CON LA CABINA", use_container_width=True):
            if input_pass == CLAVE_INSTRUCTOR:
                st.session_state.auth = True
                st.session_state.rol = "instructor"
                st.session_state.usuario = "Fabricio Pizzolato" #
                st.success("Acceso INSTRUCTOR: Panel de control liberado.")
                time.sleep(1)
                st.rerun()
            
            elif input_pass == CLAVE_ALUMNO:
                st.session_state.auth = True
                st.session_state.rol = "alumno"
                st.session_state.usuario = "Operador en Evaluación"
                st.success("Acceso ALUMNO: Consola de perforación activa.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Código inválido. Verifique con el Instructor de MENFA.")
    st.stop()

# --- 3. INICIO DEL SIMULADOR (POST-AUTENTICACIÓN) ---
piz = pm.conectar_pizarra() #

# Inicialización de variables persistentes en la Pizarra
if "volumen_piletas" not in piz: piz["volumen_piletas"] = 1200.0
if "profundidad_actual" not in piz: piz["profundidad_actual"] = 0.0

# 4. FILTRO DE CONFIGURACIÓN (Yacimiento Mendoza)
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz) #
    st.stop()

# 5. PROCESAMIENTO TÉCNICO (Motor de Física)
datos_fisica = motor.calcular_todo(piz) #

# --- 6. MOTOR DE AVANCE GLOBAL Y GEONAVEGACIÓN ---
if not piz.get("bop_cerrado"): # Si el pozo está abierto, progresa
    # A. Avance de Profundidad (Metros Medidos)
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_tiempo = 5 # Acelera la visibilidad en clase
        avance = (rop_actual / 3600) * factor_tiempo
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4)
        
        # B. Geonavegación (Cambios de trayectoria en Vaca Muerta)
        # Actualiza inclinación y azimut basados en el Toolface del alumno
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
    
    # C. Dinámica de Tanques (Reacción a Kicks o Pérdidas)
    influjo_rate = datos_fisica.get("Influjo", 0)
    if influjo_rate != 0:
        piz["volumen_piletas"] += (influjo_rate * 0.1)

# 7. RENDERIZADO SEGÚN EL ROL DEFINIDO EN LOGIN
st.sidebar.title(f"👤 {st.session_state.usuario}")
st.sidebar.caption(f"ROL: {st.session_state.rol.upper()}")

if st.session_state.rol == "alumno":
    # El alumno solo opera, no puede sabotearse a sí mismo
    vis.renderizar_cabina_perforador(piz, datos_fisica)
elif st.session_state.rol == "instructor":
    # El instructor monitorea y genera eventos críticos
    control.panel_instructor(piz)

# Botón de desconexión rápida
if st.sidebar.button("Cerrar Sesión (Log Out)"):
    st.session_state.auth = False
    st.session_state.rol = None
    st.rerun()

# 8. LATIDO Y REFRESCO AUTOMÁTICO
time.sleep(0.5)
st.rerun()

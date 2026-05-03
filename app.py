import streamlit as st
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis

# 1. CONFIGURACIÓN E IDENTIDAD (MENFA)
st.set_page_config(layout="wide", page_title="MENFA Drilling Sim 3.0", page_icon="assets/logo_menfa.png")

# --- 2. SISTEMA DE SEGURIDAD (Persistente) ---
CLAVE_ALUMNO = "menfa2026"
CLAVE_INSTRUCTOR = "admin_mza"

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.rol = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color:#00ffcc;'>🛡️ MENFA 3.0 | ACCESO AL RIG</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        input_pass = st.text_input("Código de Seguridad:", type="password")
        if st.button("CONECTAR CON LA CABINA", use_container_width=True):
            if input_pass == CLAVE_INSTRUCTOR:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "instructor", "Fabricio Pizzolato" #
                st.rerun()
            elif input_pass == CLAVE_ALUMNO:
                st.session_state.auth, st.session_state.rol, st.session_state.usuario = True, "alumno", "Operador en Evaluación"
                st.rerun()
            else: st.error("Código inválido.")
    st.stop()

# --- 3. CONEXIÓN A LA VERDADERA PIZARRA (Lectura del Archivo) ---
# pm.conectar_pizarra() debe leer de un JSON para que ambos vean lo mismo
piz = pm.conectar_pizarra()

# 4. FILTRO DE CONFIGURACIÓN
if not piz.get("configurado"):
    pm.selector_yacimiento_mendoza(piz)
    st.stop()

# 5. PROCESAMIENTO TÉCNICO
datos_fisica = motor.calcular_todo(piz)

# --- 6. EL MOTOR DE AVANCE Y GEONAVEGACIÓN REAL ---
if not piz.get("bop_cerrado"):
    # A. Avance de Profundidad
    rop_actual = datos_fisica.get("ROP", 0)
    if rop_actual > 0:
        factor_avance = 15 
        avance = (rop_actual / 3600) * factor_avance
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4) #
        
        # B. GEONAVEGACIÓN (Sincronización de Trayectoria)
        # Aquí es donde los parámetros CAMBIAN y se guardan
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
        piz["tvd"] = datos_fisica.get("TVD", piz.get("tvd", 0))
    
    # C. CONTROL DE POZO (Well Control)
    # Si vos como instructor activás un influjo en tu panel, el alumno lo recibe aquí
    influjo_rate = piz.get("influjo_instructor", 0) # El instructor escribe esto en la pizarra
    piz["volumen_piletas"] += (influjo_rate * 0.1)
    
    # Actualizamos el reporte de física para que el visualizador lo muestre
    datos_fisica["Influjo"] = influjo_rate 

# --- 7. GUARDAR CAMBIOS (CRÍTICO PARA LA CONEXIÓN) ---
# Sin esto, el alumno y el instructor nunca están conectados
pm.actualizar_fichero(piz) #

# --- 8. INTERFAZ Y RENDERIZADO ---
st.sidebar.title(f"👤 {st.session_state.usuario}")

# Barra de progreso basada en la profundidad compartida
meta = piz.get("tvd_target", 2500.0)
progreso = min(piz["profundidad_actual"] / meta, 1.0)
st.progress(progreso, text=f"Progreso: {piz['profundidad_actual']:.2f} m / {meta} m")

if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica) # El alumno solo mueve perillas
elif st.session_state.rol == "instructor":
    control.panel_instructor(piz) # El instructor inyecta problemas

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# 9. LATIDO (Refresco cada 0.5s para ver el avance)
time.sleep(0.5)
st.rerun()

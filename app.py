import streamlit as st
import time
import pizarra_maestra as pm
import motor_perforacion as motor
import control_operativo as control
import visual_pro as vis
import sarta_pro as sarta # Importamos el nuevo módulo
# --- 2. SISTEMA DE SEGURIDAD (Optimizado) ---
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
                st.session_state.auth = True
                st.session_state.rol = "instructor"
                st.session_state.usuario = "Fabricio Pizzolato"
                st.rerun()
            elif input_pass == CLAVE_ALUMNO:
                st.session_state.auth = True
                st.session_state.rol = "alumno"
                st.session_state.usuario = "Operador en Evaluación"
                st.rerun()
            else:
                st.error("Código inválido.")
    st.stop() # Bloquea el resto del script hasta estar autenticado

# --- 3. CONEXIÓN A LA PIZARRA (Con manejo de errores) ---
try:
    piz = pm.conectar_pizarra()
except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")
    st.stop()

# --- 4. FILTRO DE CONFIGURACIÓN (Evitar pantalla negra) ---
# Si no está configurado, mostramos el selector pero NO detenemos todo el flujo visual
if not piz.get("configurado"):
    st.warning("⚠️ El sistema requiere configuración inicial del yacimiento.")
    pm.selector_yacimiento_mendoza(piz)
    # Importante: No ponemos st.stop() aquí si queremos que el instructor vea algo
    if st.session_state.rol == "alumno":
        st.info("Esperando que el instructor configure el pozo...")
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
        piz["profundidad_actual"] = round(piz.get("profundidad_actual", 0) + avance, 4) 
        
        # B. GEONAVEGACIÓN
        piz["inclinacion"] = datos_fisica.get("nueva_inclinacion", piz.get("inclinacion", 0))
        piz["azimut"] = datos_fisica.get("nuevo_azimut", piz.get("azimut", 0))
        piz["tvd"] = datos_fisica.get("TVD", piz.get("tvd", 0))
    
    # C. CONTROL DE POZO
    influjo_rate = piz.get("influjo_instructor", 0) 
    piz["volumen_piletas"] += (influjo_rate * 0.1)
    datos_fisica["Influjo"] = influjo_rate 

# --- 7. MÓDULO DE SARTAS (API 5DP INTEGRADO) ---
# Calculamos la tensión real vs resistencia antes de renderizar
# Usamos S-135 por defecto para Vaca Muerta como sugeriste
resistencia = sarta.modulo_sartas_api(piz) 
datos_fisica["hook_load"] = resistencia.get("hook_load", 0)
datos_fisica["max_yield"] = resistencia.get("max_yield", 0)

# --- 8. GUARDAR CAMBIOS ---
pm.actualizar_fichero(piz) 

# --- 9. INTERFAZ Y RENDERIZADO ---
st.sidebar.title(f"👤 {st.session_state.usuario}")

# Barra de progreso
meta = piz.get("tvd_target", 2500.0)
progreso = min(piz["profundidad_actual"] / meta, 1.0)
st.progress(progreso, text=f"Progreso: {piz['profundidad_actual']:.2f} m / {meta} m")

if st.session_state.rol == "alumno":
    vis.renderizar_cabina_perforador(piz, datos_fisica)
elif st.session_state.rol == "instructor":
    # El instructor ve el panel de control y puede configurar la sarta
    tab1, tab2 = st.tabs(["🎮 Control de Pozo", "🔩 Configuración de Sarta"])
    with tab1:
        control.panel_instructor(piz)
    with tab2:
        sarta.configuracion_ui() # La parte visual de los selectbox que pasaste

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# 10. ALERTAS DE SEGURIDAD OPERATIVA
if datos_fisica["hook_load"] > (datos_fisica["max_yield"] * 0.9):
    st.warning("⚠️ TENSIÓN EN SARTA PRÓXIMA AL LÍMITE DE FLUENCIA")

# 11. LATIDO
time.sleep(0.5)
st.rerun()

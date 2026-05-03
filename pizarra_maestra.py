import streamlit as st

def conectar_pizarra():
    """
    Inicializa y conecta con el estado global de la simulación.
    Se elimina @st.cache_resource para permitir reactividad total en tiempo real.
    """
    if "pizarra" not in st.session_state:
        st.session_state.pizarra = {
            # Estado del Sistema
            "configurado": False,
            "yacimiento": None,
            "profundidad_actual": 0.0,
            "tvd_target": 0.0,
            "gradiente": 0.44,
            
            # Variables Mecánicas (Entradas del Alumno)
            "caudal": 0.0,
            "rpm": 0.0,
            "wob": 0.0,
            
            # Variables de Salida (Cálculos)
            "spp": 0.0,
            "torque": 0.0,
            "rop": 0.0,
            
            # Comunicación y Seguridad
            "mensaje_instructor": None,
            "ultima_accion": None,
            "bop_cerrado": False,
            "alarma": False,
            "densidad_lodo": 9.5
        }
    
    if "rol" not in st.session_state:
        st.session_state.rol = None # Se define en el login de app.py o aquí
        
    return st.session_state.pizarra

def selector_yacimiento_mendoza(piz):
    """
    Interfaz de configuración inicial para el Instructor o Alumno.
    Establece las bases físicas de la perforación.
    """
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #00ffcc; color: black; font-weight: bold; }
        .stSelectbox label { color: #00ffcc; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📍 IPCL MENFA - Configuración de Pozo")
    st.subheader("Selección de Yacimiento (Cuenca Cuyana / Neuquina)")
    
    # Datos técnicos reales de Mendoza para el simulador
    yacimientos = {
        "Barrancas (Mendoza)": {
            "tvd": 2450, 
            "grad": 0.44, 
            "lit": "Areniscas Potrerillos",
            "desc": "Yacimiento convencional, presiones normales."
        },
        "Cruz de Piedra (Mendoza)": {
            "tvd": 3100, 
            "grad": 0.45, 
            "lit": "Tobas / Formación Cacheuta",
            "desc": "Desafío en estabilidad de paredes."
        },
        "Malargüe (Vaca Muerta)": {
            "tvd": 2900, 
            "grad": 0.65, 
            "lit": "Shale Orgánico",
            "desc": "No convencional, alta presión (Overpressure)."
        }
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        seleccion = st.selectbox("Área de Operación:", list(yacimientos.keys()))
        data = yacimientos[seleccion]
        st.info(f"**Litología:** {data['lit']}\n\n**Descripción:** {data['desc']}")
    
    with col2:
        st.markdown(f"""
            <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border: 1px solid #00ffcc;">
                <h4 style="margin-top:0;">Parámetros de Diseño</h4>
                <p><b>Profundidad Objetivo:</b> {data['tvd']} m</p>
                <p><b>Gradiente de Formación:</b> {data['grad']} psi/ft</p>
                <p><b>Presión de Fondo Est.:</b> {int(data['tvd'] * 3.28 * data['grad'])} PSI</p>
            </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identificación Profesional:", placeholder="Ej: Fabricio Pizzolato")
    
    st.divider()
    
    if st.button("INICIALIZAR SISTEMAS Y ENTRAR A CABINA"):
        if user:
            # Seteo de variables en la pizarra
            piz["yacimiento"] = seleccion
            piz["tvd_target"] = data["tvd"]
            piz["gradiente"] = data["grad"]
            piz["configurado"] = True
            st.session_state["user"] = user
            
            # Lógica de Rol Automática
            if user.lower() in ["fabricio", "instructor", "admin", "pizzolato"]:
                st.session_state.rol = "instructor"
            else:
                st.session_state.rol = "alumno"
            
            st.success("Configuración cargada. Accediendo...")
            st.rerun()
        else:
            st.error("Por favor, ingrese un nombre para el registro de la sesión.")

def resetear_simulacion(piz):
    """Limpia los datos para comenzar un nuevo pozo"""
    piz["configurado"] = False
    piz["profundidad_actual"] = 0.0
    piz["bop_cerrado"] = False
    piz["mensaje_instructor"] = None
    st.rerun()

import streamlit as st

@st.cache_resource
def conectar_pizarra():
    if "pizarra" not in st.session_state:
        st.session_state.pizarra = {
            "configurado": False,
            "yacimiento": None,
            "profundidad_actual": 0.0,
            "tvd_target": 0.0,
            "gradiente": 0.44,
            "caudal": 0.0,
            "rpm": 0.0,
            "wob": 0.0,
            "spp": 0.0,
            "bop_cerrado": False,
            "alarma": False
        }
    if "rol" not in st.session_state:
        st.session_state.rol = "perforador" # Por defecto
    return st.session_state.pizarra

def selector_yacimiento_mendoza(piz):
    st.title("📍 Selección de Yacimiento - Mendoza")
    
    yacimientos = {
        "Barrancas": {"tvd": 2450, "grad": 0.44, "lit": "Areniscas"},
        "Cruz de Piedra": {"tvd": 3100, "grad": 0.45, "lit": "Tobas"},
        "Malargüe (Vaca Muerta)": {"tvd": 2900, "grad": 0.65, "lit": "Shale"}
    }
    
    seleccion = st.selectbox("Elegir área:", list(yacimientos.keys()))
    data = yacimientos[seleccion]
    
    st.info(f"Objetivo: {data['lit']} a {data['tvd']} metros.")
    
    # Login simple para la clase
    user = st.text_input("Nombre del Alumno / Instructor:")
    
    if st.button("CONFIGURAR Y ENTRAR A CABINA"):
        piz["yacimiento"] = seleccion
        piz["tvd_target"] = data["tvd"]
        piz["gradiente"] = data["grad"]
        piz["configurado"] = True
        
        if user.lower() in ["fabricio", "instructor", "admin"]:
            st.session_state.rol = "instructor"
        else:
            st.session_state.rol = "perforador"
            
        st.rerun()

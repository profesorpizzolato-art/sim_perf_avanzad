import streamlit as st

def selector_yacimiento_mendoza():
    st.title("📍 PLANIFICACIÓN DE POZO - CUENCA CUYANA / NEUQUINA")
    
    # Base de Datos Técnica de Mendoza
    yacimientos = {
        "Barrancas (Cuenca Cuyana)": {
            "objetivo": "Formación Barrancas / Rio Blanco",
            "tvd_target": 2450,
            "litologia": "Areniscas y Arcilitas",
            "gradiente": 0.44, # psi/ft (Normal)
            "temp_fondo": 85 # °C
        },
        "Cruz de Piedra (Maipú)": {
            "objetivo": "Formación Potrerillos",
            "tvd_target": 3100,
            "litologia": "Tobas y Areniscas",
            "gradiente": 0.45,
            "temp_fondo": 98
        },
        "Malargüe (Vaca Muerta - Norte)": {
            "objetivo": "Formación Vaca Muerta (Unconv.)",
            "tvd_target": 2900,
            "litologia": "Shale Orgánico / Carbonatos",
            "gradiente": 0.65, # Sobrepresión típica
            "temp_fondo": 110
        },
        "El Vizcacheral": {
            "objetivo": "Formación Víctor",
            "tvd_target": 2100,
            "litologia": "Conglomerados",
            "gradiente": 0.43,
            "temp_fondo": 75
        }
    }

    st.subheader("Seleccionar Área de Operación")
    area = st.selectbox("Yacimiento / Área:", list(yacimientos.keys()))
    
    data = yacimientos[area]
    
    # Mostrar Ficha Técnica del Pozo
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Objetivo Geológico", data["objetivo"])
        st.metric("Profundidad (TVD)", f"{data['tvd_target']} m")
    with c2:
        st.metric("Litología Dominante", data["litologia"])
        st.metric("Gradiente de Presión", f"{data['gradiente']} psi/ft")
    with c3:
        st.metric("Temperatura de Fondo", f"{data['temp_fondo']} °C")
        # Alerta de temperatura para la electrónica del LWD
        if data["temp_fondo"] > 105:
            st.warning("⚠️ ALTA TEMPERATURA: Requiere herramientas MWD/LWD Clase H.")

    if st.button(f"CONFIGURAR PERFORACIÓN EN {area.upper()}"):
        st.session_state.depth_target = data["tvd_target"]
        st.session_state.gradiente_local = data["gradiente"]
        st.success(f"Configuración cargada. Iniciando movilización de equipo a {area}...")

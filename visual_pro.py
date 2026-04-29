import streamlit as st
import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    """Función universal para crear los relojes del simulador"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"<b>{titulo}</b><br><span style='font-size:0.8em;color:gray'>{unidad}</span>", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color_bar},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0,255,0,0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255,0,0,0.2)'}
            ],
        }
    ))
    fig.update_layout(
        height=280, 
        margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"}
    )
    return fig

def renderizar_cabina_perforador(piz, datos):
    """Esta es la pantalla que ve el alumno"""
    # Usamos .get con un valor por defecto para evitar errores si la llave no existe
    nombre_yacimiento = piz.get('yacimiento', 'Sin seleccionar')
    st.header(f"🎮 Consola de Perforación - {nombre_yacimiento}")
    
    # --- FILA 1: CONTROLES DE OPERACIÓN ---
    with st.sidebar:
        try:
            st.image("logo_menfa.png", width=200)
        except:
            st.warning("Logo no encontrado")
            
        st.subheader("🕹️ Mandos del Cuadro")
        
        # IMPORTANTE: Forzamos int() y usamos 'key' para evitar el StreamlitAPIException
        val_rpm = int(piz.get("rpm", 0))
        val_wob = int(piz.get("wob", 0))
        val_caudal = int(piz.get("caudal", 0))

        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, val_rpm, key="s_rpm")
        piz["wob"] = st.slider("Peso en el Trépano (klbs)", 0, 60, val_wob, key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, val_caudal, key="s_caudal")
        
        if st.button("🚨 PARADA DE EMERGENCIA", key="btn_emergencia"):
            piz["rpm"] = 0
            piz["caudal"] = 0
            st.rerun()

    # --- FILA 2: RELOJES (MANÓMETROS) ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.plotly_chart(crear_manometro(datos.get("SPP", 0), "Presión de Bomba", "PSI", 5000, "#00ffcc"), use_container_width=True)
    with c2:
        st.plotly_chart(crear_manometro(datos.get("ROP", 0), "Penetración", "m/h", 80, "#ffcc00"), use_container_width=True)
    with c3:
        st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "Hook Load", "klbs", 400, "#ff3300"), use_container_width=True)

    # --- FILA 3: DATOS TÉCNICOS ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Profundidad Actual", f"{piz.get('profundidad_actual', 0)} m")
        st.metric("Densidad de Lodo", f"{piz.get('densidad_lodo', 9.5)} ppg")
    with col_b:
        st.metric("ECD (Dens. Equivalente)", f"{datos.get('ECD', 0)} ppg")
        st.metric("Presión Hidrostática", f"{datos.get('PH', 0)} PSI")

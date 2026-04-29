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
    st.header(f"🎮 Consola de Perforación - {piz['yacimiento']}")
    
    # --- FILA 1: CONTROLES DE OPERACIÓN ---
    with st.sidebar:
        st.image("logo_menfa.png", width=200)
        st.subheader("🕹️ Mandos del Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, piz.get("rpm", 0))
        piz["wob"] = st.slider("Peso en el Trépano (klbs)", 0, 60, piz.get("wob", 0))
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, piz.get("caudal", 0))
        
        if st.button("🚨 PARADA DE EMERGENCIA"):
            piz["rpm"] = 0
            piz["caudal"] = 0
            st.rerun()

    # --- FILA 2: RELOJES (MANÓMETROS) ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.plotly_chart(crear_manometro(datos["SPP"], "Presión de Bomba", "PSI", 5000, "#00ffcc"), use_container_width=True)
    with c2:
        st.plotly_chart(crear_manometro(datos["ROP"], "Penetración", "m/h", 80, "#ffcc00"), use_container_width=True)
    with c3:
        st.plotly_chart(crear_manometro(datos["Carga_Gancho"], "Hook Load", "klbs", 400, "#ff3300"), use_container_width=True)

    # --- FILA 3: DATOS TÉCNICOS ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Profundidad Actual", f"{piz['profundidad_actual']} m")
        st.metric("Densidad de Lodo", f"{piz.get('densidad_lodo', 9.5)} ppg")
    with col_b:
        st.metric("ECD (Dens. Equivalente)", f"{datos['ECD']} ppg")
        st.metric("Presión Hidrostática", f"{datos['PH']} PSI")

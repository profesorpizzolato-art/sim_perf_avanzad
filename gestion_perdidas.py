import streamlit as st
import time
import random
import streamlit as st

def render_tanques(pizarra):
    st.subheader("Estado de Piletas")
    
    # Creamos 3 columnas para los 3 tanques
    col1, col2, col3 = st.columns(3)
    
    nivel = pizarra.get("piletas_nivel", 80.0) # Valor por defecto 80%
    
    with col1:
        st.metric("Tanque 1 (Activo)", f"{nivel:.1f} %")
        st.progress(nivel / 100)
        
    with col2:
        st.metric("Tanque 2 (Reserva)", "75.0 %")
        st.progress(0.75)
        
    with col3:
        st.metric("Tanque 3 (Píldora)", "40.0 %")
        st.progress(0.40)

    # Lógica visual si hay pérdida o ganancia
    if pizarra.get("evento_activo") == "KICK":
        st.warning("⚠️ ¡Nivel de piletas subiendo! Posible surgencia.")
    elif pizarra.get("evento_activo") == "PERDIDA":
        st.error("📉 ¡Nivel de piletas bajando! Pérdida en formación.")
def modulo_perdida_circulacion():
    st.title("⚠️ ALERTA: PÉRDIDA DE CIRCULACIÓN (LCM)")
    
    if "nivel_tanques" not in st.session_state:
        st.session_state.nivel_tanques = 1000 # Barriles (bbl)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Monitoreo de Volumen de Lodo")
        # Simulación de pérdida activa
        tasa_perdida = st.session_state.get('tasa_perdida', 0)
        st.session_state.nivel_tanques -= tasa_perdida
        
        fig_tanque = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = st.session_state.nivel_tanques,
            title = {'text': "Nivel Total en Tanques (bbl)"},
            gauge = {
                'axis': {'range': [0, 1000]},
                'bar': {'color': "red" if st.session_state.nivel_tanques < 400 else "green"},
                'steps': [
                    {'range': [0, 300], 'color': "darkred"},
                    {'range': [300, 600], 'color': "orange"}
                ]
            }
        ))
        st.plotly_chart(fig_tanque, use_container_width=True)

    with col2:
        st.subheader("Acciones de Mitigación")
        lcm_type = st.selectbox("Seleccionar Material Obturante (LCM):", 
                                ["Cáscara de Nuez (Fina)", "Fibras Celulósicas", "Carbonato de Calcio", "Píldora de Cemento"])
        
        if st.button("BOMBEAR PÍLDORA OBTURANTE"):
            with st.status("Bombeando bache de LCM..."):
                time.sleep(3)
                st.session_state.tasa_perdida = 0
                st.success(f"¡ÉXITO! Filtración sellada con {lcm_type}.")
                st.balloons()

    if st.session_state.nivel_tanques < 200:
        st.error("🚨 ¡POZO VACÍO! Riesgo inminente de pérdida de control. Activar plan de contingencia.")

import streamlit as st
import time
import random
import plotly.graph_objects as go

def render_tanques(pizarra):
    st.subheader("Estado de Piletas")
    
    # 1. Aseguramos el nivel del Tanque Activo (Normalización 0.0 a 1.0)
    # Si 'piletas_nivel' viene como barriles (ej. 450), lo dividimos por la capacidad
    capacidad_max = 500.0
    nivel_real = pizarra.get("piletas_nivel", 400.0)
    
    # Normalizamos para st.progress (0.0 a 1.0)
    progreso_tanque1 = max(0.0, min(nivel_real / capacidad_max, 1.0))
    porcentaje_display = progreso_tanque1 * 100

    # Creamos 3 columnas para los 3 tanques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tanque 1 (Activo)", f"{porcentaje_display:.1f} %")
        st.progress(progreso_tanque1)
        
    with col2:
        st.metric("Tanque 2 (Reserva)", "75.0 %")
        st.progress(0.75)
        
    with col3:
        st.metric("Tanque 3 (Píldora)", "40.0 %")
        st.progress(0.40)

    # Lógica visual de eventos
    evento = pizarra.get("evento_activo")
    if evento == "KICK" or evento == "PATADA":
        st.warning("⚠️ ¡Nivel de piletas subiendo! Posible surgencia (Kick).")
    elif evento == "PERDIDA":
        st.error("📉 ¡Nivel de piletas bajando! Pérdida de circulación detectada.")

def modulo_perdida_circulacion(pizarra):
    st.title("⚠️ ALERTA: PÉRDIDA DE CIRCULACIÓN (LCM)")
    
    # Inicialización de volumen en barriles
    if "nivel_tanques" not in st.session_state:
        st.session_state.nivel_tanques = 1000.0 
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Monitoreo de Volumen de Lodo")
        
        # Si hay pérdida activa, restamos del total
        if pizarra.get("evento_activo") == "PERDIDA":
            st.session_state.nivel_tanques -= 2.5 # Tasa de pérdida
            
        fig_tanque = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = st.session_state.nivel_tanques,
            title = {'text': "Nivel Total (bbl)"},
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
        st.subheader("Mitigación")
        lcm_type = st.selectbox("Seleccionar Material Obturante (LCM):", 
                                ["Cáscara de Nuez", "Fibras Celulósicas", "Carbonato de Calcio", "Píldora de Cemento"])
        
        if st.button("BOMBEAR PÍLDORA"):
            with st.status("Bombeando bache de LCM..."):
                time.sleep(2)
                st.session_state.nivel_tanques += 100 # Recuperamos algo de nivel
                pizarra["evento_activo"] = None # Frenamos la pérdida
                st.success(f"¡ÉXITO! Filtración sellada con {lcm_type}.")
                st.balloons()
                st.rerun()

    if st.session_state.nivel_tanques < 200:
        st.error("🚨 ¡POZO VACÍO! Riesgo de pérdida de control.")

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
    """Dibuja el reloj indicador de parámetros"""
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
    # 0. Mensajes y Alertas del Instructor
    if piz.get("mensaje_profesor"):
        st.chat_message("assistant").write(f"**INSTRUCTOR:** {piz['mensaje_profesor']}")

    if piz.get("alarma"):
        st.error(f"🚨 ALERTA: {piz.get('mensaje_evento', 'Surgencia en curso')}")

    st.header(f"🎮 Consola de Perforación - {piz.get('yacimiento', 'Mendoza')}")
    
    # --- Sidebar con controles ---
    with st.sidebar:
        st.subheader("🕹️ Mandos del Cuadro")
        piz["rpm"] = st.slider("Rotación (RPM)", 0, 180, int(piz.get("rpm", 0)), key="s_rpm")
        piz["wob"] = st.slider("Peso (klbs)", 0, 60, int(piz.get("wob", 0)), key="s_wob")
        piz["caudal"] = st.slider("Bombas (GPM)", 0, 1200, int(piz.get("caudal", 0)), key="s_caudal")
        
        st.divider()
        st.metric("Profundidad TVD", f"{piz.get('profundidad_actual', 0)} m")

    # --- Estructura de Pestañas ---
    tab_principal, tab_geo, tab_tanques, tab_seguridad = st.tabs([
        "📊 Panel Principal", "🌍 Geonavegación", "🛢️ Sistema de Lodos", "🛡️ BOP & Seguridad"
    ])

    with tab_principal:
        c1, c2, c3 = st.columns(3)
        # Aquí es donde fallaba: ahora 'crear_manometro' existe arriba
        with c1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "Presión", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with c2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "Penetración", "m/h", 80, "#ffcc00"), use_container_width=True)
        with c3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "Hook Load", "klbs", 400, "#ff3300"), use_container_width=True)
        
        st.subheader("⚙️ Parámetros de Torsión")
        torque_val = datos.get("Torque", 0)
        st.progress(min(torque_val/100, 1.0), text=f"Torque: {torque_val} ft-lbs")

    with tab_geo:
        st.subheader("📍 Geonavegación y Litología")
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            st.write(f"**Formación:** {piz.get('litologia', 'Cuyana')}")
            st.write(f"**Gradiente:** {piz.get('gradiente', 0.44)} psi/ft")
        with col_g2:
            gr_data = pd.DataFrame({
                'Gamma Ray': np.random.randint(40, 140, 20),
                'Prof': np.linspace(piz.get('profundidad_actual', 0)-20, piz.get('profundidad_actual', 0), 20)
            })
            st.line_chart(gr_data, x="Prof", y="Gamma Ray", color="#ffaa00")

    with tab_tanques:
        st.subheader("📈 Monitoreo de Piletas")
        t1, t2 = st.columns(2)
        gain_loss = datos.get("Influjo", 0)
        t1.metric("Volumen Total", "1250 bbl", delta=f"{gain_loss} bbl/min", delta_color="inverse")
        t2.metric("Densidad Salida", f"{piz.get('densidad_lodo', 9.5)} ppg")

    with tab_seguridad:
        st.subheader("🛡️ Panel de BOP")
        if piz.get("bop_cerrado"):
            st.error("⚠️ POZO CERRADO (SHUT-IN)")
            if st.button("ABRIR RAMS", key="open_bop"):
                piz["bop_cerrado"] = False
                st.rerun()
        else:
            st.success("✅ FLUJO ABIERTO")
            if st.button("CERRAR ANULAR", key="close_bop"):
                piz["bop_cerrado"] = True
                st.rerun()

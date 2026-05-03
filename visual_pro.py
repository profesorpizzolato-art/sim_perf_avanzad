import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def crear_manometro(valor, titulo, unidad, max_val, color_bar):
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
    fig.update_layout(height=260, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

def renderizar_cabina_perforador(piz, datos):
    # --- 1. PANEL DEL INSTRUCTOR (SABOTAJE TÉCNICO) ---
    with st.sidebar.expander("👨‍🏫 PANEL DE CONTROL - INSTRUCTOR", expanded=False):
        st.subheader("Eventos Críticos")
        piz["evento_activo"] = st.selectbox("Simular Crisis:", [None, "KICK", "LOST_CIRC"], index=0)
        
        st.subheader("Geología")
        piz["litologia"] = st.selectbox("Formación:", ["Areniscas", "Arcillas", "Vaca Muerta (Shale)"])
        
        st.subheader("Estado del Trépano")
        piz["factor_desgaste"] = st.slider("Desgaste (1=Nuevo, 3=Gastado)", 1.0, 3.0, 1.0)
        
        if st.button("RESET TOTAL DEL POZO"):
            piz["densidad_lodo"] = 9.5
            piz["evento_activo"] = None
            st.rerun()

    # --- 2. MANDOS DEL ALUMNO (SIDEBAR) ---
    st.sidebar.header("🕹️ CONSOLA DEL PERFORADOR")
    
    # Parámetros de Perforación
    piz["wob"] = st.sidebar.slider("Peso sobre Trépano (WOB klbs)", 0, 60, value=int(piz.get("wob", 0)))
    piz["rpm"] = st.sidebar.slider("Rotación (RPM)", 0, 180, value=int(piz.get("rpm", 0)))
    piz["caudal"] = st.sidebar.slider("Caudal Bombas (GPM)", 0, 1200, value=int(piz.get("caudal", 0)))
    
    st.sidebar.divider()
    
    # Control de Lodos (Clave para matar el pozo)
    st.sidebar.subheader("🛢️ GESTIÓN DE FLUIDOS")
    piz["densidad_lodo"] = st.sidebar.number_input("Densidad Actual (ppg)", 8.0, 18.0, value=float(piz.get("densidad_lodo", 9.5)), step=0.1)
    
    # Navegación
    st.sidebar.subheader("🧭 NAVEGACIÓN")
    piz["toolface"] = st.sidebar.number_input("Toolface Orient. (°)", 0, 360, value=int(piz.get("toolface", 0)))

    # --- 3. ESTILO Y CABECERA ---
    st.markdown("""<style>.console-box { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 5px solid #00ffcc; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

    col_logo, col_tit = st.columns([1, 4])
    with col_logo:
        if os.path.exists("assets/logo_menfa.png"): st.image("assets/logo_menfa.png", width=120)
        else: st.markdown("<h2 style='color:#00ffcc;'>MENFA</h2>", unsafe_allow_html=True)
    with col_tit:
        st.title("🛡️ MENFA 3.0 | CONTROL DE POZO")
        st.caption(f"YACIMIENTO: {piz.get('yacimiento', 'MENDOZA')} | FORMACIÓN: {piz.get('litologia', 'Vaca Muerta')}")

    # --- 4. ALERTAS DE BROTE (KICK) ---
    if datos.get("Influjo", 0) > 0:
        st.error(f"🚨 ALERTA DE BROTE: Ganancia de {datos['Influjo']} bbl/min detectada.")
    elif datos.get("Influjo", 0) < 0:
        st.warning(f"📉 PÉRDIDA DE CIRCULACIÓN: {abs(datos['Influjo'])} bbl/min.")

    # --- 5. PANELES TÉCNICOS ---
    t_op, t_well_control, t_geo = st.tabs(["📊 OPERACIÓN", "🛡️ CONTROL DE POZO", "🧭 TRAYECTORIA"])

    with t_op:
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(crear_manometro(datos.get("SPP", 0), "PRESIÓN (SPP)", "PSI", 5000, "#00ffcc"), use_container_width=True)
        with c2: st.plotly_chart(crear_manometro(datos.get("ROP", 0), "AVANCE (ROP)", "m/h", 80, "#ffcc00"), use_container_width=True)
        with c3: st.plotly_chart(crear_manometro(datos.get("Carga_Gancho", 150), "PESO (HOOK)", "klbs", 400, "#ff3300"), use_container_width=True)
        
        st.divider()
        cg, ci = st.columns([2, 1])
        with cg:
            st.subheader("Torque Dinámico")
            df_t = pd.DataFrame({'Torque': np.random.normal(datos.get("Torque", 15), 1, 20), 'Prof': np.linspace(piz.get("profundidad_actual", 1000)-20, piz.get("profundidad_actual", 1000), 20)})
            fig_t = go.Figure(go.Scatter(x=df_t['Torque'], y=df_t['Prof'], line=dict(color='#00ffcc')))
            fig_t.update_layout(yaxis=dict(autorange="reversed"), template="plotly_dark", height=300)
            st.plotly_chart(fig_t, use_container_width=True)
        with ci:
            st.markdown(f"""<div class="console-box">
                <p><b>ECD:</b> {datos.get('ECD')} ppg</p>
                <p><b>P. Hidrostática:</b> {int(datos.get('PH'))} PSI</p>
                <p><b>WOB Real:</b> {piz.get('wob')} klbs</p>
            </div>""", unsafe_allow_html=True)

    with t_well_control:
        st.subheader("Consola de Seguridad (BOP)")
        b1, b2 = st.columns(2)
        with b1:
            if piz.get("bop_cerrado"):
                st.error("BOP CERRADO")
                if st.button("ABRIR POZO"): piz["bop_cerrado"] = False; st.rerun()
            else:
                st.success("BOP ABIERTO")
                if st.button("CERRAR POZO (SHUT-IN)"): piz["bop_cerrado"] = True; st.rerun()
        
        with b2:
            st.metric("Presión en Casing (SIDP/SICP)", f"{datos.get('Presion_Casing')} PSI")
            st.metric("Presión de Formación", f"{datos.get('P_Formacion')} PSI")

    with t_geo:
        # Lógica de gráfico 3D similar a la anterior...
        st.subheader("Visualización de Trayectoria")
        st.info("Módulo de Geonavegación Activo")

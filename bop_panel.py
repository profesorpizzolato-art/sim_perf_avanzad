import streamlit as st
import pandas as pd

def render_bop_ui(pizarra):
    st.header("🛡️ Control Avanzado de Pozos")
    
    es_cerrado = pizarra.get("bop_cerrado", False)
    
    # --- BLOQUE 1: EL CHOKE MANIFOLD (Mando Físico) ---
    st.subheader("🕹️ Control de Estrangulación (Choke)")
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        # El Choke se mide en 1/64 de pulgada. 0 es cerrado, 64 es abierto total.
        choke_pos = st.slider("Apertura del Choke (1/64\")", 0, 64, pizarra.get("choke_pos", 0))
        pizarra["choke_pos"] = choke_pos
    
    with col_c2:
        # Efecto visual de presión según el choke
        presion_choke = (64 - choke_pos) * 15 # Simulación simple de contrapresión
        st.metric("Presión en Choke", f"{presion_choke} psi", delta="-5 psi" if choke_pos > 0 else "0")

    st.divider()

    # --- BLOQUE 2: ESTADO Y MANDOS ---
    color_bg = "#FF4B4B" if es_cerrado else "#28a745"
    st.markdown(f"<div style='background-color:{color_bg}; padding:10px; border-radius:10px; text-align:center; color:white;'><h3>POZO: {'CERRADO' if es_cerrado else 'ABIERTO'}</h3></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🔴 CERRAR POZO", use_container_width=True): pizarra["bop_cerrado"] = True; st.rerun()
    with c3: 
        if st.button("🟢 ABRIR POZO", use_container_width=True): pizarra["bop_cerrado"] = False; st.rerun()

    # --- BLOQUE 3: KILL SHEET (Ingeniería) ---
    if es_cerrado:
        st.divider()
        st.subheader("📝 Hoja de Ahogo (Kill Sheet)")
        
        with st.expander("Abrir Cálculos de Ingeniería", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                sidpp = st.number_input("SIDPP (psi)", 0, 2500, 500)
                sicp = st.number_input("SICP (psi)", 0, 2500, 750)
                tvd = pizarra["profundidad_actual"] * 3.28
            
            with col2:
                mw_actual = pizarra["densidad_lodo"]
                kmw = mw_actual + (sidpp / (0.052 * tvd))
                st.metric("KMW (Lodo de Ahogo)", f"{round(kmw, 2)} ppg")
                
            # Generar datos para el reporte
            datos_kill = {
                "Parámetro": ["Densidad Actual", "SIDPP", "SICP", "Profundidad TVD", "Lodo de Ahogo (KMW)"],
                "Valor": [f"{mw_actual} ppg", f"{sidpp} psi", f"{sicp} psi", f"{round(tvd)} ft", f"{round(kmw, 2)} ppg"]
            }
            df_kill = pd.DataFrame(datos_kill)
            st.table(df_kill)

            # Botón de descarga de la Kill Sheet (CSV para este ejemplo rápido)
            csv = df_kill.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar Kill Sheet (Data)",
                csv,
                "kill_sheet_menfa.csv",
                "text/csv",
                key='download-csv'
            )

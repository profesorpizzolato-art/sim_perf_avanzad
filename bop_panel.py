import streamlit as st
from datetime import datetime

def render_bop_ui(pizarra):
    st.header("🛡️ Control Avanzado de Pozos")
    
    # --- SEGURIDAD: Inicialización de variables en el session_state ---
    if "log_eventos" not in st.session_state:
        st.session_state.log_eventos = []
    if "strokes_totales" not in st.session_state:
        st.session_state.strokes_totales = 0  
    
    # --- CONTADOR DE STROKES (EMBOLADAS) ---
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        strokes = int(st.session_state.get('strokes_totales', 0))
        st.metric("Total Strokes (Emboladas)", strokes)
    with c_st2:
        st.write("")  # Espaciador para alineación vertical
        if st.button("Reset Counter", key="btn_reset_strokes_clean"):
            st.session_state.strokes_totales = 0  
            st.rerun()

    st.divider()
    
    es_cerrado = pizarra.get("bop_cerrado", False)
    
    # --- BLOQUE 1: COLECTOR O CHOKE ---
    st.subheader("🕹️ Control de Estrangulación (Choke)")
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        choke_pos = st.slider(
            'Apertura del Choke (1/64")', 
            0, 64, 
            int(pizarra.get("choke_pos", 0)), 
            key="bop_clean_choke_slider"
        )
        
        if abs(choke_pos - pizarra.get("choke_pos", 0)) > 5:
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚙️ Choke ajustado a {choke_pos}/64"
            )
        pizarra["choke_pos"] = choke_pos
    
    with col_c2:
        presion_choke = (64 - choke_pos) * 15 
        st.metric("Presión en Choke", f"{presion_choke} psi")

    st.divider()

    # --- BLOQUE 2: ESTADO Y MANDOS DEL BOP ---
    color_bg = "#FF4B4B" if es_cerrado else "#28a745"
    st.markdown(
        f"<div style='background-color:{color_bg}; padding:10px; border-radius:10px; text-align:center; color:white;'>"
        f"<h3>POZO: {'CERRADO' if es_cerrado else 'ABIERTO'}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.write("") 

    c1, _, c3 = st.columns([1.2, 0.6, 1.2])
    with c1: 
        if st.button("🔴 CERRAR POZO", use_container_width=True, key="btn_bop_close_clean"): 
            pizarra["bop_cerrado"] = True
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 ACCIÓN: Pozo Cerrado por el operador."
            )
            st.rerun()
            
    with c3:
        if st.button("🟢 ABRIR POZO", use_container_width=True, key="btn_bop_open_clean"):
            pizarra["bop_cerrado"] = False
            st.session_state.log_eventos.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ ACCIÓN: Pozo Abierto."
            )
            st.rerun()

    # --- BLOQUE 3: HOJA DE AHOGO (KILL SHEET) ---
    if es_cerrado:
        st.divider()
        st.subheader("📝 Hoja de Ahogo (Kill Sheet)")
        with st.expander("Abrir Cálculos de Ingeniería", expanded=True):
            metodo = pizarra.get('metodo_sugerido', 'Perforador')
            st.info(f"Método recomendado para esta profundidad: {metodo}")

    if st.session_state.log_eventos:
        st.divider()
        st.subheader("📑 Últimos Eventos")
        for ev in reversed(st.session_state.log_eventos[-3:]):
            st.caption(ev)

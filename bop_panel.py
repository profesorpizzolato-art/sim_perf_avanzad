import streamlit as st
import pandas as pd
import datetime

def render_bop_ui(pizarra):
    st.header("🛡️ Control Avanzado de Pozos")
    
    # --- MEJORA: CONTADOR DE STROKES ---
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        st.metric("Total Strokes (Emboladas)", int(st.session_state.get('strokes_totales', 0)))
    with c_st2:
        if st.button("Reset Counter"):
            st.session_state.strokes_totales = 0
            st.rerun()

    st.divider()
    
    es_cerrado = pizarra.get("bop_cerrado", False)
    
    # --- BLOQUE 1: EL CHOKE MANIFOLD ---
    st.subheader("🕹️ Control de Estrangulación (Choke)")
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        choke_pos = st.slider("Apertura del Choke (1/64\")", 0, 64, pizarra.get("choke_pos", 0))
        # Registramos en bitácora si hay cambios bruscos
        if abs(choke_pos - pizarra.get("choke_pos", 0)) > 5:
            st.session_state.log_eventos.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⚙️ Choke ajustado a {choke_pos}/64")
        pizarra["choke_pos"] = choke_pos
    
    with col_c2:
        presion_choke = (64 - choke_pos) * 15 
        st.metric("Presión en Choke", f"{presion_choke} psi")

    st.divider()

    # --- BLOQUE 2: ESTADO Y MANDOS (Conectados a Bitácora) ---
    color_bg = "#FF4B4B" if es_cerrado else "#28a745"
    st.markdown(f"<div style='background-color:{color_bg}; padding:10px; border-radius:10px; text-align:center; color:white;'><h3>POZO: {'CERRADO' if es_cerrado else 'ABIERTO'}</h3></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🔴 CERRAR POZO", use_container_width=True): 
            pizarra["bop_cerrado"] = True
            st.session_state.log_eventos.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🛑 ACCIÓN: Pozo Cerrado por el operador.")
            st.rerun()
    with c3: 
        if st.button("🟢 ABRIR POZO", use_container_width=True): 
            pizarra["bop_cerrado"] = False
            st.session_state.log_eventos.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ ACCIÓN: Pozo Abierto.")
            st.rerun()

    # --- BLOQUE 3: KILL SHEET (Tu lógica original mejorada) ---
    if es_cerrado:
        st.divider()
        st.subheader("📝 Hoja de Ahogo (Kill Sheet)")
        with st.expander("Abrir Cálculos de Ingeniería", expanded=True):
            # ... (Aquí va el mismo código de inputs y tabla que me pasaste) ...
            st.info(f"Método recomendado para esta profundidad: {pizarra.get('metodo_sugerido', 'Perforador')}")

        # BITÁCORA VISUAL RÁPIDA
        st.divider()
        st.subheader("📑 Últimos Eventos")
        for ev in reversed(st.session_state.log_eventos[-3:]):
            st.caption(ev)

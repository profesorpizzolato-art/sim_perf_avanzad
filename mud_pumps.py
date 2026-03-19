import streamlit as st

def mud_pumps_panel():
    st.title("🚜 SISTEMA DE BOMBAS DE LODO")
    
    spm1 = st.number_input("Bomba 1 (SPM)", 0, 120, 60)
    spm2 = st.number_input("Bomba 2 (SPM)", 0, 120, 0)
    
    total_gpm = (spm1 + spm2) * 5.2 # Galones por embolada
    presion_spp = total_gpm * 4.5 # Simulación de fricción
    
    st.metric("Caudal Total (GPM)", f"{total_gpm}")
    st.metric("Presión SPP (psi)", f"{int(presion_spp)}")

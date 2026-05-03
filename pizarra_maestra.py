import streamlit as st
import json
import os

# Definimos la ruta del archivo que compartirá toda la red
FICHERO_PIZARRA = "pizarra_maestra.json"

def conectar_pizarra():
    """
    Lee la pizarra desde un archivo JSON físico para que 
    Instructor y Alumno compartan la misma información.
    """
    # 1. Si el archivo no existe, lo creamos con valores iniciales
    if not os.path.exists(FICHERO_PIZARRA):
        datos_iniciales = {
            "configurado": False,
            "yacimiento": None,
            "profundidad_actual": 0.0,
            "tvd_target": 0.0,
            "gradiente": 0.44,
            "caudal": 0.0,
            "rpm": 0.0,
            "wob": 0.0,
            "spp": 0.0,
            "torque": 0.0,
            "rop": 0.0,
            # GEONAVEGACION (Los parámetros que decís que no cambian)
            "inclinacion": 0.0,
            "azimut": 0.0,
            "toolface": 0.0,
            # CONTROL DE POZO
            "bop_cerrado": False,
            "alarma": False,
            "influjo_activo": 0.0, # El instructor sube esto
            "volumen_piletas": 1200.0,
            "densidad_lodo": 9.5
        }
        actualizar_fichero(datos_iniciales)

    # 2. Leemos el estado actual del archivo
    with open(FICHERO_PIZARRA, "r") as f:
        pizarra_real = json.load(f)
    
    return pizarra_real

def actualizar_fichero(datos):
    """Guarda los cambios en el disco para que el otro usuario los vea"""
    with open(FICHERO_PIZARRA, "w") as f:
        json.dump(datos, f, indent=4)

def selector_yacimiento_mendoza(piz):
    # ... (Tu código de UI actual está perfecto, pero al final debés llamar a actualizar_fichero)
    # Ejemplo al final del botón:
    if st.button("INICIALIZAR SISTEMAS"):
        # ... (tus asignaciones)
        actualizar_fichero(piz) # IMPORTANTE: Graba el cambio en el disco
        st.rerun()

def resetear_simulacion(piz):
    if os.path.exists(FICHERO_PIZARRA):
        os.remove(FICHERO_PIZARRA)
    st.rerun()

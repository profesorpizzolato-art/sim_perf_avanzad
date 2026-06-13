# =====================================================================
# MENFA 3.0 - MÓDULO DE CONTROL OPERATIVO Y FRICCIÓN INDUSTRIAL
# Desarrollado por: Inst. Fabricio Pizzolato (Mendoza, Argentina)
# =====================================================================

import numpy as np
import random
import streamlit as st

def obtener_formacion_mendoza(profundidad_m):
    """Matriz geológica real de la cuenca cuyana."""
    if profundidad_m < 1200:
        return {"nombre": "Punta de las Bardas", "dureza": 1.0, "tipo": "Arcillosa", "desc": "Arcillas blandas. ¡Ojo con el taponamiento (Bit Balling)!"}
    elif profundidad_m < 2200:
        return {"nombre": "Barrancas", "dureza": 2.2, "tipo": "Intercalada", "desc": "Areniscas compactas y arcilitas. Fluctuaciones de torque moderadas."}
    else:
        return {"nombre": "Cacheuta / Potrerillos", "dureza": 3.8, "tipo": "Abrasiva/Dura", "desc": "Roca lutítica compacta y basaltos duros. Alto desgaste de trépano."}

def aplicar_friccion_operativa(piz, rop_real, rotaria_activa, bombas_ok):
    """
    Simula el desgaste, contaminación del lodo y cambios litológicos 
    afectando directamente los parámetros de la pizarra.
    """
    # 1. Identificar Geología Actual
    prof = float(piz["profundidad_actual"])
    geo = obtener_formacion_mendoza(prof)
    piz["geo_actual"] = geo["nombre"]
    piz["geo_desc"] = geo["desc"]
    
    # Si no está perforando, detenemos la fricción reactiva
    if not (rotaria_activa and bombas_ok and rop_real > 0):
        return

    # 2. Desgaste del Trépano (Bit Wear)
    # El desgaste aumenta con el WOB, las RPM y la dureza del terreno
    wob = float(piz["wob_maestro"])
    rpm = float(piz["rpm_maestro"])
    
    factor_desgaste = (wob * 0.005) + (rpm * 0.002) * geo["dureza"]
    piz["vida_trepano"] = max(round(piz.get("vida_trepano", 100.0) - factor_desgaste, 2), 0.0)

    # 3. Degradación y Contaminación Química del Lodo
    # Perforar tramos arcillosos incorpora sólidos alterando la viscosidad plástica de forma interna
    if geo["tipo"] == "Arcillosa":
        piz["contaminacion_lodo"] = min(piz.get("contaminacion_lodo", 0.0) + 0.15, 100.0)
    else:
        piz["contaminacion_lodo"] = min(piz.get("contaminacion_lodo", 0.0) + 0.05, 100.0)

    # Si el lodo se contamina, la eficiencia de limpieza anular sufre una penalización oculta
    penalizacion_limpieza = (piz["contaminacion_lodo"] / 100.0) * 15.0
    piz["eficiencia_limpieza"] = max(piz["eficiencia_limpieza"] - penalizacion_limpieza, 0.0)

    # 4. Evento Dinámico: Taponamiento del Trépano (Bit Balling)
    # Si perfora arcilla con mucho WOB pero poco caudal (< 550 GPM), el trépano se emboza
    caudal = float(piz["caudal_maestro"])
    if geo["tipo"] == "Arcillosa" and wob > 20.0 and caudal < 550.0:
        piz["bit_balling_activo"] = True
    else:
        piz["bit_balling_activo"] = False

# =====================================================================
# MENFA 3.0 - MÓDULO EXPERTO DE FLUIDOS DE PERFORACIÓN Y SINCRONÍA (DINÁMICO)
# Desarrollado por: Inst. Fabricio Pizzolato (Mendoza, Argentina)
# =====================================================================

import numpy as np
import pandas as pd
import streamlit as st
import random

def evaluar_sincronia_operativa(caudal_gpm, densidad_lodo, presion_standpipe, rpm, wob, rop_actual, profundidad_m):
    """
    Simula la interacción de los sistemas mecánico, hidráulico y geológico
    generando fluctuaciones dinámicas en tiempo real para simular movimiento continuo.
    """
    alertas = []
    penalizaciones = []
    
    # --- 1. GEOMECÁNICA: Ventana de Lodos ---
    gradiente_poro = 9.8      # ppg equivalente
    gradiente_fractura = 15.5  # ppg equivalente
    
    # --- 2. HIDRÁULICA DINÁMICA: Cálculo de ECD con Fluctuación de Bombeo ---
    viscosidad_plastica = 25.0  # cP
    # Si las bombas están encendidas, el fluido genera micro-presiones dinámicas
    ruido_hidraulico = random.uniform(-0.03, 0.03) if caudal_gpm > 0 else 0.0
    
    apl = (viscosidad_plastica * caudal_gpm / 2000) / 10 if caudal_gpm > 0 else 0.0
    ecd = densidad_lodo + apl + ruido_hidraulico
    
    # Verificación de integridad del pozo
    if ecd < gradiente_poro:
        alertas.append({
            "tipo": "ERROR",
            "msg": f"🚨 RIESGO DE BROTE (KICK): El ECD ({ecd:.2f} ppg) es inferior al gradiente de poro ({gradiente_poro} ppg)."
        })
        penalizaciones.append("Riesgo inminente de surgencia por baja densidad/ECD.")
    elif ecd > gradiente_fractura:
        alertas.append({
            "tipo": "ERROR",
            "msg": f"🛑 RIESGO DE FRACTURA: El ECD ({ecd:.2f} ppg) superó el gradiente de fractura ({gradiente_fractura} ppg)."
        })
        penalizaciones.append("Fractura de formación por exceso de presión hidráulica.")

    # --- 3. TRANSPORTE DE RECORTES: Limpieza de Hoyo Dinámica ---
    punto_cedente_yp = 20.0  # lb/100ft2
    diametro_hoyo = 8.5      # pulgadas
    diametro_tuberia = 5.0   # pulgadas
    
    if caudal_gpm > 0:
        v_anular = (24.5 * caudal_gpm) / (diametro_hoyo**2 - diametro_tuberia**2)
        v_deslizamiento = 0.45 * (punto_cedente_yp / densidad_lodo)**0.5 * 60
        # Agregamos una pequeña oscilación por el régimen de flujo
        ruido_limpieza = random.uniform(-1.5, 1.5)
        eficiencia_limpieza = (((v_anular - v_deslizamiento) / v_anular) * 100) + ruido_limpieza
    else:
        v_anular = 0
        eficiencia_limpieza = 0

    if rop_actual > 0 and eficiencia_limpieza < 70:
        alertas.append({
            "tipo": "WARNING",
            "msg": f"⚠️ LIMPIEZA INEFICIENTE ({eficiencia_limpieza:.1f}%): Recortes acumulándose en el fondo. ¡Riesgo de pega!"
        })
        if eficiencia_limpieza < 50:
            penalizaciones.append("Perforación con limpieza crítica de hoyo (Riesgo de Embocamiento).")

    # --- 4. OPTIMIZACIÓN MECÁNICA Y TORQUE DINÁMICO (MOVIMIENTO CONTINUO) ---
    # El torque real en campo nunca es fijo, vibra por la interacción trépano-roca
    if rpm > 0 and wob > 0:
        factor_friccion_base = 0.28
        # Micro-vibraciones tensionales del acero (Stick-Slip simulado)
        vibracion_torque = random.uniform(-150.0, 150.0) if rpm < 50 else random.uniform(-60.0, 60.0)
        torque_base = factor_friccion_base * wob * (diametro_hoyo / 12) * 1000 # Escala a ft-lbs
        torque_estimado = torque_base + vibracion_torque
    else:
        torque_estimado = 0.0

    # Cálculo de Energía Específica Mecánica (MSE) reactiva
    if rop_actual > 0 and rpm > 0:
        term_rot = (480 * (torque_estimado / 1000) * rpm) / (diametro_hoyo**2 * rop_actual)
        term_axl = (4 * wob) / (np.pi * diametro_hoyo**2)
        mse = (term_rot + term_axl) * 1000  # PSI reales
    else:
        mse = 0.0

    return {
        "ecd": round(ecd, 2),
        "apl": round(apl, 2),
        "eficiencia_limpieza": round(min(max(eficiencia_limpieza, 0.0), 100.0), 1),
        "mse": int(mse),
        "torque": round(max(torque_estimado, 0.0), 1),
        "alertas": alertas,
        "penalizaciones": penalizaciones,
        "poro": gradiente_poro,
        "frac": gradiente_fractura
    }

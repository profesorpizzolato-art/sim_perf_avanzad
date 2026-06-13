# =====================================================================
# MENFA 3.0 - MÓDULO EXPERTO DE FLUIDOS DE PERFORACIÓN Y SINCRONÍA
# Desarrollado por: Inst. Fabricio Pizzolato (Mendoza, Argentina)
# =====================================================================

import numpy as np
import pandas as pd
import streamlit as st

def evaluar_sincronia_operativa(caudal_gpm, densidad_lodo, presion_standpipe, rpm, wob, rop_actual, profundidad_m):
    """
    Simula la interacción de los sistemas mecánico, hidráulico y geológico
    basado en las 12 funciones críticas del fluido de perforación.
    """
    alertas = []
    penalizaciones = []
    
    # Conversión útil: Profundidad a pies para fórmulas API
    tvd_ft = profundidad_m * 3.28084
    
    # --- 1. GEOMECÁNICA: Ventana de Lodos (Funciones 2 y 5) ---
    # Gradientes simulados para la geología típica de Mendoza (ej. Cacheuta)
    gradiente_poro = 9.8      # ppg equivalente
    gradiente_fractura = 15.5  # ppg equivalente
    
    # --- 2. HIDRÁULICA DINÁMICA: Cálculo de ECD (Funciones 2, 7 y 10) ---
    viscosidad_plastica = 25.0  # cP (Valor por defecto o dinámico)
    # Pérdida de carga anular aproximada (APL)
    apl = (viscosidad_plastica * caudal_gpm / 2000) / 10 if caudal_gpm > 0 else 0.0
    ecd = densidad_lodo + apl
    
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

    # --- 3. TRANSPORTE DE RECORTES: Limpieza de Hoyo (Funciones 1, 3 y 8) ---
    punto_cedente_yp = 20.0  # lb/100ft2
    diametro_hoyo = 8.5      # pulgadas
    diametro_tuberia = 5.0   # pulgadas
    
    if caudal_gpm > 0:
        # Velocidad Anular (ft/min)
        v_anular = (24.5 * caudal_gpm) / (diametro_hoyo**2 - diametro_tuberia**2)
        # Velocidad de deslizamiento del ripio (Fórmula de Walker simplificada)
        v_deslizamiento = 0.45 * (punto_cedente_yp / densidad_lodo)**0.5 * 60
        eficiencia_limpieza = ((v_anular - v_deslizamiento) / v_anular) * 100
    else:
        v_anular = 0
        eficiencia_limpieza = 0

    # Lógica de acumulación si está perforando sin limpiar
    if rop_actual > 0 and eficiencia_limpieza < 70:
        alertas.append({
            "tipo": "WARNING",
            "msg": f"⚠️ LIMPIEZA INEFICIENTE ({eficiencia_limpieza:.1f}%): Recortes acumulándose en el fondo. ¡Riesgo de pega!"
        })
        if eficiencia_limpieza < 50:
            penalizaciones.append("Perforación con limpieza crítica de hoyo (Riesgo de Embocamiento).")

    # --- 4. OPTIMIZACIÓN MECÁNICA: Energía Específica Mecánica (MSE) (Función 7 y 8) ---
    # Simulación de torque correlacionado con lubricación del lodo, WOB y RPM
    factor_friccion_lodo = 0.28  # Un buen lodo reduce este factor
    torque_estimado = factor_friccion_lodo * wob * (diametro_hoyo / 12) if wob > 0 else 1.0
    
    # CORRECCIÓN SINTÁCTICA: Evaluación de variables limpias
    if rop_actual > 0 and rpm > 0:
        term_rot = (480 * torque_estimado * rpm) / (diametro_hoyo**2 * rop_actual)
        term_axl = (4 * wob) / (np.pi * diametro_hoyo**2)
        mse = term_rot + term_axl
    else:
        mse = 0.0

    # Retornamos un diccionario con todo procesado para los relojes y lógicas del app.py
    return {
        "ecd": round(ecd, 2),
        "apl": round(apl, 2),
        "eficiencia_limpieza": round(min(max(eficiencia_limpieza, 0.0), 100.0), 1),
        "mse": int(mse),
        "torque": round(torque_estimado, 2),
        "alertas": alertas,
        "penalizaciones": penalizaciones,
        "poro": gradiente_poro,
        "frac": gradiente_fractura
    }

import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, profundidad, flow_rate):
    # ROP: Basado en tus fórmulas de Vaca Muerta
    rop_base = (wob * rpm) / 1000
    if flow_rate < 300: rop_base *= 0.5
    
    # MSE: Eficiencia mecánica
    mse = (480 * torque * rpm) / (rop_base + 0.1)
    
    # Hook Load (Cálculo de peso)
    peso_lineal = 0.02 # klbs/m
    hook_load = (profundidad * peso_lineal) - wob
    
    return {
        "ROP": round(rop_base, 2),
        "MSE": round(mse, 2),
        "HOOK_LOAD": round(hook_load, 2)
    }

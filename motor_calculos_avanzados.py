import numpy as np

def calcular_fisica_perforacion(wob, rpm, torque, rop, depth, flow_rate):
    # Constantes Vaca Muerta
    diam_mecha = 8.5 
    area_mecha = np.pi * (diam_mecha**2) / 4
    
    # 1. MSE (Energía Específica Mecánica)
    mse = (wob / area_mecha) + (480 * torque * rpm) / (area_mecha * rop * 3.28)
    mse_kpsi = mse / 1000

    # 2. Hidráulica (Velocidad Anular)
    id_casing = 9.625
    od_dp = 5.0
    av = (24.5 * flow_rate) / (id_casing**2 - od_dp**2)
    
    # 3. Control de Pozos (Kill Mud Weight)
    sidpp = 500
    tvd = depth * 3.28
    mw_actual = 11.5
    kmw = mw_actual + (sidpp / (0.052 * tvd))

    # 4. Carga en el Gancho (Hook Load)
    bf = 0.82
    peso_sarta = depth * 25
    hook_load = (peso_sarta * bf) - (wob * 1000)

    return {
        "MSE": round(mse_kpsi, 2),
        "AV": round(av, 2),
        "KMW": round(kmw, 2),
        "HOOK_LOAD": round(hook_load / 1000, 1)
    }

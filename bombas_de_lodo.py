def calcular_presion_bomba(caudal, densidad):
    # Lógica simple para evitar errores
    presion = (caudal * 2) * (densidad / 8.33)
    return round(presion, 2)
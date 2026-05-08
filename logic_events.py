def gestionar_fallas(piz):
    if piz["evento_activo"] == "KICK":
        # Si hay un Kick, la presión sube y el nivel de tanques (simulado) debería subir
        piz["presion_base"] += 5.5
        if piz["presion_base"] > 3500:
            piz["evento_activo"] = "¡REVENTÓN! (Pozo fuera de control)"
            
    if piz["evento_activo"] == "PÉRDIDA":
        # La presión cae drásticamente
        piz["presion_base"] = max(0, piz["presion_base"] - 15.0)

    if piz["bop_cerrado"] and piz["evento_activo"] == "KICK":
        # Si el alumno cierra el BOP, la presión se estabiliza
        piz["alarma_activa"] = False
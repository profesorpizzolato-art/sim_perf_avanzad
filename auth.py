import streamlit as st

PASSWORD_ALUMNO = "alumno2026"
PASSWORD_PROFE = "menfa2026"

USUARIOS_ALUMNOS = {
    "Usubiaga": PASSWORD_ALUMNO, "Flores": PASSWORD_ALUMNO,
    "Moya": PASSWORD_ALUMNO, "Perez": PASSWORD_ALUMNO,
    "Paredes": PASSWORD_ALUMNO, "Casanueva": PASSWORD_ALUMNO,
    "Pizzolato": PASSWORD_ALUMNO, "Villalba": PASSWORD_ALUMNO,
    "Invitado": PASSWORD_ALUMNO
}

def validar_acceso(usuario, clave, tipo):
    if tipo == "alumno":
        return usuario in USUARIOS_ALUMNOS and USUARIOS_ALUMNOS[usuario] == clave
    if tipo == "instructor":
        return clave == PASSWORD_PROFE
    return False
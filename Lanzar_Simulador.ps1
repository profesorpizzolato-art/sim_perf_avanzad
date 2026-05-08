# --- Script de Lanzamiento MENFA 3.0 ---
Clear-Host
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   SISTEMA DE ENTRENAMIENTO PETROLERO - MENFA" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Verificar si existe entorno virtual y activarlo
if (Test-Path ".\venv") {
    Write-Host "[*] Activando entorno virtual..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[!] No se detectó carpeta 'venv'. Usando Python global." -ForegroundColor Yellow
}

# 2. Configurar la política de ejecución para esta sesión (evita errores de permisos)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# 3. Lanzar Streamlit con el archivo modularizado
Write-Host "[*] Iniciando Servidor Streamlit en Puerto 8501..." -ForegroundColor White
streamlit run app.py --server.port 8501 --server.headless false

# Pausar en caso de error para poder leer el log
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[!] Hubo un error al iniciar el simulador." -ForegroundColor Red
    pause
}
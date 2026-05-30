# Instala Docker Desktop no Windows via winget
# Execute como Administrador: powershell -ExecutionPolicy Bypass -File install-docker-windows.ps1

Write-Host "🐳 Instalando Docker Desktop..." -ForegroundColor Cyan

# Verificar winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "❌ winget não encontrado. Baixe em: https://aka.ms/getwinget" -ForegroundColor Red
    exit 1
}

# Instalar Docker Desktop
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

Write-Host ""
Write-Host "✅ Docker Desktop instalado!" -ForegroundColor Green
Write-Host "⚠️  REINICIE o computador e depois execute:" -ForegroundColor Yellow
Write-Host '   cd "G:\Meu Drive\projetos\CANMOS-NITI"' -ForegroundColor White
Write-Host "   copy .env.example .env" -ForegroundColor White
Write-Host "   docker compose up --build" -ForegroundColor White

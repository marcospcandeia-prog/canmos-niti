# Script para criar repositório GitHub e fazer push
# Execute após: gh auth login

param(
    [string]$RepoName = "canmos-niti",
    [string]$Visibility = "private"
)

$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

Write-Host "🐙 Configurando GitHub para CANMOS-NITI..." -ForegroundColor Cyan

# Verificar auth
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Você precisa autenticar no GitHub primeiro:" -ForegroundColor Red
    Write-Host "   gh auth login" -ForegroundColor Yellow
    exit 1
}

# Criar repositório
Write-Host "📦 Criando repositório $RepoName ($Visibility)..."
gh repo create $RepoName --$Visibility --description "CANMOS-NITI — Infraestrutura Tributária Inteligente" 2>&1

# Configurar remote
$ghUser = gh api user --jq .login 2>&1
git remote remove origin 2>$null
git remote add origin "https://github.com/$ghUser/$RepoName.git"

# Push
Write-Host "⬆️  Fazendo push..."
git push -u origin main

Write-Host ""
Write-Host "✅ Repositório criado e código enviado!" -ForegroundColor Green
Write-Host "   🔗 https://github.com/$ghUser/$RepoName" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Conecte o repo ao Vercel (frontend): https://vercel.com/import"
Write-Host "   2. Conecte ao Railway (backend): https://railway.app/new"
Write-Host "   3. Adicione os secrets no GitHub: Settings → Secrets → Actions"
Write-Host "      VPS_HOST, VPS_USER, VPS_SSH_KEY"

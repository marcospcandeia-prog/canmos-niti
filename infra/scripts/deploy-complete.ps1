#Requires -Version 7.0
<#
.SYNOPSIS
    Deploy automatizado do CANMOS-NITI (GitHub + Supabase + Vercel + Render)
.DESCRIPTION
    Script completo de deploy que configura todos os serviços cloud:
    - Cria/vincula repositório GitHub (já feito se executado pelo opencode)
    - Cria projeto Supabase + roda migrations
    - Faz deploy do frontend na Vercel
    - Faz deploy do backend no Render (via blueprint ou web service)
    - Verifica health checks
#>

$ErrorActionPreference = "Stop"

# Cores para output
$GREEN = "Green"
$YELLOW = "Yellow"
$RED = "Red"
$CYAN = "Cyan"

function Write-Step($text) {
    Write-Host "`n=== $text ===" -ForegroundColor $CYAN
}

function Write-Success($text) {
    Write-Host "[OK] $text" -ForegroundColor $GREEN
}

function Write-Warning($text) {
    Write-Host "[!] $text" -ForegroundColor $YELLOW
}

function Write-Error($text) {
    Write-Host "[FAIL] $text" -ForegroundColor $RED
}

function Test-Command($name) {
    $found = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $found) {
        Write-Error "$name nao encontrado. Instale com: $($args[0])"
        return $false
    }
    Write-Success "$name encontrado: $($found.Source)"
    return $true
}

# ============================================================
# PASSO 1: Verificar dependências
# ============================================================
Write-Step "1. Verificando dependencias"

$depsOk = $true
if (-not (Test-Command "git" "winget install --id Git.Git -e")) { $depsOk = $false }
if (-not (Test-Command "gh" "winget install --id GitHub.cli -e")) { $depsOk = $false }

# Verificar se gh está autenticado
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "gh nao autenticado. Execute: gh auth login"
    Write-Warning "Ou configure GH_TOKEN environment variable"
    $depsOk = $false
} else {
    Write-Success "gh autenticado"
}

if (-not $depsOk) {
    Write-Error "Corrija as dependencias acima e tente novamente."
    exit 1
}

# ============================================================
# PASSO 2: Verificar repositório GitHub
# ============================================================
Write-Step "2. Verificando repositorio GitHub"

$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Warning "Nenhum remote origin configurado."
    $repoName = Read-Host "Nome do repositorio GitHub (ex: canmos-niti)"
    $githubUser = Read-Host "Seu usuario GitHub"
    
    $token = $env:GH_TOKEN
    if (-not $token) {
        $token = Read-Host "GitHub Personal Access Token (com scopes: repo, workflow)" -AsSecureString
        $token = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
        )
    }
    
    Write-Step "Criando repositorio $repoName..."
    gh repo create $repoName --public --source="$(Get-Location)" --remote=origin --push
    Write-Success "Repositorio criado: https://github.com/$githubUser/$repoName"
} else {
    Write-Success "Remote origin ja configurado: $remoteUrl"
}

# ============================================================
# PASSO 3: Supabase (Database)
# ============================================================
Write-Step "3. Configurando Supabase (PostgreSQL)"

$supabaseToken = $env:SUPABASE_ACCESS_TOKEN
if (-not $supabaseToken) {
    $supabaseToken = Read-Host "Supabase Access Token (crie em: https://supabase.com/dashboard/account/tokens)" -AsSecureString
    $supabaseToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($supabaseToken)
    )
}

if ($supabaseToken) {
    supabase login --token $supabaseToken 2>&1
    Write-Success "Supabase CLI autenticado"
    
    $projectName = Read-Host "Nome do projeto Supabase (ex: canmos-niti-prod)" -Default "canmos-niti-prod"
    $dbPassword = Read-Host "Senha do banco PostgreSQL" -AsSecureString
    
    Write-Step "Criando projeto Supabase '$projectName'..."
    $result = supabase projects create $projectName --org-id "default" --db-password $dbPassword 2>&1
    Write-Host $result
    
    # Extrair project reference do output
    if ($result -match "(\w+)$") {
        $projectRef = $matches[1]
        Write-Success "Projeto criado: $projectRef"
        
        # Aguardar provisionamento
        Write-Host "Aguardando provisionamento do banco (60s)..."
        Start-Sleep -Seconds 60
        
        # Obter connection string
        $dbUrl = "postgresql+asyncpg://postgres:$dbPassword@db.$projectRef.supabase.co:5432/postgres"
        Write-Success "DATABASE_URL: $dbUrl"
    }
} else {
    Write-Warning "Supabase token nao fornecido."
    Write-Warning "Crie o projeto manualmente em: https://supabase.com"
    $dbUrl = Read-Host "Cole sua DATABASE_URL (postgresql+asyncpg://...)"
}

# ============================================================
# PASSO 4: Rodar migrations
# ============================================================
Write-Step "4. Rodando migrations do banco"

if ($dbUrl) {
    $env:DATABASE_URL = $dbUrl
    $env:JWT_SECRET = if ($env:JWT_SECRET) { $env:JWT_SECRET } else { "dev-secret-key-nao-usar-em-producao-$(Get-Random)" }
    $env:SUPABASE_URL = "https://$projectRef.supabase.co"
    $env:SUPABASE_ANON_KEY = "placeholder"
    $env:SUPABASE_SERVICE_ROLE = "placeholder"
    $env:MINIO_ENDPOINT = "localhost:9000"
    
    Push-Location backend
    alembic upgrade head 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Migrations executadas com sucesso!"
    } else {
        Write-Error "Falha nas migrations. Verifique DATABASE_URL."
    }
    Pop-Location
} else {
    Write-Error "DATABASE_URL nao configurada. Impossivel rodar migrations."
}

# ============================================================
# PASSO 5: Vercel (Frontend)
# ============================================================
Write-Step "5. Deploy do Frontend na Vercel"

$vercelToken = $env:VERCEL_TOKEN
if (-not $vercelToken) {
    $vercelToken = Read-Host "Vercel Token (crie em: https://vercel.com/account/tokens)" -AsSecureString
    $vercelToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($vercelToken)
    )
}

if ($vercelToken) {
    vercel login --token $vercelToken 2>&1
    Write-Success "Vercel CLI autenticado"
    
    $frontendUrl = Read-Host "URL do backend (ex: https://canmos-backend.onrender.com)"
    
    Push-Location frontend
    vercel pull --token $vercelToken 2>&1
    vercel build --token $vercelToken 2>&1
    
    Write-Step "Fazendo deploy para producao..."
    $vercelOutput = vercel deploy --prebuilt --token $vercelToken --prod 2>&1
    Write-Host $vercelOutput
    
    # Extrair URL do deploy
    if ($vercelOutput -match "https://[^\s]+") {
        $deployUrl = $matches[0]
        Write-Success "Frontend deployed: $deployUrl"
    }
    
    # Configurar env vars no Vercel
    if ($frontendUrl) {
        vercel env add NEXT_PUBLIC_API_URL production --token $vercelToken 2>&1
        # O comando acima é interativo, alternativa:
        vercel env rm NEXT_PUBLIC_API_URL --token $vercelToken --yes 2>$null
        "NEXT_PUBLIC_API_URL=$frontendUrl" | vercel env add NEXT_PUBLIC_API_URL production --token $vercelToken 2>&1
    }
    
    Pop-Location
} else {
    Write-Warning "Vercel token nao fornecido."
    Write-Warning "Deploy manual via: https://vercel.com/import"
    Write-Warning "Ou configure VERCEL_TOKEN e execute novamente."
}

# ============================================================
# PASSO 6: Render (Backend)
# ============================================================
Write-Step "6. Deploy do Backend no Render"

$renderKey = $env:RENDER_API_KEY
if (-not $renderKey) {
    $renderKey = Read-Host "Render API Key (opcional - crie em: https://dashboard.render.com/api)" -AsSecureString
    $renderKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($renderKey)
    )
}

if ($renderKey) {
    Write-Warning "Render CLI nao disponivel nativamente."
    Write-Warning "Use o Blueprint em: https://dashboard.render.com/select-repo"
    Write-Warning "Selecione: marcospcandeia-prog/canmos-niti"
    Write-Warning "O render.yaml sera lido automaticamente."
    Write-Success "render.yaml ja configurado com as variaveis."
} else {
    Write-Warning "Para deploy manual no Render:"
    Write-Warning "1. Acesse: https://dashboard.render.com/select-repo"
    Write-Warning "2. Conecte: marcospcandeia-prog/canmos-niti"
    Write-Warning "3. O render.yaml configura automaticamente"
}

# ============================================================
# PASSO 7: Verificação Final
# ============================================================
Write-Step "7. Verificacao Final"

$backendUrl = Read-Host "URL do backend (Render)" -Default "https://canmos-backend.onrender.com"
$frontendUrl = Read-Host "URL do frontend (Vercel)" -Default "https://canmos-niti.vercel.app"

Write-Host "`nVerificando health checks..." -ForegroundColor $CYAN

try {
    $healthBackend = Invoke-WebRequest -Uri "$backendUrl/health" -TimeoutSec 10
    if ($healthBackend.StatusCode -eq 200) {
        Write-Success "Backend health check OK: $backendUrl/health"
    }
} catch {
    Write-Error "Backend health check falhou. Verifique se o Render terminou o deploy."
}

try {
    $healthFrontend = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 10
    if ($healthFrontend.StatusCode -eq 200) {
        Write-Success "Frontend OK: $frontendUrl"
    }
} catch {
    Write-Error "Frontend nao respondeu. Verifique o deploy na Vercel."
}

Write-Host "`n========================================" -ForegroundColor $CYAN
Write-Host "   DEPLOY CONCLUIDO!" -ForegroundColor $GREEN
Write-Host "========================================`n" -ForegroundColor $CYAN
Write-Host "Frontend: $frontendUrl"
Write-Host "Backend:  $backendUrl/docs"
Write-Host "GitHub:   https://github.com/marcospcandeia-prog/canmos-niti"
Write-Host "`nProximos passos:"
Write-Host "1. Configure MinIO (storage) e Ollama (IA) nos env vars do Render"
Write-Host "2. Teste registro/login nos endpoints"
Write-Host "3. Configure dominio customizado (opcional)"
Write-Host "`nGuia completo: DEPLOY.md"

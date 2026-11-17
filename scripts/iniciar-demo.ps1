param([ValidateRange(1024,65535)][int]$Porta = 8080)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$demoPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) {
    throw 'Ambiente .venv ausente. Consulte docs/entregas/COMO_USAR_E_GRAVAR.md para instalar.'
}
$env:ACOLHE_OLLAMA_MODEL = 'qwen2.5:3b-instruct'
$env:ACOLHE_OLLAMA_NUM_GPU = '-1'
$env:ACOLHE_OLLAMA_KEEP_ALIVE = '2m'
$env:HOST = '127.0.0.1'
$env:PORT = [string]$Porta
New-Item -ItemType Directory -Force -Path 'docs/qa' | Out-Null
$env:ACOLHE_DB = Join-Path (Get-Location) 'docs\qa\demonstracao.db'
& $demoPython -B -m genai.local
if ($LASTEXITCODE -ne 0) {
    throw 'Abra o Ollama e confira o modelo: ollama pull qwen2.5:3b-instruct'
}
Write-Host "Abra http://127.0.0.1:$Porta - Ctrl+C encerra o servidor."
& $demoPython -B -m app.server

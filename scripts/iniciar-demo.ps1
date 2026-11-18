param([ValidateRange(1024,65535)][int]$Porta = 8080)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$demoPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) {
    throw 'Ambiente .venv ausente. Consulte docs/entregas/COMO_USAR_E_GRAVAR.md para instalar.'
}
$demoListeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty LocalPort)
$demoFreePort = $Porta..([Math]::Min($Porta + 10, 65535)) | Where-Object { $_ -notin $demoListeners } | Select-Object -First 1
if ($null -eq $demoFreePort) {
    throw 'Nenhuma porta livre nas 11 portas verificadas. Escolha outra com -Porta.'
}
$Porta = [int]$demoFreePort
$env:ACOLHE_OLLAMA_MODEL = 'qwen2.5:3b-instruct'
$env:ACOLHE_OLLAMA_NUM_GPU = '-1'
$env:ACOLHE_OLLAMA_KEEP_ALIVE = '2m'
$env:HOST = '127.0.0.1'
$env:PORT = [string]$Porta
New-Item -ItemType Directory -Force -Path 'docs/qa' | Out-Null
$env:ACOLHE_DB = Join-Path (Get-Location) 'docs\qa\demonstracao.db'
& $demoPython -B -m genai.local --verify-release
if ($LASTEXITCODE -ne 0) {
    throw 'Abra o Ollama e confira o modelo e digest registrados em genai/model_manifest.json.'
}
& $demoPython -B -c "import json; from vision.service import status; result=status(); print(json.dumps(result, ensure_ascii=False)); raise SystemExit(0 if result['ready'] else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'Vision indisponivel. Execute scripts/preparar-demo.ps1 e confira vision/release.'
}
Write-Host "Abra http://127.0.0.1:$Porta - Ctrl+C encerra o servidor."
& $demoPython -B -m app.server

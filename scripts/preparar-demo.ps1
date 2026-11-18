$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Instale Python 3.12 antes de preparar a demonstracao.'
}
$demoOllamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
$demoOllama = if ($demoOllamaCommand) { $demoOllamaCommand.Source } else { Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe' }
if (-not (Test-Path -LiteralPath $demoOllama)) {
    throw 'Instale e abra Ollama: https://ollama.com/download'
}
$demoPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) {
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel criar .venv.' }
}
& $demoPython -m ensurepip
if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar pip no ambiente .venv.' }
& $demoPython -m pip install -r vision/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependencias Vision.' }
$demoManifest = Get-Content -LiteralPath genai/model_manifest.json -Raw | ConvertFrom-Json
& $demoOllama pull $demoManifest.model
if ($LASTEXITCODE -ne 0) { throw 'Falha ao baixar a LLM. Abra Ollama e confira a conexao.' }
& $demoPython -B -m genai.local --verify-release
if ($LASTEXITCODE -ne 0) { throw 'A LLM instalada nao corresponde ao manifesto da entrega.' }
& $demoPython -B -c "import json; from vision.service import status; result=status(); print(json.dumps(result, ensure_ascii=False)); raise SystemExit(0 if result['ready'] else 1)"
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint Vision ausente, alterado ou sem dependencias.' }
Write-Host 'Pronto. Execute .\scripts\iniciar-demo.ps1; as tres fotos estao em vision\examples.'

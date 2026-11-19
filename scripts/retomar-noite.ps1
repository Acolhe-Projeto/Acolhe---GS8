$ErrorActionPreference = 'Stop'
$nightRoot = Split-Path $PSScriptRoot -Parent
Set-Location $nightRoot
$nightDir = Join-Path $nightRoot 'docs\qa\night'
$nightConfig = Get-Content -LiteralPath (Join-Path $nightDir 'resume.json') -Raw | ConvertFrom-Json
$nightDeadline = [DateTimeOffset]::Parse($nightConfig.deadline_local)
if ([DateTimeOffset]::Now -ge $nightDeadline -or (Test-Path -LiteralPath (Join-Path $nightDir 'finalized.json'))) { exit }
$nightMutex = New-Object System.Threading.Mutex($false, 'Local\AcolheGS8NightSupervisor')
if (-not $nightMutex.WaitOne(0)) { exit }
try {
    Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class AcolheAwake { [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint flags); }'
    if ([AcolheAwake]::SetThreadExecutionState([uint32]2147483649) -eq 0) { throw 'Cannot keep system awake' }
    $nightPython = Join-Path $nightRoot '.venv\Scripts\python.exe'
    $nightWorker = Start-Process -FilePath $nightPython -ArgumentList @('-B', (Join-Path $PSScriptRoot 'night_worker.py')) -WorkingDirectory $nightRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $nightDir 'worker.stdout.log') -RedirectStandardError (Join-Path $nightDir 'worker.stderr.log')
    $nightResumeAt = [DateTimeOffset]::Parse($nightConfig.resume_after_utc).AddMinutes(3)
    $nightAttempts = 0
    while ([DateTimeOffset]::Now -lt $nightDeadline -and -not (Test-Path -LiteralPath (Join-Path $nightDir 'finalized.json'))) {
        $heartbeat = Join-Path $nightDir 'agent-heartbeat.txt'
        $nightAgentIdle = -not (Test-Path -LiteralPath $heartbeat) -or ((Get-Date)-(Get-Item -LiteralPath $heartbeat).LastWriteTime).TotalMinutes -gt 15
        if ([DateTimeOffset]::Now -ge $nightResumeAt -and $nightAgentIdle -and $nightAttempts -lt 3) {
            $nightAttempts++
            $nightCodex = $nightConfig.codex
            if (-not (Test-Path -LiteralPath $nightCodex)) { $nightCodex = (Get-Command codex).Source }
            $nightReply = Join-Path $nightDir ('resume-'+$nightAttempts+'-reply.txt')
            $nightResume = Start-Process -FilePath $nightCodex -WorkingDirectory $nightRoot -WindowStyle Hidden -PassThru -ArgumentList @('exec','resume',$nightConfig.session_id,'-','--json','-o',$nightReply,'-c','approval_policy=never') -RedirectStandardInput (Join-Path $nightDir 'RESUME_PROMPT.txt') -RedirectStandardOutput (Join-Path $nightDir ('resume-'+$nightAttempts+'.jsonl')) -RedirectStandardError (Join-Path $nightDir ('resume-'+$nightAttempts+'.stderr.log'))
            $nightResume.WaitForExit()
            $nightResumeAt = [DateTimeOffset]::Now.AddMinutes(20)
        }
        Start-Sleep -Seconds 30
    }
} finally {
    [AcolheAwake]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    $nightMutex.ReleaseMutex()
    $nightMutex.Dispose()
}

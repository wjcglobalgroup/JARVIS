$ErrorActionPreference = 'Stop'
$root = Join-Path $env:USERPROFILE '.openclaw'
$outPath = Join-Path $root 'reports\audit-20261114-112451\elevated-gateway-start.result.json'
try {
  $cli = Join-Path $env:APPDATA 'npm\openclaw.ps1'
  & $cli gateway start
  $exit = $LASTEXITCODE
  $task = Get-ScheduledTask -TaskName 'OpenClaw Gateway'
  $listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 18789 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  $result = [ordered]@{ exitCode = $exit; taskState = [string]$task.State; listener = [bool]$listener; pid = if ($listener) { [int]$listener.OwningProcess } else { $null } }
  $result | ConvertTo-Json -Compress | Set-Content -LiteralPath $outPath -Encoding utf8
  exit $exit
} catch {
  $result = [ordered]@{ exitCode = 1; errorType = $_.Exception.GetType().Name; errorCode = $_.Exception.HResult; taskState = [string](Get-ScheduledTask -TaskName 'OpenClaw Gateway').State }
  $result | ConvertTo-Json -Compress | Set-Content -LiteralPath $outPath -Encoding utf8
  exit 1
}
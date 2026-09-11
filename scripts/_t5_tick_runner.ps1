$ErrorActionPreference = 'Stop'
$env:PGCONNECT_TIMEOUT = '10'
Get-Content -Path '.env' | ForEach-Object {
  $line = $_
  if ($line -match '^\s*#' -or $line -match '^\s*$') { return }
  $eq = $line.IndexOf('=')
  if ($eq -gt 0) {
    $k = $line.Substring(0, $eq).Trim()
    $v = $line.Substring($eq + 1)
    Set-Item -Path ("Env:" + $k) -Value $v
  }
}
& .\.venv\Scripts\python.exe scripts\_t5_queue_watch.py

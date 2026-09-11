$env:PGCONNECT_TIMEOUT = " 10\
Get-Content .env | ForEach-Object {
 if ($_ -match \^\\s*#\ -or $_ -match \^\\s*$\) { return }
 $parts = $_.Split(\=\, 2)
 if ($parts.Length -eq 2) {
 [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), \Process\)
 }
}
& .\.venv\Scripts\python.exe scripts\_t5_queue_watch.py

<#
    dev-up.ps1 - bring the PharmFoldMDK local rig up with one command.

    What it does, in order:
      1. Loads .env into this session's environment (and fails loudly on placeholders).
      2. Opens the MPG proxy on the FIXED port 16380, in its own window.
      3. Waits for the port to actually ACCEPT connections.
      4. Verifies the DB is reachable - a real query, not just the port (a live port is
         not a live connection: that was one of the first-fold night's silent failures).
      5. Verifies the worker's token against the LIVE transport before starting it - never
         start the worker against an unverified transport (the other silent failure: a wrong
         token that only surfaced as 401s in the Fly logs).
      6. Starts the worker in its own window, INHERITING the loaded env (no secret is
         interpolated into a command string - that avoids PowerShell nested-quote fragility
         and keeps the token off the child's command line).

    Usage:   .\scripts\dev-up.ps1                 # proxy + verify + worker
             .\scripts\dev-up.ps1 -NoWorker       # proxy + verify only (enqueue / UI-arc days)

    Requires: a filled-in .env in the repo root (see .env.example), flyctl on PATH, the .venv.

    Why port 16380 is hardcoded: 'fly mpg proxy' takes --local-port and defaults to 16380, so
    the port is PINNED, not random. That is what lets DATABASE_URL be fully static in .env with
    nothing to probe or prompt for. Change it only by changing .env's DATABASE_URL to match.

    NOTE: kept pure ASCII on purpose - Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI, and
    a stray UTF-8 dash/box char decodes into a quote that breaks parsing.
#>

param(
    [switch]$NoWorker
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot        # repo root = parent of scripts/
Set-Location -LiteralPath $repo

$py = Join-Path $repo ".venv\Scripts\python.exe"
$port = 16380

# --- 1. Load .env ---
$envFile = Join-Path $repo ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: no .env found at $envFile" -ForegroundColor Red
    Write-Host "Copy .env.example to .env and fill in the real values." -ForegroundColor Yellow
    exit 1
}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $idx = $line.IndexOf("=")
        $name = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim().Trim('"').Trim("'")   # strip optional quotes
        Set-Item -Path "Env:$name" -Value $value
    }
}
Write-Host "[.env] loaded" -ForegroundColor Green

# Required vars present, and NOT still placeholders (fail loudly, before touching the network).
foreach ($req in @("WORKER_AUTH_TOKEN", "DATABASE_URL", "MPG_CLUSTER")) {
    if (-not [Environment]::GetEnvironmentVariable($req)) {
        Write-Host "ERROR: $req is empty in .env" -ForegroundColor Red
        exit 1
    }
}
if ($env:WORKER_AUTH_TOKEN -like "*PUT_THE_REAL*" -or $env:DATABASE_URL -like "*PUT_THE_REAL*") {
    Write-Host "ERROR: .env still has placeholder values - fill in the real token and password." -ForegroundColor Red
    exit 1
}
if (-not $env:TRANSPORT_URL) { $env:TRANSPORT_URL = "https://pharmfoldmdk.fly.dev" }

# --- 2. Open the MPG proxy on the fixed port (its own window) ---
Write-Host "[proxy] opening MPG proxy on localhost:$port (cluster $env:MPG_CLUSTER)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "fly mpg proxy $env:MPG_CLUSTER --local-port $port"
) -WindowStyle Normal

# --- 3. Wait for the port to accept connections ---
Write-Host "[proxy] waiting for localhost:$port " -NoNewline
$ok = $false
foreach ($i in 1..30) {
    Start-Sleep -Seconds 1
    $t = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($t) { $ok = $true; break }
    Write-Host "." -NoNewline
}
Write-Host ""
if (-not $ok) {
    Write-Host "ERROR: proxy port $port never came up. Check the proxy window for errors" -ForegroundColor Red
    Write-Host "(fly auth, wireguard, or the cluster id). Fix and re-run." -ForegroundColor Yellow
    exit 1
}
Write-Host "[proxy] port $port is up" -ForegroundColor Green

# --- 4. Verify the DB with a real query (a live port is NOT a live connection) ---
# The verify is a real .py file (scripts/dev_check_db.py), not python -c with a here-string:
# PowerShell 5.1 mangles quotes passing a multi-line string to a native exe.
Write-Host "[db] verifying connection..." -ForegroundColor Cyan
& $py (Join-Path $repo "scripts\dev_check_db.py")
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: DB verify failed even though the port is up." -ForegroundColor Red
    Write-Host "Most likely the DATABASE_URL password/scheme is wrong in .env, or the tunnel dropped." -ForegroundColor Yellow
    exit 1
}

# --- 5. Start the worker - but only against a VERIFIED transport ---
if ($NoWorker) {
    Write-Host "[worker] skipped (-NoWorker). This window has the env loaded - use it for enqueue / queries." -ForegroundColor Yellow
} else {
    # Verify the worker's token against the LIVE transport before starting it (real .py helper).
    Write-Host "[transport] verifying worker token against $env:TRANSPORT_URL ..." -ForegroundColor Cyan
    & $py (Join-Path $repo "scripts\dev_check_transport.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: transport auth/reachability check failed - NOT starting the worker." -ForegroundColor Red
        Write-Host "Fix WORKER_AUTH_TOKEN in .env (it must match the Fly secret) and re-run." -ForegroundColor Yellow
        exit 1
    }

    # The child window INHERITS this process's environment (WORKER_AUTH_TOKEN, TRANSPORT_URL are
    # already loaded above), so nothing secret is interpolated into the command string.
    Write-Host "[worker] starting worker in its own window..." -ForegroundColor Cyan
    $workerCmd = "Set-Location -LiteralPath '$repo'; " +
                 "Write-Host 'worker starting - polls silently; watch: fly logs -a pharmfoldmdk' -ForegroundColor Green; " +
                 "& '$repo\.venv\Scripts\python.exe' -m worker.main"
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $workerCmd) -WindowStyle Normal
    Write-Host "[worker] launched." -ForegroundColor Green
}

Write-Host ""
Write-Host "Rig is up. Proxy on :$port, env loaded, worker $(if ($NoWorker) { 'skipped' } else { 'running' })." -ForegroundColor Green
Write-Host "This window has DATABASE_URL set - use it for enqueue and queries." -ForegroundColor Green

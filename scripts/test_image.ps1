# ---------------------------------------------------------------------------
# Acceptance test for the practice image.
#
# Tests what a READER gets, not what you built. By default it deletes the
# local copy of the image and pulls from Docker Hub, because a local build and
# a published image are not the same artifact and only one of them is what
# people download. Pass -Local to test the image already on this machine.
#
#   .\test_image.ps1                 # pull from Docker Hub and test that
#   .\test_image.ps1 -Local          # test the local image as-is
#   .\test_image.ps1 -Keep           # leave the container running afterwards
#   .\test_image.ps1 -Force          # also stop whatever holds the ports
#   .\test_image.ps1 -PgPort 5433    # publish elsewhere, e.g. if you run
#                                     # PostgreSQL natively on 5432
# ---------------------------------------------------------------------------
param(
    [switch]$Local,
    [switch]$Keep,
    [switch]$Force,
    [int]$PgPort      = 5432,
    [int]$JupyterPort = 8888,
    [string]$Image = "bilearner/postgres1000-practice:1.1",
    [string]$Name  = "pg1000-acceptance",
    [int]$ExpectedNotebooks = 53
)

$ErrorActionPreference = "Continue"
$script:Pass = 0
$script:Fail = 0

function Check {
    param([string]$What, [string]$Got, [string]$Want)
    if ($Got -eq $Want) {
        Write-Host ("  [ok ] {0,-44} {1}" -f $What, $Got) -ForegroundColor Green
        $script:Pass++
    } else {
        Write-Host ("  [BAD] {0,-44} {1}  (expected {2})" -f $What, $Got, $Want) -ForegroundColor Red
        $script:Fail++
    }
}

function CheckTrue {
    param([string]$What, [bool]$Ok, [string]$Detail = "")
    if ($Ok) {
        Write-Host ("  [ok ] {0,-44} {1}" -f $What, $Detail) -ForegroundColor Green
        $script:Pass++
    } else {
        Write-Host ("  [BAD] {0,-44} {1}" -f $What, $Detail) -ForegroundColor Red
        $script:Fail++
    }
}

function FreePort {
    # A port can be held by another container (usually an earlier test of this
    # same image) or by a process on the host (usually a natively installed
    # PostgreSQL). The two need different answers, so they are told apart
    # rather than lumped into one "port in use" message.
    param([int]$P)
    $holders = @(docker ps --filter "publish=$P" --format "{{.Names}}" 2>$null |
                 Where-Object { $_ -and $_.Trim() -ne "" })
    if ($holders.Count -eq 0) { return $true }
    $allFreed = $true
    foreach ($h in $holders) {
        $h = $h.Trim()
        if ($Force -or $h -like "pg1000*") {
            Write-Host ("   port {0}: stopping container '{1}'" -f $P, $h) -ForegroundColor Yellow
            docker rm -f $h 2>$null | Out-Null
        } else {
            Write-Host ("   port {0} is held by container '{1}'" -f $P, $h) -ForegroundColor Red
            Write-Host ("     docker rm -f {0}" -f $h)
            Write-Host  "     or re-run with -Force to stop it automatically"
            $allFreed = $false
        }
    }
    return $allFreed
}

function Sql {
    param([string]$Query)
    return (docker exec $Name psql -U book -d pg1000 -tAX -c $Query 2>$null | Out-String).Trim()
}

Write-Host ""
Write-Host "PostgreSQL: 1,000 Examples - practice image acceptance test" -ForegroundColor Cyan
Write-Host ("Image: {0}" -f $Image)
Write-Host ("=" * 70)

# --- start clean -----------------------------------------------------------
docker rm -f $Name 2>$null | Out-Null

if (-not $Local) {
    Write-Host ""
    Write-Host ">> removing the local copy and pulling from Docker Hub"
    Write-Host "   (this is the point: test what readers download, not your build)"
    docker rmi $Image 2>$null | Out-Null
    docker pull $Image
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: could not pull the image." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host ">> checking the ports are free"
$portsOk = (FreePort $PgPort) -and (FreePort $JupyterPort)
if (-not $portsOk) {
    Write-Host ""
    Write-Host "Ports are in use. Free them, or re-run with -Force." -ForegroundColor Red
    exit 1
}

Write-Host ">> starting the container as the docs tell a reader to"
docker run -d --name $Name -p "${JupyterPort}:8888" -p "${PgPort}:5432" $Image | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "FAILED: the container would not start." -ForegroundColor Red
    Write-Host "No container holds the ports, so something on Windows itself does."
    Write-Host "A locally installed PostgreSQL service is the usual cause."
    Write-Host ""
    Write-Host "  See what:   netstat -ano | findstr :$PgPort"
    Write-Host "  Then:       Get-Process -Id <PID>"
    Write-Host ""
    Write-Host "Either stop that service, or publish elsewhere:"
    Write-Host "  .\test_image.ps1 -PgPort 5433"
    exit 1
}

Write-Host ">> waiting for PostgreSQL"
$ready = $false
foreach ($i in 1..90) {
    docker exec $Name pg_isready -U book -d pg1000 -q 2>$null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
CheckTrue "PostgreSQL accepts connections" $ready
if (-not $ready) {
    Write-Host ""
    Write-Host "Container log:" -ForegroundColor Yellow
    docker logs $Name
    exit 1
}

# --- the database ----------------------------------------------------------
Write-Host ""
Write-Host "The database" -ForegroundColor Cyan
Check "collation (C, or text sorts wrong)" (Sql "SELECT datcollate FROM pg_database WHERE datname = current_database()") "C"
Check "encoding" (Sql "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database()") "UTF8"
Check "ecommerce.order_items" (Sql "SELECT count(*) FROM ecommerce.order_items") "14998"
Check "ecommerce.orders"      (Sql "SELECT count(*) FROM ecommerce.orders")      "5000"
Check "ecommerce.customers"   (Sql "SELECT count(*) FROM ecommerce.customers")   "804"
Check "hr.employees"          (Sql "SELECT count(*) FROM hr.employees")          "1200"
Check "hr.departments"        (Sql "SELECT count(*) FROM hr.departments")        "26"

$ext = [int](Sql "SELECT count(*) FROM pg_extension")
CheckTrue "extensions installed" ($ext -ge 8) ("{0} present" -f $ext)

# --- the settings that decide execution plans ------------------------------
Write-Host ""
Write-Host "Settings the printed plans depend on" -ForegroundColor Cyan
Check "max_parallel_workers_per_gather" (Sql "SELECT setting FROM pg_settings WHERE name = 'max_parallel_workers_per_gather'") "0"
Check "jit"                             (Sql "SELECT setting FROM pg_settings WHERE name = 'jit'") "off"
Check "work_mem (kB)"                   (Sql "SELECT setting FROM pg_settings WHERE name = 'work_mem'") "4096"
Check "default_statistics_target"       (Sql "SELECT setting FROM pg_settings WHERE name = 'default_statistics_target'") "1000"
Check "DateStyle"                       (Sql "SELECT setting FROM pg_settings WHERE name = 'DateStyle'") "ISO, YMD"
Check "TimeZone"                        (Sql "SELECT setting FROM pg_settings WHERE name = 'TimeZone'") "UTC"

# --- connecting from outside, which is what every GUI client does ----------
# Going out to host.docker.internal and back in through the published port
# makes the connection arrive from the Docker bridge, exactly as pgAdmin's
# would. Connecting to 127.0.0.1 inside the container would match a different
# pg_hba rule and prove nothing.
Write-Host ""
Write-Host "Connecting the way pgAdmin / DBeaver do" -ForegroundColor Cyan
$ok = (docker exec -e PGPASSWORD=book $Name psql -h host.docker.internal -p $PgPort -U book -d pg1000 -tAX -c "SELECT 1" 2>$null | Out-String).Trim()
CheckTrue "external TCP with the documented password" ($ok -eq "1") $(if ($ok -eq "1") { "connected" } else { "REFUSED" })

docker exec -e PGPASSWORD=definitely-wrong $Name psql -h host.docker.internal -p $PgPort -U book -d pg1000 -tAX -c "SELECT 1" 2>$null | Out-Null
CheckTrue "external TCP rejects a wrong password" ($LASTEXITCODE -ne 0)

# --- JupyterLab and the notebooks -----------------------------------------
Write-Host ""
Write-Host "JupyterLab and the notebooks" -ForegroundColor Cyan
$jup = $false
foreach ($i in 1..45) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$JupyterPort/api" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) { $jup = $true; break }
    } catch { Start-Sleep -Seconds 2 }
}
CheckTrue ("JupyterLab answers on :" + $JupyterPort) $jup

$nb = (docker exec $Name sh -c "ls /practice/*/*.ipynb 2>/dev/null | wc -l" | Out-String).Trim()
Check "chapter notebooks in /practice" $nb $ExpectedNotebooks

docker exec $Name test -f /practice/START-HERE.md
CheckTrue "START-HERE.md present" ($LASTEXITCODE -eq 0)

docker exec $Name test -d /practice/_chapter-index
CheckTrue "chapter index present" ($LASTEXITCODE -eq 0)

docker exec $Name sh -c "test -x /usr/local/bin/load-large-dataset"
CheckTrue "load-large-dataset is runnable" ($LASTEXITCODE -eq 0)

# The notebooks must be problems, not answers. Every %%sql cell should be the
# empty prompt; anything else means solutions were published.
$prompts = (docker exec $Name sh -c "grep -rho 'Your answer here' --include='*.ipynb' /practice | wc -l" | Out-String).Trim()
Check "empty answer prompts (no solutions)" $prompts "1000"

# --- the book's own verifier ----------------------------------------------
Write-Host ""
Write-Host "The book's environment check" -ForegroundColor Cyan
$verify = (docker exec $Name python3 /opt/verify_env.py | Out-String)
CheckTrue "verify_env.py reports PASS" ($verify -match "PASS") ""
if ($verify -notmatch "PASS") { Write-Host $verify -ForegroundColor Yellow }

# --- a real query from the book -------------------------------------------
# Example 291 joins orders to customers. If collation, data and settings are
# all right, this returns the same first row the book prints.
Write-Host ""
Write-Host "A query from the book" -ForegroundColor Cyan
$q = Sql "SELECT o.order_id || '|' || c.country FROM ecommerce.orders o JOIN ecommerce.customers c ON c.customer_id = o.customer_id ORDER BY o.order_id LIMIT 1"
Check "example 291, first row" $q "1|United States"

# --- summary ---------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 70)
if ($script:Fail -eq 0) {
    Write-Host ("ALL {0} CHECKS PASSED - the image is good to publish." -f $script:Pass) -ForegroundColor Green
} else {
    Write-Host ("{0} passed, {1} FAILED - see the [BAD] lines above." -f $script:Pass, $script:Fail) -ForegroundColor Red
}
Write-Host ""

if ($Keep) {
    Write-Host "Container left running as '$Name'."
    Write-Host ("  Browse:  http://localhost:{0}/lab" -f $JupyterPort)
    Write-Host "  psql:    docker exec -it $Name psql -U book -d pg1000"
    Write-Host "  Stop:    docker rm -f $Name"
} else {
    Write-Host "Removing the test container (use -Keep to leave it running)."
    docker rm -f $Name | Out-Null
}

if ($script:Fail -gt 0) { exit 1 }

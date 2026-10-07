# ---------------------------------------------------------------------------
# Replace the companion repository's contents with a new release zip.
#
#   .\UPDATE_COMPANION.ps1 -Zip C:\Downloads\postgresql-1000-examples-companion.zip
#
# Why a script rather than "extract over the folder": extracting never
# deletes. The 1.1 release moves every notebook from notebooks\16-joins.ipynb
# to notebooks\16-joins\16-joins.ipynb, so extracting on top leaves BOTH --
# and the image would then ship 53 folders and 53 loose duplicates. The same
# mistake is what produced 1,086 examples from a 1,000-example book earlier.
#
# This wipes the working tree (keeping .git), unpacks the new release, and
# lets git work out what was added, changed and removed.
# ---------------------------------------------------------------------------
param(
    [Parameter(Mandatory = $true)][string]$Zip,
    [string]$Remote = "postgresql-1000-examples"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    Write-Host "Run this from inside the companion repository." -ForegroundColor Red
    Write-Host "There is no .git folder here, so this is not it."
    exit 1
}
if (-not (Test-Path $Zip)) {
    Write-Host "Zip not found: $Zip" -ForegroundColor Red
    exit 1
}

# Confirm we are pointed at the repository we think we are. A wrong remote is
# how the first push ended up at the old repository.
$origin = (git remote get-url origin 2>$null)
Write-Host ""
Write-Host "Repository: $origin" -ForegroundColor Cyan
if ($origin -notlike "*$Remote*") {
    Write-Host "That does not look like '$Remote'." -ForegroundColor Yellow
    $go = Read-Host "Continue anyway? (y/N)"
    if ($go -ne "y") { exit 1 }
}

# Anything uncommitted would be destroyed by the wipe below.
$dirty = git status --porcelain
if ($dirty) {
    Write-Host ""
    Write-Host "You have uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    Write-Host "Commit or stash them first - this script replaces the working tree." -ForegroundColor Yellow
    exit 1
}

# --- unpack to a scratch folder first, so a bad zip cannot leave the repo
# --- half-emptied
$tmp = Join-Path $env:TEMP ("pg1000-release-" + [guid]::NewGuid().ToString("N").Substring(0,8))
New-Item -ItemType Directory -Path $tmp | Out-Null
Write-Host ">> unpacking the release"
Expand-Archive -Path $Zip -DestinationPath $tmp -Force

# The zip contains one top-level folder; its contents are what we want.
$inner = Get-ChildItem $tmp -Directory
if ($inner.Count -ne 1) {
    Write-Host "Expected one folder inside the zip, found $($inner.Count)." -ForegroundColor Red
    Remove-Item $tmp -Recurse -Force
    exit 1
}
$src = $inner[0].FullName
$newCount = (Get-ChildItem $src -Recurse -File).Count
Write-Host "   $newCount files in the release"

# --- replace --------------------------------------------------------------
Write-Host ">> clearing the working tree (keeping .git)"
Get-ChildItem -Force | Where-Object { $_.Name -ne ".git" } |
    Remove-Item -Recurse -Force

Write-Host ">> copying the release in"
Copy-Item -Path (Join-Path $src "*") -Destination . -Recurse -Force
Remove-Item $tmp -Recurse -Force

# --- show what changed ----------------------------------------------------
Write-Host ""
Write-Host "What git sees:" -ForegroundColor Cyan
git add -A
$added    = (git diff --cached --name-only --diff-filter=A | Measure-Object).Count
$modified = (git diff --cached --name-only --diff-filter=M | Measure-Object).Count
$deleted  = (git diff --cached --name-only --diff-filter=D | Measure-Object).Count
Write-Host ("  added    {0}" -f $added)
Write-Host ("  modified {0}" -f $modified)
Write-Host ("  deleted  {0}" -f $deleted)

$nb = (Get-ChildItem notebooks -Recurse -Filter *.ipynb | Measure-Object).Count
Write-Host ""
if ($nb -eq 53) {
    Write-Host "  53 notebooks, one per chapter." -ForegroundColor Green
} else {
    Write-Host "  $nb notebooks - expected 53. Stop and check before pushing." -ForegroundColor Red
}

$loose = (Get-ChildItem notebooks -Filter *.ipynb -File | Measure-Object).Count
if ($loose -gt 0) {
    Write-Host "  $loose loose notebooks left at the top level - these are stale." -ForegroundColor Red
} else {
    Write-Host "  No loose notebooks: every one is in its chapter folder." -ForegroundColor Green
}

Write-Host ""
$go = Read-Host "Commit and push? (y/N)"
if ($go -ne "y") {
    Write-Host "Staged but not committed. 'git status' to review, 'git reset' to undo."
    exit 0
}

git commit -m "Release 1.1: chapter folders, Part VIII dataset check, external connection fix"
git push
Write-Host ""
Write-Host "Pushed. Now publish the image:" -ForegroundColor Cyan
Write-Host "  git tag v1.1"
Write-Host "  git push origin v1.1"

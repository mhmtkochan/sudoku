# Builds the portable Windows exe (desktop/dist/Sudoku-<version>-portable.exe).
#
#   powershell -ExecutionPolicy Bypass -File desktop\build.ps1
#
# Steps: copies web/index.html into the app, stages the sources into an
# ASCII-only work folder (Windows build tools break on non-ASCII paths),
# runs npm install + electron-builder there and copies the exe back.
param(
    [string]$WorkDir = (Join-Path $env:LOCALAPPDATA 'sudoku-desktop-build')
)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$repo = Split-Path $here

# 1) Game file
$game = Join-Path $repo 'web\index.html'
if (-not (Test-Path $game)) { throw "Missing $game (run web\build.ps1 first)" }
New-Item -ItemType Directory -Force (Join-Path $here 'app') | Out-Null
Copy-Item $game (Join-Path $here 'app\index.html') -Force

# 2) Icon
if (-not (Test-Path (Join-Path $here 'assets\icon.ico'))) { & (Join-Path $here 'make-icon.ps1') }

# 3) Stage into ASCII work folder (node_modules is kept between builds)
New-Item -ItemType Directory -Force $WorkDir | Out-Null
foreach ($d in 'app', 'assets', 'dist') {
    $p = Join-Path $WorkDir $d
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
Copy-Item (Join-Path $here 'package.json') $WorkDir -Force
Copy-Item (Join-Path $here 'main.js') $WorkDir -Force
$lock = Join-Path $here 'package-lock.json'
if (Test-Path $lock) { Copy-Item $lock $WorkDir -Force }
Copy-Item (Join-Path $here 'app') $WorkDir -Recurse -Force
Copy-Item (Join-Path $here 'assets') $WorkDir -Recurse -Force

# 4) Build (unsigned)
$env:CSC_IDENTITY_AUTO_DISCOVERY = 'false'
Push-Location $WorkDir
try {
    npm install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'npm install failed' }
    npm run dist
    if ($LASTEXITCODE -ne 0) { throw 'electron-builder failed' }
} finally { Pop-Location }

# 5) Copy result back
$out = Join-Path $here 'dist'
New-Item -ItemType Directory -Force $out | Out-Null
$exe = Get-ChildItem (Join-Path $WorkDir 'dist') -Filter '*-portable.exe' | Select-Object -First 1
if (-not $exe) { throw 'No portable exe produced' }
Copy-Item $exe.FullName $out -Force
Write-Host ("Done: {0} ({1:N1} MB)" -f (Join-Path $out $exe.Name), ($exe.Length / 1MB))

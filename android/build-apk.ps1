# Builds the Sudoku Android app: signed release APK (for direct install) and signed AAB (for Google Play).
#   powershell -ExecutionPolicy Bypass -File .\build-apk.ps1            # APK + AAB  ->  .\dist\
#   powershell -ExecutionPolicy Bypass -File .\build-apk.ps1 -Refresh   # first copy the latest index.html from the web game folder
#   powershell -ExecutionPolicy Bypass -File .\build-apk.ps1 -DebugOnly # quick debug APK only
#
# The Android Gradle plugin refuses project paths with non-ASCII characters (this folder is under "Masa..st.."),
# so the project is mirrored to an ASCII path (%LOCALAPPDATA%\Android\build\sudoku) and built there.
# Only the results are copied back to .\dist. This also keeps build intermediates out of OneDrive.
param(
  [switch]$Refresh,
  [switch]$DebugOnly,
  [string]$GameSource = "C:\Users\azor0\OneDrive\Masa$([char]0x00FC)st$([char]0x00FC)\Mehmet\Claude oyunlar\sudoku\index.html"
)
$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot
Set-Location $proj
$base  = Join-Path $env:LOCALAPPDATA "Android"
$sdk   = Join-Path $base "Sdk"
$stage = Join-Path $base "build\sudoku"

if (-not (Test-Path "$sdk\platforms\android-36\android.jar") -or -not (Test-Path "$base\jdk-17\bin\java.exe")) {
  Write-Host "Build tools are missing. Run: powershell -ExecutionPolicy Bypass -File .\tools\install-tools.ps1 -AcceptLicenses"
  exit 1
}
$env:JAVA_HOME = "$base\jdk-17"
$env:ANDROID_HOME = $sdk
$env:ANDROID_SDK_ROOT = $sdk
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# game: web\index.html is the copy that gets packed into the app
if ($Refresh) {
  if (Test-Path $GameSource) { Copy-Item $GameSource "$proj\web\index.html" -Force; Write-Host "Game refreshed from: $GameSource" }
  else { Write-Host "Game source not found, using existing web\index.html: $GameSource" }
}
Copy-Item "$proj\web\index.html" "$proj\app\src\main\assets\index.html" -Force

$ver = ([regex]::Match((Get-Content "$proj\app\build.gradle.kts" -Raw), 'versionName\s*=\s*"([^"]+)"')).Groups[1].Value
$tasks = if ($DebugOnly) { @("assembleDebug") } else { @("assembleRelease", "bundleRelease") }
if (-not $DebugOnly -and -not (Test-Path "$proj\signing\keystore.properties")) { Write-Host "signing\keystore.properties is missing: release build cannot be signed."; exit 1 }

# mirror the project to the ASCII build folder (build caches there are kept between runs)
New-Item -ItemType Directory -Force -Path $stage | Out-Null
robocopy $proj $stage /MIR /XD build .gradle dist .git .idea tools /XF local.properties /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Write-Host "Could not copy the project to $stage"; exit 1 }
[System.IO.File]::WriteAllText("$stage\local.properties", ("sdk.dir=" + ($sdk -replace '\\', '\\')) + "`n", (New-Object System.Text.UTF8Encoding($false)))

Push-Location $stage
cmd /c ".\gradlew.bat $($tasks -join ' ') --no-daemon --console=plain 2>&1"
$code = $LASTEXITCODE
Pop-Location
if ($code -ne 0) { Write-Host "BUILD FAILED"; exit 1 }

New-Item -ItemType Directory -Force -Path "$proj\dist" | Out-Null
if ($DebugOnly) {
  Copy-Item "$stage\app\build\outputs\apk\debug\app-debug.apk" "$proj\dist\sudoku-$ver-debug.apk" -Force
} else {
  Copy-Item "$stage\app\build\outputs\apk\release\app-release.apk" "$proj\dist\sudoku-$ver.apk" -Force
  Copy-Item "$stage\app\build\outputs\bundle\release\app-release.aab" "$proj\dist\sudoku-$ver.aab" -Force
}
Write-Host ""
Write-Host "Done. Output:"
Get-ChildItem "$proj\dist" | Where-Object { $_.Name -like "sudoku-$ver*" } | ForEach-Object { "  {0}  ({1:N1} MB)" -f $_.FullName, ($_.Length / 1MB) }

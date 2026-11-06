# Boots the test phone (Android 16 emulator, AVD "sudoku_test"), installs dist\sudoku-<version>.apk and launches it.
#   powershell -ExecutionPolicy Bypass -File .\tools\run-emulator.ps1
# One-time setup (about 2 GB): the emulator package, the android-36 google_apis x86_64 system image and the AVD were installed with:
#   sdkmanager "emulator" "system-images;android-36;google_apis;x86_64"
#   avdmanager create avd -n sudoku_test -k "system-images;android-36;google_apis;x86_64" -d pixel_6
param([string]$Apk)
$ErrorActionPreference = "Continue"
$proj = Split-Path $PSScriptRoot -Parent
$base = Join-Path $env:LOCALAPPDATA "Android"
$sdk  = Join-Path $base "Sdk"
$adb  = "$sdk\platform-tools\adb.exe"
$env:ANDROID_AVD_HOME = "$base\avd"; $env:ANDROID_SDK_ROOT = $sdk; $env:ANDROID_HOME = $sdk

if (-not $Apk) { $Apk = (Get-ChildItem "$proj\dist\sudoku-*.apk" | Where-Object { $_.Name -notlike '*debug*' } | Sort-Object LastWriteTime | Select-Object -Last 1).FullName }
if (-not $Apk -or -not (Test-Path $Apk)) { Write-Host "No APK found in dist. Run build-apk.ps1 first."; exit 1 }
if (-not (Test-Path "$sdk\emulator\emulator.exe") -or -not (Test-Path "$base\avd\sudoku_test.avd")) { Write-Host "Emulator or AVD missing (see the comment at the top of this script)."; exit 1 }

# adb has trouble with non-ASCII paths: install from a temp copy
$tmp = Join-Path $env:TEMP "sudoku-test.apk"
Copy-Item $Apk $tmp -Force

& $adb start-server 2>&1 | Out-Null
$running = [bool](& $adb devices 2>$null | Select-String 'emulator-\d+\s+device')
if (-not $running) {
  Start-Process -FilePath "$sdk\emulator\emulator.exe" -ArgumentList "-avd sudoku_test -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect" -WindowStyle Normal
  $t0 = Get-Date
  while (((Get-Date) - $t0).TotalSeconds -lt 300) {
    Start-Sleep -Seconds 5
    if (& $adb devices 2>$null | Select-String 'emulator-\d+\s+device') {
      if ((& $adb shell getprop sys.boot_completed 2>$null).Trim() -eq "1") { $running = $true; break }
    }
  }
}
if (-not $running) { Write-Host "Emulator did not boot in time."; exit 1 }
Write-Host ("Installing: " + (& $adb install -r $tmp 2>&1))
& $adb shell am start -n com.sudokuoyunu.app/.MainActivity | Out-Null
Write-Host "Launched. To close the emulator: adb emu kill"

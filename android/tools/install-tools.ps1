# Installs the Android build toolchain under %LOCALAPPDATA%\Android (no admin needed):
#   JDK 17 (Temurin), Android command-line tools, SDK platform 36 + build-tools 36.0.0 + platform-tools, Gradle 8.13.
# Usage: powershell -ExecutionPolicy Bypass -File .\tools\install-tools.ps1 [-AcceptLicenses]
# -AcceptLicenses means you accept the Android SDK License Agreement: https://developer.android.com/studio/terms
param([switch]$AcceptLicenses)
# Native tools (java, sdkmanager) write normal output to stderr, so errors are checked explicitly instead of via "Stop".
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$base = Join-Path $env:LOCALAPPDATA "Android"
$sdk  = Join-Path $base "Sdk"
$dl   = Join-Path $env:TEMP "sudoku-android-dl"
New-Item -ItemType Directory -Force -Path $dl, $base, $sdk | Out-Null

function Get-File($url, $out) {
  if (Test-Path $out) { "already downloaded: $out"; return }
  Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -ErrorAction Stop
  "downloaded: {0} ({1:N0} MB)" -f $out, ((Get-Item $out).Length / 1MB)
}
function Unzip($zip, $dest) {
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  tar -xf $zip -C $dest
  if ($LASTEXITCODE -ne 0) { throw "extract failed: $zip" }
}

# 1) JDK 17 (Temurin)
if (-not (Test-Path "$base\jdk-17\bin\java.exe")) {
  $z = "$dl\jdk17.zip"
  Get-File "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse" $z
  Unzip $z "$dl\jdk-x"
  $inner = Get-ChildItem "$dl\jdk-x" -Directory | Select-Object -First 1
  if (Test-Path "$base\jdk-17") { Remove-Item "$base\jdk-17" -Recurse -Force }
  Move-Item $inner.FullName "$base\jdk-17"
}
if (-not (Test-Path "$base\jdk-17\bin\java.exe")) { throw "JDK install failed" }
"JDK ready"

# 2) Android command-line tools
if (-not (Test-Path "$sdk\cmdline-tools\latest\bin\sdkmanager.bat")) {
  $z = "$dl\cmdline-tools.zip"
  Get-File "https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip" $z
  Unzip $z "$dl\cmd-x"
  New-Item -ItemType Directory -Force -Path "$sdk\cmdline-tools" | Out-Null
  if (Test-Path "$sdk\cmdline-tools\latest") { Remove-Item "$sdk\cmdline-tools\latest" -Recurse -Force }
  Move-Item "$dl\cmd-x\cmdline-tools" "$sdk\cmdline-tools\latest"
}
if (-not (Test-Path "$sdk\cmdline-tools\latest\bin\sdkmanager.bat")) { throw "command-line tools install failed" }
"command-line tools ready"

# 3) SDK packages
$env:JAVA_HOME = "$base\jdk-17"
$sm = "$sdk\cmdline-tools\latest\bin\sdkmanager.bat"
if ($AcceptLicenses) {
  # "y" answers are read from a file (piping from PowerShell does not reach sdkmanager's prompt)
  $yes = Join-Path $dl "yes.txt"
  [System.IO.File]::WriteAllText($yes, (("y" + [Environment]::NewLine) * 60), (New-Object System.Text.ASCIIEncoding))
  cmd /c "`"$sm`" --sdk_root=`"$sdk`" --licenses < `"$yes`" > nul 2>&1"
}
& $sm "--sdk_root=$sdk" "platform-tools" "platforms;android-36" "build-tools;36.0.0"
foreach ($p in 'platforms\android-36\android.jar', 'build-tools\36.0.0\aapt2.exe', 'platform-tools\adb.exe') {
  if (-not (Test-Path "$sdk\$p")) { throw "SDK package missing: $p (were the licenses accepted? re-run with -AcceptLicenses)" }
}
"SDK packages ready"

# 4) Gradle 8.13 (only used once to generate the project's wrapper)
if (-not (Test-Path "$base\gradle-8.13\bin\gradle.bat")) {
  $z = "$dl\gradle.zip"
  Get-File "https://services.gradle.org/distributions/gradle-8.13-bin.zip" $z
  Unzip $z "$dl\gradle-x"
  if (Test-Path "$base\gradle-8.13") { Remove-Item "$base\gradle-8.13" -Recurse -Force }
  Move-Item "$dl\gradle-x\gradle-8.13" "$base\gradle-8.13"
}
"Gradle ready"
"ALL DONE"

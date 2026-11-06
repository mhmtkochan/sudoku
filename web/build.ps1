# Sudoku oyununu kaynaklardan yeniden derler.
#   kullanım (bu klasörde):  powershell -ExecutionPolicy Bypass -File .\build.ps1
#   isteğe bağlı:            ... -File .\build.ps1 -Palettes     (önce palet tablosunu palettes_gen.py ile yeniden üretir)
#
# Girdi : template.html (oyunun kaynağı), sudoku_puzzles.json (120 bulmaca), palettes_gen.py (palet üretici + kontrast ölçümü)
# Çıktı : index.html           oyun, tek dosya (çift tıklayıp açılır)
#         tamamla-ornek.html   son 8 hücre boş kalmış örnek bölüm
#         sudoku-oyunu.artifact.html   claude.ai Artifact'ına yayınlanan sürüm (html/head/body sarmalayıcısı yok)
param([switch]$Palettes)
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
Set-Location $here
$utf8 = New-Object System.Text.UTF8Encoding($false)

$tpl = Get-Content "template.html" -Raw -Encoding UTF8

if ($Palettes) {
  # palet tablosunu yeniden üret ve şablondaki PALETTES bloğuyla değiştir; kontrast raporunu göster
  python palettes_gen.py
  $new = (Get-Content "palettes.js.txt" -Raw -Encoding UTF8).Replace("`r`n", "`n")   # Python Windows'ta CRLF yazar; şablon LF kullanır
  $a = $tpl.IndexOf("const PALETTES = ["); $b = $tpl.IndexOf("const PKEY")
  if ($a -lt 0 -or $b -lt 0) { throw "template.html içinde PALETTES bloğu bulunamadı" }
  $tpl = $tpl.Substring(0, $a) + $new + $tpl.Substring($b)
  [System.IO.File]::WriteAllText("$here\template.html", $tpl, $utf8)
}

# 1) oyun: bulmacalar sayfanın içine gömülür
$json = Get-Content "sudoku_puzzles.json" -Raw -Encoding UTF8 | ConvertFrom-Json | ConvertTo-Json -Depth 6 -Compress
$main = $tpl.Replace("/*PUZZLES_JSON*/", $json)
[System.IO.File]::WriteAllText("$here\index.html", $main, $utf8)

# 2) Tamamla örneği: ayrı kayıt anahtarı kullanır, oyun ilerlemesine dokunmaz
$demo = $main.Replace('"sudoku-bolumler-v1"', '"sudoku-tamamla-ornek"').Replace('<title>Sudoku</title>', '<title>Sudoku - Tamamla örneği</title>')
$boot = @'
// ---- ÖRNEK: son 8 hücre boş kalmış bölüm; "Tamamla"ya basıp animasyonu izle. Sayfayı yenileyince tekrar başlar. ----
save = freshSave(); persist();
startLevel(2, "home");
(() => { const e = emptyCells(); e.slice(0, e.length - 8).forEach(i => { G.vals[i] = G.sol[i]; }); G.seconds = 95; renderGame(); })();
toast("Örnek: son 8 hücre kaldı. Tamamla'ya bas.");
'@
$marker = "renderHome();`n</script>"
if (-not $demo.Contains($marker)) { throw "Örnek için yerleştirme noktası bulunamadı" }
$demo = $demo.Replace($marker, "renderHome();`n" + $boot + "`n</script>")
[System.IO.File]::WriteAllText("$here\tamamla-ornek.html", $demo, $utf8)

# 3) Artifact sürümü: <html>/<head>/<body> yok; başlık + stil + içerik + betik. Güvenli alan dolgusunu pencere kendisi ekler.
$m  = [regex]::Match($main, '(?s)<title>.*?</title>.*?</style>')
$bd = [regex]::Match($main, '(?s)<body>\s*(.*)</body>')
if (-not $m.Success -or -not $bd.Success) { throw "Artifact sürümü için sayfa ayrıştırılamadı" }
$head = $m.Value.Replace('<title>Sudoku</title>', '<title>Sudoku Oyunu</title>')
$head = $head.Replace('--shadow:0 8px 28px rgba(0,0,0,.5);', '--shadow:0 8px 28px rgba(0,0,0,.5);color-scheme:dark;')
$head = $head.Replace('padding:0 16px;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}', 'padding:0 16px}')
[System.IO.File]::WriteAllText("$here\sudoku-oyunu.artifact.html", ($head + "`n" + $bd.Groups[1].Value), $utf8)

"Derlendi:"
Get-Item index.html, tamamla-ornek.html, sudoku-oyunu.artifact.html | ForEach-Object { "  {0}  ({1:N0} bayt)" -f $_.Name, $_.Length }

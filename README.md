# Sudoku

Tarayıcıda çalışan tek dosyalık bir Sudoku oyunu ve bu oyunu WebView ile saran Android uygulaması.

## Klasörler

- `web/` : Oyunun kaynağı. `template.html` asıl düzenlenen dosya; `build.ps1` bulmacaları (`sudoku_puzzles.json`) gömerek tek dosyalık `index.html` üretir. Python betikleri bulmaca üretimi/doğrulaması içindir. Ayrıntılar: [web/README.md](web/README.md)
- `android/` : Java/Gradle Android projesi (WebView sarmalayıcı). `android/web/index.html` uygulamaya paketlenen oyun kopyasıdır; derleme sırasında `app/src/main/assets/index.html` içine kopyalanır. `store/` Play Store görsellerini içerir. Ayrıntılar: [android/README.md](android/README.md)

## Güncelleme akışı

1. `web/template.html` dosyasını düzenle.
2. `web/build.ps1` çalıştır -> `web/index.html` üretilir.
3. `android/build-apk.ps1 -Refresh` çalıştır -> güncel `index.html` Android projesine kopyalanır ve APK/AAB derlenir.

Not: `build-apk.ps1` içindeki `-GameSource` parametresinin varsayılanı bu repodaki `web/` klasörünü değil, bilgisayardaki orijinal yerel web klasörünü gösterir. Bu repodan derlerken `-GameSource` ile bu repodaki `web\index.html` dosyasının tam yolunu ver.

## Repoda olmayanlar

İmzalama anahtarı ve parolaları (`android/signing/`), derleme çıktıları (`dist/`, `build/`, APK/AAB) ve `local.properties` bilerek repoya eklenmemiştir. Yayın derlemesi için kendi keystore dosyanı `android/signing/` altına koyman gerekir.

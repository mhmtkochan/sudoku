# Sudoku (Android)

120 bölümlü Sudoku oyununun Android uygulaması. Oyun tek bir `index.html` dosyasıdır ve uygulamanın içine gömülür. Uygulama sade bir WebView sarmalayıcısıdır.

- **Uygulama kimliği:** `com.sudokuoyunu.app`. Play'e ilk yüklemeden sonra **değiştirilemez**. Farklı bir kimlik istiyorsan yüklemeden önce değiştir (`app/build.gradle.kts` içinde `namespace` ve `applicationId`, `app/src/main/java/` altındaki klasör adları ve `MainActivity.java` içindeki `package`).
- **Hedef:** `targetSdk 36` (Android 16, Google Play'in 31 Ağustos 2026'dan beri istediği seviye), `minSdk 26` (Android 8).
- **İzinler:** hiç yok. Bilerek `INTERNET` izni verilmedi. Oyun tamamen cihazda çalışır, hiçbir veri dışarı çıkmaz.

## Derlemek

```
powershell -ExecutionPolicy Bypass -File .\build-apk.ps1
```

Çıktılar `dist\` klasörüne gelir:

| Dosya | Ne için |
|---|---|
| `sudoku-<sürüm>.apk` | Doğrudan telefona kurmak için (imzalı) |
| `sudoku-<sürüm>.aab` | **Google Play'e yüklenecek dosya** (imzalı) |

Seçenekler: `-Refresh` oyunun güncel `index.html`'ini web klasöründen alıp derler, `-DebugOnly` hızlı bir test APK'sı üretir.

## Oyunu güncellemek

1. Web oyununu (`Claude oyunlar\sudoku`) güncelle ve oradaki `build.ps1`'i çalıştır, `index.html` yenilenir.
2. Bu klasörde `app/build.gradle.kts` içinde `versionCode`'u **1 artır** (Play her yüklemede daha büyük bir sayı ister), gerekirse `versionName`'i de değiştir.
3. `build-apk.ps1 -Refresh` ile derle, yeni `.aab`'yi Play'e yükle.

## İmza anahtarı (çok önemli)

`signing\sudoku-upload.jks` ve parolası `signing\keystore.properties` içinde. **Bu iki dosyayı güvenli bir yere yedekle** (ör. parola yöneticisi). Anahtarı kaybedersen Play'e güncelleme yükleyemezsin; kurtarmak için Play desteğine başvurman gerekir.

Play Console'da **Play Uygulama İmzalama**'yı (varsayılan) kullan: bu anahtar yalnızca "yükleme anahtarı" olur, kullanıcıya giden uygulamayı Google kendi anahtarıyla imzalar. Bu klasör `.gitignore` ile imza dosyalarını depoya sokmaz.

## Klasör yapısı

| Yol | Ne |
|---|---|
| `web/index.html` | Uygulamaya gömülen oyun kopyası |
| `app/src/main/java/.../MainActivity.java` | WebView sarmalayıcısı: tam ekran, tema rengiyle uyumlu sistem çubukları, geri hareketi, dışarıya kapalı ağ |
| `app/src/main/assets/native-bridge.js` | Sayfa yüklenince çalışır: sistem çubuğu rengini sayfa zeminiyle eşitler, geri tuşunu oyunun akışına bağlar |
| `app/src/main/res/` | Simge, tema, ad |
| `store/` | Play Store görselleri: `play-icon-512.png`, `feature-graphic-1024x500.png` ve `screenshots/` (Android 16 emülatöründen alınmış 5 gerçek ekran görüntüsü, 1080×2160) |
| `tools/install-tools.ps1` | JDK 17, Android SDK 36 ve Gradle'ı kullanıcı klasörüne (`%LOCALAPPDATA%\Android`) kurar |
| `tools/run-emulator.ps1` | Test telefonunu (Android 16 emülatörü) açar, `dist` içindeki APK'yı kurar ve başlatır |
| `build-apk.ps1` | Tek komutla derleme |

> **Neden `AppData` altında derleniyor?** Android derleme eklentisi, yolunda Türkçe karakter olan (`Masaüstü`) projelerde hata verir. `build-apk.ps1` projeyi `%LOCALAPPDATA%\Android\build\sudoku` klasörüne yansıtıp orada derler, sonuçları `dist\` içine geri kopyalar. Bu klasör ara dosyalarla OneDrive'ı da doldurmaz.

## Test edildi

APK, Android 16 (API 36) emülatöründe kuruldu ve gerçek dokunuşlarla denendi: açılış, oyun, tema ve palet, kenardan kenara düzen ve sistem çubuğu rengi, geri tuşu (yardım → oyun → ana menü → çıkış), uygulama kapatılıp açılınca ilerleme ve temanın korunması, "Nasıl Oynanır" simülasyonu. Çökme yok. Gerçek bir telefonda da denemen iyi olur.

> Telefona doğrudan APK kuracaksan: Play'e yüklediğin sürümü Google kendi anahtarıyla imzalar, o yüzden telefona elle kurduğun APK'yı Play sürümüne geçmeden önce kaldırman gerekir.

## Google Play'e yüklerken

1. Play Console geliştirici hesabı (tek seferlik 25 dolar).
2. Yeni uygulama oluştur, `dist\sudoku-<sürüm>.aab`'yi yükle.
3. Mağaza girişi: ad, kısa ve uzun açıklama, `store\play-icon-512.png`, `store\feature-graphic-1024x500.png` ve **en az 2 telefon ekran görüntüsü** (gerçek cihazdan almak en iyisi).
4. Zorunlu formlar: içerik derecelendirme anketi, hedef kitle, Veri güvenliği (uygulama hiçbir veri toplamıyor ve paylaşmıyor), gizlilik politikası bağlantısı.
5. Kişisel geliştirici hesaplarında yayına çıkmadan önce kapalı test şartı olabilir; Play Console hesabın için neyin gerektiğini gösterir.

# Sudoku – Windows masaüstü (Electron)

Oyunun tek dosyalık HTML sürümünü ([`web/index.html`](../web/index.html)) Electron ile saran,
kurulum gerektirmeyen **taşınabilir (portable) tek .exe**.

## Özellikler

- 480×860 dikey pencere (yeniden boyutlandırılabilir, en küçük 380×680), menü çubuğu yok
- `contextIsolation`, `sandbox` açık, `nodeIntegration` kapalı; geliştirici araçları kapalı
- Ağ erişimi yok: `file://` dışındaki tüm istekler engellenir, dış bağlantılar ve sayfa dışına gezinme açılmaz
- İlerleme `localStorage` içinde, Electron'un kullanıcı veri klasöründe (`%APPDATA%\Sudoku`) saklanır

## Dosyalar

| Dosya | Açıklama |
|---|---|
| `main.js` | Electron ana süreci (pencere, güvenlik ayarları) |
| `package.json` | Sürüm, bağımlılıklar ve `electron-builder` ayarları (`portable`, x64) |
| `assets/icon.ico` | 16–256 px çok boyutlu simge (`make-icon.ps1` ile `android/store/play-icon-512.png`'den üretilir) |
| `build.ps1` | Derleme betiği |
| `app/` | Derlemede `web/index.html` buraya kopyalanır (repoda yok) |

## Derleme

Gerekenler: Node.js (npm dahil).

```powershell
powershell -ExecutionPolicy Bypass -File desktop\build.ps1
```

Betik `web/index.html` dosyasını `app/` içine kopyalar, kaynakları ASCII bir çalışma klasörüne
(`%LOCALAPPDATA%\sudoku-desktop-build`, Windows araçları Türkçe karakterli yollarda sorun çıkarabildiği için)
aktarır, `npm install` + `electron-builder` çalıştırır ve sonucu `desktop/dist/Sudoku-1.0.0-portable.exe` olarak bırakır.

Geliştirme sırasında hızlıca denemek için (önce `build.ps1` bir kez çalışmış olmalı, `app/index.html` gerekir):

```powershell
cd desktop; npm install; npm start
```

Exe **imzasızdır**; Windows SmartScreen ilk açılışta uyarı gösterebilir ("Ek bilgi" > "Yine de çalıştır").

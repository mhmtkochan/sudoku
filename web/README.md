# Sudoku

120 bölümlü sudoku oyunu: 4 seviye (Kolay, Orta, Zor, Efsanevi) × 30 bölüm, 4 renk paleti (Mavi, Adaçayı, Gri-mavi, Sıcak kum), açık/koyu tema, kenar notları, ipucu, "Tamamla".

- **Oyun:** `index.html` dosyasına çift tıkla. Tek dosyadır, internet gerekmez.
- **Claude Artifact:** https://claude.ai/artifact/MunLhLYjtmwAV3n9BsSev3 (özel; paylaşmak için sayfanın Paylaş menüsünü kullan). Son yayınlanan sürüm: 7.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| `index.html` | Oyun. `build.ps1` üretir, elle düzenleme. |
| `template.html` | Oyunun **düzenlenebilir kaynağı** (HTML + CSS + JS). Değişiklikleri buraya yap. |
| `sudoku_puzzles.json` | 120 bulmaca (`easy`/`medium`/`hard`/`legendary`, her biri `id`, `puzzle`, `solution`, `clues`). |
| `generate.py` | Bulmaca üretici: tek çözümlü bulmaca üretir ve tekniğe göre zorluk derecelendirir. |
| `verify.py` | `sudoku_puzzles.json` doğrulama: 30'ar adet, tek çözüm, geçerli çözüm, seviye eşleşmesi. |
| `palettes_gen.py` | Renk paletlerini üretir ve WCAG kontrastını ölçer. Palet renkleri `SPEC` içinde. |
| `build.ps1` | `template.html` + bulmacalar → `index.html`, `tamamla-ornek.html`, `sudoku-oyunu.artifact.html`. |
| `tamamla-ornek.html` | Son 8 hücre boş kalmış örnek bölüm. Kendi kaydını kullanır, oyun ilerlemesine dokunmaz. |
| `sudoku-oyunu.artifact.html` | Claude Artifact'ına yayınlanan sürüm (html/head/body sarmalayıcısı yok). |
| `tamamla-ani.jpg` | Tamamla animasyonundan bir kare. |

## Değişiklik yapmak

1. `template.html`'i düzenle.
2. Derle (bu klasörde):
   ```
   powershell -ExecutionPolicy Bypass -File .\build.ps1
   ```
3. Palet renklerini değiştirdiysen `palettes_gen.py` içindeki `SPEC`'i düzenle ve şöyle derle. Kontrast raporu da yazdırılır (hedef 4,5:1; koyu temada seçili hücre içinde girilen rakam 3,2:1):
   ```
   powershell -ExecutionPolicy Bypass -File .\build.ps1 -Palettes
   ```
4. Yeni bulmaca üretmek için: `python generate.py`, sonra `python verify.py`. `sudoku_puzzles.json` oluşur, ardından yine `build.ps1`.
5. Artifact'ı güncellemek için Claude'a "sudoku-oyunu.artifact.html'i Artifact'a yayınla" demen yeterli.

## Oyun kuralları ve ayarlar (`template.html`)

- Hata hakkı: Kolay 3, Orta 4, Zor 5, Efsanevi 6 (`DIFFS`). Hata olursa bölüm baştan başlar.
- İpucu: bölüm başına 3 (`MAX_HINTS`). "Tamamla": son 8 boş hücrede çıkar (`COMPLETE_AT`).
- Yanlış rakam girildiği anda hata sayılır ve silinene kadar kırmızı kalır. Aynı yanlış rakama tekrar basmak da hata sayılır.
- "Nasıl Oynanır", tek bir 3×3 kutuyla tıklayarak öğreten bir simülasyon: hücre seç, rakam yaz, bilerek yanlış yaz ve hatayı gör, Sil, İpucu, Not (gerçekten çizilir), Tamamla. Ana menüden ve oyun başlığındaki ? düğmesinden açılır. Adımlar `template.html` içindeki `U_STEPS` dizisinde; her adımda yalnızca o adımın istediği yere dokunulabilir. Hata hakları ve ipucu sayısı koddaki değerlerden gelir. İlk açılana kadar ana menü butonunda "Yeni" etiketi görünür.
- İlerleme tarayıcının `localStorage`'ında: `sudoku-bolumler-v1` (kayıt), `sudoku-tema`, `sudoku-palet`, `sudoku-yardim` (yardım görüldü mü).

## Yapılacaklar

- **Yıldız algoritması:** `calcStars()` şimdilik her zaman 3 döndürüyor. Hata, ipucu ve süreye göre yıldız verilecek.
- Arka plan görselleri (araştırılıyor).
- Zorluk dengesi: bölümleri oynayarak kontrol et; Efsanevi seviye "mantık tekniklerimin çözemediği" bulmacalar demek.

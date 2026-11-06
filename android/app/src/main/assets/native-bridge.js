// APK sarmalayıcısı: sayfa yüklenince çalıştırılır. Oyunun kendi kodunu değiştirmez, yalnızca ona bağlanır.
(function () {
  if (window.__nativeBridgeReady) return;
  window.__nativeBridgeReady = true;

  // 1) Sistem çubuğu rengi, sayfanın zemin rengiyle (tema ve palete göre değişir) aynı olsun
  function pageBg() {
    var c = getComputedStyle(document.body).backgroundColor;
    var m = c.match(/\d+(\.\d+)?/g) || [0, 0, 0];
    var rgb = m.slice(0, 3).map(function (n) { return Math.max(0, Math.min(255, Math.round(+n))); });
    var hex = '#' + rgb.map(function (n) { return ('0' + n.toString(16)).slice(-2); }).join('');
    var lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255;
    return {hex: hex, light: lum > 0.5};
  }
  var last = '';
  function sync() {
    try {
      var b = pageBg();
      if (b.hex === last) return;
      last = b.hex;
      window.SudokuNative && window.SudokuNative.setBars(b.hex, b.light);
    } catch (e) {}
  }
  new MutationObserver(sync).observe(document.documentElement, {attributes: true, attributeFilter: ['style', 'data-theme']});
  sync();
  setTimeout(sync, 300);

  // 2) Geri tuşu: sırasıyla açık pencereyi kapat, oyundan çık, bölümler/yardım ekranından menüye dön.
  //    true dönerse geri hareketi oyun içinde işlenmiştir; false dönerse uygulamadan çıkılır.
  window.__nativeBack = function () {
    try {
      if (!document.getElementById('modal').hidden) { closeModal(); return true; }
      if (current === 'game') { if (!(G && G.busy)) leaveGame(); return true; }
      if (current === 'levels') { renderHome(); show('home'); return true; }
      if (current === 'help') { closeHelp(); return true; }
    } catch (e) {}
    return false;
  };
})();

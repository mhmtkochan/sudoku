'use strict';

// Sudoku - Windows masaustu sarmalayicisi (Electron).
// Oyunun kendisi app/index.html icindedir (build.ps1 web/index.html'den kopyalar).
// Ag erisimi yok, menu yok, dis baglantilar engellenir; ilerleme localStorage'da
// (Electron'un varsayilan userData klasorunde) saklanir.

const { app, BrowserWindow, Menu, session, nativeTheme } = require('electron');
const path = require('path');

const isDev = !app.isPackaged;

// Tek kopya: ikinci kez acilirsa mevcut pencereyi one getir.
if (!app.requestSingleInstanceLock()) {
  app.quit();
}

let win = null;

function createWindow() {
  win = new BrowserWindow({
    title: 'Sudoku',
    width: 480,
    height: 860,
    minWidth: 380,
    minHeight: 680,
    center: true,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: nativeTheme.shouldUseDarkColors ? '#12151c' : '#f4f1ea',
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      devTools: isDev,
      spellcheck: false
    }
  });

  // Sayfa basligi degisse bile pencere basligi "Sudoku" kalsin.
  win.on('page-title-updated', (e) => e.preventDefault());

  // Yeni pencere / dis baglanti acmayi engelle.
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));

  // Oyun sayfasindan baska bir yere gitmeyi engelle.
  const startUrl = require('url').pathToFileURL(path.join(__dirname, 'app', 'index.html')).href;
  win.webContents.on('will-navigate', (e, url) => {
    if (url !== startUrl) e.preventDefault();
  });
  win.webContents.on('will-redirect', (e) => e.preventDefault());

  // Uretimde gelistirici araclari kisayollarini da kapat.
  if (!isDev) {
    win.webContents.on('before-input-event', (e, input) => {
      const k = (input.key || '').toLowerCase();
      if (k === 'f12' || ((input.control || input.meta) && input.shift && (k === 'i' || k === 'j' || k === 'c'))) {
        e.preventDefault();
      }
    });
  }

  win.once('ready-to-show', () => win.show());
  win.on('closed', () => { win = null; });

  win.loadFile(path.join(__dirname, 'app', 'index.html'));
}

app.on('second-instance', () => {
  if (win) {
    if (win.isMinimized()) win.restore();
    win.focus();
  }
});

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);

  // Oyun tamamen cevrimdisi: file:// disindaki tum istekleri engelle.
  session.defaultSession.webRequest.onBeforeRequest((details, cb) => {
    const u = details.url;
    const ok = u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:') || u.startsWith('devtools:');
    cb({ cancel: !ok });
  });

  // Hicbir izin (kamera, mikrofon, bildirim vb.) verilmez.
  session.defaultSession.setPermissionRequestHandler((wc, perm, cb) => cb(false));

  createWindow();
});

app.on('window-all-closed', () => app.quit());

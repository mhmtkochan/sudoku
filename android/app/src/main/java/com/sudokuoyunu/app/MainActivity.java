package com.sudokuoyunu.app;

import android.annotation.SuppressLint;
import android.content.pm.ApplicationInfo;
import android.content.res.Configuration;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.FrameLayout;

import androidx.activity.ComponentActivity;
import androidx.activity.OnBackPressedCallback;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewClientCompat;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/**
 * Sudoku oyununu (assets/index.html) tam ekran bir WebView içinde çalıştırır.
 * - Oyun https://appassets.androidplatform.net/assets/index.html adresinden sunulur (localStorage kalıcı olur).
 * - Dış ağa hiçbir istek gönderilmez; INTERNET izni de yoktur.
 * - Sistem çubuklarının rengi sayfanın zeminiyle senkronlanır, geri tuşu oyunun kendi geri akışını izler.
 */
public class MainActivity extends ComponentActivity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + HOST + "/assets/index.html";

    private FrameLayout root;
    private WebView web;
    private String bridgeJs = "";

    @SuppressLint({"SetJavaScriptEnabled", "ClickableViewAccessibility"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);   // kenardan kenara; boşlukları aşağıda kendimiz bırakıyoruz

        boolean night = (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK)
                == Configuration.UI_MODE_NIGHT_YES;
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor(night ? "#161C1A" : "#F4F1EA"));

        web = new WebView(this);
        web.setBackgroundColor(Color.TRANSPARENT);
        root.addView(web, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        // Sistem çubuklarının ve çentiğin altında kalmasın: boşluk kadar iç dolgu ver
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, insets) -> {
            Insets bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            return WindowInsetsCompat.CONSUMED;
        });

        if ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            WebView.setWebContentsDebuggingEnabled(true);
        }

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // ilerleme, tema ve palet localStorage'da tutulur
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setTextZoom(100);                    // sistem yazı boyutu tahta düzenini bozmasın
        s.setMediaPlaybackRequiresUserGesture(true);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setLongClickable(false);
        web.setOnLongClickListener(v -> true);
        web.setHapticFeedbackEnabled(false);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web.setWebViewClient(new WebViewClientCompat() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (HOST.equals(request.getUrl().getHost())) {
                    return loader.shouldInterceptRequest(request.getUrl());
                }
                // oyun dışarıdan hiçbir şey istemez; gelenleri boş cevapla engelle
                return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return true;                   // sayfadan dışarı gezinmeyi engelle
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                if (!bridgeJs.isEmpty()) view.evaluateJavascript(bridgeJs, null);
            }
        });

        web.addJavascriptInterface(new Bridge(), "SudokuNative");
        bridgeJs = readAsset("native-bridge.js");

        // Geri hareketi: önce oyunun kendi akışı (modal kapat / bölümden çık / menüye dön), ana menüdeyse uygulamadan çık
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                web.evaluateJavascript("(window.__nativeBack ? window.__nativeBack() : false)", value -> {
                    if (!"true".equals(value)) {
                        setEnabled(false);
                        MainActivity.this.getOnBackPressedDispatcher().onBackPressed();
                    }
                });
            }
        });

        web.loadUrl(START_URL);
    }

    /** Sayfadaki betikten çağrılır: sistem çubuğu rengini sayfa zeminiyle aynı yapar. */
    private final class Bridge {
        @JavascriptInterface
        public void setBars(String hexColor, boolean lightBackground) {
            runOnUiThread(() -> {
                try {
                    root.setBackgroundColor(Color.parseColor(hexColor));
                } catch (IllegalArgumentException ignored) {
                    return;
                }
                WindowInsetsControllerCompat c = WindowCompat.getInsetsController(getWindow(), root);
                c.setAppearanceLightStatusBars(lightBackground);
                c.setAppearanceLightNavigationBars(lightBackground);
            });
        }
    }

    private String readAsset(String name) {
        try (InputStream in = getAssets().open(name); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return out.toString(StandardCharsets.UTF_8.name());
        } catch (IOException e) {
            return "";
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            root.removeView(web);
            web.destroy();
        }
        super.onDestroy();
    }
}

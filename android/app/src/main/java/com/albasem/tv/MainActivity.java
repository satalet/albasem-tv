package com.albasem.tv;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView myWebView;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // وضع الشاشة الكاملة المغمورة للـ TV
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        );

        myWebView = new WebView(this);
        setContentView(myWebView);

        WebSettings settings = myWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // السماح بتدفقات البث المختلفة دون حظر
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }

        // دعم أسهم الريموت كونترول (D-Pad)
        myWebView.setFocusable(true);
        myWebView.setFocusableInTouchMode(true);
        myWebView.requestFocus();

        myWebView.setWebViewClient(new WebViewClient());
        myWebView.setWebChromeClient(new WebChromeClient());

        // تحميل المنصة
        myWebView.loadUrl("https://satalet.github.io/albasem-tv/index.html");
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // زر الرجوع في الريموت
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            if (myWebView.canGoBack()) {
                myWebView.goBack();
                return true;
            }
        }
        return super.onKeyDown(keyCode, event);
    }
}

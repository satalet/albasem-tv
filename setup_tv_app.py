import os

# 1. إنشاء المجلدات المطلوبة للتطبيق والـ CI/CD
paths = [
    ".github/workflows",
    "android/app/src/main/java/com/albasem/tv",
    "android/app/src/main/res/values",
    "android/app/src/main/res/drawable"
]
for p in paths:
    os.makedirs(p, exist_ok=True)

# 2. ملف workflow لبناء الـ APK في غيت هاب تلقائياً
workflow_content = """name: Build Android TV APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: 8.5

      - name: Build Debug APK
        run: |
          cd android
          gradle assembleDebug

      - name: Publish APK to GitHub Releases
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cp android/app/build/outputs/apk/debug/app-debug.apk albasem-tv.apk
          gh release create v1.0 albasem-tv.apk --title "Albasem TV App v1.0" --notes "تطبيق الباسم سات المخصص لشاشات أندرويد و TV Box و Firestick" --clobber
"""
with open(".github/workflows/build-tv-apk.yml", "w", encoding="utf-8") as f:
    f.write(workflow_content)

# 3. إعدادات Gradle الرئيسية
with open("android/settings.gradle", "w", encoding="utf-8") as f:
    f.write("include ':app'\nrootProject.name = 'AlbasemTV'\n")

root_build_gradle = """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.2'
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
"""
with open("android/build.gradle", "w", encoding="utf-8") as f:
    f.write(root_build_gradle)

with open("android/gradle.properties", "w", encoding="utf-8") as f:
    f.write("org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\nandroid.useAndroidX=true\n")

# 4. إعدادات تطبيق الـ App
app_build_gradle = """plugins {
    id 'com.android.application'
}

android {
    namespace 'com.albasem.tv'
    compileSdk 34

    defaultConfig {
        applicationId "com.albasem.tv"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        debug {
            minifyEnabled false
        }
        release {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
"""
with open("android/app/build.gradle", "w", encoding="utf-8") as f:
    f.write(app_build_gradle)

# 5. ملف البيان (AndroidManifest) لدعم Android TV وريموت التحكم
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- تعريف التوافق مع شاشات التلفزيون وأجهزة الاستقبال -->
    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />
    <uses-feature android:name="android.software.leanback" android:required="false" />

    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:icon="@drawable/banner"
        android:banner="@drawable/banner"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen"
        android:hardwareAccelerated="true"
        android:usesCleartextTraffic="true">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout"
            android:screenOrientation="landscape">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
with open("android/app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
    f.write(manifest_content)

# 6. الموارد الثابتة (أيقونة الشاشة واسم التطبيق)
with open("android/app/src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
    f.write('<resources><string name="app_name">الباسم سات</string></resources>\n')

banner_svg = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="320dp"
    android:height="180dp"
    android:viewportWidth="320"
    android:viewportHeight="180">
    <path
        android:fillColor="#0B132B"
        android:pathData="M0,0h320v180h-320z"/>
    <path
        android:fillColor="#1C2541"
        android:pathData="M16,16h288v148h-288z"/>
    <path
        android:fillColor="#48CAE4"
        android:pathData="M160,50 L195,115 L125,115 Z"/>
</vector>
"""
with open("android/app/src/main/res/drawable/banner.xml", "w", encoding="utf-8") as f:
    f.write(banner_svg)

# 7. كود MainActivity: متصفح شاشة مخصص لتشغيل البث والتحكم بالريموت
main_activity_code = """package com.albasem.tv;

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
"""
with open("android/app/src/main/java/com/albasem/tv/MainActivity.java", "w", encoding="utf-8") as f:
    f.write(main_activity_code)

print("✅ تم تجهيز مشروع تطبيق الأندرويد وإعدادات البناء التلقائي بنجاح!")

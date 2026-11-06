import java.util.Properties

plugins {
    id("com.android.application")
}

// signing/keystore.properties varsa release derlemesi onunla imzalanır (Play'e yüklenecek AAB için gerekli)
val keystoreProps = Properties().apply {
    val f = rootProject.file("signing/keystore.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}

android {
    namespace = "com.sudokuoyunu.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.sudokuoyunu.app"
        minSdk = 26
        targetSdk = 36          // Google Play: yeni uygulamalar ve güncellemeler için en az 36
        versionCode = 1
        versionName = "1.0.0"
    }

    signingConfigs {
        if (keystoreProps.isNotEmpty()) {
            create("release") {
                storeFile = rootProject.file(keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false   // kendi kodumuz birkaç yüz satır; küçültmeye gerek yok
            if (keystoreProps.isNotEmpty()) signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.webkit:webkit:1.14.0")       // WebViewAssetLoader: oyunu güvenli bir https adresinden sunar, localStorage kalıcı olur
    implementation("androidx.activity:activity:1.11.0")   // geri hareketi (predictive back) için OnBackPressedDispatcher
    implementation("androidx.core:core:1.17.0")           // kenardan kenara ekran ve sistem çubuğu denetimi
}

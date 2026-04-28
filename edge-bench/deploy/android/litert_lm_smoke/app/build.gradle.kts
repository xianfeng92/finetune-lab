plugins {
    id("com.android.application")
}

android {
    namespace = "ai.finetunelab.edgebench.litertlm"
    compileSdk = 35

    defaultConfig {
        applicationId = "ai.finetunelab.edgebench.litertlm"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
    }

    packaging {
        jniLibs {
            useLegacyPackaging = true
        }
    }
}

dependencies {
    implementation("com.google.ai.edge.litertlm:litertlm-android:0.10.2")
}

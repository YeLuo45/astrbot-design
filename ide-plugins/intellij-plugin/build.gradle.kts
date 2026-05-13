plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.22"
    id("org.jetbrains.intellij") version "1.17.4"
}

group = "com.astrbot"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.google.code.gson:gson:2.10.1")
}

kotlin {
    jvmToolchain(17)
}

intellij {
    pluginName.set("AstrBot Buddy")
    version.set("2024.1")
    type.set("IC")
}

tasks {
    patchPluginXml {
        pluginDescription.set("""
            AstrBot Buddy - IntelliJ Plugin for AstrBot Development
            Provides status panel, plugin template generation, and debug integration.
        """.trimIndent())
        sinceBuild.set("231")
        untilBuild.set("241.*")
    }

    runIde {
        headless.set(false)
    }
}

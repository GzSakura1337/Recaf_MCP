plugins {
    id("java")
}

group = "com.zinja"
version = "0.1.0"

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(25))
    }
}

val recafJar = listOfNotNull(
    System.getenv("RECAF_JAR")?.takeIf { it.isNotBlank() }?.let(::file),
    rootProject.file("libs/recaf.jar"),
    rootProject.file("../recaf/recaf.jar")
).firstOrNull { it.exists() }
    ?: error("Missing Recaf jar. Set RECAF_JAR or place recaf.jar at libs/recaf.jar.")

dependencies {
    compileOnly(files(recafJar))
    compileOnly("jakarta.enterprise:jakarta.enterprise.cdi-api:4.0.1")
    compileOnly("jakarta.inject:jakarta.inject-api:2.0.1")
    compileOnly("org.ow2.asm:asm:9.7")
    compileOnly("org.ow2.asm:asm-tree:9.7")
    compileOnly("com.google.code.gson:gson:2.10.1")
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release.set(25)
}

tasks.jar {
    archiveBaseName.set("recaf-mcp-plugin")
}

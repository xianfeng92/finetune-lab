# LiteRT-LM Android Smoke

Minimal Android app for W3 LiteRT-LM base-only smoke.

This demo intentionally uses the official base `.litertlm` bundle, not the
fused finetune-lab LoRA. Its role is to prove the Android AAR path:

```text
Gradle dependency -> APK install -> model push -> Activity -> LiteRT-LM Engine -> first response
```

## Inputs

- A running Android ARM64 emulator or device.
- Official base model:
  `gemma-4-E2B-it.litertlm`
- Maven dependency:
  `com.google.ai.edge.litertlm:litertlm-android:0.10.2`

The dependency shape follows the official LiteRT-LM Android guide. The version
is pinned from Google Maven metadata on 2026-04-28.

## Run

```bash
edge-bench/deploy/android/litert_lm_smoke/run_smoke.sh
```

Override model or serial:

```bash
ANDROID_SERIAL=emulator-5554 \
LITERTLM_MODEL=/path/to/gemma-4-E2B-it.litertlm \
edge-bench/deploy/android/litert_lm_smoke/run_smoke.sh
```

The script writes logs under:

```text
outputs/edge-bench/android/litert-lm-smoke/
```

## Current Pixel 7 Emulator Result

On `Pixel_7_API_35_ARM64`, the AAR integration path reaches:

```text
Gradle assembleDebug: success
adb install: success
.litertlm push: success
Activity launch: success
LiteRT-LM native runtime: SIGILL in liblitertlm_jni.so during Engine.initialize()
```

Observed log signature:

```text
SMOKE_START model=/data/local/tmp/edge-bench/gemma-4-E2B-it.litertlm prompt=What is the capital of France?
Fatal signal 4 (SIGILL), code 1 (ILL_ILLOPC)
liblitertlm_jni.so
Java_com_google_ai_edge_litertlm_LiteRtLmJni_nativeCreateEngine
```

Treat this as an emulator/runtime compatibility limitation. The next useful
validation target is a physical ARM64 device.

## Boundary

This is a base-only Android AAR smoke. It does not claim same-LoRA consistency
with MLX or llama.cpp. Full LoRA export remains a separate follow-up.

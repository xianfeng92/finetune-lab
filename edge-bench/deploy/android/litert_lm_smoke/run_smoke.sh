#!/usr/bin/env bash
# Build, install, and run the LiteRT-LM Android base-only smoke app.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
APP_DIR="${ROOT}/edge-bench/deploy/android/litert_lm_smoke"
OUTPUT_DIR="${ROOT}/outputs/edge-bench/android/litert-lm-smoke"
ANDROID_SERIAL="${ANDROID_SERIAL:-emulator-5554}"
DEVICE_MODEL_PATH="${DEVICE_MODEL_PATH:-/data/local/tmp/edge-bench/gemma-4-E2B-it.litertlm}"
PROMPT="${PROMPT:-}"
DEFAULT_MODEL="${HOME}/.cache/huggingface/hub/models--litert-community--gemma-4-E2B-it-litert-lm/snapshots/d23202ebbc77c976719090aaa080362f29d746e2/gemma-4-E2B-it.litertlm"
LITERTLM_MODEL="${LITERTLM_MODEL:-${DEFAULT_MODEL}}"
GRADLE_BIN="${GRADLE_BIN:-}"

if [ -z "${JAVA_HOME:-}" ] && [ -x "/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/java" ]; then
  export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
fi
if [ -n "${JAVA_HOME:-}" ]; then
  export PATH="${JAVA_HOME}/bin:${PATH}"
fi
export ANDROID_HOME="${ANDROID_HOME:-${HOME}/Library/Android/sdk}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-${ANDROID_HOME}}"
export PATH="${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/emulator:${ANDROID_HOME}/cmdline-tools/latest/bin:${PATH}"

if [ -z "${GRADLE_BIN}" ]; then
  if command -v gradle >/dev/null 2>&1; then
    GRADLE_BIN="$(command -v gradle)"
  else
    GRADLE_BIN="$(find "${HOME}/.gradle/wrapper/dists" -path "*/bin/gradle" -type f | sort -r | head -1)"
  fi
fi

if [ -z "${GRADLE_BIN}" ] || [ ! -x "${GRADLE_BIN}" ]; then
  echo "gradle not found; install Gradle or set GRADLE_BIN" >&2
  exit 2
fi

if [ ! -f "${LITERTLM_MODEL}" ]; then
  echo "LiteRT-LM model not found: ${LITERTLM_MODEL}" >&2
  echo "Fetch it with: litert-lm run --from-huggingface-repo=litert-community/gemma-4-E2B-it-litert-lm gemma-4-E2B-it.litertlm --prompt='hello'" >&2
  exit 2
fi

mkdir -p "${OUTPUT_DIR}"

cd "${APP_DIR}"
printf "sdk.dir=%s\n" "${ANDROID_HOME}" > local.properties
"${GRADLE_BIN}" --no-daemon :app:assembleDebug | tee "${OUTPUT_DIR}/gradle-assemble.log"

adb -s "${ANDROID_SERIAL}" wait-for-device
adb -s "${ANDROID_SERIAL}" shell mkdir -p "$(dirname "${DEVICE_MODEL_PATH}")"
local_model_bytes="$(wc -c < "${LITERTLM_MODEL}" | tr -d ' ')"
device_model_bytes="$(adb -s "${ANDROID_SERIAL}" shell "wc -c '${DEVICE_MODEL_PATH}' 2>/dev/null" | awk '{print $1}' | tr -d '\r' || true)"
if [ "${device_model_bytes}" = "${local_model_bytes}" ]; then
  echo "model already present on device: ${DEVICE_MODEL_PATH} (${device_model_bytes} bytes)"
else
  adb -s "${ANDROID_SERIAL}" push "${LITERTLM_MODEL}" "${DEVICE_MODEL_PATH}"
fi
adb -s "${ANDROID_SERIAL}" install -r app/build/outputs/apk/debug/app-debug.apk | tee "${OUTPUT_DIR}/adb-install.log"
adb -s "${ANDROID_SERIAL}" logcat -c
if [ -n "${PROMPT}" ]; then
  adb -s "${ANDROID_SERIAL}" shell am start \
    -n ai.finetunelab.edgebench.litertlm/.MainActivity \
    --es model_path "${DEVICE_MODEL_PATH}" \
    --es prompt "${PROMPT}" | tee "${OUTPUT_DIR}/am-start.log"
else
  adb -s "${ANDROID_SERIAL}" shell am start \
    -n ai.finetunelab.edgebench.litertlm/.MainActivity \
    --es model_path "${DEVICE_MODEL_PATH}" | tee "${OUTPUT_DIR}/am-start.log"
fi

for _ in $(seq 1 90); do
  adb -s "${ANDROID_SERIAL}" logcat -d -s LiteRTLMEdgeSmoke:I '*:S' > "${OUTPUT_DIR}/logcat.txt"
  adb -s "${ANDROID_SERIAL}" logcat -d \
    | grep -E "LiteRTLMEdgeSmoke|Fatal signal|AndroidRuntime|DEBUG   :|liblitertlm_jni|ai.finetunelab.edgebench.litertlm" \
    > "${OUTPUT_DIR}/logcat-full-filtered.txt" || true
  if grep -q "SMOKE_OK\\|SMOKE_ERROR" "${OUTPUT_DIR}/logcat.txt"; then
    cat "${OUTPUT_DIR}/logcat.txt"
    grep -q "SMOKE_OK" "${OUTPUT_DIR}/logcat.txt"
    exit $?
  fi
  if grep -q "Fatal signal .*liblitertlm_jni\\|liblitertlm_jni.so\\|nativeCreateEngine" "${OUTPUT_DIR}/logcat-full-filtered.txt"; then
    cat "${OUTPUT_DIR}/logcat-full-filtered.txt"
    echo "LiteRT-LM native runtime crashed before SMOKE_OK" >&2
    exit 1
  fi
  sleep 2
done

cat "${OUTPUT_DIR}/logcat.txt"
echo "timed out waiting for LiteRT-LM smoke result" >&2
exit 1

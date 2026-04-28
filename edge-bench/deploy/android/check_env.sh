#!/usr/bin/env bash
# Check local Android readiness for edge-bench W3.
#
# This script is intentionally read-only: it reports SDK / AVD / NDK state and
# suggests the next command, but does not install packages or create devices.

set -uo pipefail

SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"
AVD_ROOT="${ANDROID_AVD_HOME:-$HOME/.android/avd}"

ok() { printf "✅ %s\n" "$*"; }
warn() { printf "⚠️  %s\n" "$*"; }
miss() { printf "❌ %s\n" "$*"; }
info() { printf "• %s\n" "$*"; }

find_bin() {
  local name="$1"
  shift
  local candidate
  for candidate in "$@"; do
    if [ -x "$candidate" ]; then
      printf "%s" "$candidate"
      return 0
    fi
  done
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  return 1
}

print_header() {
  printf "\n== %s ==\n" "$1"
}

print_header "Android SDK"
info "ANDROID_HOME=${ANDROID_HOME:-<unset>}"
info "ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-<unset>}"
info "resolved SDK_ROOT=$SDK_ROOT"
if [ -d "$SDK_ROOT" ]; then
  ok "SDK root exists"
else
  miss "SDK root not found"
fi

ADB="$(find_bin adb "$SDK_ROOT/platform-tools/adb" || true)"
EMULATOR="$(find_bin emulator "$SDK_ROOT/emulator/emulator" || true)"
SDKMANAGER="$(find_bin sdkmanager "$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" "$SDK_ROOT/tools/bin/sdkmanager" || true)"
AVDMANAGER="$(find_bin avdmanager "$SDK_ROOT/cmdline-tools/latest/bin/avdmanager" "$SDK_ROOT/tools/bin/avdmanager" || true)"
NDK_BUILD="$(find_bin ndk-build "$SDK_ROOT/ndk-bundle/ndk-build" "$SDK_ROOT"/ndk/*/ndk-build || true)"
CMAKE_BIN="$(find_bin cmake "$SDK_ROOT"/cmake/*/bin/cmake || true)"
NINJA_BIN="$(find_bin ninja "$SDK_ROOT"/cmake/*/bin/ninja || true)"
JAVA_BIN="$(find_bin java "${JAVA_HOME:-}/bin/java" "/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/java" || true)"

print_header "Tools"
for pair in \
  "adb:$ADB" \
  "emulator:$EMULATOR" \
  "sdkmanager:$SDKMANAGER" \
  "avdmanager:$AVDMANAGER" \
  "ndk-build:$NDK_BUILD" \
  "cmake:$CMAKE_BIN" \
  "ninja:$NINJA_BIN"; do
  name="${pair%%:*}"
  value="${pair#*:}"
  if [ -n "$value" ]; then
    ok "$name -> $value"
  else
    miss "$name not found"
  fi
done

if [ -n "$JAVA_BIN" ]; then
  if "$JAVA_BIN" -version >/tmp/edge-bench-java-version.txt 2>&1; then
    ok "java runtime available"
    info "java -> $JAVA_BIN"
    sed 's/^/  /' /tmp/edge-bench-java-version.txt | sed -n '1,3p'
  else
    miss "java command exists but no runtime is available"
    info "java -> $JAVA_BIN"
    sed 's/^/  /' /tmp/edge-bench-java-version.txt | sed -n '1,3p'
  fi
else
  miss "java not found"
fi

print_header "AVDs"
if [ -n "$EMULATOR" ]; then
  avds="$("$EMULATOR" -list-avds 2>/dev/null || true)"
  if [ -n "$avds" ]; then
    printf "%s\n" "$avds" | sed 's/^/  - /'
  else
    warn "No AVDs found"
  fi
else
  warn "Cannot list AVDs without emulator binary"
fi

pixel7_found=0
fallback_avd_found=0
if [ -d "$AVD_ROOT" ]; then
  for config in "$AVD_ROOT"/*.avd/config.ini; do
    [ -f "$config" ] || continue
    name="$(basename "$(dirname "$config")" .avd)"
    device="$(grep -E '^hw.device.name=' "$config" | cut -d= -f2- || true)"
    display="$(grep -E '^avd.ini.displayname=' "$config" | cut -d= -f2- || true)"
    abi="$(grep -E '^abi.type=' "$config" | cut -d= -f2- || true)"
    target="$(grep -E '^target=' "$config" | cut -d= -f2- || true)"
    ram="$(grep -E '^hw.ramSize=' "$config" | cut -d= -f2- || true)"
    data_size="$(grep -E '^disk.dataPartition.size=' "$config" | cut -d= -f2- || true)"
    image="$(grep -E '^image.sysdir.1=' "$config" | cut -d= -f2- || true)"
    info "$name: display=${display:-unknown}, device=${device:-unknown}, abi=${abi:-unknown}, target=${target:-unknown}, ram=${ram:-unknown}MB, data=${data_size:-unknown}, image=${image:-unknown}"
    if [ "$device" = "pixel_7" ] || [ "$display" = "Pixel 7" ]; then
      pixel7_found=1
    fi
    if [ "$abi" = "arm64-v8a" ]; then
      fallback_avd_found=1
      if [ "${ram:-0}" -lt 8192 ] 2>/dev/null; then
        warn "$name is ARM64 and usable for smoke, but RAM=${ram:-unknown}MB is below the 8192MB target for Q4_K_M GGUF."
      fi
    fi
  done
fi

if [ "$pixel7_found" -eq 1 ]; then
  ok "Pixel 7 AVD found"
else
  warn "Pixel 7 AVD not found"
  if [ "$fallback_avd_found" -eq 1 ]; then
    ok "At least one ARM64 AVD exists; use it as a temporary smoke-test fallback and label results accordingly."
  fi
fi

print_header "System Images"
if [ -d "$SDK_ROOT/system-images" ]; then
  find "$SDK_ROOT/system-images" -maxdepth 4 -type d | sort | sed "s#^$SDK_ROOT/system-images#  - system-images#"
else
  warn "No system-images directory"
fi

print_header "ADB Devices"
if [ -n "$ADB" ]; then
  "$ADB" devices -l 2>&1 | sed 's/^/  /'
else
  warn "Cannot list devices without adb"
fi

print_header "Edge Bench Artifacts"
GGUF="outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf"
if [ -f "$GGUF" ]; then
  ok "$GGUF exists ($(du -h "$GGUF" | awk '{print $1}'))"
else
  warn "$GGUF missing; run the MLX fuse + llama.cpp convert path before Android llama.cpp smoke"
fi

if command -v llama-completion >/dev/null 2>&1; then
  ok "llama-completion -> $(command -v llama-completion)"
else
  warn "llama-completion not found on host"
fi

if command -v litert-lm >/dev/null 2>&1; then
  ok "litert-lm -> $(command -v litert-lm)"
else
  warn "litert-lm not found on host"
fi

print_header "Recommendation"
if [ -z "$SDKMANAGER" ] || [ -z "$AVDMANAGER" ]; then
  warn "Install Android command-line tools so sdkmanager/avdmanager are available."
fi
if [ -z "$NDK_BUILD" ]; then
  warn "Install Android NDK r26+ before llama.cpp Android build."
fi
if [ "$pixel7_found" -eq 0 ]; then
  warn "Create a Pixel 7 ARM64 AVD with 8GB RAM for W3 comparability."
fi
if [ -z "$ADB" ] || [ -z "$EMULATOR" ]; then
  warn "Add platform-tools and emulator to PATH, or export ANDROID_HOME=$SDK_ROOT."
fi
ok "Read-only check complete"

# Deploy On Android Emulator

> W3 目标：把 edge-bench 从 Mac native baseline 推到 Android emulator。当前路径采用 spec path (b)：llama.cpp 负责同一 fused LoRA 的 Android 侧 smoke；LiteRT-LM 先保留 base-only fallback，不声称同一 LoRA 三引擎一致。

## Current Local Audit

本机审计时间：2026-04-28。

已发现：

- Android SDK root: `~/Library/Android/sdk`
- `adb`: `~/Library/Android/sdk/platform-tools/adb`，版本 `37.0.0`
- `emulator`: `~/Library/Android/sdk/emulator/emulator`，版本 `36.5.10.0`
- Android command-line tools: installed at `~/Library/Android/sdk/cmdline-tools/latest`
- NDK: `27.2.12479018`
- CMake: `3.22.1`
- Java runtime: Android Studio JBR, `openjdk 21.0.10`
- 已安装 AVD: `Pixel_Tablet`
- `Pixel_Tablet`: `arm64-v8a`, `android-35`, `google_apis_playstore_tablet`, RAM `8192MB`
- 已安装 system image: `system-images/android-35/google_apis_playstore_tablet/arm64-v8a`
- Mac host tools: `llama-completion`, `litert-lm`

缺口：

- 当前 AVD 是 Pixel Tablet，不是 W3 计划里的 Pixel 7。

结论：你已经有一个可启动的 ARM64 Android emulator 基础，也已经具备 Java / NDK / CMake / command-line tools。它还不是 W3 的目标 Pixel 7 环境，但可以先作为 smoke-test fallback，用来验证 `adb -> push -> shell -> Android ARM64 binary` 这条链路；RAM 已经调到 `8192MB`，可以进入 Q4_K_M GGUF smoke 尝试。W3 的最终 benchmark 口径仍建议创建 Pixel 7 ARM64 AVD，或在所有报告里明确标注 `Pixel Tablet emulator`。

当前设备状态：

- `adb devices -l`: `emulator-5554`, `model:Pixel_Tablet`, `device:emu64a`
- `ro.product.model`: `Pixel Tablet`
- `ro.product.cpu.abi`: `arm64-v8a`
- `ro.build.version.sdk`: `35`
- `/proc/meminfo` total: about `7.9GB`
- `/data` after GGUF + llama.cpp binaries: about `926MB` free

## Can `Pixel_Tablet` Be Used?

可以，但要分层使用：

| 用途 | `Pixel_Tablet` 是否可用 | 说明 |
|---|---:|---|
| `adb devices` / `adb push` / shell smoke | 可以 | 它是 ARM64 AVD，适合先验证 Android 基础链路 |
| Android ARM64 `llama-completion` 二进制能否执行 | 可以 | 不依赖 Pixel 7 机型本身 |
| 加载 3.2GB Q4_K_M GGUF | 可以尝试 | 当前 RAM 已是 `8192MB`，仍需留意 emulator 可用内存和 KV cache |
| 对外 benchmark 数字 | 不建议直接当 Pixel 7 | 它是 tablet profile，需要标注 `Pixel Tablet emulator` |
| W3 最终验收 | 临时可替代，最终建议 Pixel 7 | spec 原口径是 Pixel 7 ARM64 + 8GB RAM |

如果后续配置被 Android Studio 改回低内存，可以再把现有 `Pixel_Tablet` 调成 8GB：

```bash
AVD_CONFIG="$HOME/.android/avd/Pixel_Tablet.avd/config.ini"
/usr/bin/sed -i '' 's/^hw.ramSize=.*/hw.ramSize=8192/' "$AVD_CONFIG"
```

启动时也显式传内存：

```bash
"$ANDROID_HOME/emulator/emulator" -avd Pixel_Tablet \
  -memory 8192 \
  -no-snapshot-load \
  -gpu host
```

## Readiness Check

仓库提供一个只读检查脚本：

```bash
edge-bench/deploy/android/check_env.sh
```

它会检查：

- SDK root / `ANDROID_HOME`
- `adb` / `emulator` / `sdkmanager` / `avdmanager`
- Java runtime
- NDK / CMake / Ninja
- AVD 列表和每个 AVD 的 `device / abi / target / ram / image`
- adb devices
- edge-bench 的 Q4_K_M GGUF 是否已经存在

## Recommended Environment Variables

当前 shell 没有 `ANDROID_HOME`，建议写入 shell profile：

```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/ndk/27.2.12479018:$ANDROID_HOME/cmake/3.22.1/bin:$PATH"
```

重新打开 shell 后验证：

```bash
adb version
emulator -list-avds
```

## Install Missing Android Tooling

如果 Android Studio 已安装，优先在 GUI 里补：

1. 打开 Android Studio。
2. Settings / Preferences -> Languages & Frameworks -> Android SDK。
3. SDK Tools 里安装：
   - Android SDK Command-line Tools
   - Android SDK Platform-Tools
   - Android Emulator
   - NDK (Side by side), r26+
   - CMake

也可以用 command-line tools 完成，但前提是 `sdkmanager` 已经存在：

```bash
sdkmanager --licenses
sdkmanager \
  "platform-tools" \
  "emulator" \
  "platforms;android-35" \
  "system-images;android-35;google_apis;arm64-v8a" \
  "ndk;27.2.12479018" \
  "cmake;3.22.1"
```

Java runtime 缺失时，Android command-line tools 和 Gradle 项目会受影响。推荐安装 Android Studio bundled JBR 或 Temurin JDK 17，然后设置：

```bash
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

## Create Pixel 7 AVD

当前已有 `Pixel_Tablet`，但 W3 benchmark 需要 phone form factor，推荐创建 `Pixel_7_API_35_ARM64`。

Android Studio GUI 路径：

1. Tools -> Device Manager。
2. Create Device。
3. Phone -> Pixel 7。
4. System Image -> API 35 ARM64, Google APIs。
5. Advanced Settings:
   - RAM: `8192 MB`
   - Internal storage: at least `8 GB`
   - Graphics: `Automatic` or `Hardware`
6. Finish。

CLI 路径：

```bash
sdkmanager "system-images;android-35;google_apis;arm64-v8a"
avdmanager create avd \
  --name Pixel_7_API_35_ARM64 \
  --package "system-images;android-35;google_apis;arm64-v8a" \
  --device "pixel_7"
```

把 RAM 调到 8GB：

```bash
AVD_CONFIG="$HOME/.android/avd/Pixel_7_API_35_ARM64.avd/config.ini"
/usr/bin/sed -i '' 's/^hw.ramSize=.*/hw.ramSize=8192/' "$AVD_CONFIG"
```

验证：

```bash
emulator -list-avds
edge-bench/deploy/android/check_env.sh
```

## Start Emulator

```bash
emulator -avd Pixel_7_API_35_ARM64 \
  -memory 8192 \
  -no-snapshot-load \
  -gpu host
```

等待启动：

```bash
adb wait-for-device
adb shell getprop ro.product.model
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.build.version.sdk
adb shell cat /proc/meminfo | head
```

## llama.cpp Android Path

W3 的第一目标不是完整 UI，而是证明 Android emulator 能加载 fused Q4_K_M GGUF 并跑出 first token / smoke result。

输入模型：

```text
outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf
```

当前策略：

1. NDK 构建或获取 Android ARM64 `llama-cli` / `llama-completion`。
2. `adb push` 二进制和 Q4_K_M GGUF 到 `/data/local/tmp/edge-bench/`。
3. 先跑一个 prompt smoke，不跑完整 144-case benchmark。
4. 如果 smoke 稳定，再接 `adb_bridge.py` 或 runner 统一收集 wall time / memory / stdout。

### Pixel Tablet Smoke Result

本机已完成一次 `Pixel_Tablet` fallback smoke。这个结果只证明 Android ARM64 llama.cpp 路径可跑，不替代 Pixel 7 benchmark。

构建源码：

```bash
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git \
  outputs/edge-bench/android/llama.cpp-src
```

当前 clone commit:

```text
f42e29f webui: Server tools (#21237)
```

配置 Android ARM64 build：

```bash
cmake -S outputs/edge-bench/android/llama.cpp-src \
  -B outputs/edge-bench/android/llama.cpp-build-arm64 \
  -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$ANDROID_HOME/ndk/27.2.12479018/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=android-28 \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_OPENMP=OFF \
  -DGGML_METAL=OFF \
  -DLLAMA_CURL=OFF \
  -DLLAMA_BUILD_SERVER=OFF \
  -DLLAMA_BUILD_TESTS=OFF \
  -DLLAMA_BUILD_EXAMPLES=OFF
```

构建 target：

```bash
cmake --build outputs/edge-bench/android/llama.cpp-build-arm64 \
  --target llama-completion \
  -j4
```

需要一起 push `llama-completion` 和 shared libraries：

```bash
adb shell mkdir -p /data/local/tmp/edge-bench
adb push outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/llama-completion /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/libllama-common.so /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/libllama.so /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/libggml.so /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/libggml-cpu.so /data/local/tmp/edge-bench/
adb push outputs/edge-bench/android/llama.cpp-build-arm64/bin/libggml-base.so /data/local/tmp/edge-bench/
adb shell 'chmod +x /data/local/tmp/edge-bench/llama-completion /data/local/tmp/edge-bench/*.so'
```

first-token smoke：

```bash
adb shell 'cd /data/local/tmp/edge-bench && \
  LD_LIBRARY_PATH=. ./llama-completion \
    -m ggml-stage4-Q4_K_M.gguf \
    -p "hello" \
    -n 1 \
    -c 512 \
    -b 64 \
    -ub 32 \
    -t 4 \
    --temp 0 \
    --no-display-prompt \
    -no-cnv'
```

结果：退出码 `0`，模型成功加载并完成 prompt eval / prediction path。`-no-cnv` 必须保留；否则当前 Gemma4 chat template 会触发 `this custom template is not supported, try using --jinja`。

可读短输出 smoke：

```bash
adb shell 'cd /data/local/tmp/edge-bench && \
  LD_LIBRARY_PATH=. ./llama-completion \
    -m ggml-stage4-Q4_K_M.gguf \
    -p "The capital of France is" \
    -n 8 \
    -c 512 \
    -b 64 \
    -ub 32 \
    -t 4 \
    --temp 0 \
    --no-display-prompt \
    -no-cnv'
```

输出包含：

```text
Paris.
```

关键性能片段：

```text
prompt eval time = 99.95 ms / 6 tokens (60.03 tokens per second)
eval time = 54.84 ms / 2 runs (36.47 tokens per second)
total time = 156.18 ms / 8 tokens
Host memory = 3295 MiB
```

### Generic Target Command

后续换成 Pixel 7 AVD 时，可以沿用同一条形状：

```bash
adb shell mkdir -p /data/local/tmp/edge-bench
adb push outputs/edge-bench/fused/stage4-consolidation-fp16/ggml-stage4-Q4_K_M.gguf /data/local/tmp/edge-bench/
adb push path/to/android-arm64/llama-completion /data/local/tmp/edge-bench/
adb shell chmod +x /data/local/tmp/edge-bench/llama-completion
adb shell /data/local/tmp/edge-bench/llama-completion \
  -m /data/local/tmp/edge-bench/ggml-stage4-Q4_K_M.gguf \
  -p "hello" \
  -n 32 \
  --temp 0
```

注意：Mac native probe 使用 HF tokenizer 预先 apply chat template + tools。Android shell smoke 的 first-token-out 可以先用 plain prompt；要做 4 维 PolicyGateway probe，需要把 prompt 文件也预先生成并 push 到设备。

## LiteRT-LM Android Path

当前 LiteRT-LM 只作为 base-only fallback：

- 使用官方 `litert-community/gemma-4-E2B-it-litert-lm`。
- 不声称 fused LoRA 已可转 `.litertlm`。
- emulator 上的 LiteRT-LM 性能只写作“工程可行性 demo”，不作为真实性能基准，因为 emulator 不等价于 Pixel GPU / NNAPI / NPU。

后续如果接 AAR，最小目标是：

1. 建一个最小 Android project。
2. 接入 LiteRT-LM AAR 或官方 Gradle artifact。
3. 加载官方 base-only `.litertlm`。
4. 跑单条 prompt，记录 first-token-out。

## Acceptance

W3 Android 这一步完成的最小验收：

- `edge-bench/deploy/android/check_env.sh` 显示 Pixel 7 AVD 存在。
- Pixel 7 AVD 可启动，`adb devices -l` 显示 `device`。
- Android NDK r26+ 可用。
- llama.cpp Android ARM64 binary 可以在 emulator 上执行。
- Q4_K_M GGUF 可以被 push 到 emulator 并跑出 first token。
- `edge-bench/docs/04-deploy-android-emulator.md` 记录了当前 emulator 限制和 LiteRT-LM base-only fallback 边界。

当前本机已经达到的是“Android SDK + ARM64 tablet emulator + llama.cpp Android ARM64 binary + Q4_K_M GGUF first-token smoke”。还未达到 W3 最终验收的是 Pixel 7 AVD 口径和 LiteRT-LM AAR base-only demo。

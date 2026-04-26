# 2026-04-22 finetune-lab Static Lab Polish Impl Notes

## 背景

在解决 app 内置浏览器 `file://` 空白页之后，`web/dist/index.html` 已经能打开，但首版静态页更像“把交互前端压平成 HTML”，教学叙事和可读性还不够强。

## 本轮改动

- 重写 `web/scripts/export-standalone-html.mjs`
- 把单文件静态页调整为更适合 IAB 阅读的教学型报告布局
- 增加以下内容区块：
  - 顶部 hero snapshot
  - 四段式 workflow rail
  - dataset profile
  - run registry and artifacts
  - probe score matrix
  - case-by-case comparison
  - teaching notes
- 调整视觉语言：
  - 更明确的版面层次
  - 更强的背景氛围和卡片区分
  - 更适合静态浏览的标题、表格和样本卡片
- 保留 `make web-build` 的标准入口，不增加额外手工步骤

## 实际验证

本轮实际跑过：

```bash
make web-build
```

验证结果：

- `web/dist/index.html` 已成功导出
- 生成页中已包含 `Dataset profile`、`Probe score matrix`、`Case-by-case comparison`、`Teaching Notes`
- IAB 可继续直接打开 `file:///Users/xforg/AI_SPACE/finetune-lab/web/dist/index.html`

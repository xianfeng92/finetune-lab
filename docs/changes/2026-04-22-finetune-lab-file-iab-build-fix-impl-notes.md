# 2026-04-22 finetune-lab File IAB Build Fix Impl Notes

## 背景

`web/dist/index.html` 通过 `file://` 在 app 内置浏览器打开时出现空白页。

根因有两层：

- Vite 构建产物默认使用根路径 `/assets/...`，在 `file://` 场景下无法正确解析静态资源
- app 内置浏览器对 `file://` 下的模块脚本执行兼容性不足，导致 React 入口即使修正为相对路径后仍可能不执行
- 前端数据层默认通过 `fetch("/lab-data.json")` 读取聚合数据，对本地文件协议不稳定

## 本轮改动

- 给 `web/vite.config.ts` 增加 `base: "./"`，让构建产物使用相对资源路径
- 扩展 `web/scripts/build-lab-data.mjs`，在生成 `web/public/lab-data.json` 的同时生成 `web/src/generated/lab-data.generated.ts`
- 调整 `web/src/data-layer.ts`
  在 `file://` 场景下直接读取构建时内嵌数据
  在常规页面访问场景下继续请求 `lab-data.json`
- 调整 `web/src/App.tsx`
  增加加载失败错误态，避免再次出现空白页但没有提示
- 新增 `web/scripts/export-standalone-html.mjs`
  在 `make web-build` 末尾导出一个零 JS 依赖的单文件 `web/dist/index.html`
  让 app 内置浏览器直接打开 `file://.../dist/index.html` 时也能显示完整内容

## 实际验证

本轮实际跑过：

```bash
make web-sync-data
make web-build
```

验证结果：

- `web/src/generated/lab-data.generated.ts` 已生成
- `web/dist/index.html` 已导出为单文件静态页，不再依赖模块脚本执行
- 前端生产构建通过

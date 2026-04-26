# 2026-04-22 finetune-lab Rename Impl Notes

## 本轮改动

把项目目录从 `modeltrain/` 重命名为 `finetune-lab/`，并同步收口以下内容：

- 根仓库 `AGENTS.md` 子项目索引
- 项目内 `README.md` / `AGENTS.md` / `project-context.json`
- `Makefile` 里的绝对路径
- 前端品牌名、页面标题、包名
- spec / impl-notes 文件名与标题

## 实际验证

本轮实际跑过：

```bash
make data-demo
make compare-probes
make web-install
make web-build
```

## 结果

- 新目录：`/Users/xforg/AI_SPACE/finetune-lab`
- `web/package-lock.json` 已更新为 `finetune-lab-web`
- 前端构建通过
- 数据与 probe 入口在新目录名下正常工作

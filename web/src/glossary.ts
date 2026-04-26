// 术语表：第一次出现时由 <Term> 组件挂上 hover 解释。
// key 用全小写、空格分隔的"自然名"（lookup 时会 normalize）。

export interface GlossaryEntry {
  short: string;       // 鼠标 hover 时浏览器原生 title 显示的中文释义
  full?: string;       // 详细描述，未来可挂自定义 tooltip
  related?: string[];  // 关联术语 key，方便后续 cross-link
}

export const GLOSSARY: Record<string, GlossaryEntry> = {
  sft: {
    short: "SFT (Supervised Fine-Tuning) — 监督微调：用 (输入, 期望输出) 对让模型学会按特定格式回答。",
  },
  lora: {
    short: "LoRA — 低秩适配。只训一小块权重就能改模型行为，省显存、产物只有几 MB 到几十 MB。",
  },
  mlx: {
    short: "MLX — Apple Silicon 上的本地 LLM 框架，本仓库 real run 都走 mlx-lm.lora。",
  },
  "mlx-lm.lora": {
    short: "mlx-lm.lora — MLX 框架里跑 LoRA 微调的命令行工具。",
  },
  "gemma 4": {
    short: "Gemma 4 — Google 2026-04 发布的开源模型家族（E2B / E4B / 26B / 31B 四档）。",
  },
  e2b: {
    short: "E2B — Gemma 4 的 ~2B 参数变体。本地能跑，作教学主线。",
  },
  e4b: {
    short: "E4B — Gemma 4 的 ~4B 参数变体。比 E2B 强一些，需要更多内存。",
  },
  "-it": {
    short: "-it 后缀 — instruction-tuned，指对话/指令调过的版本（相对 base 而言）。",
  },
  "4bit": {
    short: "4bit — 4 位量化版本，体积约为 fp16 的 1/4，本地推理友好。",
  },
  adapter: {
    short: "adapter — LoRA 训练产出的小权重补丁；不是完整模型，要叠在 base model 上才能用。",
  },
  checkpoint: {
    short: "checkpoint — 模型在某一步训练时的完整权重快照。",
  },
  "base model": {
    short: "base model — 基础模型，没有针对你这个任务调过；对应的另一个常见词是 instruct（已对话调）。",
  },
  "held-out": {
    short: "held-out — 不参与训练、专门留出来评估的样本子集。和 train split 互不相交。",
  },
  probe: {
    short: "probe — 用 held-out 样本去推一遍模型，看输出是否符合预期。这里的指标都是 probe 跑出来的。",
  },
  "smoke train": {
    short: "smoke train — 跑几十步只验证流水线能不能跑通，不在意训练效果。",
  },
  simulated: {
    short: "simulated — 教学占位：脚本写假 loss、假 adapter，不真的更新模型。和 real run 对照看。",
  },
  "real run": {
    short: "real run — 真的调用 mlx-lm.lora 跑出来的 LoRA 训练，会更新真实 adapter 权重。",
  },
  curriculum: {
    short: "curriculum — 课程式训练：把数据按难度分阶段（先单工具、再 reroute、再多工具）依次喂模型。",
  },
  consolidation: {
    short: "consolidation — 课程末尾用所有阶段的混合数据再训一次，对抗「只记住最后一阶段」的遗忘。",
  },
  replay: {
    short: "replay — 后续训练里重新掺入早期阶段的数据，缓解 catastrophic forgetting。",
  },
  "exact name match": {
    short: "exact name match — 模型预测的工具名集合和期望集合完全一致（不多不少）。最严指标。",
  },
  "any hit": {
    short: "any hit — 期望工具至少被命中一个。比 exact 宽松。",
  },
  "parsed json": {
    short: "parsed json — 模型输出能被 JSON parser 解析（结构没坏）。和「内容对不对」是两回事。",
  },
  "tool signal": {
    short: "tool signal — 模型输出里出现了 tool_call 的标记/标签（无论选对没）。",
  },
  "route hit": {
    short: "route hit — 路由对：在多个候选工具里选到了正确的那个。",
  },
  "loss delta": {
    short: "loss delta — 训练第一步到最后一步的 loss 降幅。loss 降很多 ≠ 模型质量好，要交叉看 probe。",
  },
  iter: {
    short: "iter — 训练的迭代步数，和 step 几乎同义；epoch 是把整个 train split 走完一遍。",
  },
  step: {
    short: "step — 一次梯度更新；max_steps = 总训练步数上限。",
  },
  epoch: {
    short: "epoch — 把整个 train split 完整过一遍。",
  },
  "structured output": {
    short: "structured output — 让模型按固定结构（JSON / 字段）输出，而不是自由文本。",
  },
  "tool calling": {
    short: "tool calling — 模型决定要调哪个工具、传什么参数；本仓库 SFT 主要在教这件事。",
  },
  "preference tuning": {
    short: "preference tuning — 用 (chosen, rejected) 成对数据再调一次，让模型更偏向你想要的风格。",
  },
  dpo: {
    short: "DPO — Direct Preference Optimization，preference tuning 的常见做法（不需要 reward model）。",
  },
  "focus metrics": {
    short: "focus metrics — 这一关重点要看的指标；其它指标可以参考但不主导判断。",
  },
  "failure bucket": {
    short: "failure bucket — 失败模式分桶：模型挂在哪种类型的 case 上，比「总分多少」信息更细。",
  },
  artifacts: {
    short: "artifacts — 训练/评估产物文件（adapter 权重、probe 结果、metric 报告等）。",
  },
};

function normalize(key: string): string {
  return key.toLowerCase().trim().replace(/\s+/g, " ");
}

export function lookupTerm(key: string): GlossaryEntry | undefined {
  return GLOSSARY[normalize(key)];
}

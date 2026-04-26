import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(webRoot, "..");

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function readJsonIfExists(filePath, fallback) {
  try {
    return await readJson(filePath);
  } catch {
    return fallback;
  }
}

async function readMarkdownIfExists(filePath) {
  try {
    return await fs.readFile(filePath, "utf8");
  } catch {
    return null;
  }
}

// Minimal YAML frontmatter parser. Handles: scalars, nested objects (one level),
// arrays of strings, quoted strings. We control the producer (governance.py),
// so we don't need a full YAML implementation.
function parseFrontmatter(markdown) {
  if (!markdown.startsWith("---")) return { frontmatter: {}, body: markdown };
  const endIdx = markdown.indexOf("\n---", 3);
  if (endIdx === -1) return { frontmatter: {}, body: markdown };
  const head = markdown.slice(3, endIdx).trim();
  const body = markdown.slice(endIdx + 4).replace(/^\n/, "");
  const frontmatter = {};
  const lines = head.split("\n");
  let currentKey = null;
  let currentMode = null; // 'list' | 'object'
  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, "");
    if (!line.trim()) continue;
    const indent = line.match(/^( *)/)[1].length;
    if (indent === 0) {
      const m = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
      if (!m) continue;
      const [, key, valueRaw] = m;
      currentKey = key;
      const value = valueRaw.trim();
      if (value === "") {
        frontmatter[key] = null;
        currentMode = "pending";
      } else {
        frontmatter[key] = parseScalar(value);
        currentMode = null;
      }
    } else if (currentKey != null) {
      const trimmed = line.trim();
      if (trimmed.startsWith("- ")) {
        if (!Array.isArray(frontmatter[currentKey])) frontmatter[currentKey] = [];
        frontmatter[currentKey].push(parseScalar(trimmed.slice(2)));
        currentMode = "list";
      } else {
        const m = trimmed.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
        if (m) {
          if (!frontmatter[currentKey] || Array.isArray(frontmatter[currentKey])) {
            frontmatter[currentKey] = {};
          }
          frontmatter[currentKey][m[1]] = parseScalar(m[2].trim());
          currentMode = "object";
        }
      }
    }
  }
  return { frontmatter, body };
}

function parseScalar(value) {
  if (value === "true") return true;
  if (value === "false") return false;
  if (value === "null" || value === "") return null;
  if (/^-?\d+$/.test(value)) return Number(value);
  if (/^-?\d+\.\d+$/.test(value)) return Number(value);
  if (/^"(.*)"$/.test(value)) return value.slice(1, -1);
  return value;
}

async function readJsonl(filePath) {
  const raw = await fs.readFile(filePath, "utf8");
  return raw.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

async function readJsonlIfExists(filePath, fallback) {
  try {
    return await readJsonl(filePath);
  } catch {
    return fallback;
  }
}

function countBy(items) {
  const map = new Map();
  for (const item of items) {
    map.set(item, (map.get(item) ?? 0) + 1);
  }
  return [...map.entries()].map(([key, count]) => ({ key, count })).sort((a, b) => b.count - a.count);
}

function sampleCurve(points, maxPoints = 40) {
  if (!points.length || points.length <= maxPoints) return points;
  const stride = (points.length - 1) / (maxPoints - 1);
  const out = [];
  for (let i = 0; i < maxPoints; i += 1) {
    const idx = Math.min(points.length - 1, Math.round(i * stride));
    out.push(points[idx]);
  }
  return out;
}

async function loadTrainingCurve(runDir) {
  const raw = await readJsonlIfExists(path.join(runDir, "train-metrics.jsonl"), []);
  const cleaned = raw
    .filter((row) => typeof row?.step === "number" && typeof row?.loss === "number")
    .map((row) => ({ step: row.step, loss: row.loss }));
  const sampled = sampleCurve(cleaned);
  const firstLoss = cleaned[0]?.loss ?? null;
  const lastLoss = cleaned[cleaned.length - 1]?.loss ?? null;
  const loss_delta_pct = Number.isFinite(firstLoss) && Number.isFinite(lastLoss) && firstLoss !== 0
    ? +(((firstLoss - lastLoss) / firstLoss) * 100).toFixed(1)
    : null;
  return {
    total_steps: cleaned.length,
    first_loss: firstLoss,
    last_loss: lastLoss,
    loss_delta_pct,
    points: sampled,
  };
}

function buildProbeMetrics(probeResults) {
  return {
    total: probeResults.length,
    exactNameMatch: probeResults.filter((row) => row.exact_name_match).length,
    anyExpectedNameHit: probeResults.filter((row) => row.predicted_names.some((name) => row.expected_names.includes(name))).length,
    parsedJson: probeResults.filter((row) => row.parsed_output !== null).length,
    toolSignal: probeResults.filter((row) => row.has_tool_calls_signal).length,
    nonEmptyOutput: probeResults.filter((row) => (row.raw_output || "").trim().length > 0).length,
    schemaEcho: probeResults.filter((row) => row.looks_like_schema_echo).length,
  };
}

async function findManifestsRecursive(rootDir) {
  const found = [];
  async function walk(dir, depth) {
    if (depth > 3) return;
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(full, depth + 1);
      } else if (entry.isFile() && entry.name === "run-manifest.json") {
        found.push(full);
      }
    }
  }
  await walk(rootDir, 0);
  return found;
}

async function getRuns() {
  const outputsDir = path.join(repoRoot, "outputs");
  const manifestPaths = await findManifestsRecursive(outputsDir);
  const runs = [];
  for (const manifestPath of manifestPaths) {
    const runDir = path.dirname(manifestPath);
    const relFromOutputs = path.relative(outputsDir, runDir);
    const segments = relFromOutputs.split(path.sep);
    const family = segments[0];
    const isTopLevel = segments.length === 1;
    const manifest = await readJson(manifestPath);
    if (!isTopLevel) {
      manifest.run_id = `${family}/${manifest.run_id}`;
    }
    manifest.family = family;
    manifest.is_top_level = isTopLevel;
    try {
      const stat = await fs.stat(manifestPath);
      manifest.completed_at = stat.mtime.toISOString();
    } catch {
      manifest.completed_at = null;
    }
    const probeResultsPath = path.join(repoRoot, manifest.probe_results_path);
    const probeResults = await readJsonIfExists(probeResultsPath, []);
    const adapterDir = path.join(repoRoot, manifest.adapter_dir);
    const artifacts = [];
    try {
      for (const entry of await fs.readdir(adapterDir, { withFileTypes: true })) {
        if (!entry.isFile()) continue;
        const absolute = path.join(adapterDir, entry.name);
        const stat = await fs.stat(absolute);
        artifacts.push({
          name: entry.name,
          relative_path: path.relative(repoRoot, absolute),
          size_bytes: stat.size,
        });
      }
    } catch {
      // adapter dir may not exist for simulated runs
    }
    const trainingCurve = await loadTrainingCurve(runDir);
    runs.push({
      manifest,
      probeResults,
      metrics: buildProbeMetrics(probeResults),
      artifacts,
      trainingCurve,
    });
  }
  return runs.sort((a, b) => a.manifest.max_steps - b.manifest.max_steps);
}

function buildRunDelta(allRuns) {
  const runs = allRuns.filter((r) => r.manifest.is_top_level && r.manifest.training_mode !== "simulated");
  if (runs.length < 2) return null;
  const first = runs[0];
  const last = runs[runs.length - 1];
  return {
    baseline: {
      run_id: first.manifest.run_id,
      title: first.manifest.title,
      max_steps: first.manifest.max_steps,
      avg_loss: first.manifest.avg_loss,
      metrics: first.metrics,
    },
    improved: {
      run_id: last.manifest.run_id,
      title: last.manifest.title,
      max_steps: last.manifest.max_steps,
      avg_loss: last.manifest.avg_loss,
      metrics: last.metrics,
    },
    avg_loss_delta: +(first.manifest.avg_loss - last.manifest.avg_loss).toFixed(4),
    avg_loss_delta_pct: first.manifest.avg_loss
      ? +(((first.manifest.avg_loss - last.manifest.avg_loss) / first.manifest.avg_loss) * 100).toFixed(1)
      : null,
    steps_multiplier: first.manifest.max_steps
      ? +(last.manifest.max_steps / first.manifest.max_steps).toFixed(1)
      : null,
    exact_delta: last.metrics.exactNameMatch - first.metrics.exactNameMatch,
    parsed_delta: last.metrics.parsedJson - first.metrics.parsedJson,
    signal_delta: last.metrics.toolSignal - first.metrics.toolSignal,
  };
}

async function loadDatasetCards() {
  const dataRoot = path.join(repoRoot, "data");
  const cards = [];
  async function walk(dir, depth) {
    if (depth > 4) return;
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isFile() && entry.name === "dataset-card.md") {
        const md = await readMarkdownIfExists(full);
        const reportPath = path.join(dir, "redaction-report.md");
        const reportMd = await readMarkdownIfExists(reportPath);
        if (md) {
          const card = parseFrontmatter(md);
          const report = reportMd ? parseFrontmatter(reportMd) : null;
          cards.push({
            dir_relative: path.relative(repoRoot, dir),
            frontmatter: card.frontmatter,
            body: card.body,
            redaction: report
              ? {
                  frontmatter: report.frontmatter,
                  body: report.body,
                }
              : null,
          });
        }
      } else if (entry.isDirectory()) {
        await walk(full, depth + 1);
      }
    }
  }
  await walk(dataRoot, 0);
  cards.sort((a, b) => a.dir_relative.localeCompare(b.dir_relative));
  return cards;
}

async function main() {
  const projectContext = await readJson(path.join(repoRoot, "project-context.json"));
  const datasetPath = path.join(repoRoot, "data", "sft", "v1-seed-anchor-demo", "samples.jsonl");
  const trainDatasetPath = path.join(repoRoot, "data", "sft", "v1-seed-anchor-demo", "train.jsonl");
  const heldOutDatasetPath = path.join(repoRoot, "data", "sft", "v1-seed-anchor-demo", "held-out.jsonl");
  const samples = await readJsonl(datasetPath);
  const gemmaTrackPack = await readJsonIfExists(path.join(repoRoot, "outputs", "gemma", "base-vs-instruct-pack.json"), null);
  const level1TaskPack = await readJsonIfExists(path.join(repoRoot, "outputs", "level1", "task-framing-pack.json"), null);
  const level1BaselinePack = await readJsonIfExists(path.join(repoRoot, "outputs", "level1", "baseline-eval-pack.json"), null);
  const level5ToolPack = await readJsonIfExists(path.join(repoRoot, "outputs", "level5", "tool-routing-dataset-pack.json"), null);
  const level5StructuredPack = await readJsonIfExists(path.join(repoRoot, "outputs", "level5", "structured-output-probe-pack.json"), null);
  const behaviorEvalPack = await readJsonIfExists(path.join(repoRoot, "outputs", "behavior", "behavior-eval-pack.json"), null);
  const dataScaleComparePack = await readJsonIfExists(path.join(repoRoot, "outputs", "compare", "data-scale-compare-pack.json"), null);
  const level6PreferencePack = await readJsonIfExists(path.join(repoRoot, "outputs", "level6", "preference-dataset-pack.json"), null);
  const level6PolicyCompare = await readJsonIfExists(path.join(repoRoot, "outputs", "level6", "policy-compare-report.json"), null);
  const level6ScaleUpRubric = await readJsonIfExists(path.join(repoRoot, "outputs", "level6", "scale-up-rubric.json"), null);
  const level6ScaleUpCompare = await readJsonIfExists(path.join(repoRoot, "outputs", "level6", "gemma-scale-up-compare.json"), null);
  const onboarding = await readJsonIfExists(
    path.join(repoRoot, "outputs", "agent", "onboarding-report.json"),
    {
      generated_at: new Date().toISOString(),
      repo: {
        name: projectContext.project.name,
        root: repoRoot,
        tagline: projectContext.project.tagline,
      },
      overall_status: "unknown",
      readiness: [],
      next_steps: [],
      agent_prompts: projectContext.ai_native_onboarding?.agent_prompts ?? [],
      workflow_stages: projectContext.workflow_stages ?? [],
      reading_order: projectContext.reading_order ?? [],
      machine: {},
      stage_readiness: [],
      learning_progress: {
        completed_stage_ids: [],
        completed_stage_count: 0,
        total_stage_count: 0,
        next_stage: null,
      },
    },
  );
  const runs = await getRuns();
  let beginnerGuideMarkdown = null;
  try {
    beginnerGuideMarkdown = await fs.readFile(path.join(repoRoot, "docs", "ai", "beginner-guide.md"), "utf8");
  } catch {
    beginnerGuideMarkdown = null;
  }
  const datasetCards = await loadDatasetCards();
  const payload = {
    generated_at: new Date().toISOString(),
    project: projectContext.project,
    beginner_guide_markdown: beginnerGuideMarkdown,
    dataset_cards: datasetCards,
    manifesto: projectContext.manifesto ?? null,
    agent_handoff_timeline: projectContext.agent_handoff_timeline ?? [],
    teaching_takeaways: projectContext.teaching_takeaways ?? [],
    gemma_track: projectContext.gemma_track ?? null,
    learning_roadmap: projectContext.learning_roadmap ?? null,
    reference_projects: projectContext.reference_projects ?? [],
    gemma_track_pack: gemmaTrackPack,
    level1: {
      task_framing_pack: level1TaskPack,
      baseline_eval_pack: level1BaselinePack,
    },
    level5: {
      tool_routing_pack: level5ToolPack,
      structured_output_pack: level5StructuredPack,
    },
    behavior_eval_pack: behaviorEvalPack,
    data_scale_compare_pack: dataScaleComparePack,
    level6: {
      preference_dataset_pack: level6PreferencePack,
      policy_compare_report: level6PolicyCompare,
      scale_up_rubric: level6ScaleUpRubric,
      scale_up_compare: level6ScaleUpCompare,
    },
    source: {
      dataset: path.relative(repoRoot, datasetPath),
      train_dataset: path.relative(repoRoot, trainDatasetPath),
      held_out_dataset: path.relative(repoRoot, heldOutDatasetPath),
    },
    agent_prompts: projectContext.ai_native_onboarding?.agent_prompts ?? [],
    workflow_stages: projectContext.workflow_stages ?? [],
    onboarding,
    dataset: {
      samples,
      summary: {
        total_samples: samples.length,
        category_counts: countBy(samples.map((s) => s.category)).map(({ key, count }) => ({ category: key, count })),
        behavior_counts: countBy(samples.map((s) => s.behavior)).map(({ key, count }) => ({ behavior: key, count })),
        risk_counts: countBy(samples.map((s) => s.risk)).map(({ key, count }) => ({ risk: key, count })),
        expected_system_action_counts: countBy(
          samples
            .map((s) => s.expected_system_action?.type)
            .filter(Boolean),
        ).map(({ key, count }) => ({ action: key, count })),
        generator_counts: countBy(samples.map((s) => s.meta.generator_model)).map(({ key, count }) => ({ model: key, count })),
        domain_counts: countBy(samples.flatMap((s) => s.domains_loaded)).map(({ key, count }) => ({ domain: key, count })),
      },
    },
    runs,
    run_delta: buildRunDelta(runs),
  };
  await fs.writeFile(path.join(webRoot, "public", "lab-data.json"), JSON.stringify(payload, null, 2), "utf8");
  const generatedDir = path.join(webRoot, "src", "generated");
  await fs.mkdir(generatedDir, { recursive: true });
  await fs.writeFile(
    path.join(generatedDir, "lab-data.generated.ts"),
    `export const embeddedLabData = ${JSON.stringify(payload, null, 2)};\n`,
    "utf8",
  );
  console.log("Wrote lab-data.json");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

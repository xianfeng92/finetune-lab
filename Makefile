SHELL := /bin/bash

ROOT := /Users/xforg/AI_SPACE/finetune-lab
PYTHON ?= python3
DATA_VENV ?= $(ROOT)/.venv-data
DATA_PYTHON := $(DATA_VENV)/bin/python
REAL_TRAIN_VENV ?= $(ROOT)/.venv-real-train
REAL_TRAIN_PYTHON := $(REAL_TRAIN_VENV)/bin/python
REAL_MLX_LORA := $(REAL_TRAIN_VENV)/bin/mlx_lm.lora
FULL_DATASET ?= $(ROOT)/data/sft/v1-seed-anchor-demo/samples.jsonl
TRAIN_DATASET ?= $(ROOT)/data/sft/v1-seed-anchor-demo/train.jsonl
HELD_OUT_DATASET ?= $(ROOT)/data/sft/v1-seed-anchor-demo/held-out.jsonl
MEDIUM_DATASET_DIR ?= $(ROOT)/data/sft/v1-gemma4-e2b-medium
MEDIUM_FULL_DATASET ?= $(MEDIUM_DATASET_DIR)/samples.jsonl
MEDIUM_TRAIN_DATASET ?= $(MEDIUM_DATASET_DIR)/train.jsonl
MEDIUM_HELD_OUT_DATASET ?= $(MEDIUM_DATASET_DIR)/held-out.jsonl
MEDIUM_PUBLIC_AUG_DATASET_DIR ?= $(ROOT)/data/sft/v1-gemma4-e2b-medium-public-augmented
MEDIUM_PUBLIC_AUG_FULL_DATASET ?= $(MEDIUM_PUBLIC_AUG_DATASET_DIR)/samples.jsonl
MEDIUM_PUBLIC_AUG_TRAIN_DATASET ?= $(MEDIUM_PUBLIC_AUG_DATASET_DIR)/train.jsonl
MEDIUM_PUBLIC_AUG_HELD_OUT_DATASET ?= $(MEDIUM_PUBLIC_AUG_DATASET_DIR)/held-out.jsonl
LARGE_DATASET_DIR ?= $(ROOT)/data/sft/v1-gemma4-e2b-large
LARGE_FULL_DATASET ?= $(LARGE_DATASET_DIR)/samples.jsonl
LARGE_TRAIN_DATASET ?= $(LARGE_DATASET_DIR)/train.jsonl
LARGE_HELD_OUT_DATASET ?= $(LARGE_DATASET_DIR)/held-out.jsonl
REAL_FT_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-toolcall-demo
REAL_FT_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack.json
MEDIUM_REAL_FT_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-medium
MEDIUM_REAL_FT_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-medium.json
MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-medium-public-augmented
MEDIUM_PUBLIC_AUG_REAL_FT_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-medium-public-augmented.json
LARGE_REAL_FT_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-large
LARGE_REAL_FT_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-large.json
REAL_SMALL_DIRECT_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-small-direct
REAL_MEDIUM_DIRECT_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-direct
REAL_MEDIUM_PUBLIC_AUG_DIRECT_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-public-augmented-direct
REAL_LARGE_DIRECT_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-large-direct
REAL_CATEGORY_FILTER ?=
REAL_ITERS ?=
REAL_EPOCHS ?=
REAL_RESUME_ADAPTER_FILE ?=
REAL_STEPS_PER_REPORT ?=
REAL_STEPS_PER_EVAL ?=
REAL_SAVE_EVERY ?=
OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-mlx-demo-unsloth-vlm
OUTPUT_DIR_100 ?= $(ROOT)/outputs/gemma4-e2b-mlx-demo-unsloth-vlm-100step
REAL_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-demo
REAL_PROBE_DATASET ?= $(REAL_FT_DATA_DIR)/test.jsonl
REAL_PROBE_MAX_SAMPLES ?=
REAL_SINGLE_TOOL_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-single-tool-control
REAL_SINGLE_TOOL_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-single-tool-control.json
REAL_SINGLE_TOOL_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-single-tool-control
REAL_SINGLE_TOOL_EPOCHS ?= 3
REAL_CURRICULUM_ROOT ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-stage-curriculum
REAL_CURRICULUM_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-stage-curriculum
REAL_CURRICULUM_PACK_ROOT ?= $(ROOT)/outputs/real
REAL_CURRICULUM_STAGE_EPOCHS ?= 3
REAL_CURRICULUM_CONSOLIDATION_EPOCHS ?= 1
REAL_CURRICULUM_REPLAY_RATIO ?= 0.25
REAL_CURRICULUM_REPLAY_ROOT ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-stage-curriculum-replay
REAL_CURRICULUM_REPLAY_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-replay
REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-stage-curriculum-consolidation
REAL_TAIL_POLISH_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-tail-polish
REAL_TAIL_POLISH_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-tail-polish.json
REAL_TAIL_POLISH_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-tail-polish/stage5-focus
REAL_TAIL_POLISH_REPEAT_FACTOR ?= 3
REAL_TAIL_POLISH_EPOCHS ?= 1
REAL_MEDIUM_STAGE_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum
REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-stage-curriculum-consolidation
REAL_MEDIUM_CURRICULUM_ROOT ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-medium-stage-curriculum
REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-public-augmented-stage-curriculum
REAL_MEDIUM_PUBLIC_AUG_CONSOLIDATION_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-public-augmented-stage-curriculum-consolidation
REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-medium-public-augmented-stage-curriculum
REAL_LARGE_STAGE_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum
REAL_LARGE_CONSOLIDATION_OUTPUT_ROOT ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-large-stage-curriculum-consolidation
REAL_LARGE_CURRICULUM_ROOT ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-large-stage-curriculum
REAL_MEDIUM_CROSS_DOMAIN_FOCUS_DATA_DIR ?= $(ROOT)/data/real-finetune/v1-gemma4-e2b-medium-cross-domain-focus
REAL_MEDIUM_CROSS_DOMAIN_FOCUS_PACK ?= $(ROOT)/outputs/real/real-finetune-dataset-pack-medium-cross-domain-focus.json
REAL_MEDIUM_CROSS_DOMAIN_FOCUS_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-cross-domain-focus/stage5-cross-domain
REAL_MEDIUM_CROSS_DOMAIN_FOCUS_REPEAT_FACTOR ?= 3
REAL_MEDIUM_CROSS_DOMAIN_MICRO_REFRESH_OUTPUT_DIR ?= $(ROOT)/outputs/gemma4-e2b-real-mlx-lora-medium-cross-domain-focus-refresh/stage6-micro-refresh
REAL_MEDIUM_CROSS_DOMAIN_MICRO_REFRESH_EPOCHS ?= 0.25
MODEL_NAME ?= demo/gemma-4-e2b-it
REAL_MODEL_NAME ?= mlx-community/gemma-4-e2b-it-4bit

.PHONY: help ai-onboarding ai-setup ai-lab bootstrap-data bootstrap-real-finetune data-demo data-medium data-medium-public-augmented data-large import-car-bench import-clarifyvc test-data env-probe smoke-train-mac probe-mac smoke-train-mac-100 probe-mac-100 compare-probes behavior-eval-pack level1-pack gemma-track-pack real-finetune-data real-finetune-data-medium real-finetune-data-medium-public-augmented real-finetune-data-large real-train-mac real-probe-mac real-mini-lab real-small-direct-compare real-medium-direct-compare real-medium-public-augmented-direct-compare real-large-direct-compare real-single-tool-compare real-stage-curriculum real-stage-curriculum-consolidation real-medium-stage-curriculum-consolidation real-medium-public-augmented-stage-curriculum-consolidation real-large-stage-curriculum-consolidation real-stage-curriculum-replay real-tail-polish real-medium-cross-domain-focus-refresh data-scale-compare-pack level5-pack level6-demo dataset-governance web-install web-sync-data web-dev web-build

help:
	@echo "Available targets:"
	@echo "  ai-onboarding       Generate AI-native onboarding report"
	@echo "  ai-setup            Prepare Python/frontend deps and refresh onboarding report"
	@echo "  ai-lab              Run the minimal AI-native teaching loop"
	@echo "  bootstrap-data      Install Python dependencies for data pipeline"
	@echo "  bootstrap-real-finetune Install MLX LoRA dependencies for Apple Silicon real training"
	@echo "  data-demo           Generate demo SFT dataset"
	@echo "  data-medium         Generate a medium Gemma 4 SFT dataset (400 train / 100 held-out)"
	@echo "  data-medium-public-augmented Build a medium dataset augmented with imported public samples"
	@echo "  data-large          Generate a large Gemma 4 SFT dataset (800 train / 200 held-out)"
	@echo "  import-car-bench    Download CAR-Bench task files and build a finetune-lab mapping preview"
	@echo "  import-clarifyvc    Mirror ClarifyVC OpenReview artifacts and build a protocol-seed mapping preview"
	@echo "  test-data           Run data pipeline tests"
	@echo "  env-probe           Print local training environment summary"
	@echo "  smoke-train-mac     Run 20-step local smoke train"
	@echo "  probe-mac           Generate 20-step probe results"
	@echo "  smoke-train-mac-100 Run 100-step local smoke train"
	@echo "  probe-mac-100       Generate 100-step probe results"
	@echo "  compare-probes      Compare 20-step vs 100-step probe summaries"
	@echo "  behavior-eval-pack  Build behavior-level eval pack from probe results"
	@echo "  level1-pack         Build baseline and task-framing teaching packs"
	@echo "  gemma-track-pack    Build base-vs-instruct teaching pack"
	@echo "  real-finetune-data  Convert train/held-out into MLX chat+tools dataset"
	@echo "  real-finetune-data-medium Convert the medium SFT dataset into MLX chat+tools format"
	@echo "  real-finetune-data-medium-public-augmented Convert the public-augmented medium dataset into MLX chat+tools format"
	@echo "  real-finetune-data-large Convert the large SFT dataset into MLX chat+tools format"
	@echo "  real-train-mac      Run a real MLX LoRA mini fine-tune on Gemma 4 E2B-it"
	@echo "  real-probe-mac      Run best-effort real probe on the MLX LoRA adapters"
	@echo "  real-mini-lab       Refresh real dataset, run real MLX LoRA, and probe it"
	@echo "  real-small-direct-compare Run a 1-epoch direct small-data LoRA compare baseline"
	@echo "  real-medium-direct-compare Run a 1-epoch direct medium-data LoRA compare baseline"
	@echo "  real-medium-public-augmented-direct-compare Run a 1-epoch direct public-augmented medium LoRA baseline"
	@echo "  real-medium-public-augmented-stage-curriculum-consolidation Run the public-augmented medium staged curriculum and consolidation path"
	@echo "  real-large-direct-compare Run a 1-epoch direct large-data LoRA compare baseline"
	@echo "  real-single-tool-compare Run a 3-epoch single_domain_single_tool control experiment"
	@echo "  real-stage-curriculum Run single_tool -> reroute/meta -> multi_tool staged curriculum"
	@echo "  real-stage-curriculum-consolidation Run staged curriculum, then add a short full-mixed consolidation stage"
	@echo "  real-medium-stage-curriculum-consolidation Run the medium-data staged curriculum and consolidation path"
	@echo "  real-large-stage-curriculum-consolidation Run the large-data staged curriculum and consolidation path"
	@echo "  real-stage-curriculum-replay Run staged curriculum with 25% replay from earlier stages"
	@echo "  real-tail-polish Run a short focused tail-repair stage on top of curriculum consolidation"
	@echo "  real-medium-cross-domain-focus-refresh Run medium cross-domain focus, then a short full-mixed micro refresh"
	@echo "  data-scale-compare-pack Build a compare pack for small vs medium and direct vs curriculum strategies"
	@echo "  level5-pack         Build tool-routing and structured-output teaching packs"
	@echo "  level6-demo         Build preference-pair demo and policy compare pack"
	@echo "  web-install         Install frontend dependencies"
	@echo "  web-sync-data       Generate unified frontend lab-data.json"
	@echo "  web-dev             Start frontend dev server"
	@echo "  web-build           Build frontend"

ai-onboarding:
	cd $(ROOT) && $(PYTHON) scripts/ai_onboarding_report.py

ai-setup:
	$(MAKE) -C $(ROOT) bootstrap-data
	$(MAKE) -C $(ROOT) web-install
	$(MAKE) -C $(ROOT) ai-onboarding

ai-lab:
	$(MAKE) -C $(ROOT) ai-setup
	$(MAKE) -C $(ROOT) data-demo
	$(MAKE) -C $(ROOT) test-data
	$(MAKE) -C $(ROOT) level1-pack
	$(MAKE) -C $(ROOT) gemma-track-pack
	$(MAKE) -C $(ROOT) env-probe
	$(MAKE) -C $(ROOT) smoke-train-mac
	$(MAKE) -C $(ROOT) probe-mac
	$(MAKE) -C $(ROOT) level5-pack
	$(MAKE) -C $(ROOT) web-build
	$(MAKE) -C $(ROOT) ai-onboarding

bootstrap-data:
	cd $(ROOT) && $(PYTHON) -m venv $(DATA_VENV)
	cd $(ROOT) && $(DATA_PYTHON) -m pip install --upgrade pip
	cd $(ROOT) && $(DATA_PYTHON) -m pip install "jsonschema>=4.23" "pytest>=8.3"

bootstrap-real-finetune:
	cd $(ROOT) && $(PYTHON) -m venv $(REAL_TRAIN_VENV)
	cd $(ROOT) && $(REAL_TRAIN_PYTHON) -m pip install --upgrade pip
	cd $(ROOT) && $(REAL_TRAIN_PYTHON) -m pip install "mlx-lm[train]"

data-demo:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/pipeline.py --output-dir data/sft/v1-seed-anchor-demo

data-medium:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/pipeline.py --output-dir data/sft/v1-gemma4-e2b-medium --multiplier 5

data-medium-public-augmented:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/build_public_augmented_dataset.py --base-train $(MEDIUM_TRAIN_DATASET) --base-held-out $(MEDIUM_HELD_OUT_DATASET) --car-bench $(ROOT)/data/public-normalized/car-bench-v1/samples.jsonl --clarifyvc $(ROOT)/data/public-normalized/clarifyvc-v1/samples.jsonl --output-dir $(MEDIUM_PUBLIC_AUG_DATASET_DIR) --base-summary $(MEDIUM_DATASET_DIR)/dataset_summary.json

data-large:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/pipeline.py --output-dir data/sft/v1-gemma4-e2b-large --multiplier 10

import-car-bench:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/import_car_bench.py

import-clarifyvc:
	cd $(ROOT) && $(DATA_PYTHON) training/data_pipeline/import_clarifyvc.py

test-data:
	cd $(ROOT) && bash training/data_pipeline/scripts/test.sh

env-probe:
	cd $(ROOT) && $(PYTHON) training/finetune/env_probe.py

smoke-train-mac:
	cd $(ROOT) && $(PYTHON) training/finetune/mlx_tune_sft.py --model-name $(MODEL_NAME) --dataset $(TRAIN_DATASET) --output-dir $(OUTPUT_DIR) --max-steps 20

probe-mac:
	cd $(ROOT) && $(PYTHON) training/finetune/post_train_probe.py --dataset $(HELD_OUT_DATASET) --run-dir $(OUTPUT_DIR)

smoke-train-mac-100:
	cd $(ROOT) && $(PYTHON) training/finetune/mlx_tune_sft.py --model-name $(MODEL_NAME) --dataset $(TRAIN_DATASET) --output-dir $(OUTPUT_DIR_100) --max-steps 100

probe-mac-100:
	cd $(ROOT) && $(PYTHON) training/finetune/post_train_probe.py --dataset $(HELD_OUT_DATASET) --run-dir $(OUTPUT_DIR_100)

compare-probes:
	cd $(ROOT) && $(PYTHON) training/finetune/scripts/compare_probes.py

behavior-eval-pack:
	cd $(ROOT) && $(PYTHON) training/finetune/build_behavior_eval_pack.py --output-dir outputs/behavior --run-dir $(OUTPUT_DIR) --run-dir $(OUTPUT_DIR_100) --run-dir $(REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --run-dir $(REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --run-dir $(REAL_LARGE_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation

level1-pack:
	cd $(ROOT) && $(PYTHON) training/finetune/build_level1_pack.py --dataset $(FULL_DATASET) --output-dir outputs/level1

gemma-track-pack:
	cd $(ROOT) && $(PYTHON) training/finetune/build_gemma_track_pack.py --output-dir outputs/gemma

real-finetune-data:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(TRAIN_DATASET) --held-out-dataset $(HELD_OUT_DATASET) --output-dir $(REAL_FT_DATA_DIR) --pack-output $(REAL_FT_PACK) $(if $(REAL_CATEGORY_FILTER),--category-filter $(REAL_CATEGORY_FILTER))

real-finetune-data-medium:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_TRAIN_DATASET) --held-out-dataset $(MEDIUM_HELD_OUT_DATASET) --output-dir $(MEDIUM_REAL_FT_DATA_DIR) --pack-output $(MEDIUM_REAL_FT_PACK)

real-finetune-data-medium-public-augmented:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_PUBLIC_AUG_TRAIN_DATASET) --held-out-dataset $(MEDIUM_PUBLIC_AUG_HELD_OUT_DATASET) --output-dir $(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR) --pack-output $(MEDIUM_PUBLIC_AUG_REAL_FT_PACK)

real-finetune-data-large:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(LARGE_TRAIN_DATASET) --held-out-dataset $(LARGE_HELD_OUT_DATASET) --output-dir $(LARGE_REAL_FT_DATA_DIR) --pack-output $(LARGE_REAL_FT_PACK)

real-train-mac:
	cd $(ROOT) && $(PYTHON) training/finetune/mlx_real_lora_train.py --mlx-lora-cmd $(REAL_MLX_LORA) --model-name $(REAL_MODEL_NAME) --data-dir $(REAL_FT_DATA_DIR) --output-dir $(REAL_OUTPUT_DIR) $(if $(REAL_ITERS),--iters $(REAL_ITERS)) $(if $(REAL_EPOCHS),--epochs $(REAL_EPOCHS)) $(if $(REAL_RESUME_ADAPTER_FILE),--resume-adapter-file $(REAL_RESUME_ADAPTER_FILE)) $(if $(REAL_STEPS_PER_REPORT),--steps-per-report $(REAL_STEPS_PER_REPORT)) $(if $(REAL_STEPS_PER_EVAL),--steps-per-eval $(REAL_STEPS_PER_EVAL)) $(if $(REAL_SAVE_EVERY),--save-every $(REAL_SAVE_EVERY))

real-probe-mac:
	cd $(ROOT) && $(REAL_TRAIN_PYTHON) training/finetune/mlx_real_probe.py --model-name $(REAL_MODEL_NAME) --dataset $(REAL_PROBE_DATASET) --run-dir $(REAL_OUTPUT_DIR) $(if $(REAL_PROBE_MAX_SAMPLES),--max-samples $(REAL_PROBE_MAX_SAMPLES))

real-mini-lab:
	$(MAKE) -C $(ROOT) bootstrap-real-finetune
	$(MAKE) -C $(ROOT) real-finetune-data
	$(MAKE) -C $(ROOT) real-train-mac
	$(MAKE) -C $(ROOT) real-probe-mac
	$(MAKE) -C $(ROOT) ai-onboarding
	$(MAKE) -C $(ROOT) web-build

real-small-direct-compare:
	$(MAKE) -C $(ROOT) real-finetune-data
	$(MAKE) -C $(ROOT) real-train-mac REAL_OUTPUT_DIR=$(REAL_SMALL_DIRECT_OUTPUT_DIR) REAL_EPOCHS=1
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_SMALL_DIRECT_OUTPUT_DIR) REAL_PROBE_MAX_SAMPLES=10

real-medium-direct-compare:
	$(MAKE) -C $(ROOT) real-finetune-data-medium
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(MEDIUM_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_EPOCHS=1 REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48

real-medium-public-augmented-direct-compare:
	$(MAKE) -C $(ROOT) data-medium-public-augmented
	$(MAKE) -C $(ROOT) real-finetune-data-medium-public-augmented
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_EPOCHS=1 REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48

real-large-direct-compare:
	$(MAKE) -C $(ROOT) real-finetune-data-large
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(LARGE_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_LARGE_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_EPOCHS=1 REAL_STEPS_PER_REPORT=40 REAL_STEPS_PER_EVAL=160 REAL_SAVE_EVERY=160
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_LARGE_DIRECT_OUTPUT_DIR) REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=96

real-single-tool-compare:
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_SINGLE_TOOL_DATA_DIR) REAL_FT_PACK=$(REAL_SINGLE_TOOL_PACK) REAL_CATEGORY_FILTER=single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_SINGLE_TOOL_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_SINGLE_TOOL_OUTPUT_DIR) REAL_EPOCHS=$(REAL_SINGLE_TOOL_EPOCHS)
	$(MAKE) -C $(ROOT) real-probe-mac REAL_FT_DATA_DIR=$(REAL_SINGLE_TOOL_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_SINGLE_TOOL_OUTPUT_DIR)

real-stage-curriculum:
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage1-single-tool REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage1-single-tool.json REAL_CATEGORY_FILTER=single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage1-single-tool REAL_OUTPUT_DIR=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage1-single-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS)
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage2-reroute-meta REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage2-reroute-meta.json REAL_CATEGORY_FILTER=reroute_to_meta,full_tool_fallback,confirm_required_action,reject_unsafe_action
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage2-reroute-meta REAL_OUTPUT_DIR=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage2-reroute-meta REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage1-single-tool/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage3-multi-tool REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage3-multi-tool.json REAL_CATEGORY_FILTER=single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_ROOT)/stage3-multi-tool REAL_OUTPUT_DIR=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage3-multi-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage2-reroute-meta/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage3-multi-tool REAL_PROBE_DATASET=$(ROOT)/data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl

real-stage-curriculum-consolidation:
	$(MAKE) -C $(ROOT) real-stage-curriculum
	$(MAKE) -C $(ROOT) real-finetune-data
	$(MAKE) -C $(ROOT) real-train-mac REAL_OUTPUT_DIR=$(REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_EPOCHS=$(REAL_CURRICULUM_CONSOLIDATION_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_OUTPUT_ROOT)/stage3-multi-tool/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_PROBE_DATASET=$(ROOT)/data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl REAL_PROBE_MAX_SAMPLES=10

real-medium-stage-curriculum-consolidation:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_TRAIN_DATASET) --held-out-dataset $(MEDIUM_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_CURRICULUM_ROOT)/stage1-single-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-stage1-single-tool.json --category-filter single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_CURRICULUM_ROOT)/stage1-single-tool REAL_OUTPUT_DIR=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage1-single-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_TRAIN_DATASET) --held-out-dataset $(MEDIUM_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_CURRICULUM_ROOT)/stage2-reroute-meta --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-stage2-reroute-meta.json --category-filter reroute_to_meta,full_tool_fallback,confirm_required_action,reject_unsafe_action
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_CURRICULUM_ROOT)/stage2-reroute-meta REAL_OUTPUT_DIR=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage2-reroute-meta REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage1-single-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_TRAIN_DATASET) --held-out-dataset $(MEDIUM_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_CURRICULUM_ROOT)/stage3-multi-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-stage3-multi-tool.json --category-filter single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_CURRICULUM_ROOT)/stage3-multi-tool REAL_OUTPUT_DIR=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage2-reroute-meta/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48
	$(MAKE) -C $(ROOT) real-finetune-data-medium
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(MEDIUM_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_EPOCHS=$(REAL_CURRICULUM_CONSOLIDATION_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_STAGE_OUTPUT_ROOT)/stage3-multi-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48

real-medium-public-augmented-stage-curriculum-consolidation:
	$(MAKE) -C $(ROOT) data-medium-public-augmented
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_PUBLIC_AUG_TRAIN_DATASET) --held-out-dataset $(MEDIUM_PUBLIC_AUG_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage1-single-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-public-aug-stage1-single-tool.json --category-filter single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage1-single-tool REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage1-single-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_PUBLIC_AUG_TRAIN_DATASET) --held-out-dataset $(MEDIUM_PUBLIC_AUG_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage2-reroute-meta --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-public-aug-stage2-reroute-meta.json --category-filter reroute_to_meta,full_tool_fallback,confirm_required_action,reject_unsafe_action
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage2-reroute-meta REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage2-reroute-meta REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage1-single-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(MEDIUM_PUBLIC_AUG_TRAIN_DATASET) --held-out-dataset $(MEDIUM_PUBLIC_AUG_HELD_OUT_DATASET) --output-dir $(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage3-multi-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-medium-public-aug-stage3-multi-tool.json --category-filter single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_PUBLIC_AUG_CURRICULUM_ROOT)/stage3-multi-tool REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage2-reroute-meta/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48
	$(MAKE) -C $(ROOT) real-finetune-data-medium-public-augmented
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_EPOCHS=$(REAL_CURRICULUM_CONSOLIDATION_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_PUBLIC_AUG_STAGE_OUTPUT_ROOT)/stage3-multi-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_PUBLIC_AUG_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_PROBE_DATASET=$(MEDIUM_PUBLIC_AUG_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=48

real-large-stage-curriculum-consolidation:
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(LARGE_TRAIN_DATASET) --held-out-dataset $(LARGE_HELD_OUT_DATASET) --output-dir $(REAL_LARGE_CURRICULUM_ROOT)/stage1-single-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-large-stage1-single-tool.json --category-filter single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_LARGE_CURRICULUM_ROOT)/stage1-single-tool REAL_OUTPUT_DIR=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage1-single-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=60 REAL_SAVE_EVERY=60
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(LARGE_TRAIN_DATASET) --held-out-dataset $(LARGE_HELD_OUT_DATASET) --output-dir $(REAL_LARGE_CURRICULUM_ROOT)/stage2-reroute-meta --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-large-stage2-reroute-meta.json --category-filter reroute_to_meta,full_tool_fallback,confirm_required_action,reject_unsafe_action
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_LARGE_CURRICULUM_ROOT)/stage2-reroute-meta REAL_OUTPUT_DIR=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage2-reroute-meta REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage1-single-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=60 REAL_SAVE_EVERY=60
	cd $(ROOT) && $(PYTHON) training/finetune/build_real_finetune_dataset.py --train-dataset $(LARGE_TRAIN_DATASET) --held-out-dataset $(LARGE_HELD_OUT_DATASET) --output-dir $(REAL_LARGE_CURRICULUM_ROOT)/stage3-multi-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-large-stage3-multi-tool.json --category-filter single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_LARGE_CURRICULUM_ROOT)/stage3-multi-tool REAL_OUTPUT_DIR=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage2-reroute-meta/adapters/adapters.safetensors REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage3-multi-tool REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=96
	$(MAKE) -C $(ROOT) real-finetune-data-large
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(LARGE_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_LARGE_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_EPOCHS=$(REAL_CURRICULUM_CONSOLIDATION_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_LARGE_STAGE_OUTPUT_ROOT)/stage3-multi-tool/adapters/adapters.safetensors REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=40 REAL_STEPS_PER_EVAL=160 REAL_SAVE_EVERY=160
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_LARGE_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation REAL_PROBE_DATASET=$(LARGE_REAL_FT_DATA_DIR)/test.jsonl REAL_PROBE_MAX_SAMPLES=96

real-stage-curriculum-replay:
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage1-single-tool REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage1-single-tool-replay.json REAL_CATEGORY_FILTER=single_domain_single_tool
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage1-single-tool REAL_OUTPUT_DIR=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage1-single-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS)
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage2-reroute-meta-primary REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage2-reroute-meta-primary-replay.json REAL_CATEGORY_FILTER=reroute_to_meta,full_tool_fallback
	cd $(ROOT) && $(PYTHON) training/finetune/build_replay_dataset.py --primary-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage2-reroute-meta-primary --replay-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage1-single-tool --replay-ratio $(REAL_CURRICULUM_REPLAY_RATIO) --output-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage2-reroute-meta --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage2-reroute-meta-replay.json
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage2-reroute-meta REAL_OUTPUT_DIR=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage2-reroute-meta REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage1-single-tool/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-finetune-data REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage3-multi-tool-primary REAL_FT_PACK=$(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage3-multi-tool-primary-replay.json REAL_CATEGORY_FILTER=single_domain_multi_tool_chain,cross_domain_multi_tool,proactive_event_driven
	cd $(ROOT) && $(PYTHON) training/finetune/build_replay_dataset.py --primary-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage3-multi-tool-primary --replay-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage1-single-tool --replay-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage2-reroute-meta-primary --replay-ratio $(REAL_CURRICULUM_REPLAY_RATIO) --output-dir $(REAL_CURRICULUM_REPLAY_ROOT)/stage3-multi-tool --pack-output $(REAL_CURRICULUM_PACK_ROOT)/real-finetune-dataset-pack-stage3-multi-tool-replay.json
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_CURRICULUM_REPLAY_ROOT)/stage3-multi-tool REAL_OUTPUT_DIR=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage3-multi-tool REAL_EPOCHS=$(REAL_CURRICULUM_STAGE_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage2-reroute-meta/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_CURRICULUM_REPLAY_OUTPUT_ROOT)/stage3-multi-tool REAL_PROBE_DATASET=$(ROOT)/data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl

real-tail-polish:
	$(MAKE) -C $(ROOT) real-finetune-data
	cd $(ROOT) && $(PYTHON) training/finetune/build_focus_dataset.py --source-dir $(REAL_FT_DATA_DIR) --output-dir $(REAL_TAIL_POLISH_DATA_DIR) --pack-output $(REAL_TAIL_POLISH_PACK) --focus-category single_domain_multi_tool_chain --focus-prompt 车里太闷了，想透透气 --repeat-factor $(REAL_TAIL_POLISH_REPEAT_FACTOR)
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_TAIL_POLISH_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_TAIL_POLISH_OUTPUT_DIR) REAL_EPOCHS=$(REAL_TAIL_POLISH_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation/adapters/adapters.safetensors
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_TAIL_POLISH_OUTPUT_DIR) REAL_PROBE_DATASET=$(ROOT)/data/real-finetune/v1-gemma4-e2b-toolcall-demo/test.jsonl

real-medium-cross-domain-focus-refresh:
	cd $(ROOT) && $(PYTHON) training/finetune/build_focus_dataset.py --source-dir $(MEDIUM_REAL_FT_DATA_DIR) --output-dir $(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_DATA_DIR) --pack-output $(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_PACK) --focus-category cross_domain_multi_tool --repeat-factor $(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_REPEAT_FACTOR)
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_OUTPUT_DIR) REAL_EPOCHS=1 REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl
	$(MAKE) -C $(ROOT) real-train-mac REAL_FT_DATA_DIR=$(MEDIUM_REAL_FT_DATA_DIR) REAL_OUTPUT_DIR=$(REAL_MEDIUM_CROSS_DOMAIN_MICRO_REFRESH_OUTPUT_DIR) REAL_EPOCHS=$(REAL_MEDIUM_CROSS_DOMAIN_MICRO_REFRESH_EPOCHS) REAL_RESUME_ADAPTER_FILE=$(REAL_MEDIUM_CROSS_DOMAIN_FOCUS_OUTPUT_DIR)/adapters/adapters.safetensors REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl REAL_STEPS_PER_REPORT=20 REAL_STEPS_PER_EVAL=80 REAL_SAVE_EVERY=80
	$(MAKE) -C $(ROOT) real-probe-mac REAL_OUTPUT_DIR=$(REAL_MEDIUM_CROSS_DOMAIN_MICRO_REFRESH_OUTPUT_DIR) REAL_PROBE_DATASET=$(MEDIUM_REAL_FT_DATA_DIR)/test.jsonl

data-scale-compare-pack:
	cd $(ROOT) && $(PYTHON) training/finetune/build_data_scale_compare_pack.py --small-pack $(REAL_FT_PACK) --medium-pack $(MEDIUM_REAL_FT_PACK) --medium-public-augmented-pack $(MEDIUM_PUBLIC_AUG_REAL_FT_PACK) --large-pack $(LARGE_REAL_FT_PACK) --run-dir $(REAL_SMALL_DIRECT_OUTPUT_DIR) --run-dir $(REAL_CURRICULUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --run-dir $(REAL_MEDIUM_DIRECT_OUTPUT_DIR) --run-dir $(REAL_MEDIUM_PUBLIC_AUG_DIRECT_OUTPUT_DIR) --run-dir $(REAL_MEDIUM_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --run-dir $(REAL_MEDIUM_PUBLIC_AUG_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --run-dir $(REAL_LARGE_DIRECT_OUTPUT_DIR) --run-dir $(REAL_LARGE_CONSOLIDATION_OUTPUT_ROOT)/stage4-consolidation --output-dir outputs/compare

level5-pack:
	cd $(ROOT) && $(PYTHON) training/finetune/build_level5_pack.py --dataset $(FULL_DATASET) --output-dir outputs/level5 --run-dir $(OUTPUT_DIR) --run-dir $(OUTPUT_DIR_100)

level6-demo:
	cd $(ROOT) && $(PYTHON) training/finetune/build_level6_demo.py --dataset $(FULL_DATASET) --preferences-dir data/preferences/v1-gemma4-e2b-demo --output-dir outputs/level6

dataset-governance:
	cd $(ROOT) && $(PYTHON) training/data_pipeline/run_governance.py --root $(ROOT)

web-install:
	cd $(ROOT)/web && npm install

web-sync-data:
	$(MAKE) -C $(ROOT) ai-onboarding
	cd $(ROOT)/web && npm run sync-data

web-dev:
	cd $(ROOT)/web && npm run dev

web-build:
	cd $(ROOT)/web && npm run build

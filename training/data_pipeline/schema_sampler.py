from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List


DEFAULT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "tool-schemas" / "automotive-v1.json"
)


def load_schema(schema_path: Path = DEFAULT_SCHEMA_PATH) -> dict:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def flatten_tools(schema: dict) -> Dict[str, dict]:
    tools: Dict[str, dict] = {}
    for domain_tools in schema["domains"].values():
        for tool in domain_tools:
            tools[tool["name"]] = tool
    return tools


def sample_loaded_tools(
    schema: dict,
    domains: List[str],
    include_meta: bool = True,
    seed: int | None = None,
) -> List[dict]:
    rng = random.Random(seed)
    selected: List[dict] = []
    for domain in domains:
        domain_tools = list(schema["domains"][domain])
        if not domain_tools:
            continue
        count = rng.randint(1, len(domain_tools))
        rng.shuffle(domain_tools)
        selected.extend(domain_tools[:count])
    if include_meta:
        selected.extend(schema["domains"].get("meta", []))
    rng.shuffle(selected)
    return selected

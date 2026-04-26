from __future__ import annotations

import json


def build_sft_text(system_prompt: str, messages: list[dict]) -> str:
    rendered = [f"<system>\n{system_prompt}\n</system>"]
    for message in messages:
        role = message["role"]
        if role == "assistant" and "tool_calls" in message:
            rendered.append("<assistant_tool_calls>")
            rendered.append(json.dumps(message["tool_calls"], ensure_ascii=False, indent=2))
            rendered.append("</assistant_tool_calls>")
            if message.get("content"):
                rendered.append(f"<assistant>\n{message['content']}\n</assistant>")
            continue
        rendered.append(f"<{role}>\n{message.get('content', '')}\n</{role}>")
    return "\n".join(rendered)

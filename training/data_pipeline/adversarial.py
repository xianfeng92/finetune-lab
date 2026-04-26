from __future__ import annotations


def mark_adversarial(sample: dict, adversarial: bool = False) -> dict:
    sample["meta"]["adversarial"] = adversarial
    return sample


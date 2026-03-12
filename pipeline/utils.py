import json
import re


def extract_json(text: str) -> dict:
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError(f"No JSON found in LLM output:\n{text}")
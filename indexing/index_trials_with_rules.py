import requests
import json
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from pipeline.utils import extract_json 
from config import OLLAMA_GEN_URL, OLLAMA_EMB_URL, LLM_MODEL, EMB_MODEL, QDRANT_COLLECTION, QDRANT_HOST, QDRANT_PORT
# ---------------- CONFIG ----------------

OLLAMA_GEN = "http://localhost:11434/api/generate"
OLLAMA_EMB = "http://localhost:11434/api/embeddings"

LLM_MODEL = "llama3:8b"
EMB_MODEL = "nomic-embed-text"

qdrant = QdrantClient("localhost", port=6333)

# -------- RULE CACHE + THREAD POOL --------
RULE_CACHE = {}
EXECUTOR = ThreadPoolExecutor(max_workers=8)

# ---------------- CRITERIA SPLITTER ----------------

def split_criteria(text: str) -> dict:
    text = text.lower()

    inc_match = re.search(
        r"inclusion criteria(.*?)(exclusion criteria|$)", text, re.DOTALL
    )
    exc_match = re.search(r"exclusion criteria(.*)", text, re.DOTALL)

    inclusion = inc_match.group(1).strip() if inc_match else ""
    exclusion = exc_match.group(1).strip() if exc_match else ""

    return {
        "inclusion": inclusion,
        "exclusion": exclusion
    }


# ---------------- LLM CALL (THREADED) ----------------

def _llm_call(prompt):
    r = requests.post(
        OLLAMA_GEN,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    r.raise_for_status()
    return extract_json(r.json()["response"])


# ---------------- RULE COMPILER (CACHED) ----------------

def compile_rules(criteria_struct: dict) -> dict:
    key_text = criteria_struct["inclusion"] + criteria_struct["exclusion"]
    key = hashlib.md5(key_text.encode()).hexdigest()

    if key in RULE_CACHE:
        return RULE_CACHE[key]

    prompt = f"""
You are NOT designing a rule system.
You are ONLY extracting values explicitly written in the text.

Return ONLY JSON inside ```json fence.

Fill only what is clearly written. If missing, use null or empty list.

Schema:
{{
  "age_min": null,
  "age_max": null,
  "gender": null,
  "cancer_type": [],
  "stage_allowed": null,
  "ecog_max": null,
  "mutations_required": [],
  "prior_treatments_excluded": [],
  "brain_metastasis_allowed": null,
  "organ_function_required": [],
  "measurable_disease_required": null,
  "surgery_required": null,
  "months_after_surgery_min": null,
  "months_after_surgery_max": null
}}

Inclusion:
{criteria_struct["inclusion"]}

Exclusion:
{criteria_struct["exclusion"]}
"""

    future = EXECUTOR.submit(_llm_call, prompt)
    rules = future.result()

    RULE_CACHE[key] = rules
    return rules


# ---------------- EMBEDDING ----------------

def embed_for_search(title: str, summary: str, conditions: list[str]):
    text = f"""
Conditions: {", ".join(conditions)}
Summary: {summary}
"""
    r = requests.post(
        OLLAMA_EMB,
        json={"model": EMB_MODEL, "prompt": text}
    )
    r.raise_for_status()
    return r.json()["embedding"]


# ---------------- INDEX ONE TRIAL ----------------

def index_trial(trial_id: str, title: str, summary: str,
                conditions: list[str], criteria_text: str):

    criteria_struct = split_criteria(criteria_text)
    rules = compile_rules(criteria_struct)
    vector = embed_for_search(title, summary, conditions)

    # Qdrant id must be int
    point_id = int(hashlib.md5(trial_id.encode()).hexdigest()[:12], 16)

    qdrant.upsert(
        collection_name="trials",
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "nct_id": trial_id,
                    "title": title,
                    "summary": summary,
                    "conditions": conditions,
                    "criteria": criteria_text,
                    "criteria_struct": criteria_struct,
                    "rules": rules
                }
            )
        ]
    )

    print(f"Indexed {trial_id}")

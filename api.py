from fastapi import FastAPI
from pydantic import BaseModel
from indexing.llm_utils import call_llm
from indexing.index_trials_with_rules import compile_rules, split_criteria
from pipeline.utils import extract_json
from pipeline.embed import embed_for_search_patient
from pipeline.matcher import match_patient
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION

app = FastAPI()
qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)


class PatientInput(BaseModel):
    text: str


def extract_patient(text: str) -> dict:
    prompt = f"""
You are extracting structured patient data.

Return ONLY JSON inside ```json fence.

Schema:
{{
  "age": number,
  "gender": "male|female|null",
  "cancer_type": [strings],
  "stage": string|null,
  "mutations": [strings],
  "treatments": [strings],
  "months_after_surgery": number|null,
  "brain_metastasis": true|false|null,
  "ecog": number|null
}}

Case:
{text}
"""
    raw = call_llm(prompt)
    return extract_json(raw)


def ensure_rules(hit) -> dict | None:
    rules = hit.payload.get("rules")
    if rules:
        return rules

    criteria = hit.payload.get("criteria")
    if not criteria:
        return None

    try:
        criteria_struct = split_criteria(criteria)
        rules = compile_rules(criteria_struct)

        qdrant.set_payload(
            collection_name=QDRANT_COLLECTION,
            payload={"rules": rules},
            points=[hit.id]
        )

        return rules

    except Exception as e:
        print(f"ensure_rules failed for {hit.id}: {e}")
        return None


@app.post("/analyze-patient")
def analyze(payload: PatientInput):

    patient = extract_patient(payload.text)

    vector = embed_for_search_patient(patient)
    hits = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=5
    ).points

    results = []

    for h in hits:
        rules = ensure_rules(h)
        if not rules:
            continue

        decision = match_patient(patient, rules)

        results.append({
            "trial_id": h.id,
            "nct_id": h.payload.get("nct_id"),
            "score": h.score,
            "title": h.payload.get("title"),
            "decision": decision
        })

    return {
        "patient": patient,
        "matches": results
    }
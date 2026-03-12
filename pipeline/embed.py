import requests
from config import OLLAMA_EMB_URL, EMB_MODEL

def embed_for_search_patient(p: dict):
    text = f"""
    Conditions: {", ".join(p.get("cancer_type", []))}
    Stage: {p.get("stage")}
    Prior Treatment: {", ".join(p.get("treatments", []))}
    Mutations: {", ".join(p.get("mutations", []))}
    """
    r = requests.post(OLLAMA_EMB_URL, json={"model": EMB_MODEL, "prompt": text})
    r.raise_for_status()
    return r.json()["embedding"]
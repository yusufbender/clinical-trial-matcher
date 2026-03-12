import requests
from config import OLLAMA_GEN_URL, LLM_MODEL
from pipeline.utils import extract_json

def call_llm(prompt: str) -> str:
    r = requests.post(
        OLLAMA_GEN_URL,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    r.raise_for_status()
    return r.json()["response"]
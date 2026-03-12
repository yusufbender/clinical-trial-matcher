# -------- LLM --------
OLLAMA_GEN_URL = "http://localhost:11434/api/generate"
OLLAMA_EMB_URL = "http://localhost:11434/api/embeddings"
LLM_MODEL      = "llama3:8b"
EMB_MODEL      = "nomic-embed-text"

# -------- Qdrant --------
QDRANT_HOST       = "localhost"
QDRANT_PORT       = 6333
QDRANT_COLLECTION = "trials"

# -------- Indexing --------
EMBED_WORKERS = 10
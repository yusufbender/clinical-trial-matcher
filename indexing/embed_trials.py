import psycopg2
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"
WORKERS = 10

qdrant = QdrantClient("localhost", port=6333)
COLLECTION = "trials"

db = psycopg2.connect(
    dbname="clinical",
    user="clinical",
    password="clinical",
    host="localhost",
)

def embed_and_upsert(pid, text):
    r = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": text
    })
    r.raise_for_status()
    vec = r.json()["embedding"]

    qdrant.upsert(
        collection_name=COLLECTION,
        points=[PointStruct(id=pid, vector=vec, payload={"criteria": text})]
    )

cur = db.cursor()
cur.execute("SELECT id, criteria_text FROM trials_oncology;")
rows = cur.fetchall()

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futures = [ex.submit(embed_and_upsert, pid, text) for pid, text in rows]
    for _ in tqdm(as_completed(futures), total=len(futures)):
        pass

from qdrant_client import QdrantClient
from pipeline.embed import embed_for_search_patient
from pipeline.matcher import match_patient

qdrant = QdrantClient("localhost", port=6333)


def run(patient: dict, top_k: int = 5):
    # 1) Semantic search
    vector = embed_for_search_patient(patient)

    hits = qdrant.query_points(
        collection_name="trials",
        query=vector,
        limit=top_k
    ).points

    # 2) Deterministic rule matching
    for h in hits:
        rules = h.payload.get("rules")
        if not rules:
            continue

        result = match_patient(patient, rules)

        print("TRIAL:", h.id, "| SCORE:", h.score)
        print("TITLE:", h.payload.get("title"))
        print("MATCH:", result)
        print("-" * 60)


if __name__ == "__main__":
    patient = {
        "age": 76,
        "gender": None,
        "cancer_type": ["nsclc"],
        "stage": "IV",
        "mutations": [],
        "treatments": ["stereotactic radiosurgery", "chemoradiation"],
        "months_after_surgery": None,
        "brain_metastasis": False
    }

    run(patient)

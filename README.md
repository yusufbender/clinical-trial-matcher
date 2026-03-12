# Clinical Trial Matcher

Serbest metin hasta vakasından → uygun klinik trial bulan AI sistemi.

## Mimari
```
Patient Text
    ↓
LLM (extraction only)
    ↓
Structured Patient JSON
    ↓
Semantic Search (Qdrant)
    ↓
Rule Engine (deterministic)
    ↓
Eligibility Decision
```

LLM sadece veri çıkarımı için kullanılır. Eligibility kararı saf Python kodu ile verilir — halüsinasyon riski sıfır.

## Kurulum

### Gereksinimler

- Python 3.12+
- [Ollama](https://ollama.ai) (llama3:8b + nomic-embed-text)
- [Qdrant](https://qdrant.tech) (Docker)

### Adımlar
```bash
# 1) Qdrant başlat
docker run -p 6333:6333 qdrant/qdrant

# 2) Modelleri indir
ollama pull llama3:8b
ollama pull nomic-embed-text

# 3) Bağımlılıkları yükle
pip install -r requirements.txt

# 4) Trialleri indexle
python -m indexing.parse_trials

# 5) API'yi başlat
uvicorn api:app --reload
```

## Kullanım
```bash
curl -X POST http://localhost:8000/analyze-patient \
  -H "Content-Type: application/json" \
  -d '{"text": "76 year old male with NSCLC stage IV..."}'
```

### Örnek yanıt
```json
{
  "patient": {
    "age": 76,
    "gender": "male",
    "cancer_type": ["nsclc"],
    "stage": "IV",
    "ecog": null,
    "mutations": [],
    "treatments": ["stereotactic radiosurgery", "chemoradiation"],
    "months_after_surgery": null,
    "brain_metastasis": false
  },
  "matches": [
    {
      "trial_id": 123456,
      "nct_id": "NCT07379801",
      "score": 0.91,
      "title": "NSCLC Immunotherapy Trial",
      "decision": {
        "eligible": true,
        "failed_rules": []
      }
    }
  ]
}
```

## Proje Yapısı
```
config.py                         # tüm ayarlar tek yerde
api.py                            # FastAPI endpoint
pipeline/
    utils.py                      # shared JSON parser
    embed.py                      # hasta embedding
    matcher.py                    # deterministic rule engine
    semantic_rules_match.py       # CLI test aracı
indexing/
    llm_utils.py                  # LLM wrapper
    parse_trials.py               # XML parser
    index_trials_with_rules.py    # trial indexer + rule compiler
data/
    trials_xml/                   # ClinicalTrials.gov XML
```

## Tasarım Kararları

**Neden LLM karar vermiyor?**
Trial uygunluk kararını LLM'e bırakmak tutarsız ve halüsinasyonlu sonuçlar üretiyor. LLM yalnızca yapılandırılmamış metinden veri çıkarmak için kullanılıyor; karar deterministik kural motoru tarafından veriliyor.

**Neden Qdrant?**
84.000 trial arasından semantik olarak ilgili olanları hızlıca bulmak için. Kural eşleştirmesi bu ön filtreleme üzerine çalışıyor.

## Veri Kaynağı

[ClinicalTrials.gov](https://clinicaltrials.gov) — AllPublicXML (~84.000 trial)
```

---

Son durum:
```
config.py          ← YENİ
requirements.txt   ← YENİ
README.md          ← YENİ
api.py             ← güncellendi
pipeline/
  utils.py         ← YENİ
  embed.py         ← güncellendi
  matcher.py       ← güncellendi
indexing/
  llm_utils.py     ← güncellendi
  index_trials_with_rules.py ← güncellendi
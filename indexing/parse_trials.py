import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from indexing.index_trials_with_rules import index_trial

CANCER_KEYWORDS = ["cancer", "carcinoma", "tumor", "neoplasm", "oncology"]


def is_oncology(conditions):
    text = " ".join(conditions).lower()
    return any(k in text for k in CANCER_KEYWORDS)


def get_text(elem, path):
    found = elem.find(path)
    return found.text.strip() if found is not None and found.text else None


def parse_xml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        nct_id = get_text(root, ".//nct_id")
        title = get_text(root, ".//brief_title")
        summary = get_text(root, ".//brief_summary")
        conditions = [c.text for c in root.findall(".//condition") if c.text]

        if not is_oncology(conditions):
            return None

        criteria = get_text(root, ".//eligibility/criteria/textblock")
        if not criteria:
            return None

        return nct_id, title, summary, conditions, criteria

    except Exception:
        return None


def main():
    base = "data/trials_xml"
    xml_files = []

    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".xml"):
                xml_files.append(os.path.join(root, f))

    # 1) Hızlıca parse et, 10k onkoloji trial topla
    parsed = []
    for file in tqdm(xml_files, desc="Parsing XML"):
        result = parse_xml(file)
        if result:
            parsed.append(result)
        if len(parsed) >= 10000:
            break

    print(f"\nOncology trials found: {len(parsed)}")

    # 2) Paralel index et
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = [
            ex.submit(
                index_trial,
                trial_id=p[0],
                title=p[1] or "",
                summary=p[2] or "",
                conditions=p[3],
                criteria_text=p[4]
            )
            for p in parsed
        ]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Indexing"):
            pass


if __name__ == "__main__":
    main()
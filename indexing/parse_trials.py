import os
import xml.etree.ElementTree as ET
from tqdm import tqdm

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

    for file in tqdm(xml_files):
        parsed = parse_xml(file)
        if not parsed:
            continue

        nct_id, title, summary, conditions, criteria = parsed

        index_trial(
            trial_id=nct_id,
            title=title or "",
            summary=summary or "",
            conditions=conditions,
            criteria_text=criteria
        )


if __name__ == "__main__":
    main()

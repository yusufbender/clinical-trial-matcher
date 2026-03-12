# ---------------- NORMALIZERS ----------------

def normalize_stage(stage) -> str | None:
    if stage is None:
        return None

    # int gelirse string'e çevir
    stage = str(stage)

    s = stage.upper().replace("STAGE", "").strip()

    mapping = {
        "I": "1", "IA": "1A", "IB": "1B",
        "II": "2", "IIA": "2A", "IIB": "2B",
        "III": "3", "IIIA": "3A", "IIIB": "3B",
        "IV": "4",
        "1": "1", "2": "2", "3": "3", "4": "4"
    }

    return mapping.get(s, s)

# ---------------- RULE CHECKS ----------------

def check_age(patient, rules):
    age = patient.get("age")
    if age is None:
        return False, "Age missing"

    if rules.get("age_min") is not None and age < rules["age_min"]:
        return False, "Too young"

    if rules.get("age_max") is not None and age > rules["age_max"]:
        return False, "Too old"

    return True, None


def check_gender(patient, rules):
    allowed = rules.get("gender")
    if not allowed:
        return True, None

    if patient.get("gender") not in allowed:
        return False, "Gender not allowed"

    return True, None


def check_stage(patient, rules):
    allowed = rules.get("stage_allowed")
    if not allowed:
        return True, None

    p_stage = normalize_stage(patient.get("stage"))
    allowed_norm = [normalize_stage(s) for s in allowed]

    if not p_stage:
        return False, "Stage missing"

    if p_stage not in allowed_norm:
        return False, "Stage not allowed"

    return True, None


def check_mutations(patient, rules):
    required = rules.get("mutations_required", [])
    if not required:
        return True, None

    patient_muts = set(m.upper() for m in patient.get("mutations", []))
    for mut in required:
        if mut.upper() not in patient_muts:
            return False, f"Missing mutation: {mut}"

    return True, None


def check_prior_treatments(patient, rules):
    excluded = rules.get("prior_treatments_excluded", [])
    if not excluded:
        return True, None

    treatments = " ".join(patient.get("treatments", [])).lower()

    for ex in excluded:
        if not isinstance(ex, str):
            continue  # ← string değilse atla
        if ex.lower() in treatments:
            return False, f"Prior treatment excluded: {ex}"

    return True, None


def check_surgery_window(patient, rules):
    if not rules.get("surgery_required"):
        return True, None

    months = patient.get("months_after_surgery")
    if months is None:
        return False, "Surgery info missing"

    if rules.get("months_after_surgery_min") is not None:
        if months < rules["months_after_surgery_min"]:
            return False, "Too early after surgery"

    if rules.get("months_after_surgery_max") is not None:
        if months > rules["months_after_surgery_max"]:
            return False, "Too late after surgery"

    return True, None


def check_brain_metastasis(patient, rules):
    allowed = rules.get("brain_metastasis_allowed")
    if allowed is None:
        return True, None

    if patient.get("brain_metastasis") and not allowed:
        return False, "Brain metastasis not allowed"

    return True, None


def check_ecog(patient, rules):          # ← YENİ
    ecog_max = rules.get("ecog_max")
    if ecog_max is None:
        return True, None

    ecog = patient.get("ecog")
    if ecog is None:
        return False, "ECOG status missing"

    if ecog > ecog_max:
        return False, f"ECOG {ecog} exceeds max {ecog_max}"

    return True, None


# ---------------- RULE REGISTRY ----------------

RULE_CHECKS = [
    check_age,
    check_gender,
    check_stage,
    check_mutations,
    check_prior_treatments,
    check_surgery_window,
    check_brain_metastasis,
    check_ecog,            # ← YENİ
]


# ---------------- MATCHER ----------------

def match_patient(patient: dict, rules: dict):
    failed = []

    for check in RULE_CHECKS:
        ok, reason = check(patient, rules)
        if not ok:
            failed.append(reason)

    return {
        "eligible": len(failed) == 0,
        "failed_rules": failed
    }
import ast
import os
import re
import xml.etree.ElementTree as ET
import pandas as pd

PRESENCE_LABELS = ["Yes", "No"]
TYPE_LABELS = ["Disk Failure", "Software Node Failure", "Server Failure", "None"]
CRIT_LABELS = ["Low", "Medium", "High", "None"]

# the annotation XMLs use short type names, map them to the labels the LLM has to predict
TYPE_MAP = {"disk": "Disk Failure", "snode": "Software Node Failure", "server": "Server Failure"}

# Set paths here
CSV_PATH = "../LLM_results/Images/Gemini/Run 1/results.csv"
ANNOTATIONS_FOLDER = "../Annotations"
DATASETS_FOLDER = "../Dataset"
EXCLUDED_DATASETS = set()

DISK_RE = r"(g\d*disk\d+|ssd\d+)"


def xml_text(node, tag):
    n = node.find(tag)
    return (n.text or "").strip() if n is not None else ""


def load_ground_truth(annotations_folder):
    gt = {}
    for f in sorted(os.listdir(annotations_folder)):
        if not f.endswith(".xml"): continue
        root = ET.parse(os.path.join(annotations_folder, f)).getroot()
        presence = "Yes" if xml_text(root, "anomaly_presence").lower() == "true" else "No"
        raw_type, raw_crit = xml_text(root, "type"), xml_text(root, "criticality")
        if presence == "No" or raw_type.lower() in ["", "none"]: anomaly_type = "None"
        elif raw_type.lower() in TYPE_MAP: anomaly_type = TYPE_MAP[raw_type.lower()]
        else: raise ValueError(f"{f}: unknown anomaly type '{raw_type}', add it to TYPE_MAP")
        crit = "None" if presence == "No" or raw_crit.lower() in ["", "none"] else raw_crit.capitalize()
        # the same anomaly is repeated in every dimension it affects, keep each (store, disk) pair once
        pairs = set()
        for a in root.iter("anomaly"):
            store, disk = xml_text(a, "store").lower(), xml_text(a, "disk").lower()
            m_store, m_disk = re.search(r"\d+", store), re.search(DISK_RE, disk)
            pairs.add((f"store{int(m_store.group())}" if m_store else None, m_disk.group(0) if m_disk else (disk or None)))
        gt[f[:-4]] = {"anomaly_presence": presence, "anomaly_type": anomaly_type, "anomaly_criticality": crit, "anomalies": [{"store": s, "disk": d} for s, d in sorted(pairs, key=str)]}
    return gt


def index_datasets(base_folder):
    index = {}
    for r, _, files in os.walk(base_folder):
        for f in files:
            if not f.endswith(".csv"): continue
            if f[:-4] in index: print(f"WARNING: dataset {f[:-4]} found more than once, using {os.path.join(r, f)}")
            index[f[:-4]] = os.path.join(r, f)
    return index


def init_confusion(labels): return {l: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for l in labels}


def update_confusion(conf, y_true, y_pred):
    for label in conf:
        if y_true == label: conf[label]["support"] += 1
        if y_pred == label and y_true == label: conf[label]["tp"] += 1
        elif y_pred == label and y_true != label: conf[label]["fp"] += 1
        elif y_pred != label and y_true == label: conf[label]["fn"] += 1


def compute_scores(conf):
    per_class, f1s, supports = {}, [], []
    for label, v in conf.items():
        tp, fp, fn = v["tp"], v["fp"], v["fn"]
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": v["support"]}
        f1s.append(f1); supports.append(v["support"])
    macro_f1 = sum(f1s) / len(f1s)  # classes with zero support count as F1 = 0
    total = sum(supports)
    weighted_f1 = sum(f * s for f, s in zip(f1s, supports)) / total if total > 0 else 0
    return per_class, macro_f1, weighted_f1


def is_missing(x): return x is None or pd.isna(x) or str(x).lower() in ["none", "nan", ""]


def extract_store_disk(dim_name):
    if is_missing(dim_name): return None, None
    dim_name = str(dim_name).lower()
    store, disk = re.search(r"store\d+", dim_name), re.search(DISK_RE, dim_name)
    return (store.group(0) if store else None, disk.group(0) if disk else None)


def dimension_matches(pred_dim, gt_anomaly):
    pred_store, pred_disk = extract_store_disk(pred_dim)
    gt_store, gt_disk = gt_anomaly.get("store"), gt_anomaly.get("disk")
    if gt_store and gt_disk: return pred_store == gt_store and pred_disk == gt_disk
    if gt_store: return pred_store == gt_store
    return False


def parse_range(raw):
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, (list, tuple)) and len(parsed) == 2: return int(float(parsed[0])), int(float(parsed[1]))
    except Exception:
        pass
    return None, None


def time_matches(df, pred_dim, start, end):
    if start is None or end is None or is_missing(pred_dim): return False
    dim_lower = str(pred_dim).lower()
    store, disk = extract_store_disk(pred_dim)
    cols = [c for c in df.columns if c.startswith("label_") and dim_lower in c.lower()]
    if not cols:  # fallback: match by store (and disk if available)
        for c in df.columns:
            if not c.startswith("label_"): continue
            base = c.replace("label_", "").lower()
            if (store and disk and store in base and disk in base) or (store and store in base): cols.append(c)
    if not cols: return False
    for c in cols:
        s, e = max(0, start), min(len(df[c]) - 1, end)
        if df[c].iloc[s:e + 1].sum() > 0: return True
    return False


def evaluate_row(row, gt, df):
    if row["anomaly_presence"] == "No":
        both = gt["anomaly_presence"] == "No"
        return both, both
    dim, raw_time = row["anomaly_dimension"], row["anomaly_time_location"]
    dim_ok = (not is_missing(dim)) and any(dimension_matches(dim, a) for a in gt.get("anomalies", []))
    time_ok = False if is_missing(raw_time) else time_matches(df, dim, *parse_range(raw_time))
    return dim_ok, time_ok


def evaluate(csv_path, annotations_folder, datasets_folder):
    preds = pd.read_csv(csv_path)
    preds["dataset"] = preds["dataset"].astype(str).str.strip()
    preds = preds[~preds["dataset"].isin(EXCLUDED_DATASETS)]
    gt_data, dataset_map = load_ground_truth(annotations_folder), index_datasets(datasets_folder)
    confs = {"presence": init_confusion(PRESENCE_LABELS), "type": init_confusion(TYPE_LABELS), "criticality": init_confusion(CRIT_LABELS)}
    dim_correct = time_correct = total = 0
    skipped, cache = [], {}

    for _, row in preds.iterrows():
        ds = row["dataset"]
        if ds not in dataset_map or ds not in gt_data:
            skipped.append(ds); continue
        if ds not in cache: cache[ds] = pd.read_csv(dataset_map[ds])
        gt, df = gt_data[ds], cache[ds]
        update_confusion(confs["presence"], gt["anomaly_presence"], row["anomaly_presence"])
        update_confusion(confs["type"], gt["anomaly_type"], row["anomaly_type"])
        update_confusion(confs["criticality"], gt["anomaly_criticality"], row["anomaly_criticality"])
        dim_ok, time_ok = evaluate_row(row, gt, df)
        dim_correct += int(dim_ok); time_correct += int(time_ok); total += 1

    if total == 0: raise SystemExit("No evaluable rows: check that dataset ids match the annotation files and the dataset folder.")
    print(f"Rows in CSV (after exclusions): {len(preds)} | evaluated: {total} | skipped (missing annotation or dataset file): {len(skipped)}")
    if skipped: print(f"  skipped ids: {skipped}")
    print(f"\nDimension localization accuracy: {dim_correct / total:.3f} ({dim_correct}/{total})")
    print(f"Time localization accuracy:      {time_correct / total:.3f} ({time_correct}/{total})")
    for name, conf in confs.items():
        per_class, macro, weighted = compute_scores(conf)
        print(f"\n{name.capitalize()} | macro-F1 = {macro:.3f} | weighted-F1 = {weighted:.3f}")
        for label, m in per_class.items(): print(f"  {label:<22} P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} support={m['support']}")


if __name__ == "__main__":
    evaluate(CSV_PATH, ANNOTATIONS_FOLDER, DATASETS_FOLDER)
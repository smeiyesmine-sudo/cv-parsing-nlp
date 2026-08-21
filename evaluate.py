"""Evaluation of skill extraction against a gold-annotated test set.

Gold file format (JSON): a list of entries
  [{"file": "samples/cv1.txt", "skills": ["python", "docker", ...]}, ...]
where "skills" are the canonical names expected from the database.

Usage:
    python -m cv_parser.evaluate gold.json
"""
import json
import sys

from .pipeline import parse_cv


def prf(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    return {"precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "tp": tp, "fp": fp, "fn": fn}


def evaluate(gold_path: str) -> dict:
    with open(gold_path, encoding="utf-8") as f:
        gold = json.load(f)

    total_tp = total_fp = total_fn = 0
    per_file = []
    for entry in gold:
        predicted = {s["skill"] for s in parse_cv(entry["file"])["skills"]}
        expected = set(entry["skills"])
        tp = len(predicted & expected)
        fp = len(predicted - expected)
        fn = len(expected - predicted)
        total_tp += tp; total_fp += fp; total_fn += fn
        per_file.append({
            "file": entry["file"],
            **prf(tp, fp, fn),
            "false_positives": sorted(predicted - expected),
            "missed": sorted(expected - predicted),
        })

    return {"overall": prf(total_tp, total_fp, total_fn), "per_file": per_file}


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m cv_parser.evaluate <gold.json>")
        sys.exit(1)
    print(json.dumps(evaluate(sys.argv[1]), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

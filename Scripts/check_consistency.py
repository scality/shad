"""Cross-check the CSV labels against the XML annotations.

For every anomalous series it verifies that

1. the dimensions labelled in the CSV are the dimensions annotated in the XML;
2. each annotated event starts within ``--tolerance`` minutes of a labelled
   period on its dimensions (times measured from the first CSV timestamp).

Usage (from the repository root):

    python Scripts/check_consistency.py [--tolerance 6]
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shad import SHAD  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerance", type=float, default=6.0, help="minutes")
    args = ap.parse_args()
    ds = SHAD()
    issues = 0
    for sid in ds.filter():
        s = ds.load(sid)
        if not s.is_anomalous:
            if s.y.any():
                print(f"[{sid}] nominal series with positive labels")
                issues += 1
            continue
        minutes = (s.data.index - s.data.index[0]).total_seconds().to_numpy() / 60
        csv_dims = set(s.anomalous_dimensions)
        xml_dims = set(s.annotation.anomalous_dimensions)
        if csv_dims != xml_dims:
            issues += 1
            print(f"[{sid}] {s.group}: labelled dimensions differ from the XML "
                  f"(only CSV: {len(csv_dims - xml_dims)}, only XML: {len(xml_dims - csv_dims)})")
        for e in s.events:
            dims = [d for d in e.related_dimensions if d in s.labels.columns]
            if not dims or e.offset_minutes is None:
                continue
            lab = s.labels[dims].to_numpy().max(axis=1)
            starts = minutes[np.flatnonzero(np.diff(np.r_[0, lab]) == 1)]
            if not len(starts) or np.min(np.abs(starts - e.offset_minutes)) > args.tolerance:
                issues += 1
                found = ", ".join(f"{m:.0f}" for m in starts) or "none"
                print(f"[{sid}] {s.group}: event on {e.component} annotated at {e.offset_minutes} min, "
                      f"labelled periods on its dimensions start at: {found} min")
    print(f"\n{issues} potential issue(s) found.")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())

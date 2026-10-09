"""A minimal semi-supervised baseline on SHAD (numpy only).

The detector learns per-dimension robust statistics (median / MAD) on the
nominal series and scores every timestamp of the anomalous series by its
mean absolute robust z-score. It also produces a per-dimension score, which we
use to measure *explainability* (is the top-ranked dimension a labelled one?).

For the full benchmark (18 detectors, VUS-PR) see TSB-AD:
https://github.com/TheDatumOrg/TSB-AD

    python examples/baseline_detector.py
"""

import numpy as np

from shad import SHAD


def average_precision(y, score):
    """Point-wise area under the precision-recall curve."""
    order = np.argsort(-score)
    y = y[order]
    tp = np.cumsum(y)
    precision = tp / np.arange(1, len(y) + 1)
    return float((precision * y).sum() / max(y.sum(), 1))


def main():
    ds = SHAD()
    train_ids, test_ids = ds.split()

    # 1. fit robust statistics on nominal data
    X_train = np.concatenate([ds.load(i, fill="ffill").X for i in train_ids])
    med = np.nanmedian(X_train, axis=0)
    mad = np.nanmedian(np.abs(X_train - med), axis=0) * 1.4826
    mad[mad < 1e-9] = np.nanstd(X_train, axis=0)[mad < 1e-9] + 1e-9

    # 2. score anomalous series
    results = []
    for sid in test_ids:
        s = ds.load(sid, fill="ffill")
        z = np.clip(np.abs((s.X - med) / mad), 0, 50)       # (n, 171)
        score = z.mean(axis=1)                             # detection score
        ap = average_precision(s.y, score)
        # explanation: rank dimensions by their score inside the anomalous period
        dim_score = z[s.y == 1].mean(axis=0)
        top1 = s.dimensions[int(np.argmax(dim_score))]
        hit = top1 in s.anomalous_dimensions
        results.append((s.group, ap, hit))

    print(f"{'group':22s} {'AP':>6s} {'top-1 dim hit':>14s}")
    groups = sorted({g for g, _, _ in results})
    for g in groups:
        r = [(ap, hit) for gg, ap, hit in results if gg == g]
        print(f"{g:22s} {np.mean([a for a, _ in r]):6.3f} {np.mean([h for _, h in r]):14.2f}")
    print(f"{'ALL':22s} {np.mean([a for _, a, _ in results]):6.3f} "
          f"{np.mean([h for _, _, h in results]):14.2f}")


if __name__ == "__main__":
    main()

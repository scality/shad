"""SHAD quick start: load a series, inspect its labels and annotation.

    python examples/quickstart.py
"""

from shad import SHAD

ds = SHAD()  # finds the repository automatically (or SHAD(root="path/to/shad"))
print(ds)
print(ds.summary().to_string(index=False), "\n")

# ---- one anomalous series ------------------------------------------------
s = ds.load("1773343796")  # Single Disk failure on store1 / g2disk01
print(s)
print("Explanation :", s.explanation)
print("Criticality :", s.criticality)
print("Shapes      : X", s.X.shape, "| y", s.y.shape, "| Y", s.Y.shape)
print("Anomalous intervals (row indices):", s.segments())
print("Labelled dimensions:", s.anomalous_dimensions)

for e in s.events:
    print(f"Event on {e.component}: onset {e.offset_minutes} min after launch, "
          f"duration {e.duration_minutes} min, {len(e.related_dimensions)} dimensions")

# ---- the benchmark split used in the paper ------------------------------
train_ids, test_ids = ds.split()
print(f"\n{len(train_ids)} nominal series for training, {len(test_ids)} anomalous for testing")

# ---- plot (requires matplotlib) ------------------------------------------
try:
    fig = s.plot()
    fig.savefig("quickstart.png", dpi=120)
    print("saved quickstart.png")
except ImportError:
    pass

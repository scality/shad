"""SHAD - Scality High-dimensional Anomaly Detection benchmark.

Quick start::

    from shad import SHAD
    ds = SHAD()                      # run from the repository (or set SHAD_ROOT)
    print(ds.summary())
    s = ds.load("1773343796")
    s.data      # (n, 171) telemetry, DatetimeIndex
    s.labels    # (n, 171) per-dimension labels
    s.label     # (n,) top-level label
    s.events    # annotated anomaly events (from the XML)
"""

from .annotations import Annotation, AnomalyEvent, parse_annotation
from .dataset import (GROUP_TYPE, GROUPS, SHAD, Series, find_root, list_series,
                      load_annotation, load_series, read_csv)
from .metrics import (DATA_DISKS, DEVICES, LABEL_COLUMNS, METRICS, STORES, MetricInfo,
                      harmonize_name, metric_info, metrics_table, select)

__version__ = "1.0.0"

__all__ = [
    "SHAD", "Series", "Annotation", "AnomalyEvent",
    "load_series", "load_annotation", "list_series", "read_csv", "parse_annotation", "find_root",
    "GROUPS", "GROUP_TYPE", "METRICS", "LABEL_COLUMNS", "STORES", "DEVICES", "DATA_DISKS",
    "MetricInfo", "metric_info", "metrics_table", "select", "harmonize_name",
]

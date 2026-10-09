"""Canonical list of the 171 SHAD dimensions and their documentation.

Every SHAD time series has exactly the same 171 dimensions, organised in four
hierarchical levels:

* ``platform`` (17)  - cluster-wide aggregates (all servers + supervisor)
* ``s3``       (13)  - S3 connector / application level metrics
* ``server``   (57)  - 19 metrics x 3 storage servers (``store1``..``store3``)
* ``device``   (84)  - 4 metrics x 7 devices x 3 storage servers

Column names follow the pattern ``<metric>`` (platform / S3),
``<store>-<metric>`` (server) and ``<store>-<device>-<metric>`` (device).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

STORES: List[str] = ["store1", "store2", "store3"]

#: Physical devices of every storage server.
DEVICES: List[str] = ["g1disk01", "g1disk02", "g2disk01", "g2disk02", "root", "ssd01", "ssd02"]

#: NVMe data disks (the ones targeted by disk-failure anomalies).
DATA_DISKS: List[str] = ["g1disk01", "g1disk02", "g2disk01", "g2disk02"]

PLATFORM_METRICS: Dict[str, str] = {
    "cpu_usage_ratio": "(ratio, 0-1) Fraction of CPU time not idle, averaged across all servers.",
    "cpu_load_ratio": "(ratio, >= 0) CPU load average across all servers, normalised by CPU count. Can exceed 1.0 when the run queue is longer than the CPU count.",
    "memory_usage_ratio": "(ratio, 0-1) Fraction of total used memory, averaged across all servers.",
    "network_in_bytes": "(bytes/s) Sum of incoming network throughput across all interfaces of all servers (S3 traffic, inter-node traffic, monitoring, ...).",
    "network_out_bytes": "(bytes/s) Sum of outgoing network throughput across all interfaces of all servers (S3 traffic, inter-node traffic, monitoring, ...).",
    "objects_count": "(count) Number of objects stored on the RING, including replicas.",
    "objects_unique_count": "(count) Number of unique (logical) objects stored on the RING, regardless of replica count.",
    "objects_missing_count": "(count) Number of objects with missing or out-of-service chunks.",
    "capacity_disk_unique_tb": "(TB) Total stored data of unique objects before replication (logical data size).",
    "capacity_disk_stored_tb": "(TB) Total stored data including replicas.",
    "capacity_disk_used_tb": "(TB) Total disk space actually consumed, including overheads beyond stored object sizes.",
    "capacity_disk_available_tb": "(TB) Total free disk space on the RING.",
    "capacity_disk_total_tb": "(TB) Total physical disk capacity. Static unless disks are removed from the RING.",
    "disk_read_bytes": "(bytes/s) Total disk read throughput summed across all disks.",
    "disk_write_bytes": "(bytes/s) Total disk write throughput summed across all disks.",
    "disk_io_time_seconds": "(s/s, 0-1) Fraction of time spent on I/O averaged across all disks. 1.0 means fully saturated.",
    "disk_errors_count": "(count) Overall error count across all disks.",
}

S3_METRICS: Dict[str, str] = {
    "s3_errors_5xx": "(errors/s) Rate of HTTP 5xx server errors across all S3 services.",
    "s3_request_get_operations": "(ops/s) GET request rate.",
    "s3_request_post_operations": "(ops/s) POST request rate (near constant: the nominal workload does not use multipart uploads).",
    "s3_request_put_operations": "(ops/s) PUT request rate.",
    "s3_request_delete_operations": "(ops/s) DELETE request rate.",
    "s3_request_head_operations": "(ops/s) HEAD request rate (metadata lookups).",
    "s3_throughput_in_bytes": "(bytes/s) Client-to-S3 data rate.",
    "s3_throughput_out_bytes": "(bytes/s) S3-to-client data rate (dominates throughput_in in the GET-heavy workload).",
    "s3_request_get_latency": "(s) 95th percentile GET request duration.",
    "s3_request_post_latency": "(s) 95th percentile POST request duration. Near constant in the nominal workload.",
    "s3_request_put_latency": "(s) 95th percentile PUT request duration.",
    "s3_request_delete_latency": "(s) 95th percentile DELETE request duration.",
    "s3_request_head_latency": "(s) 95th percentile HEAD request duration.",
}

# Alphabetical order = column order in the CSV files.
SERVER_METRICS: Dict[str, str] = {
    "balance_balanced_tasks": "(tasks/s) Rate of chunks actually rebalanced.",
    "balance_scanned_tasks": "(tasks/s) Rate of balance scanning. Rebalancing redistributes data when disk usage is uneven; may activate after disk-failure recovery.",
    "cpu_load_ratio": "(ratio, >= 0) CPU load average normalised by CPU count. Can exceed 1.0 under saturation.",
    "cpu_usage_ratio": "(ratio, 0-1) Fraction of CPU time not idle.",
    "errors_received": "(errors/s) Rate of failed inbound RING operations.",
    "errors_sent": "(errors/s) Rate of failed outbound RING operations.",
    "latency_received_milliseconds": "(ms) Average local processing time for RING operations received by this server.",
    "latency_sent_milliseconds": "(ms) Average round-trip time for RING operations sent by this server.",
    "memory_usage_ratio": "(ratio, 0-1) Fraction of total used memory.",
    "network_in_bytes": "(bytes/s) All incoming network throughput (S3 client traffic, RING inter-node traffic, monitoring, ...).",
    "network_out_bytes": "(bytes/s) All outgoing network throughput (S3 client traffic, RING inter-node traffic, monitoring, ...).",
    "operations_received": "(ops/s) Rate of internal RING operations received from other servers.",
    "operations_sent": "(ops/s) Rate of internal RING operations sent to other servers.",
    "rebuild_rebuilt_tasks": "(tasks/s) Rate of chunks actually rebuilt.",
    "rebuild_scanned_tasks": "(tasks/s) Rate of rebuild scanning. Rebuild reconstructs missing data replicas.",
    "repair_repaired_tasks": "(tasks/s) Rate of chunks actually repaired.",
    "repair_scanned_tasks": "(tasks/s) Rate of repair scanning. Repair fixes data-integrity issues (corrupted chunks, checksum mismatches).",
    "throughput_received_bytes": "(bytes/s) Data payload received via RING operations.",
    "throughput_sent_bytes": "(bytes/s) Data payload (object chunks) sent via RING operations.",
}

DEVICE_METRICS: Dict[str, str] = {
    "disk_io_time_seconds": "(s/s, 0-1) Fraction of time spent on I/O. Close to 1.0 means the disk is saturated.",
    "disk_read_bytes": "(bytes/s) Disk read throughput.",
    "disk_usage_ratio": "(ratio, 0-1) Disk space utilisation.",
    "disk_write_bytes": "(bytes/s) Disk write throughput.",
}

DEVICE_DESCRIPTIONS: Dict[str, str] = {
    "g1disk01": "NVMe data disk (RING object data)",
    "g1disk02": "NVMe data disk (RING object data)",
    "g2disk01": "NVMe data disk (RING object data)",
    "g2disk02": "NVMe data disk (RING object data)",
    "root": "OS root disk (/)",
    "ssd01": "SSD for S3 metadata and small objects",
    "ssd02": "SSD for S3 metadata and small objects",
}


def _build_columns() -> List[str]:
    cols: List[str] = list(PLATFORM_METRICS) + list(S3_METRICS)
    for m in SERVER_METRICS:
        cols += [f"{s}-{m}" for s in STORES]
    for m in DEVICE_METRICS:
        for s in STORES:
            cols += [f"{s}-{d}-{m}" for d in DEVICES]
    return cols


#: The 171 dimensions, in the canonical column order of the CSV files.
METRICS: List[str] = _build_columns()
assert len(METRICS) == 171

#: The 171 per-dimension label columns, same order as :data:`METRICS`.
LABEL_COLUMNS: List[str] = [f"label_{m}" for m in METRICS]


@dataclass(frozen=True)
class MetricInfo:
    """Structured description of one SHAD dimension."""

    name: str
    level: str  # "platform" | "s3" | "server" | "device"
    metric: str  # base metric name, e.g. "disk_read_bytes"
    store: Optional[str]  # "store1".."store3" or None
    device: Optional[str]  # "g1disk01", ..., or None
    unit: str
    description: str


_UNIT_RE = re.compile(r"^\(([^)]*)\)\s*")


def _split_unit(desc: str):
    m = _UNIT_RE.match(desc)
    if not m:
        return "", desc
    return m.group(1).split(",")[0].strip(), desc[m.end():]


def metric_info(name: str) -> MetricInfo:
    """Return the :class:`MetricInfo` of a dimension (accepts legacy ``s0-`` names)."""
    name = harmonize_name(name)
    if name.startswith("label_"):
        name = name[len("label_"):]
    if name in PLATFORM_METRICS:
        level, metric, store, device, desc = "platform", name, None, None, PLATFORM_METRICS[name]
    elif name in S3_METRICS:
        level, metric, store, device, desc = "s3", name, None, None, S3_METRICS[name]
    else:
        parts = name.split("-")
        if len(parts) == 2 and parts[1] in SERVER_METRICS:
            level, (store, metric), device = "server", parts, None
            desc = SERVER_METRICS[metric]
        elif len(parts) == 3 and parts[2] in DEVICE_METRICS:
            level, (store, device, metric) = "device", parts
            desc = f"{DEVICE_METRICS[metric]} Device: {DEVICE_DESCRIPTIONS.get(device, device)}."
        else:
            raise KeyError(f"Unknown SHAD dimension: {name!r}")
    unit, text = _split_unit(desc)
    return MetricInfo(name, level, metric, store, device, unit, text)


_LEGACY_RE = re.compile(r"(^|label_)s([0-2])-")


def harmonize_name(name: str) -> str:
    """Map legacy column names to the canonical ones.

    Some nominal series were exported with ``s0-``/``s1-``/``s2-`` prefixes
    instead of ``store1-``/``store2-``/``store3-``. This function maps them to
    the canonical names (``s0`` -> ``store1``, etc.).
    """
    return _LEGACY_RE.sub(lambda m: f"{m.group(1)}store{int(m.group(2)) + 1}-", name)


def metrics_table():
    """Return a :class:`pandas.DataFrame` documenting the 171 dimensions."""
    import pandas as pd

    return pd.DataFrame([metric_info(m).__dict__ for m in METRICS])


def select(level: Optional[str] = None, store: Optional[str] = None,
           device: Optional[str] = None, metric: Optional[str] = None) -> List[str]:
    """Select dimension names by level / store / device / base metric.

    >>> select(level="device", store="store1", device="g2disk01")
    ['store1-g2disk01-disk_io_time_seconds', 'store1-g2disk01-disk_read_bytes', ...]
    """
    out = []
    for m in METRICS:
        i = metric_info(m)
        if level is not None and i.level != level:
            continue
        if store is not None and i.store != store:
            continue
        if device is not None and i.device != device:
            continue
        if metric is not None and i.metric != metric:
            continue
        out.append(m)
    return out

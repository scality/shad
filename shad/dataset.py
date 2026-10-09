"""Loading SHAD time series, labels and annotations."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from .annotations import Annotation, AnomalyEvent, parse_annotation
from .metrics import LABEL_COLUMNS, METRICS, harmonize_name

PathLike = Union[str, Path]
SeriesId = Union[str, int]

#: The ten experiment groups (folders of ``Dataset/``), in presentation order.
GROUPS: List[str] = [
    "Nominal",
    "Single Disk", "Simultaneous Disk", "Asynchronous Disk",
    "Single Server", "Asynchronous Server", "Server Degradation",
    "Single SNode", "Simultaneous SNode", "Asynchronous SNode",
]

#: Anomaly family (``type`` in the XML) of each group.
GROUP_TYPE = {
    "Nominal": "None",
    "Single Disk": "Disk", "Simultaneous Disk": "Disk", "Asynchronous Disk": "Disk",
    "Single Server": "Server", "Asynchronous Server": "Server", "Server Degradation": "Server",
    "Single SNode": "SNode", "Simultaneous SNode": "SNode", "Asynchronous SNode": "SNode",
}


# --------------------------------------------------------------------------- #
# Locating the data
# --------------------------------------------------------------------------- #
def _is_root(p: Path) -> bool:
    return (p / "Dataset").is_dir() and (p / "Annotations").is_dir()


def find_root(root: Optional[PathLike] = None) -> Path:
    """Locate the SHAD data folder (the one containing ``Dataset/`` and ``Annotations/``).

    Resolution order: explicit ``root`` argument, ``$SHAD_ROOT`` environment
    variable, the current working directory and its parents, then the
    repository this package lives in.
    """
    candidates: List[Path] = []
    if root is not None:
        candidates.append(Path(root).expanduser())
    if os.environ.get("SHAD_ROOT"):
        candidates.append(Path(os.environ["SHAD_ROOT"]).expanduser())
    cwd = Path.cwd().resolve()
    candidates += [cwd, *cwd.parents]
    candidates.append(Path(__file__).resolve().parent.parent)
    for c in candidates:
        if _is_root(c):
            return c.resolve()
    if root is not None:
        raise FileNotFoundError(f"{root} does not contain 'Dataset/' and 'Annotations/' folders.")
    raise FileNotFoundError(
        "Could not locate the SHAD data. Clone https://github.com/scality/shad and either run "
        "from inside the repository, pass root='path/to/shad', or set the SHAD_ROOT variable.")


# --------------------------------------------------------------------------- #
# One time series
# --------------------------------------------------------------------------- #
@dataclass
class Series:
    """One SHAD multivariate time series with its labels and annotation.

    Attributes
    ----------
    id : str
        Experiment id (the unix timestamp of the experiment start).
    group : str
        Experiment group, e.g. ``"Single Disk"`` or ``"Nominal"``.
    data : pandas.DataFrame
        ``(n_timestamps, 171)`` telemetry indexed by UTC timestamp (1-minute sampling).
    labels : pandas.DataFrame
        ``(n_timestamps, 171)`` per-dimension binary labels (same columns as ``data``).
    label : pandas.Series
        ``(n_timestamps,)`` top-level binary label (1 = an anomaly is ongoing).
    annotation : Annotation
        Parsed XML annotation (metadata, per-dimension descriptions, events).
    """

    id: str
    group: str
    data: pd.DataFrame
    labels: pd.DataFrame
    label: pd.Series
    annotation: Annotation = field(repr=False)

    # --- numpy views ---------------------------------------------------- #
    @property
    def X(self) -> np.ndarray:
        """Telemetry as a float array of shape ``(n_timestamps, 171)``."""
        return self.data.to_numpy(dtype=float)

    @property
    def y(self) -> np.ndarray:
        """Top-level labels, shape ``(n_timestamps,)``."""
        return self.label.to_numpy(dtype=np.int8)

    @property
    def Y(self) -> np.ndarray:
        """Per-dimension labels, shape ``(n_timestamps, 171)``."""
        return self.labels.to_numpy(dtype=np.int8)

    # --- metadata shortcuts -------------------------------------------- #
    @property
    def dimensions(self) -> List[str]:
        return list(self.data.columns)

    @property
    def is_anomalous(self) -> bool:
        return bool(self.annotation.anomaly_presence)

    @property
    def category(self) -> str:
        return self.annotation.category

    @property
    def type(self) -> str:
        return self.annotation.type

    @property
    def criticality(self) -> str:
        return self.annotation.criticality

    @property
    def explanation(self) -> str:
        return self.annotation.explanation

    @property
    def events(self) -> List[AnomalyEvent]:
        return self.annotation.events

    @property
    def anomalous_dimensions(self) -> List[str]:
        """Dimensions with at least one positive per-dimension label."""
        return [c for c in self.labels.columns if self.labels[c].any()]

    def segments(self, dimension: Optional[str] = None) -> List[Tuple[int, int]]:
        """Anomalous intervals as ``(start, end)`` row indices (``end`` exclusive).

        With ``dimension=None`` the top-level label is used.
        """
        y = self.y if dimension is None else self.labels[harmonize_name(dimension)].to_numpy()
        d = np.diff(np.r_[0, y.astype(np.int8), 0])
        return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return (f"Series(id={self.id}, group={self.group!r}, shape={self.data.shape}, "
                f"anomaly_ratio={self.label.mean():.3f}, "
                f"anomalous_dimensions={len(self.anomalous_dimensions)})")

    # --- plotting ------------------------------------------------------- #
    def plot(self, dimensions: Optional[Sequence[str]] = None, max_dimensions: int = 12,
             ncols: int = 3, figsize_per_row: float = 1.8):
        """Plot a few dimensions with their anomalous intervals shaded.

        By default the (first ``max_dimensions``) labelled dimensions are shown,
        or the first platform metrics for nominal series. Requires matplotlib.
        """
        import matplotlib.pyplot as plt

        if dimensions is None:
            dimensions = self.anomalous_dimensions or self.dimensions
        dimensions = [harmonize_name(d) for d in dimensions][:max_dimensions]
        nrows = int(np.ceil(len(dimensions) / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, figsize_per_row * nrows),
                                 sharex=True, squeeze=False)
        t = np.arange(len(self))
        glob = self.segments()
        for ax, dim in zip(axes.ravel(), dimensions):
            ax.plot(t, self.data[dim].to_numpy(), lw=1, color="#2a78d6")
            for s, e in glob:
                ax.axvspan(s, e, color="#e34948", alpha=0.08, lw=0)
            for s, e in self.segments(dim):
                ax.axvspan(s, e, color="#e34948", alpha=0.25, lw=0)
            ax.set_title(dim, fontsize=8)
            ax.tick_params(labelsize=7)
        for ax in axes.ravel()[len(dimensions):]:
            ax.axis("off")
        fig.suptitle(f"SHAD {self.id} - {self.group}", fontsize=10)
        fig.supxlabel("minutes since start", fontsize=8)
        fig.tight_layout()
        return fig


# --------------------------------------------------------------------------- #
# Reading files
# --------------------------------------------------------------------------- #
def _fill(df: pd.DataFrame, how: Optional[str]) -> pd.DataFrame:
    if how is None:
        return df
    if how == "ffill":
        return df.ffill().bfill()
    if how == "interpolate":
        return df.interpolate(limit_direction="both")
    if how == "zero":
        return df.fillna(0.0)
    raise ValueError("fill must be one of None, 'ffill', 'interpolate', 'zero'")


def read_csv(path: PathLike, fill: Optional[str] = None
             ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Read one SHAD CSV file.

    Returns ``(data, labels, label)`` with harmonised column names and the
    canonical column order. ``fill`` optionally imputes missing values
    (``"ffill"``, ``"interpolate"`` or ``"zero"``).
    """
    df = pd.read_csv(path)
    df.columns = [harmonize_name(c) for c in df.columns]
    ts = pd.to_datetime(df["metric_timestamp"], utc=True, format="ISO8601")
    missing = [c for c in METRICS + LABEL_COLUMNS + ["label"] if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing[:5]}...")
    data = df[METRICS].astype(float)
    data.index = pd.DatetimeIndex(ts, name="timestamp")
    data = _fill(data, fill)
    labels = df[LABEL_COLUMNS].astype(np.int8)
    labels.columns = METRICS
    labels.index = data.index
    label = df["label"].astype(np.int8).rename("label")
    label.index = data.index
    return data, labels, label


class SHAD:
    """Entry point to the SHAD benchmark.

    >>> from shad import SHAD
    >>> ds = SHAD()                  # auto-detects the repository
    >>> ds.catalog.head()            # one row per series
    >>> s = ds.load("1773343796")    # a Series object
    >>> s.X.shape, s.y.mean()
    """

    def __init__(self, root: Optional[PathLike] = None):
        self.root = find_root(root)
        self.dataset_dir = self.root / "Dataset"
        self.annotation_dir = self.root / "Annotations"

    # ------------------------------------------------------------------ #
    @property
    def catalog(self) -> pd.DataFrame:
        """One row per series: id, group, type, category, criticality, explanation, paths."""
        return _catalog(str(self.root)).copy()

    @property
    def ids(self) -> List[str]:
        return self.catalog["id"].tolist()

    def __len__(self) -> int:
        return len(self.ids)

    def __iter__(self) -> Iterator[Series]:
        for i in self.ids:
            yield self.load(i)

    def __getitem__(self, series_id: SeriesId) -> Series:
        return self.load(series_id)

    def __repr__(self) -> str:
        cat = self.catalog
        return (f"SHAD(root={str(self.root)!r}, series={len(cat)}, "
                f"nominal={int((cat.group == 'Nominal').sum())}, "
                f"anomalous={int((cat.group != 'Nominal').sum())})")

    # ------------------------------------------------------------------ #
    def _row(self, series_id: SeriesId) -> pd.Series:
        cat = self.catalog.set_index("id")
        sid = str(series_id)
        if sid not in cat.index:
            raise KeyError(f"Unknown SHAD series id {sid!r}")
        return cat.loc[sid]

    def path(self, series_id: SeriesId) -> Path:
        """Path of the CSV file of a series."""
        return Path(self._row(series_id)["csv_path"])

    def annotation(self, series_id: SeriesId) -> Annotation:
        """Parsed XML annotation of a series."""
        return parse_annotation(self.annotation_dir / f"{series_id}.xml")

    def load(self, series_id: SeriesId, fill: Optional[str] = None) -> Series:
        """Load one series (telemetry, labels, annotation)."""
        row = self._row(series_id)
        data, labels, label = read_csv(row["csv_path"], fill=fill)
        return Series(id=str(series_id), group=row["group"], data=data, labels=labels,
                      label=label, annotation=self.annotation(series_id))

    def filter(self, group: Union[str, Iterable[str], None] = None,
               type: Union[str, Iterable[str], None] = None,
               category: Union[str, Iterable[str], None] = None,
               criticality: Union[str, Iterable[str], None] = None,
               exclude_broken: bool = False) -> List[str]:
        """Return the ids matching the given metadata filters.

        >>> ds.filter(type="Disk", criticality="High")
        """
        cat = self.catalog
        for col, val in (("group", group), ("type", type), ("category", category),
                         ("criticality", criticality)):
            if val is None:
                continue
            vals = [val] if isinstance(val, str) else list(val)
            cat = cat[cat[col].isin(vals)]
        if exclude_broken:
            cat = cat[~cat["broken_telemetry"]]
        return cat["id"].tolist()

    def split(self, exclude_broken: bool = False) -> Tuple[List[str], List[str]]:
        """Benchmark split used in the paper: ``(train_ids, test_ids)``.

        Semi-supervised detectors are trained on the 83 nominal series and every
        method is evaluated on the 132 anomalous series.
        """
        train = self.filter(group="Nominal")
        test = [i for i in self.filter(exclude_broken=exclude_broken) if i not in set(train)]
        return train, test

    def summary(self) -> pd.DataFrame:
        """Number of series per group, with type / category / criticality."""
        cat = self.catalog
        out = (cat.groupby(["group", "type", "category", "criticality"], sort=False)
                  .size().rename("series").reset_index())
        out["order"] = out["group"].map({g: i for i, g in enumerate(GROUPS)})
        return out.sort_values("order").drop(columns="order").reset_index(drop=True)


@lru_cache(maxsize=8)
def _catalog(root: str) -> pd.DataFrame:
    root_p = Path(root)
    rows = []
    for csv in sorted((root_p / "Dataset").glob("*/*.csv")):
        sid = csv.stem
        xml = root_p / "Annotations" / f"{sid}.xml"
        ann = parse_annotation(xml) if xml.exists() else None
        rows.append({
            "id": sid,
            "group": csv.parent.name,
            "type": ann.type if ann else GROUP_TYPE.get(csv.parent.name, "?"),
            "category": ann.category if ann else "?",
            "criticality": ann.criticality if ann else "?",
            "anomaly_presence": ann.anomaly_presence if ann else None,
            "n_events": len(ann.events) if ann else None,
            "broken_telemetry": ann.broken_telemetry if ann else False,
            "explanation": ann.explanation if ann else "",
            "csv_path": str(csv),
            "xml_path": str(xml) if xml.exists() else None,
        })
    cat = pd.DataFrame(rows)
    order = {g: i for i, g in enumerate(GROUPS)}
    cat["_o"] = cat["group"].map(lambda g: order.get(g, 99))
    return cat.sort_values(["_o", "id"]).drop(columns="_o").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Functional shortcuts
# --------------------------------------------------------------------------- #
def load_series(series_id: SeriesId, root: Optional[PathLike] = None,
                fill: Optional[str] = None) -> Series:
    """Load one series. Shortcut for ``SHAD(root).load(series_id)``."""
    return SHAD(root).load(series_id, fill=fill)


def load_annotation(series_id: SeriesId, root: Optional[PathLike] = None) -> Annotation:
    """Load the XML annotation of one series."""
    return SHAD(root).annotation(series_id)


def list_series(root: Optional[PathLike] = None) -> pd.DataFrame:
    """Return the catalog of all SHAD series."""
    return SHAD(root).catalog

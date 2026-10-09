"""Parsing of the SHAD XML annotations.

Each series ``<id>`` comes with ``Annotations/<id>.xml``::

    <dataset>
      <id/> <anomaly_presence/> <category/> <type/> <criticality/>
      <textual_explanation/>
      <dimensions>
        <dimension>
          <name/> <description/>
          <anomalies>
            <anomaly>
              <offset_minutes/> <duration_minutes/> <store/> <disk/>
              <degradation/>
              <related_dimensions> <dimension/>... </related_dimensions>
            </anomaly>
          </anomalies>
        </dimension>
        ...
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .metrics import harmonize_name


def _text(node, tag, default=None):
    if node is None:
        return default
    child = node.find(tag)
    if child is None or child.text is None:
        return default
    t = child.text.strip()
    return t if t else default


def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class AnomalyEvent:
    """One injected anomaly (root cause), as annotated by Scality experts.

    ``offset_minutes`` is counted from the start of the experiment,
    ``related_dimensions`` lists every dimension directly targeted by this event.
    """

    offset_minutes: Optional[int]
    duration_minutes: Optional[int]
    store: Optional[str]
    disk: Optional[str]
    degradation: Optional[str]
    related_dimensions: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def end_minutes(self) -> Optional[int]:
        if self.offset_minutes is None or self.duration_minutes is None:
            return None
        return self.offset_minutes + self.duration_minutes

    @property
    def component(self) -> str:
        """Human readable target, e.g. ``store1/g2disk01`` or ``store3``."""
        s = f"store{self.store}" if self.store else "?"
        return f"{s}/{self.disk}" if self.disk else s

    def to_dict(self) -> dict:
        return {
            "offset_minutes": self.offset_minutes,
            "duration_minutes": self.duration_minutes,
            "store": self.store,
            "disk": self.disk,
            "degradation": self.degradation,
            "component": self.component,
            "related_dimensions": list(self.related_dimensions),
        }


@dataclass
class Annotation:
    """Parsed content of one SHAD XML annotation file."""

    id: str
    anomaly_presence: bool
    category: str  # None | Single | Simultaneous | Asynchronous | Degradation
    type: str  # None | Disk | Server | SNode
    criticality: str  # None | Low | Medium | High
    explanation: str
    descriptions: Dict[str, str]
    dimension_anomalies: Dict[str, List[AnomalyEvent]]

    # ------------------------------------------------------------------ #
    @property
    def dimensions(self) -> List[str]:
        """The 171 dimension names (timestamp excluded)."""
        return [d for d in self.descriptions if d != "metric_timestamp"]

    @property
    def anomalous_dimensions(self) -> List[str]:
        """Dimensions annotated as directly affected by at least one anomaly."""
        return [d for d, ev in self.dimension_anomalies.items() if ev]

    @property
    def events(self) -> List[AnomalyEvent]:
        """Unique anomaly events, sorted by onset (deduplicated across dimensions)."""
        seen = {}
        for evs in self.dimension_anomalies.values():
            for e in evs:
                key = (e.offset_minutes, e.duration_minutes, e.store, e.disk, e.degradation)
                if key not in seen:
                    seen[key] = e
                else:  # merge related dimensions, if they differ
                    rel = tuple(sorted(set(seen[key].related_dimensions) | set(e.related_dimensions)))
                    seen[key] = AnomalyEvent(*key, related_dimensions=rel)
        return sorted(seen.values(), key=lambda e: (e.offset_minutes or 0, e.store or "", e.disk or ""))

    @property
    def broken_telemetry(self) -> bool:
        """True for the experiments flagged as having broken telemetry."""
        return "broken telemetry" in (self.explanation or "").lower()

    def related_dimensions(self, dimension: str) -> List[str]:
        """All dimensions affected by the same anomaly event(s) as ``dimension``."""
        dimension = harmonize_name(dimension)
        out = set()
        for e in self.dimension_anomalies.get(dimension, []):
            out |= set(e.related_dimensions)
        return sorted(out)

    def summary(self) -> dict:
        return {
            "id": self.id,
            "anomaly_presence": self.anomaly_presence,
            "category": self.category,
            "type": self.type,
            "criticality": self.criticality,
            "explanation": self.explanation,
            "n_events": len(self.events),
            "n_anomalous_dimensions": len(self.anomalous_dimensions),
        }

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (f"Annotation(id={self.id}, category={self.category}, type={self.type}, "
                f"criticality={self.criticality}, events={len(self.events)}, "
                f"anomalous_dimensions={len(self.anomalous_dimensions)})")


def parse_annotation(path: Union[str, Path]) -> Annotation:
    """Parse an XML annotation file into an :class:`Annotation`."""
    root = ET.parse(str(path)).getroot()
    descriptions: Dict[str, str] = {}
    dim_anoms: Dict[str, List[AnomalyEvent]] = {}
    dims = root.find("dimensions")
    for dim in (dims.findall("dimension") if dims is not None else []):
        name = harmonize_name(_text(dim, "name", ""))
        descriptions[name] = _text(dim, "description", "") or ""
        if name == "metric_timestamp":
            continue
        events = []
        anomalies = dim.find("anomalies")
        for an in (anomalies.findall("anomaly") if anomalies is not None else []):
            rel = an.find("related_dimensions")
            related = tuple(harmonize_name(d.text.strip()) for d in rel.findall("dimension")
                            if d.text) if rel is not None else ()
            events.append(AnomalyEvent(
                offset_minutes=_int(_text(an, "offset_minutes")),
                duration_minutes=_int(_text(an, "duration_minutes")),
                store=_text(an, "store"),
                disk=_text(an, "disk"),
                degradation=_text(an, "degradation"),
                related_dimensions=related,
            ))
        dim_anoms[name] = events
    return Annotation(
        id=_text(root, "id", Path(path).stem),
        anomaly_presence=(_text(root, "anomaly_presence", "false").lower() == "true"),
        category=_text(root, "category", "None"),
        type=_text(root, "type", "None"),
        criticality=_text(root, "criticality", "None"),
        explanation=_text(root, "textual_explanation", "") or "",
        descriptions=descriptions,
        dimension_anomalies=dim_anoms,
    )

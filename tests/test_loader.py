"""Sanity checks of the SHAD files and the python loader. Run: pytest -q"""

import numpy as np
import pandas as pd
import pytest

from shad import GROUPS, LABEL_COLUMNS, METRICS, SHAD, metric_info, select


@pytest.fixture(scope="module")
def ds():
    return SHAD()


def test_counts(ds):
    cat = ds.catalog
    assert len(cat) == 215
    assert (cat.group == "Nominal").sum() == 83
    assert set(cat.group) == set(GROUPS)
    train, test = ds.split()
    assert len(train) == 83 and len(test) == 132


def test_every_series_has_an_annotation(ds):
    assert ds.catalog.xml_path.notna().all()


def test_metric_catalog():
    assert len(METRICS) == len(set(METRICS)) == 171
    assert len(LABEL_COLUMNS) == 171
    levels = pd.Series([metric_info(m).level for m in METRICS]).value_counts().to_dict()
    assert levels == {"platform": 17, "s3": 13, "server": 57, "device": 84}
    assert len(select(level="device", store="store1", device="g2disk01")) == 4


@pytest.mark.parametrize("sid", ["1773343796", "1780480782", "1774026259", "1774656607"])
def test_load_series(ds, sid):
    s = ds.load(sid)
    assert s.data.shape[1] == 171 and list(s.data.columns) == METRICS
    assert s.labels.shape == s.data.shape
    assert len(s.label) == len(s.data) > 900
    # the top-level label is the OR of the per-dimension labels
    assert np.array_equal(s.y, s.Y.max(axis=1))
    if s.is_anomalous:
        assert s.events and s.anomalous_dimensions
        assert set(s.anomalous_dimensions) <= set(s.annotation.anomalous_dimensions) | set(METRICS)
    else:
        assert s.y.sum() == 0


def test_legacy_column_names_are_harmonised(ds):
    # 1780480782 was exported with s0-/s1-/s2- prefixes
    s = ds.load("1780480782")
    assert "store1-cpu_usage_ratio" in s.data.columns


def test_fill(ds):
    s = ds.load("1773343796", fill="ffill")
    assert not s.data.isna().any().any()

from src.semantic import get_metric_definition


def test_exact_alias():
    metric = get_metric_definition("低分率")
    assert metric is not None
    assert metric["name"] == "bad_review_rate"


def test_exact_name_ignores_case():
    metric = get_metric_definition("GMV")
    assert metric is not None
    assert metric["name"] == "gmv"


def test_fuzzy_short_name():
    metric = get_metric_definition("差评")
    assert metric is not None
    assert metric["name"] == "bad_review_rate"


def test_unknown_metric():
    assert get_metric_definition("退货率") is None
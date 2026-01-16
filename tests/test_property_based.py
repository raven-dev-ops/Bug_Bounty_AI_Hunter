import unittest

from hypothesis import HealthCheck, given, settings, strategies as st

from scripts import dataflow_map, triage_findings


SEVERITIES = sorted(triage_findings.SEVERITY_PRIORITY.keys())
TEXT_VALUES = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=8,
)
VALUE_ITEMS = st.one_of(
    TEXT_VALUES,
    st.integers(min_value=0, max_value=10),
    st.none(),
)
DICT_ITEMS = st.dictionaries(
    keys=st.sampled_from(["id", "name", "source", "type", "title"]),
    values=VALUE_ITEMS,
    max_size=3,
)
LIST_ITEMS = st.lists(
    st.one_of(
        DICT_ITEMS,
        st.integers(min_value=0, max_value=10),
        TEXT_VALUES,
        st.none(),
    ),
    max_size=5,
)


class PropertyBasedTests(unittest.TestCase):
    @given(
        st.fixed_dictionaries(
            {
                "severity": st.text(min_size=0, max_size=12),
                "impact": st.text(min_size=0, max_size=50),
            }
        )
    )
    def test_normalize_severity_in_allowed_set(self, item):
        result = triage_findings._normalize_severity(item)
        self.assertIn(result, SEVERITIES)

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(LIST_ITEMS)
    def test_normalize_stores_adds_ids(self, items):
        normalized = dataflow_map._normalize_stores(items)
        for entry in normalized:
            self.assertIsInstance(entry, dict)
            self.assertTrue(entry.get("id"))

    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(LIST_ITEMS)
    def test_normalize_flows_adds_ids(self, items):
        normalized = dataflow_map._normalize_flows(items)
        for entry in normalized:
            self.assertIsInstance(entry, dict)
            self.assertTrue(entry.get("id"))


if __name__ == "__main__":
    unittest.main()

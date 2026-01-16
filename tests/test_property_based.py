import unittest

from hypothesis import given, strategies as st

from scripts import dataflow_map, triage_findings


SEVERITIES = sorted(triage_findings.SEVERITY_PRIORITY.keys())


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

    @given(
        st.lists(
            st.one_of(
                st.dictionaries(
                    keys=st.sampled_from(["id", "name", "source", "type", "title"]),
                    values=st.one_of(
                        st.text(min_size=0, max_size=8),
                        st.integers(min_value=0, max_value=10),
                        st.none(),
                    ),
                    max_size=3,
                ),
                st.integers(),
                st.text(min_size=0, max_size=8),
                st.none(),
            ),
            max_size=5,
        )
    )
    def test_normalize_stores_adds_ids(self, items):
        normalized = dataflow_map._normalize_stores(items)
        for entry in normalized:
            self.assertIsInstance(entry, dict)
            self.assertTrue(entry.get("id"))

    @given(
        st.lists(
            st.one_of(
                st.dictionaries(
                    keys=st.sampled_from(["id", "name", "source", "type", "title"]),
                    values=st.one_of(
                        st.text(min_size=0, max_size=8),
                        st.integers(min_value=0, max_value=10),
                        st.none(),
                    ),
                    max_size=3,
                ),
                st.integers(),
                st.text(min_size=0, max_size=8),
                st.none(),
            ),
            max_size=5,
        )
    )
    def test_normalize_flows_adds_ids(self, items):
        normalized = dataflow_map._normalize_flows(items)
        for entry in normalized:
            self.assertIsInstance(entry, dict)
            self.assertTrue(entry.get("id"))


if __name__ == "__main__":
    unittest.main()

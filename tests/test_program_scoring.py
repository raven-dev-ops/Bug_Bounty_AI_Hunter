import unittest

from scripts import program_scoring


class ProgramScoringTest(unittest.TestCase):
    def test_application_required_override_public_only(self):
        program = {
            "id": "program:private",
            "name": "Private Program",
            "scope": {"in_scope": [{"type": "domain", "value": "example.com"}]},
            "restrictions": ["Application required before testing."],
            "rewards": {"max": 5000},
            "response_time": {"first_response_hours": 24},
            "safe_harbor": {"present": True},
        }
        result = program_scoring.score_program(
            program, program_scoring.DEFAULT_CONFIG, public_only=True
        )
        self.assertEqual(result["bucket"], "Impossible")
        self.assertTrue(result["review_required"])
        self.assertTrue(
            any(
                override["id"] == "application_required"
                for override in result["overrides"]
            )
        )

    def test_safe_harbor_missing_blocks_easy_bucket(self):
        program = {
            "id": "program:no-safe-harbor",
            "name": "No Safe Harbor",
            "scope": {"in_scope": [{"type": "domain", "value": "example.com"}]},
            "restrictions": [],
            "rewards": {"max": 10},
            "response_time": {"first_response_hours": 1},
            "safe_harbor": {"present": False},
        }
        result = program_scoring.score_program(
            program, program_scoring.DEFAULT_CONFIG, public_only=False
        )
        self.assertNotEqual(result["bucket"], "Easy")
        self.assertTrue(
            any(
                override["id"] == "safe_harbor_missing"
                for override in result["overrides"]
            )
        )

    def test_testing_disallowed_override(self):
        program = {
            "id": "program:blocked",
            "name": "Blocked Program",
            "scope": {"in_scope": [{"type": "domain", "value": "example.com"}]},
            "restrictions": ["Do not test production systems."],
            "rewards": {"max": 500},
            "response_time": {"first_response_hours": 12},
            "safe_harbor": {"present": True},
        }
        result = program_scoring.score_program(
            program, program_scoring.DEFAULT_CONFIG, public_only=False
        )
        self.assertEqual(result["bucket"], "Impossible")
        self.assertTrue(result["review_required"])
        self.assertTrue(
            any(
                override["id"] == "testing_disallowed"
                for override in result["overrides"]
            )
        )


if __name__ == "__main__":
    unittest.main()

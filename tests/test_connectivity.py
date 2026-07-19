"""Tests for the connectivity agent's per-target summary logic."""

import unittest

from netagent.agents.connectivity import _summarize


class SummarizeTests(unittest.TestCase):
    def test_all_successful(self):
        r = _summarize("1.1.1.1", [10.0, 12.0, 11.0])
        self.assertEqual(r["sent"], 3)
        self.assertEqual(r["lost"], 0)
        self.assertEqual(r["loss_pct"], 0.0)
        self.assertEqual(r["avg_ms"], 11.0)
        self.assertEqual(r["min_ms"], 10.0)
        self.assertEqual(r["max_ms"], 12.0)
        self.assertEqual(r["flags"], [])

    def test_high_loss_flagged(self):
        r = _summarize("8.8.8.8", [10.0, None, 12.0, None])
        self.assertEqual(r["lost"], 2)
        self.assertEqual(r["loss_pct"], 50.0)
        self.assertIn("HIGH LOSS", r["flags"])

    def test_loss_at_threshold_not_flagged(self):
        # Exactly 2% loss must NOT trip the >2% rule.
        samples = [10.0] * 49 + [None]  # 1/50 = 2.0%
        r = _summarize("8.8.8.8", samples)
        self.assertEqual(r["loss_pct"], 2.0)
        self.assertNotIn("HIGH LOSS", r["flags"])

    def test_latency_spike_flagged(self):
        r = _summarize("gw", [10.0, 10.0, 10.0, 200.0])
        self.assertIn("LATENCY SPIKE", r["flags"])
        self.assertNotIn("HIGH LOSS", r["flags"])

    def test_no_samples(self):
        r = _summarize("gw", [])
        self.assertEqual(r["sent"], 0)
        self.assertEqual(r["loss_pct"], 0.0)
        self.assertIsNone(r["avg_ms"])
        self.assertEqual(r["jitter_ms"], 0.0)
        self.assertEqual(r["flags"], [])

    def test_jitter_is_reported(self):
        r = _summarize("gw", [10.0, 20.0, 30.0])
        self.assertGreater(r["jitter_ms"], 0)


if __name__ == "__main__":
    unittest.main()

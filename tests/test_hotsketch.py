import unittest

from hotsketch import HotSketch
from sketchapi import Counter


class TestHotSketch(unittest.TestCase):
    def test_add_counts(self):
        self.assertEqual(HotSketch().add("a")["count"], 1)

    def test_estimate_of_seen(self):
        sketch = HotSketch()
        sketch.add("a")
        self.assertEqual(sketch.estimate("a"), 1)

    def test_estimate_of_unseen(self):
        self.assertEqual(HotSketch().estimate("zzz"), 0)

    def test_stats_shape(self):
        self.assertIn("rows", HotSketch().stats())

    def test_counter_wraps_sketch(self):
        counter = Counter()
        counter.add("a")
        self.assertEqual(counter.sketch.stats()["total"], 1)


if __name__ == "__main__":
    unittest.main()

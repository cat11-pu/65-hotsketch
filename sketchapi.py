"""sketchapi.py：对外门面（老接口 add 不能改）。"""
from __future__ import annotations

from hotsketch import HotSketch


class Counter:
    def __init__(self, rows: int = 2, cols: int = 8, decay_every: int = 8, threshold: int = 3):
        self.sketch = HotSketch(rows, cols, decay_every, threshold)

    def add(self, key: str, weight: int = 1) -> dict:
        return self.sketch.add(key, weight)

    def estimate(self, key: str) -> int:
        return self.sketch.estimate(key)

    def hot(self) -> list:
        return self.sketch.hot()

    def merge(self, other) -> "Counter":
        return self.sketch.merge(other.sketch if hasattr(other, "sketch") else other)

    def snapshot(self) -> bytes:
        return self.sketch.persist()

    def rebuild(self, blob: bytes = None) -> dict:
        return self.sketch.restore(blob)

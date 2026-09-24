"""hotsketch.py：热点检测（基线：精确计数）。"""
from __future__ import annotations


class HotSketch:
    def __init__(self, rows: int = 2, cols: int = 8, decay_every: int = 8, threshold: int = 3):
        self.rows = rows
        self.cols = cols
        self.decay_every = decay_every
        self.threshold = threshold
        self.counts = {}
        self.cells = [[0] * cols for _ in range(rows)]
        self.total = 0
        self.decays = 0

    def add(self, key: str, weight: int = 1) -> dict:
        """基线：精确计数，不衰减。"""
        self.counts[key] = self.counts.get(key, 0) + weight
        self.total += 1
        return {"count": self.counts[key]}

    def estimate(self, key: str) -> int:
        return self.counts.get(key, 0)

    def hot(self) -> list:
        raise NotImplementedError("热点判定还没实现")

    def decay(self) -> dict:
        raise NotImplementedError("窗口衰减还没实现")

    def merge(self, other) -> "HotSketch":
        raise NotImplementedError("合并还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"rows": self.rows, "cols": self.cols, "total": self.total,
                "decays": self.decays, "cells": sum(sum(row) for row in self.cells)}

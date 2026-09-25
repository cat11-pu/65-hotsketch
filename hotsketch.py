"""hotsketch.py：Count-Min Sketch 热点检测内核。

只用标准库。rows 行各自独立哈希到 cols 个单元格，单元格总数恒为
rows * cols，不随键数增长；估计取各行计数的最小值（只会高估）。
"""
from __future__ import annotations

import json

_FNV_OFFSET = 2166136261
_FNV_PRIME = 16777619
_MASK32 = 0xFFFFFFFF
_SNAPSHOT_PATH = "hotsketch.snapshot.json"
_SNAPSHOT_VERSION = 1


def _fnv1a(row: int, key: str) -> int:
    """每行用不同的键前缀作为哈希偏移（FNV-1a，32 位，确定性）。"""
    digest = _FNV_OFFSET
    for byte in str(row).encode("utf-8") + b"/" + key.encode("utf-8"):
        digest ^= byte
        digest = (digest * _FNV_PRIME) & _MASK32
    return digest


class HotSketch:
    def __init__(self, rows: int = 2, cols: int = 8, decay_every: int = 8, threshold: int = 3):
        self.rows = rows
        self.cols = cols
        self.decay_every = decay_every
        self.threshold = threshold
        self.cells = [[0] * cols for _ in range(rows)]
        self.total = 0
        self.decays = 0
        self._seen = set()

    def _column(self, row: int, key: str) -> int:
        return _fnv1a(row, key) % self.cols

    def add(self, key: str, weight: int = 1) -> dict:
        """每行各选一列累加 weight，并累计一次访问；每 decay_every 次自动衰减。"""
        for row in range(self.rows):
            self.cells[row][self._column(row, key)] += weight
        self._seen.add(key)
        self.total += 1
        auto_decays = 0
        if self.decay_every > 0 and self.total % self.decay_every == 0:
            self._apply_decay()
            auto_decays = 1
        return {"count": self.estimate(key), "decays": auto_decays}

    def estimate(self, key: str) -> int:
        """Count-Min 口径：取各行计数最小值，不小于真实计数。"""
        return min(self.cells[row][self._column(row, key)] for row in range(self.rows))

    def hot(self) -> list:
        """估计值 >= threshold 的键：估计降序、同值按名字升序。"""
        ranked = ((key, self.estimate(key)) for key in self._seen)
        ranked = sorted(ranked, key=lambda item: (-item[1], item[0]))
        return [key for key, value in ranked if value >= self.threshold]

    def _apply_decay(self) -> None:
        for row in self.cells:
            for col in range(self.cols):
                row[col] //= 2
        self.decays += 1

    def decay(self) -> dict:
        """手动右移一位（整除 2），返回衰减后的状态统计。"""
        self._apply_decay()
        return self.stats()

    def merge(self, other) -> "HotSketch":
        """逐单元格相加，返回新的 HotSketch（规格必须一致）。"""
        if (self.rows, self.cols) != (other.rows, other.cols):
            raise ValueError("只能合并规格相同的 sketch")
        merged = HotSketch(self.rows, self.cols, self.decay_every, self.threshold)
        merged.cells = [
            [self.cells[r][c] + other.cells[r][c] for c in range(self.cols)]
            for r in range(self.rows)
        ]
        merged.total = self.total + other.total
        merged.decays = max(self.decays, other.decays)
        merged._seen = self._seen | other._seen
        return merged

    def persist(self) -> bytes:
        """快照落盘（JSON），返回写入的字节串。"""
        snapshot = {
            "version": _SNAPSHOT_VERSION,
            "rows": self.rows,
            "cols": self.cols,
            "decay_every": self.decay_every,
            "threshold": self.threshold,
            "cells": self.cells,
            "total": self.total,
            "decays": self.decays,
            "seen": sorted(self._seen),
        }
        blob = json.dumps(snapshot, separators=(",", ":")).encode("utf-8")
        with open(_SNAPSHOT_PATH, "wb") as handle:
            handle.write(blob)
        return blob

    def restore(self, blob: bytes = None) -> dict:
        """从快照字节（或落盘文件）恢复单元格、总访问数与衰减次数。"""
        if blob is None:
            with open(_SNAPSHOT_PATH, "rb") as handle:
                blob = handle.read()
        snapshot = json.loads(blob.decode("utf-8"))
        if (snapshot["rows"], snapshot["cols"]) != (self.rows, self.cols):
            raise ValueError("快照规格与当前 sketch 不一致")
        self.decay_every = snapshot["decay_every"]
        self.threshold = snapshot["threshold"]
        self.cells = [list(row) for row in snapshot["cells"]]
        self.total = snapshot["total"]
        self.decays = snapshot["decays"]
        self._seen = set(snapshot["seen"])
        return self.stats()

    def stats(self) -> dict:
        return {"rows": self.rows, "cols": self.cols, "total": self.total,
                "decays": self.decays, "cells": sum(sum(row) for row in self.cells)}

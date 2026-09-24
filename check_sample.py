"""check_sample.py：按 sample/stream.json 走一圈，打印验收面。"""
import json
import os
import sys

from hotsketch import HotSketch


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "stream.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    sketch = HotSketch(spec["rows"], spec["cols"], spec["decay_every"], spec["threshold"])
    for key in spec["stream"]:
        sketch.add(key)
    estimates = [(key, sketch.estimate(key)) for key in spec["probe_keys"]]
    hot = sketch.hot()
    decayed = sketch.decay()
    after_decay = [(key, sketch.estimate(key)) for key in spec["probe_keys"]]
    second = HotSketch(spec["rows"], spec["cols"], spec["decay_every"], spec["threshold"])
    for key in spec["more_stream"]:
        second.add(key)
    merged = sketch.merge(second)
    blob = sketch.persist()
    reborn = HotSketch(spec["rows"], spec["cols"], spec["decay_every"], spec["threshold"])
    restored = reborn.restore(blob)
    print("各键估计值 =", estimates)
    print("热点键 =", hot)
    print("衰减后的估计 =", after_decay)
    print("合并后的估计 =", [(key, merged.estimate(key)) for key in spec["probe_keys"]])
    print("单元格数（rows × cols） =", sketch.stats().get("rows") * sketch.stats().get("cols"))
    print("衰减次数 =", decayed.get("decays"))
    print("恢复后的单元总计 =", restored.get("cells"))
    print("不变量（估计不小于真实计数） =", spec["overestimate_invariant"])
    print("阈值 =", spec["threshold"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

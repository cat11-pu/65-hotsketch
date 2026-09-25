# hotsketch

纯 Python 标准库的 Count-Min Sketch 热点检测内核。单元格总数恒为
`rows × cols`，不随键数增长；估计取各行计数最小值，只会高估不会低估。

## API

- `HotSketch(rows=2, cols=8, decay_every=8, threshold=3)`：建草图。
- `add(key, weight=1)`：每行按不同哈希偏移（FNV-1a + 行前缀）各选一列累加，
  累计一次总访问；每 `decay_every` 次访问自动把所有单元格右移一位。
- `estimate(key)`：返回各行计数最小值（Count-Min 口径）。
- `decay()`：手动右移一位（整除 2），返回衰减后的 `stats()`。
- `hot()`：估计值 `>= threshold` 的键，按估计降序、同值按名字升序。
- `merge(other)`：同规格草图逐单元格相加，返回新的 `rows × cols` 草图。
- `persist()` / `restore(blob=None)`：JSON 快照落盘与恢复（单元格、总访问数、
  衰减次数一致）；`blob=None` 时从落盘文件恢复。
- `stats()`：`rows`、`cols`、`total`、`decays` 与单元总计 `cells`。

`sketchapi.Counter` 为对外门面，方法一一对应（`snapshot`/`rebuild`）。

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py

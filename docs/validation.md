# system-comparison: validation results

All six owned Python source files compile and all five existing framework benchmark scripts execute on the supplied common historical interval.

## Verified scope

No supplied pytest test cases. Existing Backtesting.py, Backtrader, Basana, Nautilus and VectorBT benchmark smoke runs passed on the common 2024-01-01 to2024-01-02 sample.

Basana’s latest pycares source fails against this macOS SDK on3.15; current Nautilus native distribution requires3.14. The Nautilus script performs a manual SMA simulation using Nautilus data models; it does not run a full BacktestEngine. Latest compatible libraries are independently locked per framework. Existing bar API, numerical indexing, CLI percent escaping and basis-point cost conversion issues were fixed.

## Environment

Root/Backtesting/Backtrader/VectorBT Python3.15.0; Basana/Nautilus Python3.14.8

## Executed checks

Exploratory failures remain visible. Use later successful runs only for the scope they actually exercised; builds, syntax checks and benchmark smoke runs are distinct from complete test suites.

| Check | Exit | Duration | Command |
| --- | ---: | ---: | --- |
| backtesting-315-baseline | 0 | 1.84s | `uv sync --python 3.15` |
| backtesting-py-315-latest-sync | 0 | 0.85s | `uv sync --upgrade --python 3.15` |
| backtesting-py-existing-example-smoke | 1 | 1.56s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| backtesting-py-fixed-example-smoke | 0 | 2.54s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| backtesting-py-import-help | 1 | 5.43s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --help` |
| backtrader-315-latest-sync | 0 | 0.65s | `uv sync --upgrade --python 3.15` |
| backtrader-existing-example-smoke | 1 | 2.2s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| backtrader-fixed-example-smoke | 0 | 2.73s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| backtrader-import-help | 1 | 7.18s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --help` |
| basana-315-latest-sync | 1 | 2.88s | `uv sync --upgrade --python 3.15` |
| basana-current-bar-smoke | 0 | 1.79s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| basana-existing-example-smoke | 1 | 2.97s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| basana-fixed-example-smoke | 1 | 4.9s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| basana-import-help | 1 | 3.28s | `uv run --project examples/basana python examples/basana/benchmark.py --help` |
| basana314-latest-sync | 0 | 0.52s | `uv sync --upgrade --python 3.14` |
| compile-owned-python | 0 | 0.07s | `uv run --no-sync python -m compileall -q scripts/extract_data.py examples/backtesting.py/benchmark.py examples/backtrader/benchmark.py examples/basana/benchmark.py examples/nautilus_trader/benchmark.py examples/vectorbt/benchmark.py` |
| nautilus-315-baseline | 1 | 0.41s | `uv sync --python 3.15` |
| nautilus-import-help-fixed | 0 | 3.85s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --help` |
| nautilus314-latest-sync | 0 | 0.56s | `uv sync --upgrade --python 3.14` |
| nautilus_trader-315-latest-sync | 1 | 4.77s | `uv sync --upgrade --python 3.15` |
| nautilus_trader-existing-example-smoke | 0 | 4.3s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| nautilus_trader-fixed-example-smoke | 0 | 4.06s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| nautilus_trader-import-help | 1 | 5.24s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --help` |
| system-comparison-315-latest-sync | 0 | 0.35s | `uv sync --upgrade --python 3.15` |
| vectorbt-315-baseline | 0 | 21.84s | `uv sync --python 3.15` |
| vectorbt-315-latest-sync | 0 | 0.38s | `uv sync --upgrade --python 3.15` |
| vectorbt-existing-example-smoke | 1 | 7.59s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| vectorbt-fixed-example-smoke | 0 | 78.49s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` |
| vectorbt-import-help | 1 | 21.7s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --help` |

## Portable evidence

[Executed command records](maintenance/index.html) · [Machine-readable verification](maintenance/verification.json) · [Engineering guide](ayu-develop.md) · [Development workflow](development.md)

Full original logs are retained in the workspace maintenance evidence; portable records contain their hashes, exact execution metadata and available outcome lines.

# system-comparison: portable verification records

Full raw logs are retained in the workspace maintenance evidence, not distributed here. Hashes identify those original logs. A successful build or selected test subset does not imply a full test-suite pass. Commands containing <workspace> describe the original execution environment.

[Machine-readable records](verification.json) · [Repository validation summary](../validation.md)

## Executed commands

| Check | Exit | Duration | Command | Outcomes |
| --- | ---: | ---: | --- | --- |
| backtesting-315-baseline | 0 | 1.84s | `uv sync --python 3.15` | See exit status; no test-count assertion. |
| backtesting-py-315-latest-sync | 0 | 0.85s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| backtesting-py-existing-example-smoke | 1 | 1.56s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| backtesting-py-fixed-example-smoke | 0 | 2.54s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| backtesting-py-import-help | 1 | 5.43s | `uv run --project examples/backtesting.py python examples/backtesting.py/benchmark.py --help` | See exit status; no test-count assertion. |
| backtrader-315-latest-sync | 0 | 0.65s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| backtrader-existing-example-smoke | 1 | 2.2s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| backtrader-fixed-example-smoke | 0 | 2.73s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| backtrader-import-help | 1 | 7.18s | `uv run --project examples/backtrader python examples/backtrader/benchmark.py --help` | See exit status; no test-count assertion. |
| basana-315-latest-sync | 1 | 2.88s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| basana-current-bar-smoke | 0 | 1.79s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| basana-existing-example-smoke | 1 | 2.97s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| basana-fixed-example-smoke | 1 | 4.9s | `uv run --project examples/basana python examples/basana/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| basana-import-help | 1 | 3.28s | `uv run --project examples/basana python examples/basana/benchmark.py --help` | See exit status; no test-count assertion. |
| basana314-latest-sync | 0 | 0.52s | `uv sync --upgrade --python 3.14` | See exit status; no test-count assertion. |
| compile-owned-python | 0 | 0.07s | `uv run --no-sync python -m compileall -q scripts/extract_data.py examples/backtesting.py/benchmark.py examples/backtrader/benchmark.py examples/basana/benchmark.py examples/nautilus_trader/benchmark.py examples/vectorbt/benchmark.py` | See exit status; no test-count assertion. |
| nautilus-315-baseline | 1 | 0.41s | `uv sync --python 3.15` | See exit status; no test-count assertion. |
| nautilus-import-help-fixed | 0 | 3.85s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --help` | See exit status; no test-count assertion. |
| nautilus314-latest-sync | 0 | 0.56s | `uv sync --upgrade --python 3.14` | See exit status; no test-count assertion. |
| nautilus_trader-315-latest-sync | 1 | 4.77s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| nautilus_trader-existing-example-smoke | 0 | 4.3s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| nautilus_trader-fixed-example-smoke | 0 | 4.06s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| nautilus_trader-import-help | 1 | 5.24s | `uv run --project examples/nautilus_trader python examples/nautilus_trader/benchmark.py --help` | See exit status; no test-count assertion. |
| system-comparison-315-latest-sync | 0 | 0.35s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| vectorbt-315-baseline | 0 | 21.84s | `uv sync --python 3.15` | See exit status; no test-count assertion. |
| vectorbt-315-latest-sync | 0 | 0.38s | `uv sync --upgrade --python 3.15` | See exit status; no test-count assertion. |
| vectorbt-existing-example-smoke | 1 | 7.59s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| vectorbt-fixed-example-smoke | 0 | 78.49s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --data data/BTCUSDT_202401.csv --start-date 2024-01-01 --end-date 2024-01-02` | See exit status; no test-count assertion. |
| vectorbt-import-help | 1 | 21.7s | `uv run --project examples/vectorbt python examples/vectorbt/benchmark.py --help` | See exit status; no test-count assertion. |

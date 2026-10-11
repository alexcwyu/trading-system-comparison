# system-comparison: development workflow and layout

Use branch `feature/ayu_develop`. The actual upstream default branch and all fetched branch/tag identities are recorded in the maintenance sync evidence. Merge existing work; do not reset divergent branches or replace conflicting tags.

## Source synchronization

```sh
git fetch origin
git fetch upstream
git switch feature/ayu_develop
git merge origin/feature/ayu_develop
# Merge the actual default branch documented in the sync result.
```

This maintenance used namespaced remote tags before comparing tag identities. Missing upstream tags/branches were pushed to the fork; divergent branches were merged when conflict-free, and conflicting identities were retained for explicit reconciliation. The feature branch contains the default branch plus the maintenance changes. Source snapshot and architecture are documented in [ayu-develop.md](ayu-develop.md).

## Repository layout

- `docs/ayu-develop.md` and `docs/ayu-develop.html`: engineering guide with architecture, workflow, class and sequence diagrams and implementation links.
- `docs/development.md`: toolchain, layout and contributor workflow.
- `docs/validation.md`: exact executed commands, outcomes and limitations.

## Python environment

Use current uv 0.13.0 and a uv-managed interpreter. `.python-version` selects the validated runtime; `uv.lock` records exact resolved dependencies. Python 3.15 was attempted; where native dependency or embedding compatibility requires an earlier interpreter, the evidence explains the chosen fallback.

```sh
UV_PYTHON_PREFERENCE=only-managed uv sync --locked
uv run python --version
```

Libraries and services retain their existing importable source packages and build metadata. Research scripts and .NET-hosted algorithms use `package = false` where installing a synthetic Python library would change their launch/import contracts. Independent framework examples keep independent environments; external Git submodules are not forced into one mutually incompatible Python dependency graph.

## Verification and documentation

Use the commands and results in [validation.md](validation.md). Markdown is the editable source of the guide; HTML embeds rendered SVG diagrams for offline browsing. Keep actual source links valid after moving modules. Preserve existing cases/assertions while correcting incompatible APIs, genuine resource leaks or invalid fixtures. No additional test cases were requested or added.

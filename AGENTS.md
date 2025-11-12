# Repository Guidelines

## Project Structure & Module Organization
- `src/core` contains agent primitives: `agents` (base classes), `skill_cards` (schema, manager, executor), `middleware` (audit + PII) used across personas.
- `src/personal_assistant` holds runnable skills, tools, and the in-memory DB; treat JSON skill cards as declarative source of truth.
- `src/examples` (01–08) are narrative demos; keep inputs lightweight so `uv run python -m src.examples.*` stays fast.
- `tests` mirrors the module tree, while `docs/` and `logs/` capture deeper design notes and execution traces.

## Build, Test, and Development Commands
- `uv sync` installs application + dev groups; run again after touching dependencies or the lockfile.
- `uv run python -m src.examples.02_schedule_agent` (or any numbered file) verifies tutorial steps; prefer these over ad-hoc scripts.
- `uv run python -m src.examples.08_real_tools_demo` is the integration benchmark for Skill Card orchestration and tool wiring.
- `uv run pytest [-v tests/... ]` kicks off the suite; `uv run python quick_test.py` is the light pre-flight when editing a single module.

## Coding Style & Naming Conventions
- Target Python 3.13 with 4-space indents, double quotes, and descriptive type hints on public APIs.
- Enforce style via `uv run ruff check` and `uv run ruff format`; the config covers PEP 8, pep8-naming, pyupgrade, and import ordering.
- Modules, functions, and files use snake_case; classes stay PascalCase; constants are UPPER_SNAKE_CASE.
- Skill Card JSON keys remain lowerCamelCase to match existing cards and executor expectations.

## Testing Guidelines
- Leverage fixtures in `tests/conftest.py`; add new fixtures only when shared by multiple suites.
- Name tests `test_<feature>_<scenario>` and store them beside the feature (`tests/core/...`, `tests/personal_assistant/...`).
- For Skill Card or tool changes, pair unit coverage with `uv run python -m src.examples.08_real_tools_demo` and capture anomalies in `logs/`.

## Commit & Pull Request Guidelines
- Follow the lightweight conventional style seen in history (`docs: ...`, `feat: ...`, `fix: ...`) and keep subjects under 72 characters.
- PRs should summarize motivation, outline the solution, list verification commands, and attach screenshots or JSON diffs when behavior changes.
- Reference issues, flag breaking migrations, and mention new environment switches or credentials in the description.

## Agent & Skill Card Tips
- Extend capabilities via `src/core/skill_cards/schema.py` or `executor.py` rather than branching logic inside agents.
- Register new tools in `src/personal_assistant/tools/schedule_tools.py`, documenting expected inputs/outputs in the matching card.
- Middleware remains opt-in; subclass `BaseMiddleware`, then pass it through the executor configuration so flows stay composable.

# Repository Guidelines

## Project Structure

- `src/akashic/`: Python package for the `akashic` CLI, engine, server helpers, and prompt templates.
- `tests/`: pytest suite for CLI, engine behavior, prompt generation, site commands, and repository handling.
- `docs/`: user-facing Markdown documentation.
- `frontend/`: React/Vite documentation UI packaged into the Python wheel.
- `presentation/`: reveal.js presentation assets.

## Development Commands

- Install Python dependencies: `uv sync`
- Run all Python tests: `uv run pytest`
- Run a focused test: `uv run pytest tests/test_cli.py -q`
- Run the CLI from the checkout: `uv run akashic --version`
- Validate a knowledge repo manually: `uv run akashic doctor --knowledge /path/to/knowledge`

Frontend commands run from `frontend/`:

- Install frontend dependencies: `npm install`
- Type-check/build the UI: `npm run build`
- Start the Vite dev server: `npm run dev`

## Coding Guidelines

- Keep Python code compatible with Python 3.10+.
- Prefer existing engine and config helpers over adding parallel parsing or filesystem logic.
- Keep CLI behavior covered by tests when changing command output, exit behavior, or generated files.
- Preserve user-authored documentation sections marked with `<!-- HUMAN:START -->`.
- Do not commit generated frontend build artifacts, `node_modules`, `.venv`, or cache directories.

## Testing Expectations

- Run `uv run pytest` for Python changes.
- Run `npm run build` from `frontend/` for UI or packaged-site changes.
- For docs-only edits, no test run is required unless command examples or generated content behavior changes.

## Packaging Notes

- The package is named `akashic-kb`; the installed console script is `akashic`.
- Wheel packaging force-includes the `frontend/` directory under `akashic/frontend`.
- Keep package-data changes aligned with `pyproject.toml` hatch build settings.

# Repository Guidelines

## Project Structure & Module Organization
- Core Flask app lives in `web_server.py`, orchestrating `data_loader.py`, `visualization.py`, `warpage_statistics.py`, and `pdf_exporter.py`.
- Configuration defaults stay in `config.py` with runtime overrides in `config.txt`; sample datasets belong in `data/`.
- Front-end templates are under `templates/`; static PDF and analytics artifacts land in `report/`.
- Packaging outputs populate `build/` and `dist/`; avoid editing generated `.spec` files unless changing build targets.
- CLI helpers such as `Auto_PDF.py` support batch PDF generation for automation and QA exports.

## Build, Test, and Development Commands
```powershell
python -m venv .venv312 ; .\.venv312\Scripts\activate
pip install -r requirements.txt
python web_server.py             # Launch local Flask UI on http://localhost:8080
pytest                           # Run unit tests (add -k/-s as needed)
python -m PyInstaller web_server.spec --clean  # Rebuild desktop executable
.\build_pyinstaller.bat          # Windows-friendly wrapper for release builds
```

## Coding Style & Naming Conventions
- Use 4-space indentation, `snake_case` for functions/variables, and `PascalCase` for classes to mirror existing modules.
- Run `black .` before committing; `flake8` helps catch unused imports and style drift.
- Measurement data files follow the existing patterns (`*_ORI.txt`, `_ORI_A.txt`); keep generated assets out of Git per `.gitignore`.

## Testing Guidelines
- Place new tests under a top-level `tests/` package, naming files `test_<module>.py` and functions `test_<behavior>`.
- Use `pytest` fixtures for sample datasets and include regression data in `data/` subfolders that remain untracked.
- Aim for ≥80% coverage with `pytest --cov=PEMTRON_warpage --cov-report=term-missing` when introducing significant logic.
- When touching data processing, add assertions around both statistical outputs and plot metadata (figure counts, filenames).

## Commit & Pull Request Guidelines
- Recent history mixes timestamp-only commits with descriptive subjects; prefer the latter using `summary: detail` in present tense (e.g., `build: refresh PyInstaller spec`).
- Reference issue IDs or customer tickets where applicable and keep commits focused.
- Pull requests should include a purpose summary, before/after screenshots for UI changes, a list of executed commands (tests, builds), and notes on data dependencies.
- Request review from both data-processing and UI maintainers when changes span Python back end and HTML templates.

## Configuration & Security Notes
- Adjust runtime behavior through `config.py` defaults or `config.txt`; document any new keys in both files.
- Keep proprietary measurement files and generated executables in `data/`, `dist/`, or `build/`—never commit them beyond what `.gitignore` allows.
- Sanitize logs such as `data_transfer.log` before sharing; remove serial numbers or customer identifiers.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Warpage Analysis Tool** for PEMTRON semiconductor manufacturing. It analyzes warpage data from measurement files (.txt and .ptr files) and generates comprehensive reports with visualizations and statistical analysis.

### Core Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **Entry Points**: `temp/cli_interface.py` (CLI), `web_server.py` (Flask web interface)
- **Core Analysis**: `temp/analyzer.py` orchestrates the entire analysis workflow  
- **Data Pipeline**: `data_loader.py` → `warpage_statistics.py` → `visualization.py` → `pdf_exporter.py`
- **Configuration**: `config.py` contains all defaults and settings
- **User Interfaces**: `temp/cli.py` for command-line parsing and interactive mode

### Data Flow

1. **Data Loading** (`data_loader.py`): Reads .txt/.ptr files, removes zero rows/columns, handles -4000 artifacts
2. **Statistical Analysis** (`warpage_statistics.py`): Calculates mean, range, min/max, std deviation
3. **Visualization** (`visualization.py`): Creates 2D heatmaps, 3D surface plots, comparison charts
4. **PDF Export** (`pdf_exporter.py`): Generates comprehensive reports in `report/` directory

### File Structure Patterns

The tool expects data in this structure:
```
data/
├── 20250716/               # Date folder
├── 단일보드/30/            # Single board at 30°
├── 전체보드/120/           # Full board at 120°
└── PTR_CREATE/             # Contains PTR_CREATE.exe tool
```

File types:
- `@_ORI.txt`: Original measurement files (default)
- `@.txt`: Corrected measurement files
- `@.ptr`: Binary measurement files

## Common Commands

### CLI Usage
```bash
# Basic analysis with defaults
python temp/cli_interface.py

# Interactive mode
python temp/cli_interface.py --interactive

# Custom analysis
python temp/cli_interface.py --cmap=plasma --vmin=-1500 --vmax=-800 --show --stats --3d

# Web interface
python web_server.py
```

### Key Command Options
- `--base=PATH`: Set data directory path
- `--folders=F1,F2`: Specify folders to analyze
- `--cmap=NAME`: Colormap (jet, viridis, plasma, etc.)
- `--vmin/vmax=VALUE`: Color scale limits
- `--original/corrected`: File type selection
- `--stats/--3d`: Include statistical analysis and 3D plots
- `--output=FILENAME`: PDF output name
- `--show`: Display plots interactively

### Dependencies
```bash
# Install core dependencies for CLI analysis
pip install -r requirements.txt

# Install additional dependencies for web interface
pip install -r requirements_web.txt
```

**Core Requirements:**
- `numpy>=1.20.0`: Numerical computations and data processing
- `matplotlib>=3.3.0`: Plotting and visualization

**Web Interface Requirements:**
- `Flask==2.3.3`: Web framework
- `Werkzeug==2.3.7`: WSGI utilities

## Development Notes

### Current Code Structure
The codebase is currently in a transitional state:
- **Legacy CLI modules** are in `temp/` directory: `cli_interface.py`, `analyzer.py`, `cli.py`
- **Active web modules** are in root directory: `web_server.py`, `data_loader.py`, etc.
- **Shared modules** work with both interfaces: `config.py`, `visualization.py`, `pdf_exporter.py`

### Configuration Management
All defaults are centralized in `config.py`. The `DEFAULT_CONFIG` dictionary drives both CLI and web interfaces. When adding new features, update this configuration first.

### Data Processing Pipeline
The `process_folder_data()` function in `data_loader.py` is the main entry point for data processing. It handles both single files and directory traversal, applying consistent preprocessing (zero removal, artifact handling).

### Visualization System
`visualization.py` provides two main categories:
- **Individual plots**: Single file analysis with heatmaps and 3D surfaces
- **Comparison plots**: Multi-file statistical comparisons and distributions

### PDF Export Architecture
The PDF export system (`pdf_exporter.py`) creates multi-page reports with:
1. Individual file analyses (heatmaps + 3D if enabled)
2. Statistical comparison plots (mean, range, min/max, std dev)
3. Distribution plots and combined analyses

### Web GUI Structure
The Flask app (`web_server.py`) provides:
- `/api/folders`: List available data directories
- `/api/analyze`: Run analysis pipeline
- `/api/plot/<file_id>`: Generate individual plots
- `/api/stats_plot`: Statistical comparison plots
- `/api/export_pdf`: Generate and download PDF reports

### File Pattern Handling
The system supports two file types through `FILE_PATTERNS` in config:
- Original files: `@_ORI.txt` (measurement data as-is)
- Corrected files: `@.txt` (processed/corrected data, excluding @_ORI.txt)

### Error Handling Philosophy
The codebase uses defensive programming with extensive file existence checks, shape validation, and graceful degradation when files are missing or malformed.

### Testing and Development Tools
- **Synthetic Data Generation**: `synthetic_data_generator.py` creates test datasets for development
- **Advanced Statistics**: `advanced_statistics.py` provides extended statistical analysis capabilities
- **No formal test framework**: The codebase currently lacks unit tests and automated testing infrastructure

### Web Server Configuration
The Flask application (`web_server.py`) runs on:
- **Default port**: 8080 (configurable in `config.py`)
- **Host**: localhost (configurable in `config.py`)
- **Debug mode**: Configurable in `config.py`
- **Auto-browser opening**: Automatically opens browser on startup
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PEMTRON Warpage Analysis Tool: A Python-based application for analyzing semiconductor warpage measurement data with web-based GUI and automated data transfer capabilities.

**Two Main Components:**
1. **Web-based Analysis Tool** ([web_server.py](web_server.py)) - Interactive warpage data visualization and PDF report generation
2. **Data Auto Transfer** ([data_autotransfer/](data_autotransfer/)) - Automated daily transfer of dated folders to remote systems
3. **Auto PDF Generator** ([Auto_PDF.py](Auto_PDF.py)) - Scheduled PDF generation at 20:00 daily for previous day's data

## Common Commands

### Running the Application

**Web Server (Development):**
```bash
python web_server.py
```
Server starts on `http://localhost:5001` with auto-open browser (configurable port in [config.py](config.py))

**Web Server (Production Executable):**
```bash
# Build executable
python -m PyInstaller --onefile --name "PEMTRON_Warpage_Tool" web_server.py --clean

# Run from dist folder
cd dist
PEMTRON_Warpage_Tool.exe
```

**Data Auto Transfer:**
```bash
cd data_autotransfer

# Run once immediately
python main.py --once

# Test connection
python main.py --test

# Run scheduled transfers (default)
python main.py

# Use custom config
python main.py --config custom_config.txt
```

**Auto PDF Generator:**
```bash
python Auto_PDF.py
```
Runs as background service, generates PDF daily at 20:00 for previous day's folder.

### Development Setup

```bash
# Create virtual environment
python -m venv .venv312

# Activate virtual environment
.venv312\Scripts\activate  # Windows
source .venv312/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Building Executables

**Web Server:**
```bash
python -m PyInstaller --onefile --name "PEMTRON_Warpage_Tool" web_server.py --clean
```

**Data Transfer:**
```bash
cd data_autotransfer
python -m PyInstaller data_autotransfer.spec --clean
```

Note: Executables are large (~800MB for web server) due to bundled dependencies.

## Architecture Overview

### Data Flow - Web Analysis Tool

```
User selects folder → Flask API (/api/analyze) → process_folder_data_parallel()
                                                         ↓
data_loader.py: File discovery & loading (multiprocessing)
                                                         ↓
warpage_statistics.py: Statistical calculations (mean, std, range, skewness, kurtosis)
                                                         ↓
visualization.py: Plot generation (parallel processing with ProcessPoolExecutor)
                                                         ↓
Response: base64 images → Web UI display / pdf_exporter.py → PDF report
```

### Data Flow - Auto Transfer System

```
Scheduler (cron-like) → DateUtils.find_yesterday_folder() → TransferManager
                                                                    ↓
                                          Protocol selection (SSH/SMB/local)
                                                                    ↓
                                          Retry logic with password fallbacks
                                                                    ↓
                                          Optional: Delete source after transfer
```

### Core Modules

**Web Analysis Tool:**
- [web_server.py](web_server.py) - Flask REST API, global state management
- [data_loader.py](data_loader.py) - File discovery, parallel loading with ProcessPoolExecutor
- [visualization.py](visualization.py) - Plot generation (2D heatmaps, 3D surfaces, statistical charts)
- [pdf_exporter.py](pdf_exporter.py) - PDF report generation with ReportLab
- [warpage_statistics.py](warpage_statistics.py) - Statistical calculations
- [advanced_statistics.py](advanced_statistics.py) - Advanced analysis (optional)
- [config.py](config.py) - Configuration management, default settings

**Data Transfer System:**
- [data_autotransfer/main.py](data_autotransfer/main.py) - Main orchestrator
- [data_autotransfer/transfer_manager.py](data_autotransfer/transfer_manager.py) - Protocol handlers (SSH/SMB/local)
- [data_autotransfer/scheduler.py](data_autotransfer/scheduler.py) - Cron-like scheduling
- [data_autotransfer/config_parser.py](data_autotransfer/config_parser.py) - Config file parsing
- [data_autotransfer/date_utils.py](data_autotransfer/date_utils.py) - Date-based folder operations
- [data_autotransfer/logger.py](data_autotransfer/logger.py) - Structured logging

## Important Technical Details

### Performance Optimization (v2.1.0+)

**Multiprocessing Pipeline:**
- File loading uses `ProcessPoolExecutor` (not ThreadPoolExecutor) for CPU-intensive operations
- Plot generation parallelized: 5 plots per file generated simultaneously
- Auto-detects CPU cores for optimal worker count
- 3-5x speedup for large datasets

**Memory Management:**
- `cleanup_matplotlib_figures()` called after each analysis to prevent "20+ figures" warning
- Figures closed immediately after base64 conversion
- Global state cleared before new analysis

### File Format Support

**Priority System (configurable in UI):**
1. **Original files** (default): `*@_ORI.txt`, `*_ORI_A.txt` - Raw measurement data
2. **Corrected files**: `*.txt` (excluding original patterns) - Processed data
3. **Akrometrix format**: Special format with different parsing rules

File discovery is recursive with configurable depth (default: 3 levels).

### Configuration System

**Web Server Config** ([config.py](config.py)):
```python
DEFAULT_CONFIG = {
    "base_path": get_data_dir(),        # Auto-resolves for .exe vs .py
    "vmin": None, "vmax": None,         # Auto color scaling
    "cmap": "jet",                      # Colormap
    "row_fraction": 1, "col_fraction": 1,  # Region extraction
    "use_original_files": True,         # File type preference
    "dpi": 150,                         # Export quality
    "parallel_processing": True,        # Enable multiprocessing
    "max_workers": None                 # Auto-detect CPU cores
}

SCAN_CONFIG = {
    "max_directories": 100,             # Limit folder scan
    "max_scan_depth": 3,                # Recursive depth
    "max_scan_threads": 61,             # Parallel directory scanning
    "cache_ttl_seconds": 300            # Directory scan cache
}
```

**Transfer Config** ([data_autotransfer/config.txt](data_autotransfer/config.txt)):
```
SCHEDULE_TIME=06:00                    # Single daily time
SCHEDULE_TIMES=06:00, 18:00           # Multiple times
SOURCE_DIRECTORY=../data
FOLDER_PATTERN=%Y%m%d                  # Date format for folders
TARGET_IP=10.252.38.241
PROTOCOL=smb                           # ssh, smb, or local
USERNAME=user@example.com
PASSWORD=primary_password
PASSWORD_FALLBACKS=fallback1, fallback2  # Comma-separated
DELETE_AFTER_TRANSFER=false
RETRY_ATTEMPTS=3
```

### PyInstaller Considerations

**Critical for Executables:**
```python
# Always include in main entry point
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()  # Required for multiprocessing
```

**Path Resolution:**
```python
def get_data_dir():
    """Auto-detects correct path for .exe vs .py"""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'data')
```

### API Endpoints (Web Server)

**Analysis Workflow:**
1. `GET /api/folders` - List available data folders (with parallel scanning)
2. `POST /api/analyze` - Process folder with parallel file loading and plot generation
3. `GET /api/plot/<file_id>` - Retrieve individual plot
4. `GET /api/all_plots` - Get all plots in single response
5. `GET /api/export_pdf` - Generate and download PDF report
6. `GET /api/export_stats_json` - Export statistics as JSON

See [README.md](README.md) for complete API documentation.

### Data Processing Pipeline

**Artifact Removal:**
Common measurement artifacts are removed: `-4000`, `±9999`, `±99999`

**Region Extraction:**
Center region extraction using `row_fraction` and `col_fraction` (0.0-1.0)

**Statistical Calculations:**
- Basic: min, max, mean, std, range
- Advanced: skewness, kurtosis, distribution analysis

### Parallel Processing Architecture

**Worker Functions Must Be Module-Level:**
```python
# CORRECT - module-level function
def _process_single_file_worker(args):
    """Worker function for multiprocessing."""
    return result

# INCORRECT - nested or lambda functions won't work with multiprocessing
```

**Process Pool Pattern:**
```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

max_workers = multiprocessing.cpu_count()
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    results = list(executor.map(worker_function, tasks))
```

### Error Handling Strategy

**Graceful Degradation:**
- Individual file failures don't stop entire analysis
- Continue processing remaining files
- Log errors with detailed stack traces

**Transfer System Retry Logic:**
- Configurable retry attempts (default: 3)
- Configurable retry delay (default: 30s)
- Password fallback mechanism for authentication failures

## Important Conventions

### File Structure
- `data/` directory contains measurement files (auto-created)
- `templates/` contains Flask HTML templates
- `report/` for generated PDF outputs (auto-created)
- PyInstaller builds go to `dist/` directory

### Naming Conventions
- File discovery uses pattern matching, not extension-only
- Date folders follow `%Y%m%d` format (e.g., `20250110`)
- Generated files: `{folder_name}.pdf`, `{folder_name}_stats.json`

### State Management
Global variables in web_server.py:
- `current_data` - Processed measurement arrays and stats
- `current_plots` - Generated plot images (base64 encoded)
- `current_stats` - Statistical results

Always clear these before new analysis to prevent memory leaks.

### Matplotlib Backend
Always use `'Agg'` backend for server environments:
```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

## Common Issues

### "More than 20 figures" Warning
**Solution:** Call `cleanup_matplotlib_figures()` after generating plots.

### Unicode Encoding Errors (Windows)
**Solution:** Avoid Unicode symbols in print statements (✓, ✗). Use ASCII alternatives.

### PyInstaller "Module not found"
**Solution:** Add hidden imports to spec file or use `--hidden-import` flag.

### Slow Folder Scanning
**Solution:** Adjust `SCAN_CONFIG` in [config.py](config.py) - reduce `max_directories` or `max_scan_depth`.

### Transfer Authentication Failures
**Solution:** Use `PASSWORD_FALLBACKS` in config for multiple password attempts.

## Port Configuration

- **Web Server:** Port 5001 (configurable in [config.py](config.py) via `WEB_PORT`)
- **Auto PDF Service:** Connects to web server at `http://127.0.0.1:5001`
- **Network Transfer:** SSH port 22, SMB ports 445/139

## Version Management

Current version: v2.1.1 (see [README.md](README.md) for version history)

Major changes in recent versions:
- v2.1.1: Critical fixes for server errors and Unicode encoding
- v2.1.0: Multiprocessing pipeline for 3-5x performance improvement
- v2.0.x: Web interface and advanced analysis features

# PEMTRON Warpage Analysis Tool

A comprehensive Python tool for analyzing semiconductor warpage data from PEMTRON manufacturing processes. This tool processes measurement files, generates statistical analyses, and creates detailed reports with visualizations.

## Features

- **Multi-format Data Support**: Processes .txt and .ptr measurement files
- **Comprehensive Analysis**: Statistical analysis with mean, range, min/max, and standard deviation
- **Rich Visualizations**: 2D heatmaps, 3D surface plots, and comparison charts  
- **Dual Interface**: Command-line and web-based interfaces
- **PDF Reports**: Automated generation of detailed analysis reports
- **Flexible Configuration**: Customizable analysis parameters and output formats

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PEMTRON_warpage
```

2. Install dependencies:
```bash
pip install -r requirements.txt

# For web interface:
pip install -r requirements_web.txt
```

### Basic Usage

**Command Line Interface:**
```bash
# Run analysis with defaults
python cli_interface.py

# Interactive mode with guided setup
python cli_interface.py --interactive

# Custom analysis with specific parameters
python cli_interface.py --cmap=plasma --vmin=-1500 --vmax=-800 --show --stats --3d
```

**Web Interface:**
```bash
python web_server.py
# Opens browser automatically to http://localhost:8080
```

## Data Structure

Place your measurement data in the following structure:
```
data/
├── 20250716/               # Date folders
│   ├── file@.txt          # Corrected measurement files  
│   └── file@_ORI.txt      # Original measurement files
├── 단일보드/               # Single board measurements
│   ├── 30/                # Temperature folders
│   ├── 60/
│   └── 90/
└── 전체보드/               # Full board measurements
    ├── 30/
    ├── 60/
    └── 120/
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--base=PATH` | Set base path to data folders | `--base=./measurements/` |
| `--folders=F1,F2` | Specify folders to analyze | `--folders=20250716,20250717` |
| `--cmap=NAME` | Set colormap | `--cmap=viridis` |
| `--vmin/vmax=VALUE` | Set color scale limits | `--vmin=-1500 --vmax=-800` |
| `--original/corrected` | Choose file type | `--original` or `--corrected` |
| `--stats` | Include statistical analysis | `--stats` |
| `--3d` | Include 3D surface plots | `--3d` |
| `--output=FILE` | Set output PDF name | `--output=analysis_2025.pdf` |
| `--show` | Display plots interactively | `--show` |

## Web Interface Features

The web GUI provides:
- **Interactive Analysis**: Point-and-click analysis setup
- **Real-time Visualization**: Dynamic plot generation
- **Folder Browser**: Automatic detection of available data folders
- **PDF Export**: One-click report generation
- **Progress Tracking**: Live status updates during analysis

Access at `http://localhost:8080` after running `python web_server.py`

## Output

The tool generates:
- **PDF Reports**: Comprehensive analysis reports in `report/` directory
- **Statistical Summaries**: Console output with key metrics
- **Interactive Plots**: Optional matplotlib display windows
- **Comparison Charts**: Multi-file analysis and comparisons

## Configuration

Default settings are in `config.py`:
- Data paths and folder structure
- Visualization parameters (colormaps, scales)
- Output formats and quality settings
- Web server configuration

## File Types

- **@_ORI.txt**: Original measurement files (default selection)
- **@.txt**: Corrected/processed measurement files  
- **@.ptr**: Binary measurement files (processed by PTR_CREATE.exe)

## Examples

**Basic Analysis:**
```bash
python cli_interface.py --folders=20250716 --show
```

**High-Quality Report Generation:**
```bash
python cli_interface.py --cmap=plasma --stats --3d --dpi=600 --output=detailed_analysis.pdf
```

**Interactive Setup:**
```bash
python cli_interface.py --interactive
# Follow prompts to configure analysis parameters
```

**Web Analysis:**
```bash
python web_server.py
# Use browser interface for point-and-click analysis
```

## Dependencies

**Core Requirements (requirements.txt):**
- `numpy>=1.20.0` - Numerical computations
- `matplotlib>=3.3.0` - Plotting and visualization

**Web Interface (requirements_web.txt):**  
- `flask` - Web framework
- Additional web dependencies

## License

This tool is developed for PEMTRON semiconductor manufacturing analysis.

## Support

For issues or questions regarding warpage analysis workflows, refer to the CLAUDE.md file for detailed architecture and development guidance.
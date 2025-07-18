# Warpage Data Analysis Tool

A modular Python tool for analyzing warpage data across different folders. This refactored solution provides data loading, statistical analysis, visualization, PDF export capabilities, and a modern web-based GUI with consistent scaling and file size reporting.

## 📁 Project Structure

```
PEMTRON_warpage/
├── main.py              # Main entry point
├── analyzer.py          # Main analysis logic
├── cli.py               # Command line interface
├── config.py            # Configuration settings
├── data_loader.py       # Data loading and processing
├── pdf_exporter.py      # PDF export functionality
├── statistics.py        # Statistical analysis
├── visualization.py     # Plotting and visualization
├── web_gui.py           # Web-based GUI
├── templates/            # HTML templates for web GUI
│   └── index.html       # Main web interface
├── requirements.txt     # Python package dependencies
├── requirements_web.txt # Web GUI dependencies
└── README.md            # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies

#### For Command Line Interface
```bash
pip install -r requirements.txt
```

#### For Web GUI
```bash
pip install -r requirements_web.txt
```

**Note**: The web GUI runs on port 8080 by default. You can change this in `config.py` by modifying the `WEB_PORT` variable.

## 🚀 Quick Start

### Web GUI (Recommended)

Start the web interface for an easy-to-use graphical interface:

```bash
python web_gui.py
```

The browser will open automatically to: http://localhost:8080

**Features:**
- Modern, responsive web interface
- Real-time data visualization
- Interactive plot generation
- PDF export functionality
- No installation required - runs in any web browser

### Command Line Usage

```bash
# Show help and available options
python main.py --help

# Run with default settings
python main.py

# Run with custom visualization settings
python main.py --cmap=plasma --vmin=-1500 --vmax=-800 --show

# Run with colorbar disabled
python main.py --no-colorbar

# Specify custom folders to analyze
python main.py --folders=20250716,20250717

# Specify custom output filename
python main.py --output=my_analysis.pdf

# Run in interactive mode
python main.py --interactive

# Use corrected files instead of original files
python main.py --corrected

# Use original files (default behavior)
python main.py --original
```

### Using as a Module

```python
# Import the function
from analyzer import analyze_warpage
import matplotlib.pyplot as plt

# Run analysis with default settings (processes all original files)
fig, data = analyze_warpage()

# Run with custom settings
config = {
    "base_path": "./data/",
    "folders": ["20250716"],
    "vmin": -1500,
    "vmax": -800,
    "cmap": "plasma",
    "colorbar": True,
    "output_filename": "custom_analysis.pdf",
    "show_plots": False,
    "use_original_files": True  # Use original files (@_ORI.txt) vs corrected files (.txt)
}
fig, data = analyze_warpage(config)

# The data dictionary now contains all files that match the pattern:
# data = {
#     "File_01": (data_array, stats, filename),
#     "File_02": (data_array, stats, filename),
#     ...
# }

# Display plots when ready
plt.show()
```

## ⚙️ Configuration Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `base_path` | Base path to data folders | `"./data/"` |
| `folders` | Folders to analyze | `["20250716"]` |
| `vmin` | Min value for color scale | `None` (auto) |
| `vmax` | Max value for color scale | `None` (auto) |
| `cmap` | Colormap name | `"jet"` |
| `colorbar` | Whether to show colorbar | `True` |
| `row_fraction` | Fraction of rows to keep in center | `1` (full data) |
| `col_fraction` | Fraction of columns to keep in center | `1` (full data) |
| `output_filename` | Output PDF filename | `"warpage_analysis.pdf"` |
| `include_stats` | Include statistical analysis plots | `True` |
| `include_3d` | Include 3D surface plots | `True` |
| `dpi` | DPI for PDF export | `600` |
| `show_plots` | Show plots after analysis | `False` |
| `use_original_files` | Use original files (@_ORI.txt) vs corrected files (.txt) | `True` |

## 📊 Output Files

### PDF Exports
- **Analysis PDF**: Multi-page PDF with comparison plots, individual plots, and 3D surface plots
- **Report Directory**: All PDFs are saved in the `report` directory

### Console Output
- Loading progress and status messages
- Detailed statistical summaries
- File size information
- PDF export summaries

## 🛠️ Requirements

### Python Packages
```python
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
```

### Module Dependencies
The application consists of the following modules:
- `main.py`: Entry point and orchestration
- `analyzer.py`: Main analysis logic
- `cli.py`: Command line interface
- `config.py`: Configuration settings
- `data_loader.py`: Data loading and processing
- `pdf_exporter.py`: PDF export functionality
- `statistics.py`: Statistical analysis
- `visualization.py`: Plotting and visualization

## 📂 Data Structure Expected

```
data/
└── 20250716/
    ├── 20250716111845@_ORI.txt    # Original files
    ├── 20250716112257@_ORI.txt
    ├── 20250716114413@_ORI.txt
    ├── 20250716111845@.txt         # Corrected files
    ├── 20250716112257@.txt
    └── 20250716114413@.txt
```

**Note**: The tool automatically processes ALL files matching the selected pattern in each folder, not just the first one found.

## 🎯 Key Features

- **Web GUI**: Modern, responsive web interface for easy analysis
- **Enhanced Status Reporting**: Real-time progress bars and detailed status messages for both analysis and PDF export
- **Combined Statistical Plots**: Two graphs per page in up-down configuration for efficient space utilization
- **Warpage Distribution Analysis**: Histogram/Gaussian distribution plot showing warpage values vs frequency
- **Simplified File Naming**: Clean file identification using just numbers (01, 02, etc.) instead of 'File_' prefix
- **Detailed File Processing**: Shows file sizes, shapes, artifact counts, and processing parameters
- **Modular Design**: Well-organized code structure with separate modules for different functionalities
- **Multi-File Processing**: Processes ALL files matching the pattern in each folder automatically
- **Configurable Parameters**: Customize visualization and analysis settings
- **Full Data Analysis**: Analyzes complete warpage data (no center region extraction)
- **High-Resolution Output**: 600 DPI PDF exports with A4 page size
- **Consistent Scaling**: Same x,y scale for all graphs for proper comparison
- **Customizable Colormaps**: Support for various colormaps including scientific and traditional options
- **Colorbar Support**: Optional colorbars show the relationship between colors and data values
- **3D Surface Plots**: Includes 3D surface visualization
- **File Size Reporting**: Displays file sizes in human-readable format
- **Interactive Mode**: User-friendly interface for setting parameters
- **Command Line Interface**: Easy automation and scripting support
- **File Type Selection**: Choose between original (@_ORI.txt) or corrected (.txt) files
- **Zero Data Removal**: Automatically removes all-zero rows and columns (dummy data) by default
- **Artifact Filtering**: Automatically nullifies -4000 values as artifacts
- **Maintainable Code**: Clean separation of concerns for easy maintenance and extension

## 🚨 Troubleshooting

### Common Issues:

1. **"No original/corrected files found"**: Ensure your data files end with `@_ORI.txt` (original) or `.txt` (corrected)
2. **"No data found"**: Check that your folder structure matches the expected format
3. **Import errors**: Ensure you have all required Python packages installed
4. **Memory issues**: For large datasets with many files, consider processing fewer folders at once
5. **Too many files**: The tool processes ALL matching files - if you have many files, the PDF may become large

## 📝 Version History

### Version 3.9.0 (Current)
- **Enhanced**: Warpage distribution plot now shows histogram of (max-min) values
- **Improved**: X-axis shows (Max - Min) warpage values, Y-axis shows probability density
- **Updated**: Added mean line and statistics box showing mean, std, min, max values
- **Enhanced**: Better statistical analysis of warpage range distribution across files
- **Optimized**: Statistical plots now use 0.45 height and are positioned in upper half of PDF page

### Version 3.8.0
- **Fixed**: Web GUI statistical plots now match PDF export layout exactly
- **Enhanced**: Web GUI shows same combined statistical analysis as PDF (Mean, Range, Min-Max)
- **Improved**: Consistent visualization between web interface and PDF reports
- **Updated**: Web GUI statistical plots use simplified file names and same styling as PDF

### Version 3.7.0
- **New**: Combined statistical plots - two graphs per page in up-down configuration for better space utilization
- **Enhanced**: Warpage distribution plot now shows histogram/Gaussian distribution instead of CDF
- **Improved**: Statistical analysis now includes 3 pages: Mean+Range, Min-Max+StdDev, and Distribution
- **Enhanced**: Better PDF organization with combined plots reducing total page count
- **Updated**: Distribution plot shows warpage values vs frequency/density for intuitive analysis

### Version 3.6.0
- **New**: Warpage distribution plot (CDF) - shows probability vs warpage values for comprehensive analysis
- **Enhanced**: Added cumulative distribution function plot with probability on x-axis and warpage values on y-axis
- **Improved**: Statistical analysis now includes 5 focused plots: Mean, Range, Min-Max, Standard Deviation, and Distribution
- **Enhanced**: Better color coding for multiple files in distribution plots
- **Updated**: PDF export now includes warpage distribution analysis page

### Version 3.5.0
- **New**: Individual statistical plots - each statistical analysis now gets its own page in PDF
- **Enhanced**: Simplified file naming - removed 'File_' prefix, now shows just numbers (01, 02, etc.)
- **Removed**: Frequency-warpage distribution plot and data size comparison plot from statistical analysis
- **Improved**: Cleaner statistical analysis with 4 focused plots: Mean, Range, Min-Max, and Standard Deviation
- **Enhanced**: Better PDF organization with one statistical plot per page for improved readability

### Version 3.4.0
- **New**: Enhanced status reporting with detailed progress information
- **Enhanced**: Real-time status bars for both analysis and PDF export processes
- **New**: Detailed file processing information including file sizes, shapes, and artifact counts
- **Improved**: Better progress tracking with step-by-step status messages
- **Enhanced**: Status messages show file opening, processing parameters, and completion details
- **New**: PDF export status bar with progress simulation and detailed completion information

### Version 3.3.0
- **New**: Web-based GUI with modern, responsive interface
- **Enhanced**: A4 page size for PDF exports with proper plot sizing
- **New**: Automatic removal of all-zero rows and columns (dummy data) by default
- **Improved**: Better font sizing and layout for PDF reports

### Version 3.2.0
- **Enhanced**: Internal file renaming - files are now renamed from File_01 to File_N internally
- **Improved**: Clean display names in plots and statistical information
- **Enhanced**: Simplified file identification in all visualizations and reports
- **Updated**: All statistical plots now use simple File_XX identifiers
- **Maintained**: Full backward compatibility with existing functionality

### Version 3.1.0
- **Enhanced**: Multi-file processing - now processes ALL files matching the pattern in each folder
- **Improved**: Dynamic visualization layout for multiple files
- **Enhanced**: Better file identification and reporting
- **Updated**: All visualization functions to handle multiple files per folder
- **Maintained**: Full backward compatibility with existing functionality

### Version 3.0.0
- **Refactored**: Reorganized code into modular structure for better maintainability
- **Created**: Separate modules for different functionalities:
  - `main.py`: Main entry point
  - `analyzer.py`: Main analysis logic
  - `cli.py`: Command line interface
  - `config.py`: Configuration settings
  - `data_loader.py`: Data loading and processing
  - `pdf_exporter.py`: PDF export functionality
  - `statistics.py`: Statistical analysis
  - `visualization.py`: Plotting and visualization
- **Added**: File type selection configuration (`use_original_files`)
  - `--original`: Use original files (@_ORI.txt) [default]
  - `--corrected`: Use corrected files (.txt, excluding @_ORI.txt)
- **Maintained**: Full backward compatibility with existing command line interface
- **Improved**: Code organization and separation of concerns
- **Enhanced**: Easier maintenance and future feature additions

### Version 2.0.0
- **Simplified**: Consolidated all functionality into a single file
- **Enhanced**: Added interactive mode for easier configuration
- **Improved**: Streamlined command line interface
- **Updated**: Comprehensive configuration options
- **Simplified**: Removed complex module dependencies
- **Updated**: Changed to folder-based analysis instead of resolution-based
- **Enhanced**: Added 3D surface plots
- **Improved**: Increased DPI to 600 for higher quality output
- **Modified**: Now analyzes full data instead of center region only

### Previous Versions
- See git history for details on previous implementations

# Warpage Data Analysis Tool

A simple Python tool for analyzing warpage data across different resolutions. This single-file solution provides data loading, statistical analysis, visualization, and PDF export capabilities with consistent scaling and file size reporting.

## 📁 Project Structure

```
PEMTRON_warpage/
├── warpage.py           # Main analysis script (all-in-one solution)
└── README.md            # This file
```

## 🚀 Quick Start

### Command Line Usage

```bash
# Show help and available options
python warpage.py --help

# Run with default settings
python warpage.py

# Run with custom visualization settings
python warpage.py --cmap=plasma --vmin=-1500 --vmax=-800 --show

# Run with colorbar disabled
python warpage.py --no-colorbar

# Specify custom resolutions to analyze
python warpage.py --res=30,60,90,120

# Specify custom output filename
python warpage.py --output=my_analysis.pdf

# Run in interactive mode
python warpage.py --interactive
```

### Using as a Module

```python
# Import the function
from warpage import analyze_warpage
import matplotlib.pyplot as plt

# Run analysis with default settings
fig, data = analyze_warpage()

# Run with custom settings
config = {
    "base_path": "./data/단일보드",
    "resolutions": ["30", "60", "90", "120"],
    "vmin": -1500,
    "vmax": -800,
    "cmap": "plasma",
    "colorbar": True,
    "output_filename": "custom_analysis.pdf",
    "show_plots": False
}
fig, data = analyze_warpage(config)

# Display plots when ready
plt.show()
```

## ⚙️ Configuration Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `base_path` | Base path to data folders | `"./data/단일보드"` |
| `resolutions` | Resolution folders to analyze | `["30", "60", "90", "120"]` |
| `vmin` | Min value for color scale | `None` (auto) |
| `vmax` | Max value for color scale | `None` (auto) |
| `cmap` | Colormap name | `"jet"` |
| `colorbar` | Whether to show colorbar | `True` |
| `row_fraction` | Fraction of rows to keep in center | `0.4` |
| `col_fraction` | Fraction of columns to keep in center | `0.5` |
| `output_filename` | Output PDF filename | `"warpage_analysis.pdf"` |
| `include_stats` | Include statistical analysis plots | `True` |
| `include_3d` | Include 3D surface plots | `False` |
| `dpi` | DPI for PDF export | `300` |
| `show_plots` | Show plots after analysis | `False` |

## 📊 Output Files

### PDF Exports
- **Analysis PDF**: Multi-page PDF with comparison plots and individual plots
- **Report Directory**: All PDFs are saved in the `report` directory

### Console Output
- Loading progress and status messages
- Detailed statistical summaries
- File size information
- PDF export summaries

## 🛠️ Requirements

```python
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
```

## 📂 Data Structure Expected

```
data/
└── 단일보드/
    ├── 30/
    │   └── 20250716114413@_ORI.txt
    ├── 60/
    │   └── 20250716114831@_ORI.txt
    ├── 90/
    │   └── 20250716115134@_ORI.txt
    └── 120/
        └── 20250716115218@_ORI.txt
```

## 🎯 Key Features

- **Single-File Design**: All functionality in one easy-to-use file
- **Configurable Parameters**: Customize visualization and analysis settings
- **Center Region Focus**: Analyzes most important part of warpage data
- **High-Resolution Output**: 300 DPI PDF exports
- **Consistent Scaling**: Same x,y scale for all graphs for proper comparison
- **Customizable Colormaps**: Support for various colormaps including scientific and traditional options
- **Colorbar Support**: Optional colorbars show the relationship between colors and data values
- **File Size Reporting**: Displays file sizes in human-readable format
- **Interactive Mode**: User-friendly interface for setting parameters
- **Command Line Interface**: Easy automation and scripting support

## 🚨 Troubleshooting

### Common Issues:

1. **"No ORI file found"**: Ensure your data files end with `@_ORI.txt`
2. **"No data found"**: Check that your folder structure matches the expected format
3. **Import errors**: Ensure you have all required Python packages installed
4. **Memory issues**: For large datasets, consider processing fewer resolutions at once

## 📝 Version History

### Version 2.0.0 (Current)
- **Simplified**: Consolidated all functionality into a single file
- **Enhanced**: Added interactive mode for easier configuration
- **Improved**: Streamlined command line interface
- **Updated**: Comprehensive configuration options
- **Simplified**: Removed complex module dependencies

### Previous Versions
- See git history for details on previous implementations

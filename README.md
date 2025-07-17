# Warpage Data Analysis Toolkit

A comprehensive Python toolkit for analyzing warpage data across different resolutions. This modular system provides data loading, statistical analysis, visualization, and PDF export capabilities with consistent scaling and file size reporting.

## 📁 Project Structure

```
PEMTRON_warpage/
├── data_loader.py          # Data loading and processing functions
├── statistics_utils.py     # Statistical analysis functions  
├── visualization.py        # Plotting and visualization functions
├── pdf_exporter.py         # PDF export functions
├── presets.py              # Visualization presets
├── main_analysis.py        # Main analysis script with routines
├── analyze.py              # Interactive preset selection script
└── README.md               # This file
```

## 🚀 Quick Start

### Basic Usage

#### Using Command Line with Analysis Presets

```bash
# Show available analysis presets and help
python main_analysis.py --help

# Run with default resolution comparison analysis
python main_analysis.py

# Run with specific analysis preset
python main_analysis.py resolution_comparison

# Run with visualization overrides
python main_analysis.py resolution_comparison --cmap=plasma --vmin=-1500 --vmax=-800 --show

# Run with colorbar disabled
python main_analysis.py resolution_comparison --no-colorbar
```

#### Using Interactive Script

```bash
# Run the interactive script for guided analysis
python analyze.py
```

#### Using as a Module

```python
# Import the function
from main_analysis import compare_resolution
import matplotlib.pyplot as plt

# Run resolution comparison analysis with default settings
fig = compare_resolution()

# Run with custom visualization settings
fig = compare_resolution(vmin=-1500, vmax=-800, cmap="plasma", colorbar=True)

# Future: Run different analysis types when implemented
# fig = compare_resolution("date_comparison")
# fig = compare_resolution("batch_comparison")

# Display plots when ready
plt.show()
```

## 📚 Module Documentation

### 1. `data_loader.py` - Data Loading and Processing

#### Functions:

**`load_data_from_file(file_path)`**
- Loads raw data from text files
- **Args**: `file_path` (str) - Path to data file
- **Returns**: `numpy.ndarray` - Raw data array, or None if error
- **Example**:
  ```python
  from data_loader import load_data_from_file
  data = load_data_from_file('./단일보드/30/20250716114413@_ORI.txt')
  ```

**`extract_center_region(data_array, row_fraction=0.4, col_fraction=0.5)`**
- Extracts center region from data array
- **Args**: 
  - `data_array` (numpy.ndarray) - Input data
  - `row_fraction` (float) - Fraction of rows to keep (default: 0.4)
  - `col_fraction` (float) - Fraction of columns to keep (default: 0.5)
- **Returns**: `numpy.ndarray` - Center region data
- **Example**:
  ```python
  from data_loader import extract_center_region
  center_data = extract_center_region(full_data, row_fraction=0.3, col_fraction=0.6)
  ```

**`find_ori_file(folder_path)`**
- Finds ORI files in directories
- **Args**: `folder_path` (str) - Path to folder
- **Returns**: `str` - Full path to ORI file, or None if not found
- **Example**:
  ```python
  from data_loader import find_ori_file
  ori_file = find_ori_file('./단일보드/30')
  ```

**`process_resolution_data(base_path, resolution)`**
- Complete processing pipeline for one resolution
- **Args**: 
  - `base_path` (str) - Base path to data folders
  - `resolution` (str) - Resolution folder name
- **Returns**: `tuple` - (center_data, stats, ori_filename)
- **Example**:
  ```python
  from data_loader import process_resolution_data
  center_data, stats, filename = process_resolution_data('./단일보드', '30')
  ```

### 2. `statistics_utils.py` - Statistical Analysis

#### Functions:

**`calculate_statistics(data_array)`**
- Calculates comprehensive statistics
- **Args**: `data_array` (numpy.ndarray) - Input data
- **Returns**: `dict` - Statistics dictionary with keys: min, max, mean, std, shape, range
- **Example**:
  ```python
  from statistics_utils import calculate_statistics
  stats = calculate_statistics(data)
  print(f"Mean: {stats['mean']}, Std: {stats['std']}")
  ```

**`collect_resolution_statistics(base_path, resolution_folders)`**
- Collects statistics for all resolutions
- **Args**: 
  - `base_path` (str) - Base path to data folders
  - `resolution_folders` (list) - List of resolution folder names
- **Returns**: `tuple` - (resolutions, stats_data)
- **Example**:
  ```python
  from statistics_utils import collect_resolution_statistics
  resolutions, stats_data = collect_resolution_statistics('./단일보드', ['30', '60', '90', '120'])
  ```

**`print_statistics_summary(resolutions, stats_data)`**
- Prints formatted statistics summary
- **Args**: 
  - `resolutions` (list) - List of resolution values
  - `stats_data` (dict) - Dictionary of statistical data
- **Example**:
  ```python
  from statistics_utils import print_statistics_summary
  print_statistics_summary(resolutions, stats_data)
  ```

**`find_optimal_color_range(resolution_data)`**
- Finds optimal color range for consistent visualization
- **Args**: `resolution_data` (dict) - Dictionary with resolution as key and data as value
- **Returns**: `tuple` - (vmin, vmax) for color scaling
- **Example**:
  ```python
  from statistics_utils import find_optimal_color_range
  vmin, vmax = find_optimal_color_range(resolution_data)
  ```

### 3. `visualization.py` - Visualization Functions

#### Functions:

**`create_comparison_plot(resolution_data, figsize=(20, 5), vmin=None, vmax=None)`**
- Creates side-by-side comparison plots
- **Args**: 
  - `resolution_data` (dict) - Dictionary with resolution as key and (data, stats, filename) as value
  - `figsize` (tuple) - Figure size (width, height)
  - `vmin, vmax` (float) - Color scale limits
- **Returns**: `matplotlib.figure.Figure` - The created figure
- **Example**:
  ```python
  from visualization import create_comparison_plot
  fig = create_comparison_plot(resolution_data, figsize=(16, 4))
  plt.show()
  ```

**`create_individual_plot(resolution, data, stats, filename, figsize=(8, 6), vmin=None, vmax=None)`**
- Creates individual plot for single resolution
- **Args**: 
  - `resolution` (str) - Resolution value
  - `data` (numpy.ndarray) - Data array
  - `stats` (dict) - Statistics dictionary
  - `filename` (str) - Filename for title
  - `figsize` (tuple) - Figure size
  - `vmin, vmax` (float) - Color scale limits
- **Returns**: `matplotlib.figure.Figure` - The created figure
- **Example**:
  ```python
  from visualization import create_individual_plot
  fig = create_individual_plot('30', data, stats, 'file.txt', figsize=(10, 8))
  plt.show()
  ```

**`create_statistics_plots(resolutions, stats_data, figsize=(15, 10))`**
- Creates comprehensive statistics comparison plots
- **Args**: 
  - `resolutions` (list) - List of resolution values
  - `stats_data` (dict) - Dictionary of statistical data
  - `figsize` (tuple) - Figure size
- **Returns**: `matplotlib.figure.Figure` - The created figure
- **Example**:
  ```python
  from visualization import create_statistics_plots
  fig = create_statistics_plots(resolutions, stats_data)
  plt.show()
  ```

**`create_3d_surface_plot(resolution_data, figsize=(20, 15))`**
- Creates 3D surface plots for all resolutions
- **Args**: 
  - `resolution_data` (dict) - Dictionary with resolution as key and (data, stats, filename) as value
  - `figsize` (tuple) - Figure size
- **Returns**: `matplotlib.figure.Figure` - The created figure
- **Example**:
  ```python
  from visualization import create_3d_surface_plot
  fig = create_3d_surface_plot(resolution_data)
  plt.show()
  ```

### 4. `pdf_exporter.py` - PDF Export Functions

#### Functions:

**`export_to_pdf(base_path, resolution_folders, output_filename='warpage_analysis_center_region.pdf', include_stats=True, include_3d=True, dpi=300)`**
- Exports comprehensive analysis to high-resolution PDF
- **Args**: 
  - `base_path` (str) - Base path to data folders
  - `resolution_folders` (list) - List of resolution folder names
  - `output_filename` (str) - Output PDF filename
  - `include_stats` (bool) - Whether to include statistical analysis plots
  - `include_3d` (bool) - Whether to include 3D surface plots
  - `dpi` (int) - DPI for high-resolution output
- **Returns**: `str` - Path to created PDF file
- **Example**:
  ```python
  from pdf_exporter import export_to_pdf
  pdf_path = export_to_pdf('./단일보드', ['30', '60', '90', '120'], 
                          output_filename='my_analysis.pdf', dpi=300)
  ```

**`export_single_resolution_pdf(base_path, resolution, output_filename=None, dpi=300)`**
- Exports analysis for single resolution to PDF
- **Args**: 
  - `base_path` (str) - Base path to data folders
  - `resolution` (str) - Resolution folder name
  - `output_filename` (str) - Output PDF filename (auto-generated if None)
  - `dpi` (int) - DPI for high-resolution output
- **Returns**: `str` - Path to created PDF file
- **Example**:
  ```python
  from pdf_exporter import export_single_resolution_pdf
  pdf_path = export_single_resolution_pdf('./단일보드', '30', 'resolution_30um.pdf')
  ```

### 5. `presets.py` - Analysis Presets

#### Functions:

**`list_presets()`**
- Prints a list of all available analysis presets with their descriptions
- **Example**:
  ```python
  from presets import list_presets
  list_presets()  # Displays all available analysis presets
  ```

**`get_preset(preset_name)`**
- Gets an analysis preset by name
- **Args**: `preset_name` (str) - Name of the analysis preset
- **Returns**: `dict` - Preset dictionary with analysis settings
- **Example**:
  ```python
  from presets import get_preset
  preset = get_preset("resolution_comparison")
  print(preset["type"])  # Prints "resolution_comparison"
  ```

**`update_visualization_settings(preset_name, vmin=None, vmax=None, cmap=None, colorbar=None)`**
- Updates visualization settings for an analysis preset
- **Args**: 
  - `preset_name` (str) - Name of the analysis preset
  - `vmin` (float, optional) - Minimum value for color scale
  - `vmax` (float, optional) - Maximum value for color scale
  - `cmap` (str, optional) - Colormap name
  - `colorbar` (bool, optional) - Whether to show colorbar
- **Returns**: `dict` - Updated visualization settings
- **Example**:
  ```python
  from presets import update_visualization_settings
  vis_settings = update_visualization_settings("resolution_comparison", vmin=-1500, vmax=-800, cmap="plasma")
  ```

### 6. `main_analysis.py` - Resolution Comparison Analysis

#### Functions:

**`compare_resolution(preset_name="resolution_comparison", vmin=None, vmax=None, cmap=None, colorbar=None)`**
- Main function for comparing results based on selected analysis type
- Uses analysis presets with option to override visualization settings
- Analyzes data according to the selected analysis type and exports PDF
- **Args**:
  - `preset_name` (str): Name of the analysis preset to use
  - `vmin` (float, optional): Minimum value for color scale. Overrides default if provided
  - `vmax` (float, optional): Maximum value for color scale. Overrides default if provided
  - `cmap` (str, optional): Colormap name. Overrides default if provided
  - `colorbar` (bool, optional): Whether to show colorbar. Overrides default if provided
- **Returns**:
  - `matplotlib.figure.Figure`: The created comparison figure
- **Example**:
  ```python
  from main_analysis import compare_resolution
  import matplotlib.pyplot as plt
  
  # Using default analysis (resolution comparison)
  fig = compare_resolution()
  
  # Using specific analysis with custom visualization
  fig = compare_resolution("resolution_comparison", vmin=-1500, vmax=-800, cmap="plasma")
  
  # Future: Using other analysis types when implemented
  # fig = compare_resolution("date_comparison")
  
  plt.show()  # Display plots when ready
  ```

**`main()`**
- Main function to handle command line arguments and run the analysis
- Parses command line arguments and runs the analysis with the specified preset and options
- **Example**:
  ```python
  from main_analysis import main
  main()  # Runs the analysis with command line arguments
  ```

**`get_file_size(file_path)`**
- Get file size in human-readable format
- **Args**: `file_path` (str) - Path to file
- **Returns**: `str` - File size (e.g., "1.23 MB")
- **Example**:
  ```python
  from main_analysis import get_file_size
  size = get_file_size('data.txt')  # Returns "1.23 KB"
  ```
  
### 7. `analyze.py` - Interactive Preset Selection

#### Functions:

**`main()`**
- Interactive function to demonstrate preset usage
- Shows available presets, prompts for selection, and runs the analysis
- **Example**:
  ```python
  from analyze import main
  main()  # Runs the interactive preset selection
  ```

## 🎭 Analysis Presets

The system includes analysis presets for different types of analyses:

### Available Analysis Types

| Name | Description | Status |
|------|-------------|--------|
| **Resolution Comparison** | Compare warpage data across different resolutions | Available |
| **Date Comparison** | Compare warpage data across different dates | Coming Soon |
| **Batch Comparison** | Compare warpage data across different batches | Coming Soon |
| **Defect Analysis** | Analyze warpage data for defects | Coming Soon |

### Using Analysis Presets

```python
# From Python code
from main_analysis import compare_resolution
fig = compare_resolution("resolution_comparison")  # Use resolution comparison
```

```bash
# From command line
python main_analysis.py resolution_comparison  # Run resolution comparison
```

### Visualization Settings

All analysis presets use the following default visualization settings, which can be overridden:

- **vmin/vmax**: Auto-calculated from data (None)
- **cmap**: "jet" colormap
- **colorbar**: Enabled (True)

You can override these settings:

```python
# Override visualization settings
fig = compare_resolution(vmin=-1500, vmax=-800, cmap="plasma", colorbar=False)
```

## 🎨 Available Colormaps

The system supports various matplotlib colormaps for different visualization needs:

### Scientific Colormaps (Recommended)
- **`'viridis'`** - Perceptually uniform, good for scientific data
- **`'plasma'`** - High contrast, good for highlighting variations
- **`'inferno'`** - Dark background, good for presentations
- **`'magma'`** - Similar to inferno but with different hue progression

### Diverging Colormaps
- **`'coolwarm'`** - Blue to red, good for data with meaningful center
- **`'seismic'`** - Blue-white-red, good for positive/negative data
- **`'RdYlBu'`** - Red-yellow-blue, good for temperature-like data

### Traditional Colormaps
- **`'jet'`** - Default, rainbow colors (not perceptually uniform)
- **`'hot'`** - Black-red-yellow-white progression
- **`'cool'`** - Cyan-magenta progression

### Usage Examples:
```python
# Scientific visualization with colorbar
compare_resolution(cmap='viridis', colorbar=True)

# High contrast for defect detection without colorbar
compare_resolution(cmap='plasma', colorbar=False)

# Traditional rainbow colors with colorbar (default)
compare_resolution(cmap='jet')  # Default: colorbar=True

# Diverging for warpage analysis with custom range and colorbar
compare_resolution(vmin=-2000, vmax=10, cmap='coolwarm', colorbar=True)
```

### Colorbar Behavior:

**📊 Colorbar Placement:**
- **Comparison Plot (Page 1)**: No colorbar for cleaner layout
- **Individual Plots (Pages 2-5)**: Colorbars shown when enabled
- **PDF Export**: Follows the same colorbar settings

**✅ Use Colorbars When:**
- Presenting data to stakeholders who need to understand exact values
- Creating scientific publications or reports
- Analyzing quantitative warpage measurements
- Comparing different datasets where scale matters

**❌ Disable Colorbars When:**
- Creating presentation slides for overview purposes
- Focusing on patterns rather than exact values
- Space is limited (colorbars take additional room)
- Creating clean, minimalist visualizations

## 🔧 Advanced Usage Examples

### Command Line Usage with Analysis Presets

```bash
# Show help and available analysis presets
python main_analysis.py --help

# Use resolution comparison analysis and show plots
python main_analysis.py resolution_comparison --show

# Use resolution comparison with custom visualization settings
python main_analysis.py resolution_comparison --cmap=plasma --vmin=-1500 --vmax=-800

# Disable colorbar for cleaner output
python main_analysis.py resolution_comparison --no-colorbar
```

### Python Module Usage with Analysis Presets

```python
from main_analysis import compare_resolution
import matplotlib.pyplot as plt

# Run the resolution comparison analysis
fig = compare_resolution("resolution_comparison")
# This will:
# 1. Load all resolution data with file size info
# 2. Calculate global color range for consistent scaling
# 3. Apply default visualization settings (auto range, cmap=jet, colorbar=True)
# 4. Create comparison visualization
# 5. Display file information table
# 6. Show statistical comparison
# 7. Export PDF with analysis results
# 8. Create visualization (but not display it yet)

# Run with custom visualization settings
fig = compare_resolution("resolution_comparison", vmin=-1500, vmax=-800, cmap="plasma")

# Display plots when ready
plt.show()
```

### Interactive Usage

```bash
# Run the interactive script
python analyze.py
```

This will:
1. Show all available presets
2. Prompt for preset selection
3. Run the analysis with the selected preset
4. Display the plots

### Custom Center Region Extraction

```python
from data_loader import load_data_from_file, extract_center_region

# Load full data
full_data = load_data_from_file('./data/단일보드/30/20250716114413@_ORI.txt')

# Extract different center regions
small_center = extract_center_region(full_data, row_fraction=0.2, col_fraction=0.3)
large_center = extract_center_region(full_data, row_fraction=0.6, col_fraction=0.7)
```

### Custom Visualization with Consistent Scaling

```python
from data_loader import process_resolution_data
from visualization import create_individual_plot
from statistics_utils import find_optimal_color_range
from main_analysis import get_file_size
import matplotlib.pyplot as plt

# Load data for multiple resolutions
resolution_data = {}
for res in ['30', '60', '90', '120']:
    center_data, stats, filename = process_resolution_data('./data/단일보드', res)
    if center_data is not None:
        resolution_data[res] = (center_data, stats, filename)
        
        # Display file size info
        file_path = f'./data/단일보드/{res}/{filename}'
        file_size = get_file_size(file_path)
        print(f"{res}μm: {filename} ({file_size})")

# Find optimal color range for consistent scaling
data_only = {k: v[0] for k, v in resolution_data.items()}
vmin, vmax = find_optimal_color_range(data_only)
print(f"Global color range: {vmin:.6f} to {vmax:.6f}")

# Create custom plots with consistent color and axis scaling
figures = []
for res, (data, stats, filename) in resolution_data.items():
    fig = create_individual_plot(res, data, stats, filename, 
                               figsize=(12, 10), vmin=vmin, vmax=vmax)
    figures.append(fig)
    plt.savefig(f'custom_plot_{res}um.png', dpi=300, bbox_inches='tight')

# Display all figures at the end
for fig in figures:
    plt.figure(fig.number)
    plt.show()
```

### Batch PDF Export with File Size Info

```python
from pdf_exporter import export_to_pdf, export_single_resolution_pdf
from main_analysis import get_file_size

# Export complete analysis (no stats/3D for cleaner output)
complete_pdf = export_to_pdf('./data/단일보드', ['30', '60', '90', '120'], 
                           output_filename='complete_analysis.pdf',
                           include_stats=False, include_3d=False, dpi=300)

if complete_pdf:
    pdf_size = get_file_size(complete_pdf)
    print(f"Complete analysis PDF: {complete_pdf} ({pdf_size})")

# Export individual resolution PDFs
for resolution in ['30', '60', '90', '120']:
    individual_pdf = export_single_resolution_pdf('./data/단일보드', resolution, 
                                                 f'analysis_{resolution}um.pdf', dpi=300)
    if individual_pdf:
        pdf_size = get_file_size(individual_pdf)
        print(f"Exported: {individual_pdf} ({pdf_size})")
```

### Statistical Analysis (Available for Future Use)

```python
from statistics_utils import collect_resolution_statistics, calculate_statistics
from data_loader import process_resolution_data

# Collect statistics for all resolutions
resolutions, stats_data = collect_resolution_statistics('./data/단일보드', ['30', '60', '90', '120'])

# Find resolution with minimum warpage
min_warpage_idx = stats_data['mean'].index(min(stats_data['mean']))
best_resolution = resolutions[min_warpage_idx]
print(f"Best resolution (minimum warpage): {best_resolution}μm")

# Calculate custom statistics for specific resolution
center_data, _, _ = process_resolution_data('./data/단일보드', '30')
custom_stats = calculate_statistics(center_data)
print(f"30μm resolution statistics: {custom_stats}")
```

### Future: Same Resolution Comparison

```python
from data_loader import process_multiple_files_same_resolution
from visualization import create_same_resolution_comparison
from statistics_utils import find_optimal_color_range

# For future use when comparing multiple files of same resolution
resolution = '30'
data_dict = process_multiple_files_same_resolution('./data/단일보드', resolution)

# Find optimal color range
data_only = {k: v[0] for k, v in data_dict.items()}
vmin, vmax = find_optimal_color_range(data_only)

# Create comparison plot
fig = create_same_resolution_comparison(data_dict, resolution, vmin=vmin, vmax=vmax)
plt.show()
```

## 📊 Output Files

### PDF Exports
- **Complete Analysis PDF**: Multi-page PDF with comparison plots, individual plots, statistical analysis, and 3D surface plots
- **Individual Resolution PDFs**: Single-page PDFs for each resolution

### Console Output
- Loading progress and status messages
- Detailed statistical summaries
- Error messages and warnings
- PDF export summaries

## 🛠️ Requirements

```python
import os
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

- **Modular Design**: Separate modules for different functionalities
- **Center Region Focus**: Analyzes most important part of warpage data
- **High-Resolution Output**: 300 DPI PDF exports
- **Consistent Scaling**: Same x,y scale for all graphs for proper comparison
- **Customizable Colormaps**: Support for various colormaps including scientific and traditional options
- **Colorbar Support**: Optional colorbars show the relationship between colors and data values
- **Deferred Display**: Graphs are created but not shown automatically - user controls when to display
- **File Size Reporting**: Displays file sizes in human-readable format
- **Future-Ready**: Statistics functions available for future same-resolution comparisons
- **Routine Functions**: Specialized routines for different analysis types
- **Optimal Color Ranges**: Consistent color scaling across all visualizations
- **Error Handling**: Robust error handling and informative messages
- **Flexible Usage**: Can be used as modules or standalone scripts

## 🚨 Troubleshooting

### Common Issues:

1. **"No ORI file found"**: Ensure your data files end with `@_ORI.txt`
2. **"No data found"**: Check that your folder structure matches the expected format
3. **Import errors**: Ensure all module files are in the same directory
4. **Memory issues**: For large datasets, consider processing one resolution at a time

### Getting Help:

- Check that all required files are present
- Verify data file formats (space-separated numeric values)
- Ensure proper folder structure
- Review error messages for specific issues

## 📈 Performance Tips

- Use `quick_analysis()` for single resolution analysis
- Process resolutions individually for large datasets
- Adjust `row_fraction` and `col_fraction` to reduce data size
- Use lower DPI for faster PDF generation during development

## 📝 Version History

### Version 1.8.0 (Current)
- **Added**: Analysis preset system for different analysis types
- **Refactored**: Moved analysis presets to separate `presets.py` file
- **Simplified**: Main file now uses analysis presets
- **Enhanced**: Command-line interface for selecting analysis types
- **New**: Interactive `analyze.py` script for easy analysis selection
- **Future-Ready**: Structure in place for adding new analysis types

### Version 1.7.1
- **Fixed**: Custom color range (vmin/vmax) now properly applied to PDF exports
- **Improved**: Removed large colorbar from comparison plot (first page) for cleaner layout
- **Enhanced**: Individual plots still show colorbars when enabled
- **Updated**: PDF export function now correctly uses custom color ranges

### Version 1.7.0
- **Added**: Colorbar support - users can enable/disable colorbars in visualizations
- **Enhanced**: `compare_resolution()` function now accepts `colorbar` parameter
- **Updated**: All visualization functions support colorbar parameter
- **Improved**: PDF exports now include colorbars when enabled
- **Flexible**: Colorbars can be toggled on/off for cleaner presentations

### Version 1.6.0
- **Added**: Colormap support - users can specify different colormaps for visualizations
- **Enhanced**: `compare_resolution()` function now accepts `cmap` parameter
- **Updated**: All visualization functions support colormap parameter
- **Improved**: PDF exports now use specified colormap throughout
- **Available colormaps**: 'viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 'seismic', 'RdYlBu', 'jet', 'hot', 'cool'

### Version 1.5.0
- **Simplified**: Removed `main()`, `quick_analysis()`, and `compare_resolutions()` functions
- **Renamed**: `routine_resolution_comparison()` → `compare_resolution()` 
- **Streamlined**: Only one main function for resolution comparison analysis
- **Updated**: PDF output filename changed to `resolution_comparison.pdf`
- **Enhanced**: Cleaner, focused interface with single-purpose functionality

### Version 1.4.1
- **Updated**: All functions now defer plot display - plots are created but not shown automatically
- **Changed**: Removed `plt.show()` calls from all analysis functions
- **Enhanced**: Users can control when to display plots by calling `plt.show()` manually
- **Improved**: Better workflow control - analysis completes without interrupting with plot windows

### Version 1.4.0
- **Updated**: Set `axis='equal'` for all visualizations to ensure proper aspect ratio
- **Enhanced**: `routine_resolution_comparison()` displays file sizes for each resolution
- **Improved**: Consistent axis scaling with equal aspect ratios across all plots
- **Fixed**: Removed `aspect='auto'` parameter from imshow functions
- **Added**: Equal aspect ratio ensures accurate representation of warpage data geometry
# Warpage Data Masking Tool

A PyQt5-based application for annotating warpage measurement data with rectangular masks.

## Features

- Load `.rawtxt` files containing warpage measurement data (X, Y, Z coordinates)
- Automatically generates a heatmap visualization from the data
- Draw rectangular masks on the visualization
- Apply masks to the raw data (replaces coordinates with 9999.0)
- Save/load mask definitions
- Export masked data

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python mask.py
```

### Workflow

1. **Open Raw Data**: `File > Open Raw Data (.rawtxt)` or press `Ctrl+O`
   - Select a `.rawtxt` file containing X, Y, Z coordinate data
   - The application will generate a heatmap visualization automatically
   - Values of 9999.0 in the data are converted to NaN for proper visualization

2. **Draw Mask Rectangles**:
   - Left-click and drag to draw rectangular masks
   - Right-click on a rectangle to delete it

3. **Save Mask**: `File > Save Mask` or press `Ctrl+S`
   - Saves rectangle coordinates to CSV/TXT file

4. **Load Mask**: `File > Load Mask` or press `Ctrl+M`
   - Loads previously saved mask rectangles

5. **Apply Raw Mask**: `Tool > Apply Raw Mask` or press `Ctrl+R`
   - Applies the drawn masks to the raw data
   - Outputs `Raw_mask.txt` with masked coordinates replaced by 9999.0

### Tool Menu

- **Apply Raw Mask** (`Ctrl+R`): Apply masks and save masked data
- **Select All** (`Ctrl+A`): Create a mask covering the entire image
- **Delete All** (`Ctrl+D`): Remove all mask rectangles
- **Export Rectangle Coordinates** (`Ctrl+E`): Export all pixel coordinates inside rectangles

### Settings Menu

- **Set Border Thickness**: Adjust the thickness of rectangle borders
- **Set Fill Opacity**: Adjust the transparency of rectangle fills
- **Toggle Y-Axis Orientation**: Toggle between upward/downward Y-axis orientation for coordinate mapping

## File Format

### Input (.rawtxt)

The application expects tab or comma-delimited text files with at least 3 columns:
```
X,Y,Z
10.0,20.0,5.2
10.5,20.0,5.3
...
```

- Column 1: X coordinate
- Column 2: Y coordinate
- Column 3: Z value (warpage measurement)
- Values of 9999.0 are treated as invalid/masked data

### Output (Raw_mask.txt)

Same format as input, but with masked coordinates replaced:
```
X,Y,Z
9999.0,9999.0,5.2
10.5,20.0,5.3
...
```

## Key Changes from Original

- **Only accepts .rawtxt files** (no separate image file needed)
- **Automatically generates heatmap** from the selected .rawtxt data
- **Converts 9999.0 to NaN** for proper visualization in the heatmap
- Uses matplotlib to create color-coded visualization of warpage data

## Coordinate System

- **Image coordinates**: Origin at top-left, Y increases downward
- **Raw data coordinates**: Configurable (use Settings > Toggle Y-Axis Orientation)
- The application automatically handles coordinate transformation between image and data space

## Technical Details

- Built with PyQt5 for the GUI
- Uses matplotlib for heatmap generation
- Supports tab and comma delimited data files
- Automatic delimiter detection
- Handles coordinate system transformations for accurate masking

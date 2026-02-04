# .rawtxt Format Fix

## Problem Identified
The masking tool was incorrectly treating `.rawtxt` files as X,Y,Z coordinate lists, but they are actually **2D grid files** (like matrices).

## Correct .rawtxt Format

### File Structure
```
value1 value2 value3 value4 ...
value1 value2 value3 value4 ...
value1 value2 value3 value4 ...
...
```

- Each **line** represents a **row** in the grid
- Each **value** (space or tab-separated) represents a **column** in the grid
- Values are warpage measurements (Z values) in micrometers (μm)
- NO explicit X,Y coordinates are stored

### Example
```
10.5 12.3 15.7 14.2 13.8
11.2 13.1 16.2 15.5 14.1
12.8 14.5 17.3 16.8 15.2
```
This represents a 3×5 grid (3 rows, 5 columns) of warpage measurements.

## Changes Made

### 1. Updated Data Loading (`_generate_heatmap_from_raw_data`)
**Before (WRONG):**
- Expected X,Y,Z format: `x_coord, y_coord, z_value`
- Tried to extract coordinates and build a grid from them

**After (CORRECT):**
- Treats each row as a grid row
- Treats each value as a grid column
- Directly converts to 2D numpy array

### 2. Updated Grid Mapping
**Before:**
- Used unique X,Y coordinate values as grid mapping

**After:**
- Uses simple row/column indices (0 to width-1, 0 to height-1)
- `unique_x = np.arange(grid_width)` - column indices
- `unique_y = np.arange(grid_height)` - row indices

### 3. Updated Artifact Handling
Now properly converts all artifact values to NaN:
- `-4000`
- `9999`, `-9999`
- `99999`, `-99999`

Follows the same pattern as `data_loader.py` for consistency.

### 4. Updated Masking Logic
**Coordinate System:**
- Image pixels → Grid indices (row, col)
- Grid indices → Grid cells

**Masking Process:**
1. Convert image rectangle to grid row/column ranges
2. Set all grid cells in that range to `9999.0`
3. Save modified grid back to file

### 5. Updated User Messages
All messages now refer to "grid dimensions" and "columns/rows" instead of "X/Y coordinates":
- "Grid dimensions: N columns x M rows"
- "Grid bounds: Col=[0, N], Row=[0, M]"
- "Grid cells masked: X / Total"

## Coordinate Mapping

### Image to Grid Conversion
```python
# Convert image pixel to grid index
col_idx = (pixel_x / image_width) * grid_width
row_idx = (pixel_y / image_height) * grid_height

# Get grid cell bounds for rectangle
min_col = int((rect_x1 / image_width) * grid_width)
max_col = int((rect_x2 / image_width) * grid_width)
min_row = int((rect_y1 / image_height) * grid_height)
max_row = int((rect_y2 / image_height) * grid_height)
```

### Masking Grid Cells
```python
# Mask all cells in rectangle
for row in range(min_row, max_row + 1):
    for col in range(min_col, max_col + 1):
        grid_data[row, col] = 9999.0
```

## Benefits

1. **Correct Format**: Now handles actual .rawtxt file format
2. **Direct Mapping**: Simple 1:1 mapping between image and grid
3. **No Interpolation**: Grid cells map directly to pixels
4. **Consistent**: Follows same approach as `data_loader.py`
5. **Accurate Masking**: Rectangle selections now precisely mask the correct grid cells

## Testing Recommendations

1. Load a .rawtxt file with known dimensions (e.g., 100x80 grid)
2. Draw a small rectangle in the corner
3. Apply mask
4. Verify that `Raw_mask.txt` has 9999.0 values in exactly the cells you selected
5. Check that the number of masked cells matches the rectangle size

## Example Workflow

1. Open `.rawtxt` file → Heatmap displayed
2. Draw rectangle from pixel (100,100) to (200,200) on 1000x800 image
3. Conversion:
   - Grid dimensions: 50 cols x 40 rows
   - Rectangle maps to: Col[5-10], Row[5-10]
   - Masks 36 cells (6×6 grid)
4. Save → Grid cells [5:10, 5:10] now contain 9999.0

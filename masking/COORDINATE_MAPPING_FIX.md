# Coordinate Mapping Fix

## Problem
The previous implementation had incorrect coordinate mapping between the displayed heatmap image and the raw data coordinates. When users drew rectangles on the heatmap, the masked coordinates didn't accurately correspond to the selected regions.

## Solution
Implemented a proper grid-based coordinate mapping system that preserves the exact relationship between image pixels and raw data points.

## How It Works

### Three Coordinate Systems

1. **Image Pixel Coordinates** - The displayed heatmap image (e.g., 1000x800 pixels)
2. **Grid Indices** - The data grid dimensions (e.g., 50x40 grid cells based on unique X,Y values)
3. **Raw Data Coordinates** - The actual measurement coordinates (e.g., X: 0-100mm, Y: 0-80mm)

### Mapping Process

```
User draws rectangle on image
         ↓
Image Pixel Coordinates (x_pix, y_pix)
         ↓
Grid Indices: x_idx = (x_pix / img_width) * grid_width
              y_idx = (y_pix / img_height) * grid_height
         ↓
Raw Data Coordinates: x_raw = unique_x[x_idx]
                      y_raw = unique_y[y_idx]
```

## Key Changes

### 1. Store Grid Mapping Information
Added instance variables to store the grid structure:
```python
self.unique_x: Optional[np.ndarray] = None  # Unique X coordinates
self.unique_y: Optional[np.ndarray] = None  # Unique Y coordinates
self.grid_width: int = 0                     # Number of unique X values
self.grid_height: int = 0                    # Number of unique Y values
```

### 2. Save Grid Info During Heatmap Generation
When generating the heatmap, we now store the grid mapping:
```python
self.unique_x = unique_x
self.unique_y = unique_y
self.grid_width = len(unique_x)
self.grid_height = len(unique_y)
```

### 3. Use Grid Mapping for Coordinate Conversion
Both `_get_rectangle_bounds_in_raw_coords()` and `_interpolate_coords()` now use the grid-based mapping instead of linear interpolation.

## Benefits

1. **Accurate Masking** - Rectangle selections now precisely correspond to the raw data points
2. **No Approximation Errors** - Direct lookup in the grid eliminates interpolation errors
3. **Handles Non-Uniform Grids** - Works correctly even if X,Y spacing is irregular
4. **Consistent Mapping** - Same mapping logic used for both masking and saving

## Testing

To verify the fix works correctly:

1. Open a .rawtxt file
2. Draw a rectangle over a specific region in the heatmap
3. Apply the mask
4. Check that the masked coordinates in `Raw_mask.txt` correspond to the selected region
5. The output should show exactly which raw data points (X,Y coordinates) were masked

## Example

If the raw data has:
- X values: [0, 0.5, 1.0, 1.5, ..., 100]  (200 unique values)
- Y values: [0, 0.4, 0.8, 1.2, ..., 80]   (200 unique values)

And you draw a rectangle from pixel (100, 100) to (200, 200) on a 1000x800 image:

**Old behavior (incorrect):**
- Would use linear interpolation: X = 10mm to 20mm, Y = 10mm to 20mm
- Might not align with actual grid points

**New behavior (correct):**
- Maps to grid indices: x_idx = 20 to 40, y_idx = 25 to 50
- Converts to exact coordinates: X = unique_x[20] to unique_x[40], Y = unique_y[25] to unique_y[50]
- Masks exactly the data points in that grid region

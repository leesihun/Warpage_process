# Coordinate System Improvements for Mask Tool

## Overview
Enhanced the mask.py tool to properly handle coordinate transformations between image space and raw data space, addressing critical issues with size differences and coordinate system orientations.

## Problems Addressed

### 1. Size Mismatch Between Image and Raw Data
**Issue:** JPG images are typically larger than raw data coordinate spaces, but the original code didn't properly account for scaling factors.

**Solution:**
- Implemented `_get_raw_bounds()` to extract complete bounds (min_x, max_x, min_y, max_y) from raw data
- Calculate precise scaling factors: `factor_x = raw_width / img_width`, `factor_y = raw_height / img_height`
- Apply scaling with proper offset handling: `x_raw = min_x_raw + (x_img * factor_x)`

### 2. Coordinate System Orientation
**Issue:** Image coordinates always have origin at top-left with Y increasing downward, but raw measurement data may have origin at bottom-left with Y increasing upward (standard engineering/scientific convention).

**Solution:**
- Added `raw_data_y_axis_down` configuration flag (default: True)
- Implemented Y-axis flipping when orientations differ:
  - If raw data Y increases upward: `y_raw = max_y_raw - (y_img * factor_y)`
  - If raw data Y increases downward: `y_raw = min_y_raw + (y_img * factor_y)`
- Added menu option: **Settings > Toggle Y-Axis Orientation**

### 3. Coordinate System Offsets
**Issue:** Raw data coordinates may not start at (0, 0), but original code assumed zero-based coordinates.

**Solution:**
- Track minimum values (min_x, min_y) in addition to maximum values
- Apply proper offset during coordinate transformation
- All transformations now work in arbitrary coordinate spaces

## New Features

### 1. Enhanced Bounds Calculation
```python
def _get_raw_bounds(self) -> Optional[Tuple[float, float, float, float, float, float]]:
    """Returns: (min_x, max_x, min_y, max_y, width, height)"""
```
- Finds both minimum and maximum coordinates
- Calculates actual width and height
- Validates that bounds are sensible

### 2. Improved Coordinate Interpolation
```python
def _interpolate_coords(
    pixel_coords: List[Tuple[int, int, int, int]],
    raw_bounds: Tuple[float, float, float, float, float, float],
    img_dims: Tuple[int, int]
) -> List[Tuple[float, float, float, float]]:
```
- Handles size scaling
- Handles Y-axis orientation
- Handles coordinate offsets
- Comprehensive documentation of transformation logic

### 3. Raw Coordinate Space Masking
```python
def _get_rectangle_bounds_in_raw_coords(self) -> List[Tuple[float, float, float, float]]:
```
- Rectangles are now transformed to raw data coordinate space BEFORE comparison
- Ensures accurate point-in-rectangle tests
- Works correctly regardless of size differences or orientation

### 4. Coordinate System Feedback
When loading raw data, users now see:
```
Data bounds:
  X: [0.00, 1024.50] (width: 1024.50)
  Y: [0.00, 768.25] (height: 768.25)
  Total points: 786432

Current Y-axis orientation: DOWN
(Change in Settings > Toggle Y-Axis Orientation if needed)
```

When saving masks, users see:
```
Coordinate mapping:
Image size: 1920 x 1440 pixels
Raw data bounds: X=[0.00, 1024.50], Y=[0.00, 768.25]
Raw data size: 1024.50 x 768.25
Scale factors: X=0.5336, Y=0.5336
Y-axis orientation: down (image is always down)
```

When applying masks, detailed console output shows:
```
============================================================
COORDINATE SYSTEM MAPPING
============================================================
Image dimensions: 1920 x 1440 pixels
Raw data bounds: X=[0.00, 1024.50], Y=[0.00, 768.25]
Raw data size: 1024.50 x 768.25
Scale factors: X=0.533594, Y=0.533507
Y-axis orientation: Raw data DOWN, Image DOWN

Number of mask rectangles: 2
  Rectangle 0: X=[100.50, 250.75], Y=[200.00, 350.25]
  Rectangle 1: X=[500.00, 650.80], Y=[400.50, 550.90]
============================================================

Masking result: 15234 points masked out of 786432 total rows
============================================================
```

## Usage Guide

### Step 1: Load Image and Raw Data
1. **File > Open Image** - Select JPG/PNG image
2. System prompts for associated raw data file (.txt, .csv, .rawtxt)
3. Review coordinate system information in popup

### Step 2: Check Y-Axis Orientation
- If raw data Y-axis increases **downward** (like image): Keep default setting
- If raw data Y-axis increases **upward** (engineering standard): Use **Settings > Toggle Y-Axis Orientation**

### Step 3: Draw Mask Rectangles
- Left-click and drag to draw rectangles over defect areas
- Right-click on rectangle to delete it
- **Tool > Select All** to mask entire image
- **Tool > Delete All** to clear all rectangles

### Step 4: Save or Apply Mask

#### Option A: Save Mask Coordinates
- **File > Save Mask (Ctrl+S)**
- Saves rectangle definitions in raw data coordinate space
- Can be reloaded later with **File > Load Mask (Ctrl+M)**

#### Option B: Apply Mask to Raw Data
- **Tool > Apply Raw Mask (Ctrl+R)**
- Creates `Raw_mask.txt` with masked points set to (9999.0, 9999.0)
- Console shows detailed coordinate mapping and masking statistics

## Technical Implementation

### Coordinate Transformation Pipeline

```
User draws rectangle in image
         ↓
Scene coordinates (PyQt graphics scene)
         ↓
Image pixel coordinates (account for DPI)
         ↓
[APPLY SCALING AND OFFSET]
factor_x = raw_width / img_width
factor_y = raw_height / img_height
x_raw = min_x_raw + (x_img * factor_x)
         ↓
[APPLY Y-AXIS ORIENTATION]
if raw_data_y_axis_down:
    y_raw = min_y_raw + (y_img * factor_y)
else:
    y_raw = max_y_raw - (y_img * factor_y)
         ↓
Raw data coordinates
         ↓
Point-in-rectangle test against actual raw data points
         ↓
Mask matching points as (9999.0, 9999.0)
```

### Key Formulas

**X-coordinate transformation (always straightforward):**
```python
x_raw = min_x_raw + (x_pixel * (raw_width / img_width))
```

**Y-coordinate transformation (orientation-dependent):**
```python
# When both Y-axes increase downward:
y_raw = min_y_raw + (y_pixel * (raw_height / img_height))

# When raw Y increases upward, image Y increases downward:
y_raw = max_y_raw - (y_pixel * (raw_height / img_height))
```

## Validation Checklist

When using the tool, verify:

1. ✓ **Scale factors are reasonable** (typically 0.3 to 3.0)
   - If much larger/smaller, check if wrong data file was loaded

2. ✓ **Rectangle placement looks correct visually**
   - Draw test rectangle, apply mask, check if expected points are masked

3. ✓ **Y-axis orientation matches data**
   - If top of image masks bottom of data (or vice versa), toggle Y-axis orientation

4. ✓ **Masking count makes sense**
   - If masking entire image masks very few points, orientation is likely wrong
   - If masking small area masks most points, orientation is likely wrong

## Changes Made to Code

### Modified Methods:
- `__init__()` - Added `raw_data_y_axis_down` configuration
- `_create_menus()` - Added Y-axis orientation toggle menu item
- `toggle_y_axis_orientation()` - NEW: Toggle coordinate system orientation
- `_get_raw_bounds()` - REPLACED `_get_raw_dimensions()`: Now finds min/max, not just max
- `_interpolate_coords()` - Enhanced with offset handling and Y-axis flipping
- `_get_rectangle_bounds_in_raw_coords()` - REPLACED `_get_rectangle_bounds()`: Transforms to raw coordinates
- `_load_raw_data()` - Enhanced feedback showing data bounds and orientation
- `save_mask()` - Enhanced with coordinate system information dialog
- `apply_raw_mask()` - Enhanced with detailed console logging
- `_is_point_in_rectangles()` - Updated type hints for float coordinates
- `_mask_raw_data()` - Updated documentation

### Backward Compatibility
- Old mask files can still be loaded (if coordinates were in same space)
- Default Y-axis setting (downward) matches previous behavior
- All existing functionality preserved

## Example Scenarios

### Scenario 1: Typical Warpage Data
- Image: 1920x1440 JPG
- Raw data: X=[0, 1024], Y=[0, 768], ~780K points
- Y-axis: Both downward (default setting works)
- Scale: ~0.53x

### Scenario 2: Engineering Coordinate System
- Image: 2048x1536 JPG
- Raw data: X=[0, 100], Y=[0, 75] mm, ~100K points
- Y-axis: Raw data upward (TOGGLE setting needed)
- Scale: ~0.049x (image much larger than data range)

### Scenario 3: Non-Zero Origin
- Image: 1024x768 JPG
- Raw data: X=[500, 1500], Y=[200, 1000], ~800K points
- Y-axis: Both downward
- Scale: ~1.0x (similar sizes)
- Proper offset handling ensures correct mapping

## Troubleshooting

### Issue: Masked region is in wrong location
**Cause:** Y-axis orientation mismatch
**Solution:** Use **Settings > Toggle Y-Axis Orientation**

### Issue: Scale factors seem wrong
**Cause:** Loaded wrong raw data file
**Solution:** Reload correct raw data file associated with the image

### Issue: Very few or very many points masked
**Cause:** Coordinate system mismatch
**Solution:** Check orientation setting and verify raw data bounds match image

### Issue: Mask coordinates don't align when reloading
**Cause:** Different raw data file or orientation setting changed
**Solution:** Use same raw data file and orientation setting as when mask was saved

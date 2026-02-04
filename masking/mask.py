"""Image Annotation Tool for Warpage Mask Creation.

A PyQt5-based application for annotating images with rectangular regions
and applying masks to coordinate data.
"""

import csv
import math
import os
import sys
from typing import List, Tuple, Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtCore, QtGui, QtWidgets


# Constants
DEFAULT_BORDER_THICKNESS = 1
DEFAULT_FILL_OPACITY = 0.3
MASK_COLOR = QtGui.QColor(255, 0, 0)
MASK_VALUE = "9999.0"
DEFAULT_DELIMITER = ","


class ImageView(QtWidgets.QGraphicsView):
    """Custom QGraphicsView that handles rectangle drawing."""

    def __init__(self, scene: QtWidgets.QGraphicsScene, app: 'ImageAnnotationApp'):
        super().__init__(scene)
        self.app = app
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CrossCursor)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse press events for drawing and deleting rectangles."""
        if not self.app.image_item:
            return super().mousePressEvent(event)

        scene_pos = self.mapToScene(event.pos())

        if event.button() == QtCore.Qt.LeftButton:
            self._handle_left_click(scene_pos)
        elif event.button() == QtCore.Qt.RightButton:
            self._handle_right_click(scene_pos)
        else:
            super().mousePressEvent(event)

    def _handle_left_click(self, scene_pos: QtCore.QPointF) -> None:
        """Start drawing a new rectangle."""
        if self.app.image_item.contains(scene_pos):
            self.app.drawing = True
            self.app.start_pos = scene_pos
            self.app.rubber_band = self.app.create_rect_item(
                QtCore.QRectF(scene_pos, scene_pos),
                is_dashed=True
            )
            self.scene().addItem(self.app.rubber_band)

    def _handle_right_click(self, scene_pos: QtCore.QPointF) -> None:
        """Delete rectangle at clicked position."""
        items = self.scene().items(scene_pos)
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsRectItem) and item is not self.app.rubber_band:
                self.scene().removeItem(item)
                if item in self.app.rect_items:
                    self.app.rect_items.remove(item)
                break

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Update rubber band rectangle while dragging."""
        if getattr(self.app, 'drawing', False) and self.app.rubber_band:
            scene_pos = self.mapToScene(event.pos())
            rect = QtCore.QRectF(self.app.start_pos, scene_pos).normalized()
            self.app.rubber_band.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """Finalize rectangle drawing on mouse release."""
        if getattr(self.app, 'drawing', False) and event.button() == QtCore.Qt.LeftButton:
            self.app.drawing = False
            if self.app.rubber_band:
                self._finalize_rectangle()
        else:
            super().mouseReleaseEvent(event)

    def _finalize_rectangle(self) -> None:
        """Convert rubber band to permanent rectangle."""
        rect = self.app.rubber_band.rect().normalized()
        img_rect = self.app.image_item.boundingRect()
        rect = rect.intersected(img_rect)

        self.scene().removeItem(self.app.rubber_band)
        self.app.rubber_band = None

        if rect.isValid() and rect.width() > 0 and rect.height() > 0:
            rect_item = self.app.create_rect_item(rect)
            rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.scene().addItem(rect_item)
            self.app.rect_items.append(rect_item)


class ImageAnnotationApp(QtWidgets.QMainWindow):
    """Main application window for image annotation and masking."""

    def __init__(self):
        super().__init__()

        # Visual parameters
        self.border_thickness = DEFAULT_BORDER_THICKNESS
        self.fill_opacity = DEFAULT_FILL_OPACITY

        # Data handling
        self.raw_data: List[List[str]] = []
        self.raw_delimiter: str = DEFAULT_DELIMITER
        self.raw_path: Optional[str] = None

        # Grid mapping for coordinate conversion
        self.unique_x: Optional[np.ndarray] = None
        self.unique_y: Optional[np.ndarray] = None
        self.grid_width: int = 0
        self.grid_height: int = 0

        # Coordinate system configuration
        # Set to True if raw data Y-axis increases downward (like image coordinates)
        # Set to False if raw data Y-axis increases upward (typical scientific/engineering)
        self.raw_data_y_axis_down: bool = True

        # UI state
        self.image_item: Optional[QtWidgets.QGraphicsPixmapItem] = None
        self.image_path: Optional[str] = None
        self.rect_items: List[QtWidgets.QGraphicsRectItem] = []
        self.drawing: bool = False
        self.start_pos: Optional[QtCore.QPointF] = None
        self.rubber_band: Optional[QtWidgets.QGraphicsRectItem] = None

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Image Annotation App")
        self.resize(800, 600)

        # Central widget and layout
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Graphics view / scene
        self.scene = QtWidgets.QGraphicsScene()
        self.view = ImageView(self.scene, self)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setMouseTracking(True)
        self.view.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.view)

        self._create_menus()

    def _create_menus(self) -> None:
        """Create menu bar with all actions."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        self._add_action(file_menu, "Open Raw Data (.rawtxt)", "Ctrl+O", self.open_image)
        self._add_action(file_menu, "Load Mask", "Ctrl+M", self.load_mask)
        self._add_action(file_menu, "Save Mask", "Ctrl+S", self.save_mask)

        # Tool menu
        tool_menu = menubar.addMenu("Tool")
        self._add_action(tool_menu, "Apply Raw Mask", "Ctrl+R", self.apply_raw_mask)
        self._add_action(tool_menu, "Select All", "Ctrl+A", self.select_all)
        self._add_action(tool_menu, "Delete All", "Ctrl+D", self.delete_all)
        self._add_action(tool_menu, "Export Rectangle Coordinates", "Ctrl+E", self.export_rectangle_coords)

        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        self._add_action(settings_menu, "Set Border Thickness", None, self.set_border_thickness)
        self._add_action(settings_menu, "Set Fill Opacity", None, self.set_fill_opacity)
        self._add_action(settings_menu, "Toggle Y-Axis Orientation", None, self.toggle_y_axis_orientation)

    def _add_action(
        self,
        menu: QtWidgets.QMenu,
        text: str,
        shortcut: Optional[str],
        callback: callable
    ) -> QtWidgets.QAction:
        """Helper method to add an action to a menu."""
        action = QtWidgets.QAction(text, self)
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def create_rect_item(
        self,
        rect: QtCore.QRectF,
        is_dashed: bool = False
    ) -> QtWidgets.QGraphicsRectItem:
        """Create a styled rectangle item with current visual settings."""
        rect_item = QtWidgets.QGraphicsRectItem(rect)

        pen_style = QtCore.Qt.DashLine if is_dashed else QtCore.Qt.SolidLine
        pen = QtGui.QPen(MASK_COLOR, self.border_thickness, pen_style)
        rect_item.setPen(pen)

        brush = QtGui.QBrush(QtGui.QColor(
            MASK_COLOR.red(),
            MASK_COLOR.green(),
            MASK_COLOR.blue(),
            int(255 * self.fill_opacity)
        ))
        rect_item.setBrush(brush)

        return rect_item

    # ---------------------------------------------------------------------
    # Settings actions
    # ---------------------------------------------------------------------

    def set_border_thickness(self) -> None:
        """Prompt user to set border thickness."""
        new_thickness, ok = QtWidgets.QInputDialog.getInt(
            self,
            "Set Border Thickness",
            "Border Thickness (0=thinnest): ",
            value=self.border_thickness,
            min=0,
            max=20
        )
        if ok:
            self.border_thickness = new_thickness

    def set_fill_opacity(self) -> None:
        """Prompt user to set fill opacity."""
        new_opacity, ok = QtWidgets.QInputDialog.getDouble(
            self,
            "Set Fill Opacity",
            "Opacity (0.0 ~ 1.0): ",
            value=self.fill_opacity,
            min=0.0,
            max=1.0,
            decimals=2
        )
        if ok:
            self.fill_opacity = new_opacity

    def toggle_y_axis_orientation(self) -> None:
        """Toggle Y-axis orientation for raw data coordinate system."""
        self.raw_data_y_axis_down = not self.raw_data_y_axis_down
        orientation = "downward" if self.raw_data_y_axis_down else "upward"
        QtWidgets.QMessageBox.information(
            self,
            "Y-Axis Orientation",
            f"Raw data Y-axis now set to increase {orientation}\n"
            f"(Image Y-axis always increases downward)"
        )

    # ---------------------------------------------------------------------
    # Image handling
    # ---------------------------------------------------------------------

    def open_image(self) -> None:
        """Open a .rawtxt file and generate a heatmap visualization as the background."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Raw Data File",
            "",
            "Raw Text Files (*.rawtxt)"
        )
        if not file_path:
            return

        # Load the raw data
        success = self._load_raw_data(file_path)
        if not success:
            return

        # Generate heatmap from raw data
        pixmap = self._generate_heatmap_from_raw_data()
        if pixmap is None or pixmap.isNull():
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to generate heatmap from data.")
            return

        # Display the generated heatmap
        self.scene.clear()
        self.rect_items.clear()
        self.image_item = self.scene.addPixmap(pixmap)
        self.image_item.setPos(0, 0)
        self.image_item.setZValue(-1)
        self.image_path = file_path
        self._fit_image()

    def _fit_image(self) -> None:
        """Fit the image within the view, maintaining aspect ratio."""
        if self.image_item:
            self.view.fitInView(self.image_item, QtCore.Qt.KeepAspectRatio)

    def _generate_heatmap_from_raw_data(self) -> Optional[QtGui.QPixmap]:
        """Generate a heatmap visualization from loaded raw data.

        .rawtxt files are 2D grids where each line is a row and values are columns.
        Converts 9999.0 and other artifact values to NaN for proper visualization.

        Returns:
            QPixmap of the generated heatmap, or None on failure.
        """
        if not self.raw_data:
            return None

        try:
            # Parse 2D grid data from raw_data
            # Each row in raw_data is a line from the file
            # Each value in the line is a grid column
            grid_rows = []
            for row in self.raw_data:
                if len(row) == 0:
                    continue
                try:
                    # Convert all values to float
                    row_values = [float(val) for val in row]
                    grid_rows.append(row_values)
                except ValueError:
                    # Skip rows that can't be converted (headers, comments)
                    continue

            if not grid_rows:
                return None

            # Convert to numpy array (2D grid)
            grid_z = np.array(grid_rows, dtype=float)

            # Store grid dimensions for coordinate conversion
            self.grid_height, self.grid_width = grid_z.shape
            # For grid data, unique_x and unique_y are just indices
            self.unique_x = np.arange(self.grid_width)
            self.unique_y = np.arange(self.grid_height)

            # Convert artifact values to NaN (following data_loader.py pattern)
            # Artifact values: -4000, 9999, -9999, 99999, -99999
            invalid_values = np.array([-4000, 9999, -9999, 99999, -99999])
            mask = np.isin(grid_z, invalid_values)
            if mask.any():
                grid_z[mask] = np.nan

            # Create figure with proper aspect ratio based on grid dimensions
            # Use grid dimensions directly to preserve original aspect ratio
            aspect_ratio = self.grid_width / self.grid_height

            # Scale figure size while maintaining aspect ratio
            max_size = 12  # Maximum dimension in inches
            if aspect_ratio > 1:
                fig_width = max_size
                fig_height = max_size / aspect_ratio
            else:
                fig_width = max_size * aspect_ratio
                fig_height = max_size

            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)

            # Plot heatmap with original aspect ratio preserved
            ax.imshow(grid_z, cmap='jet', aspect='equal', interpolation='nearest')

            # Remove all axes, labels, and margins
            ax.set_axis_off()

            # Remove all padding and margins
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

            # Convert matplotlib figure to QPixmap
            fig.canvas.draw()

            # Get the RGBA buffer from the figure
            buf = fig.canvas.buffer_rgba()
            w, h = fig.canvas.get_width_height()

            # Create QImage from buffer
            qimage = QtGui.QImage(buf, w, h, QtGui.QImage.Format_RGBA8888)
            pixmap = QtGui.QPixmap.fromImage(qimage)

            # Clean up
            plt.close(fig)

            return pixmap

        except Exception as e:
            print(f"Error generating heatmap: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _load_raw_data(self, raw_path: str) -> bool:
        """Load raw coordinate data from a file.

        Supports CSV (comma) or tab-delimited text files.
        Detects the delimiter automatically using csv.Sniffer.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(raw_path, "r", newline="") as f:
                sample = f.read(2048)
                f.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=[',', '\t'])
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ','

                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)

            self.raw_data = rows
            self.raw_delimiter = delimiter
            self.raw_path = raw_path

            # Calculate grid dimensions
            grid_rows = []
            for row in rows:
                if len(row) == 0:
                    continue
                try:
                    [float(val) for val in row]
                    grid_rows.append(len(row))
                except ValueError:
                    continue

            if grid_rows:
                num_rows = len(grid_rows)
                num_cols = max(grid_rows) if grid_rows else 0
                msg = (
                    f"Loaded raw data from {os.path.basename(raw_path)}\n\n"
                    f"Grid dimensions:\n"
                    f"  Rows: {num_rows}\n"
                    f"  Columns: {num_cols}\n"
                    f"  Total data points: {num_rows * num_cols}\n"
                )
            else:
                msg = f"Loaded raw data from {os.path.basename(raw_path)}\n{len(rows)} rows"

            QtWidgets.QMessageBox.information(self, "Raw Data Loaded", msg)
            return True

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to read raw data: {e}"
            )
            self.raw_data = []
            return False

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Handle window resize events."""
        super().resizeEvent(event)
        self._fit_image()

    # ---------------------------------------------------------------------
    # Tool actions
    # ---------------------------------------------------------------------

    def select_all(self) -> None:
        """Create a rectangle covering the entire image."""
        if not self.image_item:
            return

        self.delete_all()
        img_rect = self.image_item.boundingRect()
        rect_item = self.create_rect_item(img_rect)
        self.scene.addItem(rect_item)
        self.rect_items.append(rect_item)

    def delete_all(self) -> None:
        """Remove all rectangles from the scene."""
        for item in self.rect_items:
            self.scene.removeItem(item)
        self.rect_items.clear()

    # ---------------------------------------------------------------------
    # Mask persistence
    # ---------------------------------------------------------------------

    def _get_pixel_coords(self) -> List[Tuple[int, int, int, int]]:
        """Return rectangle coordinates in absolute pixel coordinates.

        Returns:
            List of (x1, y1, x2, y2) tuples in pixel coordinates.
        """
        if not self.image_item:
            return []

        dpr = self.image_item.pixmap().devicePixelRatio() if self.image_item.pixmap() else 1.0
        pixel_coords = []

        img_width = int(self.image_item.pixmap().width() * dpr)
        img_height = int(self.image_item.pixmap().height() * dpr)

        for item in self.rect_items:
            r = item.rect()
            x1 = max(0, min(int(r.left() * dpr), img_width))
            y1 = max(0, min(int(r.top() * dpr), img_height))
            x2 = max(0, min(int(r.right() * dpr), img_width))
            y2 = max(0, min(int(r.bottom() * dpr), img_height))
            pixel_coords.append((x1, y1, x2, y2))

        return pixel_coords

    def _get_raw_bounds(self) -> Optional[Tuple[float, float, float, float, float, float]]:
        """Extract bounds from raw grid data.

        For 2D grid data, bounds are based on grid dimensions (rows, columns).

        Returns:
            Tuple of (min_col, max_col, min_row, max_row, width, height) or None.
        """
        if not self.raw_data or self.grid_width == 0 or self.grid_height == 0:
            return None

        # For grid data, bounds are simply the grid dimensions
        min_col = 0
        max_col = self.grid_width - 1
        min_row = 0
        max_row = self.grid_height - 1
        width = self.grid_width
        height = self.grid_height

        return (min_col, max_col, min_row, max_row, width, height)

    def _interpolate_coords(
        self,
        pixel_coords: List[Tuple[int, int, int, int]],
        raw_bounds: Tuple[float, float, float, float, float, float],
        img_dims: Tuple[int, int]
    ) -> List[Tuple[float, float, float, float]]:
        """Interpolate pixel coordinates to raw data coordinate space.

        Uses grid-based mapping: Image pixels → Grid indices → Raw data coordinates

        Args:
            pixel_coords: List of (x1, y1, x2, y2) in image pixel space
            raw_bounds: (min_x, max_x, min_y, max_y, width, height) of raw data (unused, kept for compatibility)
            img_dims: (width, height) of image in pixels

        Returns:
            List of (x1, y1, x2, y2) in raw data coordinate space
        """
        if self.unique_x is None or self.unique_y is None:
            # Fallback to pixel coordinates if grid mapping not available
            return [(float(x1), float(y1), float(x2), float(y2)) for x1, y1, x2, y2 in pixel_coords]

        img_width, img_height = img_dims

        interpolated = []
        for x1_pix, y1_pix, x2_pix, y2_pix in pixel_coords:
            # Convert pixel coordinates to grid indices
            x1_grid = (x1_pix / img_width) * self.grid_width
            x2_grid = (x2_pix / img_width) * self.grid_width
            y1_grid = (y1_pix / img_height) * self.grid_height
            y2_grid = (y2_pix / img_height) * self.grid_height

            # Clamp to valid grid indices
            x1_idx = int(max(0, min(x1_grid, self.grid_width - 1)))
            x2_idx = int(max(0, min(x2_grid, self.grid_width - 1)))
            y1_idx = int(max(0, min(y1_grid, self.grid_height - 1)))
            y2_idx = int(max(0, min(y2_grid, self.grid_height - 1)))

            # Convert grid indices to raw data coordinates
            x1_raw = self.unique_x[x1_idx]
            x2_raw = self.unique_x[x2_idx]
            y1_raw = self.unique_y[y1_idx]
            y2_raw = self.unique_y[y2_idx]

            interpolated.append((x1_raw, y1_raw, x2_raw, y2_raw))

        return interpolated

    def save_mask(self) -> None:
        """Save the mask to a CSV or TXT file.

        Coordinates are saved in raw data coordinate space, accounting for:
        - Size differences between JPG image and raw data
        - Y-axis orientation differences
        - Coordinate system offsets
        """
        if not self.image_item:
            QtWidgets.QMessageBox.information(self, "Info", "Load an image first.")
            return

        pixel_coords = self._get_pixel_coords()
        if not pixel_coords:
            QtWidgets.QMessageBox.information(self, "Info", "No mask to save.")
            return

        # Get raw data bounds
        raw_bounds = self._get_raw_bounds()
        dpr = self.image_item.pixmap().devicePixelRatio() if self.image_item.pixmap() else 1.0
        img_width = int(self.image_item.pixmap().width() * dpr)
        img_height = int(self.image_item.pixmap().height() * dpr)

        # Interpolate if raw bounds are known
        if raw_bounds:
            coords = self._interpolate_coords(pixel_coords, raw_bounds, (img_width, img_height))
            min_col, max_col, min_row, max_row, width, height = raw_bounds
            info_msg = (
                f"Coordinate mapping:\n"
                f"Image size: {img_width} x {img_height} pixels\n"
                f"Grid dimensions: {width} columns x {height} rows\n"
                f"Grid bounds: Col=[{min_col:.0f}, {max_col:.0f}], Row=[{min_row:.0f}, {max_row:.0f}]\n"
                f"Scale factors: Col={width/img_width:.4f}, Row={height/img_height:.4f}"
            )
        else:
            coords = pixel_coords
            info_msg = "No grid mapping available - saving in pixel coordinates"

        # Show coordinate system info
        QtWidgets.QMessageBox.information(self, "Coordinate System", info_msg)

        # Prompt for save location
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Mask",
            "mask.csv",
            "CSV Files (*.csv);;Text Files (*.txt)"
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        delimiter = "," if ext == ".csv" else "\t"

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(["x1", "y1", "x2", "y2"])
                for coord in coords:
                    writer.writerow([f"{c:.6f}" for c in coord])
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Mask saved to {file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def load_mask(self) -> None:
        """Load mask rectangles from a CSV or TXT file."""
        if not self.image_item:
            QtWidgets.QMessageBox.information(self, "Info", "Load an image first.")
            return

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Mask",
            "",
            "CSV Files (*.csv);;Text Files (*.txt)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)

            # Support optional header
            if rows and rows[0][0].lower().startswith('x'):
                rows = rows[1:]

            self.delete_all()
            for row in rows:
                if len(row) < 4:
                    continue
                x1, y1, x2, y2 = map(float, row[:4])
                rect = QtCore.QRectF(x1, y1, x2 - x1, y2 - y1)
                rect_item = self.create_rect_item(rect)
                self.scene.addItem(rect_item)
                self.rect_items.append(rect_item)

            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Mask loaded from {file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # ---------------------------------------------------------------------
    # Export and masking operations
    # ---------------------------------------------------------------------

    def export_rectangle_coords(self) -> None:
        """Export all integer pixel coordinates inside each rectangle to a CSV file."""
        if not self.image_item:
            QtWidgets.QMessageBox.information(self, "Info", "Load an image first.")
            return

        if not self.rect_items:
            QtWidgets.QMessageBox.information(self, "Info", "No rectangles to export.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Coordinates",
            "coords.csv",
            "CSV Files (*.csv);;Text Files (*.txt)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["rect_index", "x", "y"])

                dpr = self.image_item.pixmap().devicePixelRatio() if self.image_item.pixmap() else 1.0
                img_width = int(self.image_item.pixmap().width() * dpr)
                img_height = int(self.image_item.pixmap().height() * dpr)

                for idx, item in enumerate(self.rect_items):
                    r = item.rect()
                    x_start = max(0, min(int(math.floor(r.left() * dpr)), img_width))
                    x_end = max(0, min(int(math.ceil(r.right() * dpr)), img_width))
                    y_start = max(0, min(int(math.floor(r.top() * dpr)), img_height))
                    y_end = max(0, min(int(math.ceil(r.bottom() * dpr)), img_height))

                    for x in range(x_start, x_end):
                        for y in range(y_start, y_end):
                            writer.writerow([idx, x, y])

            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Coordinates exported to {file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def _get_rectangle_bounds_in_raw_coords(self) -> List[Tuple[float, float, float, float]]:
        """Extract rectangle bounds in raw data coordinate space.

        Maps from image pixel coordinates to raw data coordinates using the stored grid mapping.
        The conversion is: Image pixels → Grid indices → Raw data coordinates

        Returns:
            List of (min_x, min_y, max_x, max_y) tuples in raw data coordinates.
        """
        if not self.image_item or self.unique_x is None or self.unique_y is None:
            return []

        # Get image dimensions in pixels
        pixmap = self.image_item.pixmap()
        dpr = pixmap.devicePixelRatio() if pixmap else 1.0
        img_width = int(pixmap.width() * dpr)
        img_height = int(pixmap.height() * dpr)
        image_pos = self.image_item.pos()

        rects = []
        for item in self.rect_items:
            scene_rect = item.rect()

            # Convert scene coordinates to image-relative pixel coordinates
            x1_pix = max(0.0, min(scene_rect.left() - image_pos.x(), float(img_width)))
            y1_pix = max(0.0, min(scene_rect.top() - image_pos.y(), float(img_height)))
            x2_pix = max(0.0, min(scene_rect.right() - image_pos.x(), float(img_width)))
            y2_pix = max(0.0, min(scene_rect.bottom() - image_pos.y(), float(img_height)))

            # Convert pixel coordinates to grid indices
            # The heatmap grid spans the entire image, so we can map directly
            x1_grid = (x1_pix / img_width) * self.grid_width
            x2_grid = (x2_pix / img_width) * self.grid_width
            y1_grid = (y1_pix / img_height) * self.grid_height
            y2_grid = (y2_pix / img_height) * self.grid_height

            # Clamp to valid grid indices
            x1_idx = int(max(0, min(x1_grid, self.grid_width - 1)))
            x2_idx = int(max(0, min(x2_grid, self.grid_width - 1)))
            y1_idx = int(max(0, min(y1_grid, self.grid_height - 1)))
            y2_idx = int(max(0, min(y2_grid, self.grid_height - 1)))

            # Convert grid indices to raw data coordinates using unique_x and unique_y
            x1_raw = self.unique_x[x1_idx]
            x2_raw = self.unique_x[x2_idx]
            y1_raw = self.unique_y[y1_idx]
            y2_raw = self.unique_y[y2_idx]

            # Ensure min < max
            min_x = min(x1_raw, x2_raw)
            max_x = max(x1_raw, x2_raw)
            min_y = min(y1_raw, y2_raw)
            max_y = max(y1_raw, y2_raw)

            rects.append((min_x, min_y, max_x, max_y))

        return rects

    def _is_grid_cell_in_rectangles(
        self,
        row: int,
        col: int,
        rectangles: List[Tuple[float, float, float, float]]
    ) -> bool:
        """Check if a grid cell is inside any rectangle.

        Args:
            row, col: Grid cell indices
            rectangles: List of (min_col, min_row, max_col, max_row) in grid coordinates

        Returns:
            True if cell is inside any rectangle
        """
        for min_col, min_row, max_col, max_row in rectangles:
            if min_col <= col <= max_col and min_row <= row <= max_row:
                return True
        return False

    def _load_grid_file(self, file_path: str) -> Optional[Tuple[List[List[str]], str]]:
        """Load a grid file (.txt or .rawtxt) and return its data.

        Args:
            file_path: Path to the file to load

        Returns:
            Tuple of (grid_data, delimiter) or None if loading fails
        """
        try:
            with open(file_path, "r", newline="") as f:
                sample = f.read(2048)
                f.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=[',', '\t'])
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ','

                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)

            return rows, delimiter
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def _mask_grid_data(
        self,
        grid_data: List[List[str]],
        rectangles: List[Tuple[float, float, float, float]],
        grid_width: int,
        grid_height: int
    ) -> Tuple[List[List[str]], int]:
        """Apply masking to grid data based on rectangles.

        For 2D grid data, rectangles specify grid cell ranges.
        Masked cells have their values set to 9999.0.

        Args:
            grid_data: Raw grid data as list of lists
            rectangles: List of (min_col, min_row, max_col, max_row) in grid indices
            grid_width: Number of columns in the grid
            grid_height: Number of rows in the grid

        Returns:
            Tuple of (processed_data, points_masked_count).
        """
        # Convert grid_data to numpy array for processing
        grid_rows = []
        for row in grid_data:
            if len(row) == 0:
                continue
            try:
                row_values = [float(val) for val in row]
                grid_rows.append(row_values)
            except ValueError:
                # Skip non-numeric rows
                continue

        if not grid_rows:
            return [], 0

        # Convert to numpy array
        grid_array = np.array(grid_rows, dtype=float)
        points_masked = 0

        # Apply masking for each rectangle
        for min_col, min_row, max_col, max_row in rectangles:
            # Convert to integer indices
            min_col_idx = int(min_col)
            max_col_idx = int(max_col)
            min_row_idx = int(min_row)
            max_row_idx = int(max_row)

            # Clamp to valid grid bounds
            min_col_idx = max(0, min(min_col_idx, grid_width - 1))
            max_col_idx = max(0, min(max_col_idx, grid_width - 1))
            min_row_idx = max(0, min(min_row_idx, grid_height - 1))
            max_row_idx = max(0, min(max_row_idx, grid_height - 1))

            # Count cells to be masked in this rectangle
            for r in range(min_row_idx, max_row_idx + 1):
                for c in range(min_col_idx, max_col_idx + 1):
                    if r < grid_array.shape[0] and c < grid_array.shape[1]:
                        if not np.isnan(grid_array[r, c]) and grid_array[r, c] != 9999.0:
                            points_masked += 1
                        grid_array[r, c] = 9999.0

        # Convert back to list of lists with strings
        processed = []
        for row in grid_array:
            processed.append([f"{val:.1f}" if not np.isnan(val) else "9999.0" for val in row])

        return processed, points_masked

    def _mask_raw_data(
        self,
        rectangles: List[Tuple[float, float, float, float]]
    ) -> Tuple[List[List[str]], int]:
        """Apply masking to raw grid data based on rectangles.

        For 2D grid data, rectangles specify grid cell ranges.
        Masked cells have their values set to 9999.0.

        Args:
            rectangles: List of (min_col, min_row, max_col, max_row) in grid indices

        Returns:
            Tuple of (processed_data, points_masked_count).
        """
        return self._mask_grid_data(self.raw_data, rectangles, self.grid_width, self.grid_height)

    def apply_raw_mask(self) -> None:
        """Apply raw mask to all .txt and .rawtxt files in the loaded file's directory.

        For each coordinate in grid data, if it falls within any drawn rectangle,
        its value is replaced with the mask value (9999.0).

        Processes all .txt and .rawtxt files in the same directory as the loaded file,
        and saves masked versions to a 'masked/' subdirectory.

        Properly accounts for:
        - Size differences between JPG and raw data
        - Y-axis orientation differences
        - Coordinate system offsets
        """
        if not self.raw_data:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "No raw data loaded. Please load an image with associated raw data file."
            )
            return

        # Get rectangle bounds in raw data coordinate space
        rectangles = self._get_rectangle_bounds_in_raw_coords()

        if not rectangles:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "No rectangles drawn. Draw rectangles over areas to mask."
            )
            return

        # Get the directory of the loaded file
        raw_dir = os.path.dirname(self.raw_path) if self.raw_path else os.getcwd()

        # Find all .txt and .rawtxt files in the directory
        txt_files = []
        for file in os.listdir(raw_dir):
            if file.endswith('.txt') or file.endswith('.rawtxt'):
                txt_files.append(os.path.join(raw_dir, file))

        if not txt_files:
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                f"No .txt or .rawtxt files found in {raw_dir}"
            )
            return

        # Create masked output directory
        masked_dir = os.path.join(raw_dir, "masked")
        os.makedirs(masked_dir, exist_ok=True)

        # Show coordinate system info
        raw_bounds = self._get_raw_bounds()
        if raw_bounds:
            min_col, max_col, min_row, max_row, width, height = raw_bounds
            pixmap = self.image_item.pixmap()
            dpr = pixmap.devicePixelRatio() if pixmap else 1.0
            img_w = int(pixmap.width() * dpr)
            img_h = int(pixmap.height() * dpr)

            print("=" * 60)
            print("GRID MASKING COORDINATE MAPPING")
            print("=" * 60)
            print(f"Image dimensions: {img_w} x {img_h} pixels")
            print(f"Grid dimensions: {width} columns x {height} rows")
            print(f"Grid bounds: Col=[{min_col:.0f}, {max_col:.0f}], Row=[{min_row:.0f}, {max_row:.0f}]")
            print(f"Scale factors: Col={width/img_w:.6f}, Row={height/img_h:.6f}")
            print(f"\nNumber of mask rectangles: {len(rectangles)}")
            for idx, (min_col_rect, min_row_rect, max_col_rect, max_row_rect) in enumerate(rectangles):
                print(f"  Rectangle {idx}: Col=[{min_col_rect:.0f}, {max_col_rect:.0f}], "
                      f"Row=[{min_row_rect:.0f}, {max_row_rect:.0f}]")
            print("=" * 60)

        # Process each file
        total_files_processed = 0
        total_points_masked = 0
        failed_files = []

        for file_path in txt_files:
            filename = os.path.basename(file_path)
            print(f"\nProcessing: {filename}")

            # Load the file
            result = self._load_grid_file(file_path)
            if result is None:
                failed_files.append(filename)
                continue

            grid_data, delimiter = result

            # Determine grid dimensions for this file
            grid_rows = []
            for row in grid_data:
                if len(row) == 0:
                    continue
                try:
                    [float(val) for val in row]
                    grid_rows.append(len(row))
                except ValueError:
                    continue

            if not grid_rows:
                print(f"  Skipped: No valid numeric data found")
                failed_files.append(filename)
                continue

            file_grid_height = len(grid_rows)
            file_grid_width = max(grid_rows) if grid_rows else 0

            # Apply masking
            processed, points_masked = self._mask_grid_data(
                grid_data,
                rectangles,
                file_grid_width,
                file_grid_height
            )

            if not processed:
                print(f"  Skipped: Masking failed")
                failed_files.append(filename)
                continue

            # Save to masked directory
            out_path = os.path.join(masked_dir, filename)
            try:
                with open(out_path, "w", newline="") as f:
                    writer = csv.writer(f, delimiter=delimiter)
                    writer.writerows(processed)

                total_files_processed += 1
                total_points_masked += points_masked
                print(f"  Masked {points_masked} points -> {os.path.join('masked', filename)}")
            except Exception as e:
                print(f"  Error saving: {e}")
                failed_files.append(filename)

        print("=" * 60)
        print(f"\nMasking complete:")
        print(f"  Files processed: {total_files_processed}/{len(txt_files)}")
        print(f"  Total points masked: {total_points_masked}")
        print(f"  Output directory: {masked_dir}")
        if failed_files:
            print(f"  Failed files: {', '.join(failed_files)}")
        print("=" * 60)

        # Show completion message
        message = (
            f"Masking complete!\n\n"
            f"Files processed: {total_files_processed}/{len(txt_files)}\n"
            f"Total points masked: {total_points_masked}\n"
            f"Output directory: {os.path.join(os.path.basename(raw_dir), 'masked')}"
        )
        if failed_files:
            message += f"\n\nFailed files:\n" + "\n".join(f"  - {f}" for f in failed_files)

        QtWidgets.QMessageBox.information(
            self,
            "Masking Complete",
            message
        )


def main():
    """Application entry point."""
    app = QtWidgets.QApplication(sys.argv)
    window = ImageAnnotationApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

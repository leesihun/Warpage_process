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
DEFAULT_BORDER_THICKNESS = 5
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
            "Border Thickness: ",
            value=self.border_thickness,
            min=1,
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

        Converts 9999.0 values to NaN for proper visualization.

        Returns:
            QPixmap of the generated heatmap, or None on failure.
        """
        if not self.raw_data:
            return None

        try:
            # Extract X, Y, Z coordinates from raw data
            coords = []
            for row in self.raw_data:
                if len(row) < 3:
                    continue
                try:
                    x = float(row[0])
                    y = float(row[1])
                    z = float(row[2])
                    # Convert 9999.0 to NaN
                    if abs(z - 9999.0) < 0.1:
                        z = np.nan
                    coords.append((x, y, z))
                except ValueError:
                    continue

            if not coords:
                return None

            # Convert to numpy arrays
            coords_array = np.array(coords)
            x_vals = coords_array[:, 0]
            y_vals = coords_array[:, 1]

            # Get unique x and y values to determine grid dimensions
            unique_x = np.unique(x_vals)
            unique_y = np.unique(y_vals)

            # Store grid mapping for coordinate conversion
            self.unique_x = unique_x
            self.unique_y = unique_y
            self.grid_width = len(unique_x)
            self.grid_height = len(unique_y)

            # Create grid
            grid_z = np.full((len(unique_y), len(unique_x)), np.nan)

            # Fill grid with z values
            for x, y, z in coords:
                x_idx = np.searchsorted(unique_x, x)
                y_idx = np.searchsorted(unique_y, y)
                if x_idx < len(unique_x) and y_idx < len(unique_y):
                    grid_z[y_idx, x_idx] = z

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

            # Plot heatmap
            im = ax.imshow(grid_z, cmap='jet', aspect='auto', interpolation='nearest')

            # Add colorbar
            plt.colorbar(im, ax=ax, label='Warpage (μm)')

            # Set title
            ax.set_title(f'Warpage Heatmap: {os.path.basename(self.raw_path) if self.raw_path else "Unknown"}')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

            # Remove axis ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])

            # Convert matplotlib figure to QPixmap
            fig.tight_layout()
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

            # Analyze raw data bounds
            raw_bounds = self._get_raw_bounds()
            if raw_bounds:
                min_x, max_x, min_y, max_y, width, height = raw_bounds
                msg = (
                    f"Loaded raw data from {os.path.basename(raw_path)}\n\n"
                    f"Data bounds:\n"
                    f"  X: [{min_x:.2f}, {max_x:.2f}] (width: {width:.2f})\n"
                    f"  Y: [{min_y:.2f}, {max_y:.2f}] (height: {height:.2f})\n"
                    f"  Total points: {len(rows)}\n\n"
                    f"Current Y-axis orientation: {'DOWN' if self.raw_data_y_axis_down else 'UP'}\n"
                    f"(Change in Settings > Toggle Y-Axis Orientation if needed)"
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
        """Extract bounds from raw data by finding min and max coordinates.

        Returns:
            Tuple of (min_x, max_x, min_y, max_y, width, height) or None.
        """
        if not self.raw_data:
            return None

        min_x, max_x = float('inf'), -float('inf')
        min_y, max_y = float('inf'), -float('inf')

        for row in self.raw_data:
            if len(row) < 2:
                continue
            try:
                x = float(row[0])
                y = float(row[1])
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
            except ValueError:
                continue

        # Check if we found valid bounds
        if min_x == float('inf') or max_x == -float('inf'):
            return None

        width = max_x - min_x
        height = max_y - min_y

        if width <= 0 or height <= 0:
            return None

        return (min_x, max_x, min_y, max_y, width, height)

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
            min_x, max_x, min_y, max_y, width, height = raw_bounds
            info_msg = (
                f"Coordinate mapping:\n"
                f"Image size: {img_width} x {img_height} pixels\n"
                f"Raw data bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]\n"
                f"Raw data size: {width:.2f} x {height:.2f}\n"
                f"Scale factors: X={width/img_width:.4f}, Y={height/img_height:.4f}\n"
                f"Y-axis orientation: {'down' if self.raw_data_y_axis_down else 'up'} (image is always down)"
            )
        else:
            coords = pixel_coords
            info_msg = "No raw data loaded - saving in pixel coordinates"

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

    def _is_point_in_rectangles(
        self,
        x: float,
        y: float,
        rectangles: List[Tuple[float, float, float, float]]
    ) -> bool:
        """Check if a point is inside any rectangle.

        Args:
            x, y: Point coordinates in raw data space
            rectangles: List of (min_x, min_y, max_x, max_y) in raw data space

        Returns:
            True if point is inside any rectangle
        """
        for min_x, min_y, max_x, max_y in rectangles:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return True
        return False

    def _mask_raw_data(
        self,
        rectangles: List[Tuple[float, float, float, float]]
    ) -> Tuple[List[List[str]], int]:
        """Apply masking to raw data based on rectangles.

        Coordinates are properly matched between image space and raw data space,
        accounting for size differences and Y-axis orientation.

        Args:
            rectangles: List of (min_x, min_y, max_x, max_y) in raw data coordinates

        Returns:
            Tuple of (processed_data, points_masked_count).
        """
        processed = []
        points_masked = 0

        for idx, row in enumerate(self.raw_data):
            if len(row) < 2:
                processed.append(row)
                continue

            # Preserve header if present
            if idx == 0:
                try:
                    float(row[0])
                    float(row[1])
                except ValueError:
                    processed.append(row)
                    continue

            try:
                x = float(row[0])
                y = float(row[1])

                if self._is_point_in_rectangles(x, y, rectangles):
                    new_row = [MASK_VALUE, MASK_VALUE] + row[2:]
                    processed.append(new_row)
                    points_masked += 1
                else:
                    processed.append(row)
            except ValueError:
                processed.append(row)

        return processed, points_masked

    def apply_raw_mask(self) -> None:
        """Apply raw mask using previously loaded raw data.

        For each coordinate in raw_data, if it falls within any drawn rectangle,
        its x and y values are replaced with the mask value (9999.0).

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

        # Show coordinate system info
        raw_bounds = self._get_raw_bounds()
        if raw_bounds:
            min_x, max_x, min_y, max_y, width, height = raw_bounds
            pixmap = self.image_item.pixmap()
            dpr = pixmap.devicePixelRatio() if pixmap else 1.0
            img_w = int(pixmap.width() * dpr)
            img_h = int(pixmap.height() * dpr)

            print("=" * 60)
            print("COORDINATE SYSTEM MAPPING")
            print("=" * 60)
            print(f"Image dimensions: {img_w} x {img_h} pixels")
            print(f"Raw data bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")
            print(f"Raw data size: {width:.2f} x {height:.2f}")
            print(f"Scale factors: X={width/img_w:.6f}, Y={height/img_h:.6f}")
            print(f"Y-axis orientation: Raw data {'DOWN' if self.raw_data_y_axis_down else 'UP'}, Image DOWN")
            print(f"\nNumber of mask rectangles: {len(rectangles)}")
            for idx, (min_x_rect, min_y_rect, max_x_rect, max_y_rect) in enumerate(rectangles):
                print(f"  Rectangle {idx}: X=[{min_x_rect:.2f}, {max_x_rect:.2f}], "
                      f"Y=[{min_y_rect:.2f}, {max_y_rect:.2f}]")
            print("=" * 60)

        # Apply masking
        processed, points_masked = self._mask_raw_data(rectangles)

        print(f"\nMasking result: {points_masked} points masked out of {len(self.raw_data)} total rows")
        print("=" * 60)

        # Save result
        raw_dir = os.path.dirname(self.raw_path) if self.raw_path else os.getcwd()
        out_path = os.path.join(raw_dir, "Raw_mask.txt")

        try:
            with open(out_path, "w", newline="") as f:
                writer = csv.writer(f, delimiter=self.raw_delimiter)
                writer.writerows(processed)
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Raw_mask.txt saved to {out_path}\n\n"
                f"Points masked: {points_masked} / {len(self.raw_data)}\n"
                f"Y-axis orientation: {'down' if self.raw_data_y_axis_down else 'up'} "
                f"(toggle in Settings if incorrect)"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to save Raw_mask.txt: {e}"
            )


def main():
    """Application entry point."""
    app = QtWidgets.QApplication(sys.argv)
    window = ImageAnnotationApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

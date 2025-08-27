# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **PEMTRON Warpage Analysis Tool v2.0** - a modern, comprehensive solution for analyzing semiconductor warpage measurement data. The application features a complete rewrite with clean architecture, web-based interface, and advanced visualization capabilities.

### Architecture Philosophy

The codebase follows modern software engineering principles:

- **Clean Architecture**: Clear separation of concerns with distinct layers
- **Modular Design**: Components can be developed, tested, and maintained independently
- **Configuration-Driven**: Centralized configuration management with validation
- **Error Handling**: Comprehensive exception handling with custom error types
- **Extensibility**: Easy to add new analysis types, visualizations, and data formats
- **Type Safety**: Proper type hints and validation throughout the codebase

## Core Architecture

### 1. Core Layer (`core/`)
The foundation of the application containing all business logic:

- **`config.py`**: Configuration management with dataclasses and validation
- **`data_processor.py`**: Data loading, cleaning, and preprocessing
- **`statistics.py`**: Statistical analysis engine with comprehensive calculations
- **`analyzer.py`**: Main orchestrator that coordinates the entire analysis workflow
- **`exceptions.py`**: Custom exception hierarchy for specific error handling

### 2. Visualization Layer (`visualization/`)
Handles all plot generation and export functionality:

- **`plotter.py`**: Plot generation using matplotlib and plotly
- **`renderer.py`**: Plot rendering and format conversion
- **`exporters.py`**: PDF and image export with professional reporting

### 3. Web Layer (`web/`)
Modern Flask-based web interface:

- **`app.py`**: Flask application factory with proper configuration
- **`routes.py`**: Page routes for HTML rendering
- **`api.py`**: RESTful API endpoints for frontend communication
- **`templates/`**: Jinja2 templates with Bootstrap 5 styling
- **`static/`**: CSS, JavaScript, and asset files

## Key Design Patterns

### 1. Configuration Management
Uses dataclasses for type-safe, validated configuration:

```python
@dataclass
class VisualizationConfig:
    colormap: str = 'jet'
    dpi: int = 150
    figure_size: tuple = (10, 8)
    include_3d: bool = True
    # ... with validation in __post_init__
```

### 2. Error Handling
Custom exception hierarchy provides specific error types:

```python
class WarpageAnalysisError(Exception): pass
class DataLoadError(WarpageAnalysisError): pass
class DataProcessingError(WarpageAnalysisError): pass
```

### 3. Data Containers
Structured data containers for type safety and clarity:

```python
@dataclass
class MeasurementData:
    data: np.ndarray
    filename: str
    original_shape: Tuple[int, int]
    processed_shape: Tuple[int, int]
```

### 4. Factory Pattern
Flask application factory for proper initialization:

```python
def create_app(config: Config = None) -> Flask:
    app = Flask(__name__)
    # Configure app with provided config
    return app
```

## Development Workflow

### Adding New Features

1. **Core Functionality**: Add business logic to appropriate core modules
2. **Visualization**: Extend plotter with new plot types if needed
3. **API**: Add REST endpoints in `web/api.py` for web interface integration
4. **Frontend**: Update templates and JavaScript for user interface
5. **Configuration**: Add new settings to config dataclasses
6. **Tests**: Write comprehensive tests for new functionality

### Code Style Guidelines

- **Type Hints**: All functions should have proper type annotations
- **Docstrings**: Use Google-style docstrings for all public methods
- **Error Handling**: Use specific exception types, not generic Exception
- **Logging**: Use structured logging with appropriate levels
- **Configuration**: All settings should be configurable, not hardcoded
- **Validation**: Validate inputs at boundaries (API, file loading, etc.)

## Common Operations

### Running the Application

```bash
# Web interface (primary method)
python main.py

# Command line interface
python main.py --cli --directory ./data/sample

# Development mode
python main.py --debug --port 8090
```

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 .
```

### Adding New Analysis Types

1. Extend `StatisticsEngine` with new calculation methods
2. Add configuration options to `Config` classes
3. Update `WarpageAnalyzer` to orchestrate new analysis
4. Add visualization support in `PlotGenerator`
5. Expose via API endpoints if needed

### Adding New Visualization Types

1. Add plot generation method to `PlotGenerator`
2. Update `PlotRenderer` if new format conversion needed
3. Add export support in `PDFExporter`
4. Update web interface to display new plots
5. Add configuration options for customization

## File Processing Pipeline

The data processing follows a clear pipeline:

1. **File Discovery**: `DataProcessor.find_files()` locates measurement files
2. **Data Loading**: `DataProcessor.load_file()` reads and parses data
3. **Data Cleaning**: Remove artifacts, zero padding, extract regions
4. **Statistical Analysis**: `StatisticsEngine.calculate_summary()` computes statistics
5. **Visualization**: `PlotGenerator` creates various plot types
6. **Export**: `PDFExporter` generates comprehensive reports

## Web Interface Architecture

### Frontend Stack
- **Bootstrap 5**: Modern, responsive UI framework
- **jQuery**: DOM manipulation and AJAX requests
- **Plotly.js**: Interactive visualizations
- **Font Awesome**: Icons and visual elements

### Backend API
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Communication**: Structured data exchange
- **Error Handling**: Consistent error response format
- **File Handling**: Support for file uploads and downloads

### State Management
- **Application State**: Managed in JavaScript AppState object
- **Session State**: Analysis results stored in Flask app context
- **Configuration**: Centralized config object shared across components

## Testing Strategy

### Unit Tests
- **Core Logic**: Test data processing, statistics, and analysis
- **Validation**: Test configuration validation and error handling
- **Utilities**: Test helper functions and utilities

### Integration Tests
- **API Endpoints**: Test REST API functionality
- **File Processing**: Test end-to-end file processing pipeline
- **Export**: Test PDF and image export functionality

### Test Data
- **Sample Files**: Representative measurement data files
- **Edge Cases**: Files with artifacts, empty data, malformed content
- **Performance**: Large files for performance testing

## Configuration System

### Hierarchical Configuration
The configuration system uses nested dataclasses for organization:

```python
config = Config()
config.visualization.colormap = 'viridis'
config.processing.remove_artifacts = True
config.server.port = 8080
```

### Environment Support
Configuration can be loaded from:
- Default values in dataclasses
- Dictionary updates via `Config.from_dict()`
- Runtime updates via `WarpageAnalyzer.update_config()`

### Validation
All configuration classes validate their settings in `__post_init__()`:
- Range checks for numerical values
- Existence checks for file paths
- Format validation for strings

## Performance Considerations

### Memory Management
- **Lazy Loading**: Load data only when needed
- **Memory Cleanup**: Explicitly close matplotlib figures
- **Batch Processing**: Process files in configurable batch sizes

### Processing Optimization
- **Parallel Processing**: Use ThreadPoolExecutor for file processing
- **Caching**: Cache expensive calculations when possible
- **Progress Tracking**: Provide user feedback for long operations

### Web Interface Performance
- **Async Operations**: Use AJAX for non-blocking operations
- **Image Optimization**: Use appropriate DPI settings
- **Progressive Loading**: Load results incrementally

## Error Handling Philosophy

### Defensive Programming
- **Input Validation**: Validate all inputs at boundaries
- **Graceful Degradation**: Continue processing when possible
- **User-Friendly Messages**: Provide clear error messages to users
- **Detailed Logging**: Log technical details for debugging

### Error Recovery
- **File Processing**: Skip corrupted files, continue with others
- **Visualization**: Generate available plots even if some fail
- **Web Interface**: Handle API failures gracefully with user feedback

## Extension Points

### Adding New Data Formats
1. Extend `DataProcessor._read_text_file()` for new parsers
2. Add format detection logic
3. Update file pattern configuration
4. Add validation for new format

### Custom Analysis Methods
1. Add methods to `StatisticsEngine`
2. Update `StatisticalSummary` dataclass if needed
3. Add configuration options
4. Extend visualization if needed

### New Visualization Backends
1. Create new plotter class similar to `PlotGenerator`
2. Implement renderer for format conversion
3. Add export support
4. Update web interface integration

## Security Considerations

### File Handling
- **Path Validation**: Use `secure_filename()` for uploads
- **Size Limits**: Enforce file size limits
- **Type Checking**: Validate file extensions and content
- **Temporary Files**: Clean up temporary files properly

### Web Interface
- **CORS Configuration**: Properly configured CORS headers
- **Input Validation**: Validate all API inputs
- **Error Information**: Don't expose sensitive information in errors
- **File Permissions**: Proper file system permissions

## Deployment Considerations

### Production Setup
- **Configuration**: Use environment-specific configs
- **Logging**: Configure appropriate log levels and rotation
- **Error Handling**: Set up error monitoring
- **Performance**: Configure for expected load

### Environment Variables
Key settings that should be configurable in deployment:
- `WARPAGE_DATA_DIR`: Data directory path
- `WARPAGE_OUTPUT_DIR`: Output directory path
- `WARPAGE_SERVER_PORT`: Web server port
- `WARPAGE_DEBUG`: Debug mode flag

This documentation should help you understand the codebase architecture and make appropriate modifications while maintaining the design principles and code quality standards.
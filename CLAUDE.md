# PEMTRON Warpage Analysis Tool - Technical Documentation

## Project Overview

The PEMTRON Warpage Analysis Tool is a comprehensive Python-based application designed for analyzing semiconductor warpage measurement data. This tool provides both web-based GUI and command-line interfaces for processing, visualizing, and exporting warpage analysis results.

## Architecture

### Core Components

```
PEMTRON_warpage/
├── web_server.py           # Flask web application server
├── config.py              # Configuration management
├── data_loader.py         # Data file processing and loading
├── warpage_statistics.py  # Statistical calculations
├── visualization.py       # Plot generation and rendering
├── pdf_exporter.py        # PDF report generation
├── advanced_statistics.py # Advanced statistical analysis
└── templates/             # Web interface templates
    └── index.html         # Main web interface
```

### Data Flow

1. **Data Input**: Raw measurement files (.txt, .ptr formats)
2. **Processing**: Artifact removal, zero-padding cleanup, region extraction
3. **Analysis**: Statistical calculations (mean, std, range, skewness, kurtosis)
4. **Visualization**: 2D heatmaps, 3D surfaces, comparison plots
5. **Export**: PDF reports, individual plot images

## Technical Specifications

### Supported File Formats

- **Original Files**: `*@_ORI.txt`, `*_ORI_A.txt` - Raw measurement data
- **Corrected Files**: `*.txt` (excluding original patterns) - Processed data
- **Binary Files**: `*.ptr` - Binary measurement format (future support)

### Data Processing Pipeline

```python
Raw Data → Artifact Removal → Zero Padding Cleanup → Region Extraction → Statistical Analysis → Visualization
```

#### Artifact Removal
- Removes common artifact values: -4000, ±9999, ±99999
- Configurable through `DEFAULT_CONFIG['remove_artifacts']`

#### Region Extraction
- Extracts center regions using row_fraction and col_fraction
- Preserves data integrity while focusing on relevant measurement areas

### Web Server Architecture

#### Flask Application Structure
```python
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Global state management
current_data = None      # Processed measurement data
current_plots = None     # Generated plot images (base64)
current_stats = None     # Statistical results
```

#### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main web interface |
| `/api/folders` | GET | List available data folders |
| `/api/analyze` | POST | Process selected folder |
| `/api/plot/<file_id>` | GET | Get individual plot |
| `/api/stats_plot` | GET | Get statistical comparison plot |
| `/api/3d_plot` | GET | Get 3D surface plot |
| `/api/export_pdf` | GET/POST | Export PDF report |
| `/api/status` | GET | Server health check |
| `/api/debug` | GET | Diagnostic information |

### Configuration System

#### Default Configuration
```python
DEFAULT_CONFIG = {
    "base_path": get_data_dir(),
    "vmin": None,                    # Auto color scaling
    "vmax": None,
    "cmap": "jet",                   # Colormap selection
    "row_fraction": 1,               # Region extraction
    "col_fraction": 1,
    "use_original_files": True,      # File type preference
    "dpi": 150,                      # Export quality
    "include_stats": True,           # Statistical plots
    "include_3d": True,              # 3D visualizations
    "include_advanced": False        # Advanced analysis
}
```

#### Dynamic Configuration
- Runtime path resolution for executable and development modes
- Automatic data directory detection
- PyInstaller compatibility

### Data Processing Details

#### File Discovery Algorithm
```python
def find_data_files(directory, use_original=True):
    """
    Recursively scan directory for measurement files
    Priority: Original files > Corrected files
    """
    if use_original:
        patterns = ['_ORI.txt', '@_ORI.txt', '_ORI_A.txt']
    else:
        patterns = ['.txt']  # Exclude original files
    
    return matching_files
```

#### Statistical Calculations
```python
stats = {
    'shape': data.shape,
    'min': np.nanmin(data),
    'max': np.nanmax(data),
    'mean': np.nanmean(data),
    'std': np.nanstd(data),
    'range': max - min,
    'skewness': scipy.stats.skew(data, nan_policy='omit'),
    'kurtosis': scipy.stats.kurtosis(data, nan_policy='omit')
}
```

### Visualization System

#### Plot Types
1. **Individual Heatmaps**: Color-coded warpage visualization
2. **3D Surface Plots**: Interactive 3D representations
3. **Comparison Plots**: Side-by-side multi-file analysis
4. **Statistical Charts**: Mean, std, range comparisons
5. **Distribution Plots**: Histogram and density analysis

#### Matplotlib Configuration
```python
matplotlib.use('Agg')  # Non-interactive backend
plt.style.use('default')
fig.tight_layout()
```

#### Base64 Encoding
```python
def figure_to_base64(fig):
    """Convert matplotlib figure to base64 string for web display"""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return image_base64
```

### Error Handling Strategy

#### Graceful Degradation
- Continue processing if individual files fail
- Provide meaningful error messages
- Log detailed error information for debugging

#### Common Error Scenarios
1. **File Access Errors**: Permission denied, file not found
2. **Data Format Errors**: Invalid file format, corrupted data
3. **Memory Errors**: Large dataset handling
4. **Visualization Errors**: Plot generation failures

### Performance Considerations

#### Memory Management
- Process files individually to minimize memory footprint
- Close matplotlib figures after base64 conversion
- Use generators for large dataset iteration

#### Optimization Strategies
- Lazy loading of visualization modules
- Configurable DPI settings for export quality vs. speed
- Optional advanced analysis to reduce computation time

### Deployment Options

#### Development Mode
```bash
python web_server.py
```

#### Executable Build
```bash
python -m PyInstaller web_server.spec --clean
```

#### Configuration for Executable
- Data directory resolution using `sys._MEIPASS`
- Resource path handling for templates and static files
- Dependency bundling with PyInstaller spec file

### Testing Strategy

#### Unit Testing Areas
- Data loading and processing functions
- Statistical calculation accuracy
- File format detection
- Configuration management

#### Integration Testing
- Web server endpoint functionality
- Complete analysis workflow
- PDF export generation
- Error handling scenarios

### Security Considerations

#### Web Server Security
- CORS enabled for development (restrict in production)
- Input validation for file paths and parameters
- Temporary file cleanup after processing

#### File System Access
- Restricted to configured data directories
- Path traversal protection
- Safe file name handling

### Logging and Debugging

#### Debug Information
- Server startup diagnostics
- File discovery process logging
- Analysis progress tracking
- Error stack traces

#### Log Files
- `server_debug.log`: Runtime diagnostics
- Console output: Real-time status updates

### Future Enhancements

#### Planned Features
- Real-time data streaming support
- Machine learning integration for anomaly detection
- Advanced statistical models
- Multi-language support
- Cloud deployment options

#### Technical Improvements
- Database integration for result storage
- Caching system for improved performance
- Asynchronous processing for large datasets
- REST API versioning

### Dependencies

#### Core Dependencies
```
numpy>=1.21.0          # Numerical computation
scipy>=1.7.0           # Statistical functions
matplotlib>=3.5.0      # Plotting and visualization
Flask>=2.0.0           # Web framework
Flask-CORS>=3.0.0      # Cross-origin support
reportlab>=3.6.0       # PDF generation
```

#### Optional Dependencies
```
plotly>=5.0.0          # Interactive visualizations
scikit-learn>=1.0.0    # Advanced analysis
pandas>=1.3.0          # Data manipulation
kaleido>=0.2.1         # Plot export support
```

### Build and Distribution

#### PyInstaller Configuration
- Single-file executable generation
- Data file inclusion (templates, config)
- Hidden import detection
- Cross-platform compatibility

#### Deployment Checklist
1. Install dependencies: `pip install -r requirements.txt`
2. Test functionality: `python web_server.py`
3. Build executable: `python -m PyInstaller web_server.spec`
4. Test executable: `./dist/web_server.exe`
5. Distribute with data directory

This documentation provides a comprehensive technical overview of the PEMTRON Warpage Analysis Tool architecture, implementation details, and operational considerations.
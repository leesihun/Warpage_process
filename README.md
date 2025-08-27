# PEMTRON Warpage Analysis Tool v2.0

A modern, comprehensive tool for analyzing semiconductor warpage measurement data. Built with a clean architecture, web-based interface, and advanced visualization capabilities.

## 🚀 Features

### Core Capabilities
- **Multi-format Support**: Process .txt and .ptr measurement files
- **Smart Data Processing**: Automatic artifact removal and zero-padding cleanup
- **Statistical Analysis**: Comprehensive statistical calculations including mean, std, range, skewness, kurtosis
- **Advanced Visualizations**: 2D heatmaps, 3D surface plots, comparison charts, statistical plots
- **Web Interface**: Modern, responsive web-based GUI with real-time updates
- **Command Line Support**: Full CLI interface for automation and batch processing
- **PDF Reports**: Professional PDF reports with plots and statistics
- **Batch Processing**: Analyze multiple files and directories efficiently

### Visualization Types
- **Individual Heatmaps**: Color-coded warpage visualization for each measurement
- **3D Surface Plots**: Interactive 3D surface representations
- **Comparison Plots**: Side-by-side analysis of multiple measurements
- **Statistical Charts**: Mean, standard deviation, range, and distribution comparisons
- **Interactive Plots**: Plotly-powered interactive visualizations

### Technical Features
- **Clean Architecture**: Modular design with separation of concerns
- **Configurable Processing**: Customizable artifact removal, region extraction, and color scaling
- **Real-time Updates**: Live parameter adjustments and plot updates
- **Error Handling**: Comprehensive error handling and validation
- **Logging**: Detailed logging for debugging and monitoring
- **Extensible Design**: Easy to add new analysis types and visualization methods

## 📦 Installation

### Requirements
- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 1GB free disk space

### Quick Start
```bash
# Clone or download the repository
cd PEMTRON_warpage

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The web interface will automatically open at `http://localhost:8080`

### Development Installation
```bash
# Install with development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## 🖥️ Usage

### Web Interface (Recommended)
1. **Start the application**: `python main.py`
2. **Select data source**: Choose between folder analysis or file upload
3. **Configure processing**: Set options like colormap, DPI, region extraction
4. **Run analysis**: Click "Start Analysis" to process your data
5. **View results**: Browse through heatmaps, 3D plots, and statistical analysis
6. **Export reports**: Generate PDF reports with all visualizations

### Command Line Interface
```bash
# Analyze a directory
python main.py --cli --directory ./data/sample --export ./output

# Analyze a single file
python main.py --cli --file measurement.txt --export ./output

# Custom settings
python main.py --cli --directory ./data --colormap viridis --dpi 300
```

### Configuration Options
```bash
# Web interface options
python main.py --port 8090 --host 0.0.0.0 --debug

# Analysis options
python main.py --cli --data-dir ./data --output-dir ./results
```

## 📁 Project Structure

```
PEMTRON_warpage/
├── core/                   # Core analysis engine
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── data_processor.py  # Data loading and processing
│   ├── statistics.py      # Statistical calculations
│   ├── analyzer.py        # Main analysis orchestrator
│   └── exceptions.py      # Custom exceptions
├── visualization/          # Visualization system
│   ├── __init__.py
│   ├── plotter.py         # Plot generation
│   ├── renderer.py        # Plot rendering and conversion
│   └── exporters.py       # PDF and image export
├── web/                   # Web interface
│   ├── __init__.py
│   ├── app.py            # Flask application factory
│   ├── routes.py         # Page routes
│   ├── api.py            # REST API endpoints
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── data/                  # Sample data directory
├── output/               # Default output directory
├── temp/                 # Temporary files
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Application Configuration
The tool uses a hierarchical configuration system:

```python
from core import Config

config = Config()
config.visualization.colormap = 'viridis'
config.visualization.dpi = 300
config.processing.remove_artifacts = True
config.server.port = 8080
```

### File Patterns
- **Original files**: `*@_ORI.txt` - Raw measurement data
- **Corrected files**: `*.txt` (excluding `@_ORI.txt`) - Processed measurement data
- **Binary files**: `*.ptr` - Binary measurement format

### Processing Options
- **Artifact Removal**: Automatically remove common artifact values (-4000, ±9999, ±99999)
- **Zero Padding**: Remove all-zero rows and columns
- **Region Extraction**: Extract center regions using configurable fractions
- **Color Scaling**: Automatic or manual min/max value setting

## 📊 Data Format

### Input Files
The tool accepts two main file formats:

1. **Text files (.txt)**: Space-separated numerical data
```
1.234 2.456 3.789
4.567 5.890 6.123
7.456 8.789 9.012
```

2. **PTR files (.ptr)**: Binary measurement files (auto-detected format)

### Output Files
- **PNG images**: Individual plot exports
- **PDF reports**: Comprehensive analysis reports
- **JSON data**: Statistical results and metadata

## 🎨 Visualization Options

### Colormaps
- `jet` (default): Traditional rainbow colormap
- `viridis`: Perceptually uniform blue-green-yellow
- `plasma`: Purple-pink-yellow colormap
- `coolwarm`: Blue-red diverging colormap
- `seismic`: Blue-white-red diverging colormap

### Plot Types
- **2D Heatmaps**: Color-coded surface plots with statistics
- **3D Surfaces**: Interactive 3D representations
- **Comparison**: Side-by-side multi-file analysis
- **Statistics**: Bar charts, box plots, distribution plots

## 🔍 API Reference

### REST Endpoints
- `GET /api/folders` - List available data folders
- `POST /api/analyze` - Start folder analysis
- `POST /api/upload` - Upload files for analysis
- `GET /api/plots/all` - Get all generated plots
- `POST /api/export/pdf` - Export PDF report
- `GET /api/statistics` - Get statistical results
- `GET /api/status` - Application health check

### Python API
```python
from core import WarpageAnalyzer, Config

# Create analyzer
config = Config()
analyzer = WarpageAnalyzer(config)

# Analyze directory
results = analyzer.analyze_directory('./data/sample')

# Export results
analyzer.export_results('./output', export_plots=True, export_pdf=True)
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=visualization --cov=web

# Run specific test file
pytest tests/test_data_processor.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Format code (`black .`)
7. Commit changes (`git commit -am 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Create a Pull Request

## 📝 License

This project is proprietary software developed for PEMTRON semiconductor manufacturing analysis.

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

## 🔄 Version History

### v2.0.0 (Current)
- Complete rewrite with modern architecture
- Web-based interface with responsive design
- Advanced statistical analysis
- Interactive visualizations
- REST API support
- Comprehensive error handling
- Modular, extensible design

### v1.x (Legacy)
- Basic command-line interface
- Simple visualization
- Limited file format support

## 🎯 Roadmap

### Planned Features
- [ ] Machine learning integration for anomaly detection
- [ ] Real-time data streaming support
- [ ] Advanced statistical models
- [ ] Integration with external databases
- [ ] Multi-language support
- [ ] Cloud deployment options
- [ ] Advanced filtering and preprocessing
- [ ] Custom colormap creation
- [ ] Automated report scheduling
- [ ] Performance optimizations

## 💡 Tips and Best Practices

### Performance Optimization
- Use smaller DPI settings (100-150) for faster processing
- Process files in batches for large datasets
- Consider region extraction for very large measurements
- Enable only necessary plot types to reduce memory usage

### Data Quality
- Verify file formats before analysis
- Check for consistent measurement grids
- Review artifact removal settings for your data type
- Validate statistical results against known standards

### Troubleshooting
- Check log files for detailed error information
- Verify file permissions and paths
- Ensure sufficient disk space for output files
- Monitor memory usage for large datasets
# Architecture Overview

This document clarifies the responsibilities and relationships between files in the PEMTRON Warpage Analysis Tool.

## File Responsibilities

### Entry Points
| File | Type | Purpose | Contains |
|------|------|---------|----------|
| `cli_interface.py` | **CLI Entry** | Command-line interface wrapper | Argument parsing, calls `analyzer.py` |
| `web_server.py` | **Full-Stack Web Server** | Flask web application | REST API, HTML serving, session management |

**Important**: `web_server.py` is NOT just frontend - it's a complete Flask web server with backend logic.

### Core Analysis Pipeline
| File | Purpose | Responsibilities |
|------|---------|------------------|
| `analyzer.py` | **Analysis Orchestrator** | Coordinates entire analysis workflow, calls other modules |
| `data_loader.py` | **Data Input** | File reading, preprocessing, format handling (.txt/.ptr) |
| `statistics.py` | **Statistical Analysis** | Mean, range, min/max, std dev calculations |
| `visualization.py` | **Plot Generation** | 2D heatmaps, 3D surfaces, comparison charts |
| `pdf_exporter.py` | **Report Output** | PDF generation, multi-page reports |

### Configuration & Interface
| File | Purpose | Responsibilities |
|------|---------|------------------|
| `config.py` | **Central Configuration** | All default settings, paths, parameters |
| `cli.py` | **CLI Utilities** | Command-line parsing functions, help text |

## Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Web Interface  │
│ (cli_interface.py) │  │ (web_server.py) │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │    analyzer.py  │ ← Orchestrates workflow
            │   (Coordinator) │
            └─────────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│data_loader  │ │ statistics  │ │visualization│
│   .py       │ │    .py      │ │    .py      │
└─────────────┘ └─────────────┘ └─────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
            ┌─────────────────┐
            │ pdf_exporter.py │ ← Generates reports
            └─────────────────┘
```

## Interface Types

### Command Line Interface (`cli_interface.py`)
- **Type**: Synchronous, batch processing
- **Usage**: `python cli_interface.py [options]`
- **Output**: Console logs + PDF files
- **Best for**: Automated processing, scripting

### Web Interface (`web_server.py`)
- **Type**: Asynchronous web server with REST API
- **Frontend**: HTML templates (in `templates/`)
- **Backend**: Flask routes with JSON responses
- **State Management**: Global `current_analysis` variable
- **Best for**: Interactive analysis, visualization

## Key Architectural Patterns

### 1. Centralized Configuration
- All defaults in `config.py`
- Both interfaces use same configuration system
- Easy to maintain consistency

### 2. Modular Processing Pipeline
- Each module has single responsibility
- Clear data flow: load → analyze → visualize → export
- Reusable across interfaces

### 3. Dual Interface Support
- Same core analysis engine
- Different presentation layers (CLI vs Web)
- Consistent output formats

## File Type Handling

### Input Files
- **@_ORI.txt**: Original measurement data (default)
- **@.txt**: Corrected measurement data  
- **@.ptr**: Binary measurement files

### Output Files
- **PDF Reports**: Generated in `report/` directory
- **PNG Images**: Web interface base64 encoded
- **Console Output**: Statistical summaries

## Session Management

### CLI Mode
- **Stateless**: Each run is independent
- **Configuration**: Command-line arguments + config file
- **Output**: Immediate file generation

### Web Mode
- **Stateful**: Uses `current_analysis` global variable
- **Configuration**: Web form + API calls
- **Output**: On-demand plot/PDF generation

## Development Notes

### Adding New Features
1. **Analysis Logic**: Add to appropriate module (`statistics.py`, `visualization.py`)
2. **CLI Support**: Update `cli.py` argument parsing
3. **Web Support**: Add API endpoint in `web_server.py`
4. **Configuration**: Add defaults to `config.py`

### File Naming Conventions
- **Modules**: `snake_case.py` (e.g., `data_loader.py`)
- **Entry Points**: Clear purpose (e.g., `cli_interface.py`, `web_server.py`)
- **Utilities**: Function-based names (e.g., `pdf_exporter.py`)

### Import Dependencies
```
config.py         ← No dependencies (base configuration)
    ↑
data_loader.py    ← Imports config
    ↑
statistics.py     ← Imports data structures
    ↑
visualization.py  ← Imports statistics results  
    ↑
analyzer.py       ← Imports all processing modules
    ↑
cli_interface.py  ← Imports analyzer + CLI utilities
web_server.py     ← Imports analyzer + web frameworks
```

This architecture ensures clear separation of concerns while maintaining flexibility for both automated and interactive use cases.
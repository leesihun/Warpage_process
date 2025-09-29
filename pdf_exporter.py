#!/usr/bin/env python3
"""
Warpage Analyzer용 PDF 내보내기 함수들
PDF export functions for Warpage Analyzer
"""

import os
import base64
import io
from matplotlib.backends.backend_pdf import PdfPages
from config import REPORT_DIR
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import gc  # For garbage collection

# Lazy imports for better performance
def _import_visualization():
    """Lazy import visualization functions."""
    import visualization
    return visualization

def _import_advanced_stats():
    """Lazy import advanced statistics functions."""
    try:
        from advanced_statistics import create_comprehensive_advanced_analysis, create_legend_page, create_cover_page, create_table_of_contents
        return {'create_comprehensive_advanced_analysis': create_comprehensive_advanced_analysis,
                'create_legend_page': create_legend_page,
                'create_cover_page': create_cover_page,
                'create_table_of_contents': create_table_of_contents}
    except ImportError:
        return None


def ensure_report_directory():
    """
    Ensure the report directory exists, create if it doesn't.
    
    Returns:
        str: Path to the report directory
    """
    report_dir = REPORT_DIR
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f"Created report directory: {report_dir}")
    return report_dir


def base64_to_figure(base64_string, figsize=(8.27, 11.69)):
    """
    Convert base64 image string to matplotlib figure
    
    Args:
        base64_string (str): Base64 encoded image string
        figsize (tuple): Figure size for the plot
        
    Returns:
        matplotlib.figure.Figure: Figure containing the image
    """
    # Decode base64 string to image data
    img_data = base64.b64decode(base64_string)
    img_buffer = io.BytesIO(img_data)
    
    # Create figure and display image
    fig, ax = plt.subplots(figsize=figsize)
    img = mpimg.imread(img_buffer, format='png')
    ax.imshow(img)
    ax.axis('off')  # Remove axes for clean image display
    
    return fig


def export_to_pdf_from_webui_plots(plots_data, folder_data, output_filename='warpage_analysis.pdf', dpi=150):
    """
    Export PDF using pre-generated plots from web UI for maximum efficiency.

    Args:
        plots_data (dict): Pre-generated plots from web UI in base64 format
        folder_data (dict): Original folder data for cover page and metadata
        output_filename (str): Output PDF filename
        dpi (int): DPI for PDF export

    Returns:
        str: Path to created PDF file
    """
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)

    if not plots_data:
        return None

    # A4 page size in inches
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27

    # Import advanced stats functions only when needed
    advanced_funcs = _import_advanced_stats()

    # Create PDF with A4 page size
    with PdfPages(full_output_path) as pdf:

        # Create cover and info pages only if advanced functions available
        if advanced_funcs:
            # Page 1: Cover page
            cover_fig = advanced_funcs['create_cover_page'](folder_data, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(cover_fig, dpi=dpi, bbox_inches='tight')
            plt.close(cover_fig)

            # Page 2: Table of contents
            toc_fig = advanced_funcs['create_table_of_contents'](folder_data, include_stats=True, include_3d=False, include_advanced=True, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(toc_fig, dpi=dpi, bbox_inches='tight')
            plt.close(toc_fig)

            # Page 3: Legend and terminology
            legend_fig = advanced_funcs['create_legend_page'](figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(legend_fig, dpi=dpi, bbox_inches='tight')
            plt.close(legend_fig)
        
        # Pages 4 onwards: Individual plots (from web UI)
        if 'individual' in plots_data:
            print(f"Adding {len(plots_data['individual'])} individual plots from web UI...")
            for i, plot_info in enumerate(plots_data['individual']):
                print(f"  Adding individual plot {i+1}/{len(plots_data['individual'])}: {plot_info['file_id']}")
                fig = base64_to_figure(plot_info['image'], figsize=(A4_WIDTH, A4_HEIGHT))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Statistical comparison pages (from web UI)
        print("Adding statistical analysis plots from web UI...")
        
        # Add statistical comparison plot
        if 'statistics' in plots_data:
            print("  Adding statistical comparison plot...")
            fig = base64_to_figure(plots_data['statistics'], figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add individual statistical plots
        stat_plots = ['mean', 'range', 'minmax', 'std']
        for stat_name in stat_plots:
            if stat_name in plots_data:
                print(f"  Adding {stat_name} comparison plot...")
                fig = base64_to_figure(plots_data[stat_name], figsize=(A4_WIDTH, A4_HEIGHT))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Add distribution plot
        if 'distribution' in plots_data:
            print("  Adding distribution plot...")
            fig = base64_to_figure(plots_data['distribution'], figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add advanced analysis plots (from web UI)
        if 'advanced' in plots_data:
            print(f"Adding {len(plots_data['advanced'])} advanced analysis plots from web UI...")
            
            # Plots that should be in landscape mode
            landscape_plots = {
                'Local Variability', 'Distribution Analysis - Violin Plots', 
                'Cumulative Distribution Function', 'Gradient Magnitude Analysis',
                'Contour Analysis', 'Center Row/Column Profile', 'Percentile Analysis', 
                'Hotspot Analysis'
            }
            
            for i, advanced_plot in enumerate(plots_data['advanced']):
                print(f"  Adding advanced plot {i+1}/{len(plots_data['advanced'])}: {advanced_plot['title']}")
                
                # Check if this plot should be in landscape mode
                plot_title = advanced_plot.get('title', '')
                is_landscape = any(landscape_keyword in plot_title for landscape_keyword in landscape_plots)
                
                if is_landscape:
                    fig = base64_to_figure(advanced_plot['image'], figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT))
                else:
                    fig = base64_to_figure(advanced_plot['image'], figsize=(A4_WIDTH, A4_HEIGHT))
                
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
        
        # Add comparison plot (side-by-side heatmaps)
        if 'comparison' in plots_data and plots_data['comparison']:
            print("Adding comparison plot...")
            fig = base64_to_figure(plots_data['comparison'], figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT))
            pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
        
        # Add 3D plots if available (though disabled by default)
        if '3d' in plots_data:
            print("Adding 3D surface plots...")
            # Handle both single plot and list of plots
            if isinstance(plots_data['3d'], list):
                for i, plot_data in enumerate(plots_data['3d']):
                    print(f"  Adding 3D surface plot page {i+1}/{len(plots_data['3d'])}")
                    fig = base64_to_figure(plot_data, figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT))
                    pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                    plt.close(fig)
            else:
                fig = base64_to_figure(plots_data['3d'], figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT))
                pdf.savefig(fig, dpi=dpi, bbox_inches='tight')
                plt.close(fig)
    
    # Final cleanup
    plt.close('all')
    gc.collect()
    
    print(f"Efficient PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path


def export_to_pdf(folder_data, output_filename='warpage_analysis.pdf',
                  include_stats=True, include_3d=True, include_advanced=True, dpi=150, cmap='jet', colorbar=True, vmin=None, vmax=None, optimize_for_pdf=None, config=None):
    """
    Export comprehensive warpage analysis to high-resolution PDF in report directory.

    Args:
        folder_data (dict): Dictionary with folder as key and (data, stats, filename) as value
        output_filename (str): Output PDF filename
        include_stats (bool): Whether to include statistical analysis plots
        include_3d (bool): Whether to include 3D surface plots
        include_advanced (bool): Whether to include comprehensive advanced statistical analysis
        dpi (int): DPI for high-resolution output
        cmap (str): Colormap name
        colorbar (bool): Whether to show colorbar
        vmin (float, optional): Minimum value for color scale
        vmax (float, optional): Maximum value for color scale

    Returns:
        str: Path to created PDF file
    """
    if not folder_data:
        return None

    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)

    # Check config for PDF optimization if not specified
    if optimize_for_pdf is None:
        from config import DEFAULT_CONFIG
        optimize_for_pdf = DEFAULT_CONFIG.get('optimize_pdf_data', True)

    if optimize_for_pdf:
        print("DEBUG: PDF optimization enabled - data will be resized for faster generation")
    else:
        print("DEBUG: PDF optimization disabled - using full resolution data")

    # Import functions lazily
    viz = _import_visualization()
    advanced_funcs = _import_advanced_stats()

    # Optimized DPI settings for different content types
    dpi_legend = max(100, dpi - 50)
    dpi_individual = dpi
    dpi_stats = max(100, dpi - 50)
    dpi_advanced = max(100, dpi - 50)
    dpi_3d = max(100, dpi - 50)

    # A4 page size in inches
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    
    # Create PDF with A4 page size
    with PdfPages(full_output_path) as pdf:
        
        # Create cover and info pages if available
        if advanced_funcs:
            cover_fig = advanced_funcs['create_cover_page'](folder_data, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(cover_fig, dpi=dpi_legend, bbox_inches='tight')
            plt.close(cover_fig)

            toc_fig = advanced_funcs['create_table_of_contents'](folder_data, include_stats, include_3d, include_advanced, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(toc_fig, dpi=dpi_legend, bbox_inches='tight')
            plt.close(toc_fig)

            legend_fig = advanced_funcs['create_legend_page'](figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(legend_fig, dpi=dpi_legend, bbox_inches='tight')
            plt.close(legend_fig)

        # Individual plots
        for file_id, (data, stats, filename) in folder_data.items():
            individual_fig = viz.create_individual_plot(file_id, data, stats, filename,
                                                      figsize=(A4_WIDTH, A4_HEIGHT), vmin=vmin, vmax=vmax, cmap=cmap, colorbar=colorbar, optimize_for_pdf=True, config=config)
            pdf.savefig(individual_fig, dpi=dpi_individual, bbox_inches='tight')
            plt.close(individual_fig)
        
        # Statistical comparison pages
        if include_stats and len(folder_data) > 1:
            # Combined plots for efficiency
            mean_range_fig = viz.create_mean_range_combined_plot(folder_data, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(mean_range_fig, dpi=dpi_stats, bbox_inches='tight')
            plt.close(mean_range_fig)

            minmax_std_fig = viz.create_minmax_std_combined_plot(folder_data, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(minmax_std_fig, dpi=dpi_stats, bbox_inches='tight')
            plt.close(minmax_std_fig)

            # Distribution plot with reduced size
            dist_fig = viz.create_warpage_distribution_plot(folder_data, figsize=(A4_WIDTH, A4_HEIGHT / 2))
            pdf.savefig(dist_fig, dpi=dpi_stats, bbox_inches='tight')
            plt.close(dist_fig)
        
        # Advanced statistical analysis pages (if requested and available)
        if include_advanced and len(folder_data) > 1 and advanced_funcs:
            try:
                advanced_analysis = advanced_funcs['create_comprehensive_advanced_analysis'](folder_data)
                if advanced_analysis:
                    for fig, title in advanced_analysis:
                        pdf.savefig(fig, dpi=dpi_advanced, bbox_inches='tight')
                        plt.close(fig)
                gc.collect()
            except Exception:
                pass  # Skip if advanced analysis fails
        
        # 3D surface plots (if requested)
        if include_3d and len(folder_data) > 0:
            try:
                surface_figures = viz.create_3d_surface_plot(folder_data, figsize=(A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT), optimize_for_pdf=True, config=config)
                if surface_figures:
                    for surface_fig in surface_figures:
                        pdf.savefig(surface_fig, dpi=dpi_3d, bbox_inches='tight')
                        plt.close(surface_fig)
            except Exception:
                pass  # Skip if 3D plotting fails
    
    # Final cleanup
    plt.close('all')
    gc.collect()
    
    print(f"PDF created successfully: {full_output_path}")
    print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
    
    return full_output_path


# ===========================================
# PLOTLY-BASED PDF EXPORT FUNCTIONS
# ===========================================

def export_plotly_to_pdf(folder_data, output_filename="warpage_analysis_plotly.pdf", 
                         include_stats=True, include_3d=True, vmin=None, vmax=None):
    """
    Export analysis results to PDF using Plotly static images for consistent web/PDF appearance.
    
    Args:
        folder_data (dict): Processed data dictionary
        output_filename (str): Output PDF filename
        include_stats (bool): Include statistical analysis
        include_3d (bool): Include 3D surface plots
        vmin, vmax (float): Color scale limits
        
    Returns:
        str: Path to the created PDF file, or None if failed
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from PIL import Image
    import tempfile
    
    # Ensure report directory exists
    report_dir = ensure_report_directory()
    full_output_path = os.path.join(report_dir, output_filename)
    
    print(f"Creating Plotly-based PDF: {full_output_path}")
    
    if not folder_data:
        print("No data found to export!")
        return None
    
    # A4 page size
    A4_WIDTH = 8.27
    A4_HEIGHT = 11.69
    A4_LANDSCAPE_WIDTH = 11.69
    A4_LANDSCAPE_HEIGHT = 8.27
    
    try:
        with PdfPages(full_output_path) as pdf:
            
            # Cover page using advanced_statistics function
            print("Creating cover page...")
            cover_fig = create_cover_page(folder_data, figsize=(A4_WIDTH, A4_HEIGHT))
            pdf.savefig(cover_fig, dpi=150, bbox_inches='tight')
            plt.close(cover_fig)
            
            # Individual plots using Plotly
            print("Creating individual Plotly plots...")
            for i, (file_id, (data, stats, filename)) in enumerate(folder_data.items()):
                print(f"  Processing file {i+1}/{len(folder_data)}: {filename}")
                
                # Create Plotly figure
                plotly_fig = create_plotly_individual_plot(file_id, data, stats, filename, 
                                                         vmin=vmin, vmax=vmax)
                
                # Convert to static image
                img_bytes = plotly_to_static_image(plotly_fig, 
                                                 width=int((A4_WIDTH)*150),
                                                 height=int((A4_HEIGHT)*150),
                                                 format='png')
                
                # Create matplotlib figure to hold the Plotly image
                fig, ax = plt.subplots(figsize=(A4_WIDTH, A4_HEIGHT))
                
                # Load image from bytes
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_bytes)
                    tmp_file.flush()
                    
                    # Display image in matplotlib
                    img = mpimg.imread(tmp_file.name)
                    ax.imshow(img)
                    ax.axis('off')
                    
                    # Clean up temporary file
                    os.unlink(tmp_file.name)
                
                pdf.savefig(fig, dpi=150, bbox_inches='tight')
                plt.close(fig)
            
            # Comparison plot using Plotly
            if len(folder_data) > 1:
                print("Creating Plotly comparison plot...")
                plotly_fig = create_plotly_comparison_plot(folder_data, vmin=vmin, vmax=vmax)
                
                img_bytes = plotly_to_static_image(plotly_fig, 
                                                 width=int((A4_WIDTH)*150),
                                                 height=int((A4_HEIGHT)*150),
                                                 format='png')
                
                fig, ax = plt.subplots(figsize=(A4_WIDTH, A4_HEIGHT))
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_bytes)
                    tmp_file.flush()
                    
                    img = mpimg.imread(tmp_file.name)
                    ax.imshow(img)
                    ax.axis('off')
                    ax.set_title('Warpage Data Comparison', fontsize=16, fontweight='bold', pad=20)
                    
                    os.unlink(tmp_file.name)
                
                pdf.savefig(fig, dpi=150, bbox_inches='tight')
                plt.close(fig)
            
            # Statistical analysis using Plotly
            if include_stats:
                print("Creating Plotly statistical analysis...")
                plotly_fig = create_plotly_statistical_plots(folder_data)
                
                img_bytes = plotly_to_static_image(plotly_fig, 
                                                 width=int((A4_WIDTH)*150),
                                                 height=int((A4_HEIGHT)*200),  # Taller for stats
                                                 format='png')
                
                fig, ax = plt.subplots(figsize=(A4_WIDTH, A4_HEIGHT))
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_bytes)
                    tmp_file.flush()
                    
                    img = mpimg.imread(tmp_file.name)
                    ax.imshow(img)
                    ax.axis('off')
                    
                    os.unlink(tmp_file.name)
                
                pdf.savefig(fig, dpi=150, bbox_inches='tight')
                plt.close(fig)
            
            # 3D surface plots using Plotly
            if include_3d and len(folder_data) > 0:
                print("Creating Plotly 3D surface plots...")
                plotly_fig = create_plotly_3d_surface(folder_data)
                
                img_bytes = plotly_to_static_image(plotly_fig, 
                                                 width=int((A4_WIDTH)*150),
                                                 height=int((A4_HEIGHT)*150),
                                                 format='png')
                
                fig, ax = plt.subplots(figsize=(A4_WIDTH, A4_HEIGHT))
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_bytes)
                    tmp_file.flush()
                    
                    img = mpimg.imread(tmp_file.name)
                    ax.imshow(img)
                    ax.axis('off')
                    
                    os.unlink(tmp_file.name)
                
                pdf.savefig(fig, dpi=150, bbox_inches='tight')
                plt.close(fig)
        
        print(f"Plotly-based PDF created successfully: {full_output_path}")
        print(f"File size: {os.path.getsize(full_output_path) / (1024*1024):.2f} MB")
        
        return full_output_path
        
    except Exception as e:
        print(f"Error creating Plotly-based PDF: {e}")
        import traceback
        print(traceback.format_exc())
        return None
    finally:
        plt.close('all') 
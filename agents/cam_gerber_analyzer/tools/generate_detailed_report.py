"""Tool for generating detailed HTML reports with all information."""

import os
from typing import Dict, Any
from ..database import CamGerberDatabase


def generate_detailed_html_report(analysis_id: int) -> Dict[str, Any]:
    """Generate a comprehensive HTML report with all details.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with report path and URL
    """
    try:
        db = CamGerberDatabase()
        
        # Get analysis
        analysis = db.get_analysis(analysis_id)
        if not analysis:
            return {
                "success": False,
                "error": f"Analysis {analysis_id} not found"
            }
        
        # Get result
        result = db.get_analysis_result(analysis_id)
        if not result:
            return {
                "success": False,
                "error": "No analysis results found. Please generate design summary first."
            }
        
        # Get issues
        issues = db.get_analysis_issues(analysis_id)
        
        # Get design files
        design_files = db.get_design_files(analysis_id)
        
        # Get summary data (contains detailed statistics)
        from .generate_design_summary import generate_design_summary
        summary_result = generate_design_summary(analysis_id)
        summary = summary_result.get('summary', {}) if summary_result.get('success') else {}
        
        # Generate comprehensive HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed CAM Analysis Report - Analysis {analysis_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .info-card strong {{
            display: block;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
        .warning {{ color: #f39c12; font-weight: bold; }}
        .info {{ color: #3498db; }}
        .stat-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.9em;
            margin: 2px;
        }}
        .badge-primary {{ background: #3498db; color: white; }}
        .badge-success {{ background: #27ae60; color: white; }}
        .badge-warning {{ background: #f39c12; color: white; }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 5px;
        }}
        .layer-detail {{
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 3px solid #3498db;
        }}
        .drill-detail {{
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 3px solid #27ae60;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Detailed CAM Analysis Report</h1>
        <p><strong>Analysis ID:</strong> {analysis_id}</p>
        <p><strong>Project:</strong> {analysis.project_name or 'N/A'}</p>
        <p><strong>Board:</strong> {analysis.board_name or 'N/A'}</p>
        <p><strong>Created:</strong> {analysis.created_at}</p>
        
        <h2>📐 Board Information</h2>
        <div class="info-grid">
            <div class="info-card">
                <strong>Board Dimensions</strong>
                {result.board_width or 'N/A'}mm × {result.board_height or 'N/A'}mm
            </div>
            <div class="info-card">
                <strong>Layer Count</strong>
                {result.layer_count or 'N/A'} layers
            </div>
            <div class="info-card">
                <strong>Total Files</strong>
                {len(design_files)} files
            </div>
            <div class="info-card">
                <strong>Total Size</strong>
                {summary.get('total_size_mb', 0)} MB
            </div>
        </div>
        
        <h2>🔩 Drill Statistics</h2>
"""
        
        # Add drill statistics
        drill_stats = summary.get('drill_statistics', {})
        if drill_stats:
            total_holes = sum(s.get('total_holes', 0) for s in drill_stats.values())
            html += f"""
        <div class="section">
            <h3>Total Holes/Vias: <span class="stat-badge badge-primary">{total_holes}</span></h3>
"""
            for drill_type, stats in drill_stats.items():
                html += f"""
            <div class="drill-detail">
                <h4>{drill_type}</h4>
                <p><strong>Total Holes:</strong> {stats.get('total_holes', 0)}</p>
                <p><strong>Drill Tools:</strong> {stats.get('tools_count', 0)}</p>
                <p><strong>Hole Size Range:</strong> {stats.get('min_hole_size_mm', 0):.3f}mm - {stats.get('max_hole_size_mm', 0):.3f}mm</p>
                <p><strong>Unique Hole Sizes:</strong> {stats.get('unique_hole_sizes', 0)}</p>
                <p><strong>Hole Sizes:</strong> {', '.join([f'{s:.3f}mm' for s in stats.get('hole_sizes_mm', [])])}</p>
            </div>
"""
        else:
            html += "<p>No drill files found.</p>"
        
        html += """
        <h2>📊 Layer Details</h2>
"""
        
        # Add layer details
        layer_details = summary.get('layer_details', {})
        if layer_details:
            for layer_name, details in sorted(layer_details.items()):
                html += f"""
        <div class="layer-detail">
            <h3>{layer_name}</h3>
            <div class="info-grid">
                <div class="info-card">
                    <strong>Primitives</strong>
                    {details.get('primitives_count', 0):,}
                </div>
                <div class="info-card">
                    <strong>Apertures</strong>
                    {details.get('apertures_count', 0):,}
                </div>
                <div class="info-card">
                    <strong>Statements</strong>
                    {details.get('statements_count', 0):,}
                </div>
                <div class="info-card">
                    <strong>Lines</strong>
                    {details.get('lines_count', 0):,}
                </div>
                <div class="info-card">
                    <strong>Arcs</strong>
                    {details.get('arcs_count', 0):,}
                </div>
                <div class="info-card">
                    <strong>Regions</strong>
                    {details.get('regions_count', 0):,}
                </div>
"""
                if details.get('min_aperture_size'):
                    html += f"""
                <div class="info-card">
                    <strong>Aperture Size Range</strong>
                    {details.get('min_aperture_size', 0):.3f}mm - {details.get('max_aperture_size', 0):.3f}mm
                </div>
"""
                html += """
            </div>
        </div>
"""
        else:
            html += "<p>No detailed layer information available.</p>"
        
        html += f"""
        <h2>⚠️ Issues Found</h2>
        <p><strong>Total Issues:</strong> <span class="stat-badge badge-warning">{len(issues)}</span></p>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Type</th>
                    <th>Layer</th>
                    <th>Description</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for issue in issues:
            severity_class = issue.severity
            html += f"""
                <tr>
                    <td class="{severity_class}">{severity_class.upper()}</td>
                    <td>{issue.issue_type}</td>
                    <td>{issue.layer_name or 'N/A'}</td>
                    <td>{issue.description}</td>
                    <td>{issue.recommendation or 'N/A'}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>📁 Files Analyzed</h2>
        <table>
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Format</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for df in design_files:
            size_kb = df.file_size / 1024
            html += f"""
                <tr>
                    <td>{df.filename}</td>
                    <td>{df.file_type}</td>
                    <td>{df.file_format}</td>
                    <td>{size_kb:.2f} KB</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        report_dir = os.path.join(
            os.path.dirname(__file__),
            '../../../data/cam_gerber_analyzer/reports'
        )
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f'analysis_{analysis_id}_detailed.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return {
            "success": True,
            "format": "html",
            "report_path": report_path,
            "report_url": f"/reports/analysis_{analysis_id}_detailed.html"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate detailed report: {str(e)}"
        }


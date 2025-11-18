"""Generate comprehensive report with detailed file-by-file analysis."""

import os
import json
from typing import Dict, Any
from ..database import CamGerberDatabase


def generate_comprehensive_report(analysis_id: int) -> Dict[str, Any]:
    """Generate comprehensive HTML report with detailed file analysis.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with report path
    """
    try:
        from .generate_file_analysis_report import generate_file_analysis_report
        from .generate_design_summary import generate_design_summary
        
        db = CamGerberDatabase()
        analysis = db.get_analysis(analysis_id)
        design_files = db.get_design_files(analysis_id)
        issues = db.get_analysis_issues(analysis_id)
        result = db.get_analysis_result(analysis_id)
        
        # Get file analysis
        file_analysis_result = generate_file_analysis_report(analysis_id)
        file_details = file_analysis_result.get('file_details', []) if file_analysis_result.get('success') else []
        
        # Get summary
        summary_result = generate_design_summary(analysis_id)
        summary = summary_result.get('summary', {}) if summary_result.get('success') else {}
        
        # Group files by category
        categories = {
            'Copper Layers': [],
            'Solder Mask': [],
            'Silkscreen': [],
            'Drill Files': [],
            'Other': []
        }
        
        for file_detail in file_details:
            category_name = file_detail.get('llm_analysis', {}).get('file_category', 'other')
            if 'copper' in category_name:
                categories['Copper Layers'].append(file_detail)
            elif 'mask' in category_name:
                categories['Solder Mask'].append(file_detail)
            elif 'silk' in category_name:
                categories['Silkscreen'].append(file_detail)
            elif 'drill' in category_name:
                categories['Drill Files'].append(file_detail)
            else:
                categories['Other'].append(file_detail)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive CAM Analysis Report - Analysis {analysis_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        h2 {{
            color: #34495e;
            margin-top: 50px;
            margin-bottom: 25px;
            padding: 15px;
            background: #ecf0f1;
            border-left: 5px solid #3498db;
            border-radius: 5px;
        }}
        h3 {{
            color: #555;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 3px solid #95a5a6;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .info-card strong {{
            display: block;
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .info-card .value {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .file-card {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .file-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .file-badge {{
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .file-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .detail-item {{
            background: white;
            padding: 10px;
            border-radius: 4px;
        }}
        .detail-item strong {{
            display: block;
            color: #7f8c8d;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .characteristics {{
            margin-top: 15px;
        }}
        .characteristics ul {{
            list-style: none;
            padding: 0;
        }}
        .characteristics li {{
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }}
        .characteristics li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
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
        .category-section {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Comprehensive CAM Analysis Report</h1>
        
        <div style="margin-bottom: 30px;">
            <p><strong>Analysis ID:</strong> {analysis_id}</p>
            <p><strong>Project:</strong> {analysis.project_name or 'N/A'}</p>
            <p><strong>Board:</strong> {analysis.board_name or 'N/A'}</p>
            <p><strong>Created:</strong> {analysis.created_at}</p>
        </div>
        
        <h2>📐 Board Overview</h2>
        <div class="info-grid">
            <div class="info-card">
                <strong>Board Dimensions</strong>
                <div class="value">{result.board_width or summary.get('board_width', 'N/A')}mm × {result.board_height or summary.get('board_height', 'N/A')}mm</div>
            </div>
            <div class="info-card">
                <strong>Layer Count</strong>
                <div class="value">{result.layer_count or summary.get('layer_count', 'N/A')} layers</div>
            </div>
            <div class="info-card">
                <strong>Total Files</strong>
                <div class="value">{len(design_files)} files</div>
            </div>
            <div class="info-card">
                <strong>Total Size</strong>
                <div class="value">{summary.get('total_size_mb', 0):.2f} MB</div>
            </div>
            <div class="info-card">
                <strong>Total Holes/Vias</strong>
                <div class="value">{result.total_vias or summary.get('total_vias', 0)}</div>
            </div>
            <div class="info-card">
                <strong>Issues Found</strong>
                <div class="value">{len(issues)}</div>
            </div>
        </div>
"""
        
        # Add file-by-file analysis by category
        for category_name, files_list in categories.items():
            if files_list:
                html += f"""
        <h2>📁 {category_name}</h2>
        <div class="category-section">
"""
                for file_detail in files_list:
                    filename = file_detail.get('filename', 'Unknown')
                    file_type = file_detail.get('file_type', 'Unknown')
                    size_kb = file_detail.get('file_size_kb', 0)
                    llm = file_detail.get('llm_analysis', {})
                    
                    html += f"""
            <div class="file-card">
                <div class="file-header">
                    <div class="file-name">📄 {filename}</div>
                    <span class="file-badge">{file_type}</span>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <strong>Purpose:</strong> {llm.get('layer_purpose', 'N/A')}<br>
                    <strong>Manufacturing Function:</strong> {llm.get('manufacturing_function', 'N/A')}<br>
                    <strong>Used In:</strong> {', '.join(llm.get('manufacturing_processes', []))}
                </div>
                
                <div class="file-details">
                    <div class="detail-item">
                        <strong>File Size</strong>
                        {size_kb:.2f} KB
                    </div>
                    <div class="detail-item">
                        <strong>Format</strong>
                        {file_detail.get('format', 'N/A')}
                    </div>
                    <div class="detail-item">
                        <strong>Units</strong>
                        {file_detail.get('units', 'N/A')}
                    </div>
"""
                    
                    if 'total_lines' in file_detail:
                        html += f"""
                    <div class="detail-item">
                        <strong>Total Lines</strong>
                        {file_detail.get('total_lines', 0):,}
                    </div>
"""
                    
                    if 'aperture_definitions' in file_detail:
                        html += f"""
                    <div class="detail-item">
                        <strong>Aperture Definitions</strong>
                        {file_detail.get('aperture_definitions', 0)}
                    </div>
"""
                    
                    if 'draw_commands_sample' in file_detail:
                        html += f"""
                    <div class="detail-item">
                        <strong>Draw Commands (sample)</strong>
                        {file_detail.get('draw_commands_sample', 0)}
                    </div>
"""
                    
                    # Drill-specific details
                    if 'drill_data' in file_detail:
                        drill = file_detail.get('drill_data', {})
                        html += f"""
                    <div class="detail-item">
                        <strong>Total Holes</strong>
                        {drill.get('total_holes', 0)}
                    </div>
                    <div class="detail-item">
                        <strong>Drill Tools</strong>
                        {drill.get('tools_count', 0)}
                    </div>
                    <div class="detail-item">
                        <strong>Hole Size Range</strong>
                        {drill.get('min_hole_size_mm', 0):.3f}mm - {drill.get('max_hole_size_mm', 0):.3f}mm
                    </div>
                    <div class="detail-item">
                        <strong>Unique Hole Sizes</strong>
                        {drill.get('unique_hole_sizes', 0)}
                    </div>
"""
                    
                    html += """
                </div>
"""
                    
                    # Key characteristics
                    characteristics = llm.get('key_characteristics', [])
                    if characteristics:
                        html += """
                <div class="characteristics">
                    <strong>Key Characteristics:</strong>
                    <ul>
"""
                        for char in characteristics:
                            html += f"                        <li>{char}</li>\n"
                        html += """
                    </ul>
                </div>
"""
                    
                    html += """
            </div>
"""
                
                html += """
        </div>
"""
        
        # Add issues section
        html += f"""
        <h2>⚠️ CAM Analysis Issues</h2>
        <p><strong>Total Issues:</strong> {len(issues)}</p>
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
    </div>
</body>
</html>
"""
        
        # Save report
        report_dir = os.path.join(
            os.path.dirname(__file__),
            '../../../data/cam_gerber_analyzer/reports'
        )
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f'analysis_{analysis_id}_comprehensive.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return {
            "success": True,
            "report_path": report_path,
            "report_url": f"/reports/analysis_{analysis_id}_comprehensive.html"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate comprehensive report: {str(e)}"
        }


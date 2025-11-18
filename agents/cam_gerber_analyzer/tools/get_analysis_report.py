"""Tool for getting analysis report."""

from typing import Dict, Any
from ..database import CamGerberDatabase


def get_analysis_report(analysis_id: int, report_format: str = "json") -> Dict[str, Any]:
    """Generate and retrieve analysis report.
    
    Args:
        analysis_id: Analysis ID
        report_format: Report format (pdf|html|json)
        
    Returns:
        Report file path or content
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
                "error": "No analysis results found"
            }
        
        # Get issues
        issues = db.get_analysis_issues(analysis_id)
        
        # Generate report based on format
        if report_format == "json":
            report_data = result.to_dict()
            report_data["issues"] = [issue.to_dict() for issue in issues]
            return {
                "success": True,
                "format": "json",
                "report": report_data
            }
        elif report_format == "html":
            # Generate HTML report
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CAM Analysis Report - Analysis {analysis_id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .critical {{ color: red; }}
                    .warning {{ color: orange; }}
                    .info {{ color: blue; }}
                </style>
            </head>
            <body>
                <h1>CAM Analysis Report</h1>
                <h2>Analysis ID: {analysis_id}</h2>
                
                <h3>Board Information</h3>
                <table>
                    <tr><th>Property</th><th>Value</th></tr>
                    <tr><td>Board Width</td><td>{result.board_width or 'N/A'} mm</td></tr>
                    <tr><td>Board Height</td><td>{result.board_height or 'N/A'} mm</td></tr>
                    <tr><td>Layer Count</td><td>{result.layer_count or 'N/A'}</td></tr>
                    <tr><td>Panel Count</td><td>{result.panel_count}</td></tr>
                    <tr><td>Total Boards</td><td>{result.total_boards}</td></tr>
                </table>
                
                <h3>Issues Found</h3>
                <table>
                    <tr><th>Severity</th><th>Type</th><th>Description</th><th>Recommendation</th></tr>
            """
            for issue in issues:
                html += f"""
                    <tr>
                        <td class="{issue.severity}">{issue.severity}</td>
                        <td>{issue.issue_type}</td>
                        <td>{issue.description}</td>
                        <td>{issue.recommendation or 'N/A'}</td>
                    </tr>
                """
            html += """
                </table>
            </body>
            </html>
            """
            
            # Save HTML report
            import os
            report_dir = os.path.join(
                os.path.dirname(__file__),
                '../../../data/cam_gerber_analyzer/reports'
            )
            os.makedirs(report_dir, exist_ok=True)
            report_path = os.path.join(report_dir, f'analysis_{analysis_id}.html')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return {
                "success": True,
                "format": "html",
                "report_path": report_path,
                "report_url": f"/reports/analysis_{analysis_id}.html"
            }
        else:
            return {
                "success": False,
                "error": f"Report format {report_format} not yet implemented"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get analysis report: {str(e)}"
        }


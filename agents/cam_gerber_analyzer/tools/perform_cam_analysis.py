"""Tool for performing CAM analysis."""

from typing import Dict, Any
from ..database import CamGerberDatabase


def perform_cam_analysis(analysis_id: int, analysis_options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Perform comprehensive CAM analysis.
    
    Args:
        analysis_id: Analysis ID
        analysis_options: Analysis options dictionary
        
    Returns:
        Analysis results with issues and recommendations
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
        
        # Get design files
        design_files = db.get_design_files(analysis_id)
        if not design_files:
            return {
                "success": False,
                "error": "No design files found for analysis"
            }
        
        # Get CAM rules from config
        from ..config import AGENT_CONFIG
        cam_rules = AGENT_CONFIG.get("cam_rules", {})
        
        issues = []
        
        # Parse files and perform analysis
        from .parse_gerber_file import parse_gerber_file
        
        for df in design_files:
            if df.file_format == "gerber":
                parsed = parse_gerber_file(df.file_path, df.file_type)
                if parsed.get("success"):
                    # Check minimum trace width (if we can extract it)
                    # This is a simplified check - full implementation would analyze all traces
                    if parsed.get("width") and parsed.get("width") < cam_rules.get("min_trace_width", 0.1) * 1000:
                        issues.append({
                            "issue_type": "trace_width",
                            "severity": "warning",
                            "layer_name": df.file_type,
                            "description": f"Potential trace width issue detected",
                            "recommendation": f"Verify trace widths meet minimum requirement of {cam_rules.get('min_trace_width', 0.1)}mm"
                        })
        
        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.get("severity") == "critical")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        info_count = sum(1 for issue in issues if issue.get("severity") == "info")
        
        # Save issues to database
        from ..models import AnalysisIssue
        for issue_data in issues:
            issue = AnalysisIssue(
                analysis_id=analysis_id,
                issue_type=issue_data.get("issue_type", ""),
                severity=issue_data.get("severity", "info"),
                layer_name=issue_data.get("layer_name"),
                description=issue_data.get("description", ""),
                recommendation=issue_data.get("recommendation")
            )
            db.save_analysis_issue(issue)
        
        # Update analysis result with issue counts
        result = db.get_analysis_result(analysis_id)
        if result:
            result.issues_critical = critical_count
            result.issues_warning = warning_count
            result.issues_info = info_count
            db.save_analysis_result(result)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "issues_found": len(issues),
            "issues_critical": critical_count,
            "issues_warning": warning_count,
            "issues_info": info_count,
            "issues": issues[:10]  # Return first 10 issues
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to perform CAM analysis: {str(e)}"
        }


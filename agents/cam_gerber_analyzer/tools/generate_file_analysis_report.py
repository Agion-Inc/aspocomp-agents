"""Generate comprehensive file-by-file analysis report."""

import os
import json
from typing import Dict, Any
from ..database import CamGerberDatabase


def generate_file_analysis_report(analysis_id: int) -> Dict[str, Any]:
    """Generate detailed report analyzing each file's purpose and contents.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with comprehensive file analysis
    """
    try:
        db = CamGerberDatabase()
        design_files = db.get_design_files(analysis_id)
        
        if not design_files:
            return {
                "success": False,
                "error": "No design files found"
            }
        
        from .analyze_gerber_file_details import analyze_gerber_file_with_llm
        from .parse_drill_file import parse_drill_file
        
        file_analyses = []
        
        for df in design_files:
            if df.file_format == "gerber":
                analysis = analyze_gerber_file_with_llm(df.file_path, df.filename, df.file_type)
                if analysis.get("success"):
                    file_analyses.append(analysis)
            elif df.file_format == "drill":
                drill_data = parse_drill_file(df.file_path)
                if drill_data.get("success"):
                    from .analyze_file_purpose import analyze_file_purpose
                    # Read sample for analysis
                    with open(df.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content_sample = f.read(1000)
                    purpose_analysis = analyze_file_purpose(df.filename, df.file_type, content_sample)
                    
                    file_analyses.append({
                        "filename": df.filename,
                        "file_type": df.file_type,
                        "file_size_bytes": df.file_size,
                        "file_size_kb": round(df.file_size / 1024, 2),
                        "format": "Excellon",
                        "drill_data": drill_data,
                        "llm_analysis": purpose_analysis
                    })
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "files_analyzed": len(file_analyses),
            "file_details": file_analyses
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate file analysis: {str(e)}"
        }


"""Tool for analyzing Gerber files with LLM to understand their purpose and extract details."""

import os
from typing import Dict, Any, List
import subprocess
import json


def analyze_gerber_file_with_llm(file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
    """Analyze a Gerber file using LLM to understand its purpose and extract details.
    
    Args:
        file_path: Path to Gerber file
        filename: Filename
        file_type: Detected file type
        
    Returns:
        Analysis dictionary with file purpose and details
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        file_size = os.path.getsize(file_path)
        
        # Read file content (first 5000 characters for analysis)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_sample = f.read(5000)
        
        # Read full file stats
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            full_content = f.read()
            total_lines = len(full_content.split('\n'))
            total_chars = len(full_content)
        
        # Extract key information from file
        # Count commands
        draw_commands = content_sample.count('D01') + content_sample.count('D02') + content_sample.count('D03')
        flash_commands = content_sample.count('D03')
        move_commands = content_sample.count('D02')
        
        # Check for format specifiers
        has_format_spec = '%FS' in content_sample
        has_units = '%MO' in content_sample
        units = "MM" if '%MOMM' in content_sample else "IN" if '%MOIN' in content_sample else "Unknown"
        
        # Check for aperture definitions
        aperture_defs = content_sample.count('%ADD')
        
        # Use pattern-based analysis (more reliable than LLM for this)
        from .analyze_file_purpose import analyze_file_purpose
        llm_analysis = analyze_file_purpose(filename, file_type, content_sample)
        
        # Combine analysis
        analysis = {
            "success": True,
            "filename": filename,
            "file_type": file_type,
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2),
            "total_lines": total_lines,
            "total_characters": total_chars,
            "format": "RS-274X" if has_format_spec else "Unknown",
            "units": units,
            "aperture_definitions": aperture_defs,
            "draw_commands_sample": draw_commands,
            "flash_commands": flash_commands,
            "move_commands": move_commands,
            "llm_analysis": llm_analysis,
        }
        
        return analysis
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze file: {str(e)}"
        }


def analyze_all_files(analysis_id: int) -> Dict[str, Any]:
    """Analyze all files in an analysis with detailed LLM analysis.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with analysis of all files
    """
    try:
        from ..database import CamGerberDatabase
        
        db = CamGerberDatabase()
        design_files = db.get_design_files(analysis_id)
        
        if not design_files:
            return {
                "success": False,
                "error": "No design files found"
            }
        
        file_analyses = []
        
        for df in design_files:
            if df.file_format == "gerber":
                analysis = analyze_gerber_file_with_llm(df.file_path, df.filename, df.file_type)
                if analysis.get("success"):
                    file_analyses.append(analysis)
            elif df.file_format == "drill":
                # Analyze drill file
                from .parse_drill_file import parse_drill_file
                drill_analysis = parse_drill_file(df.file_path)
                if drill_analysis.get("success"):
                    file_analyses.append({
                        "success": True,
                        "filename": df.filename,
                        "file_type": df.file_type,
                        "file_size_bytes": df.file_size,
                        "file_size_kb": round(df.file_size / 1024, 2),
                        "format": "Excellon",
                        "drill_analysis": drill_analysis,
                        "llm_analysis": {
                            "layer_purpose": f"Drill file for {df.file_type}",
                            "manufacturing_function": "Defines hole locations and sizes for drilling",
                            "file_category": "drill"
                        }
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
            "error": f"Failed to analyze files: {str(e)}"
        }


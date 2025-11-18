"""Configuration for CAM Gerber Analyzer Agent."""

import os

AGENT_CONFIG = {
    "agent_id": "cam_gerber_analyzer",
    "name": "CAM Gerber Analyzer",
    "description": "Automatically performs CAM analysis based on Gerber and ODB++ files",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.3,  # Lower temperature for technical accuracy
    "max_iterations": 5,
    
    # Database configuration
    "database": {
        "type": "sqlite",  # or "sharepoint" for production
        "path": os.path.join(
            os.path.dirname(__file__),
            "../../data/cam_gerber_analyzer/analyses.db"
        ),
        "sharepoint_list": "CAMAnalyses",  # Production
        "sharepoint_site": "https://aspocomp.sharepoint.com/sites/agents"
    },
    
    # File upload configuration
    "upload_directory": os.path.join(
        os.path.dirname(__file__),
        "../../data/cam_gerber_analyzer/uploads"
    ),
    "max_file_size_mb": 200,  # Larger for ODB++ archives
    "supported_file_types": [
        # Gerber files
        ".gbr", ".ger", ".art", ".drill", ".txt", ".exc",
        # ODB++ files
        ".tgz", ".zip", ".tar.gz", ".odb"
    ],
    "supported_formats": ["gerber", "odbp"],
    
    # Tools
    "tools": [
        "upload_design_files",
        "detect_file_format",
        "parse_gerber_file",
        "parse_odbp_file",
        "generate_design_summary",
        "perform_cam_analysis",
        "get_analysis_report",
        "get_analysis_history",
        "compare_analyses"
    ],
    
    # CAM rules
    "cam_rules": {
        "min_trace_width": 0.1,  # mm
        "min_spacing": 0.1,  # mm
        "min_annular_ring": 0.05,  # mm
        "min_drill_size": 0.15,  # mm
        "min_solder_mask_clearance": 0.05  # mm
    },
    
    # System prompt
    "system_prompt_path": os.path.join(
        os.path.dirname(__file__),
        "prompts/system_prompt.txt"
    )
}


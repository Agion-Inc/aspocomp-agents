"""Tool for detecting file format."""

import os
from typing import Dict, Any


def detect_file_format(file_path: str = None, filename: str = None) -> Dict[str, Any]:
    """Automatically detect file format (Gerber vs ODB++).
    
    Args:
        file_path: Path to file (optional)
        filename: Filename (optional)
        
    Returns:
        Dictionary with format_type ("gerber" or "odbp")
    """
    try:
        # Use filename if provided, otherwise extract from path
        name = filename or (os.path.basename(file_path) if file_path else "")
        
        if not name:
            return {
                "success": False,
                "error": "No filename or file_path provided"
            }
        
        # Check file extension
        name_lower = name.lower()
        
        # ZIP files - need to check contents
        if name_lower.endswith('.zip'):
            # ZIP could contain Gerber files or ODB++
            # Default to checking contents if file_path provided
            if file_path and os.path.exists(file_path):
                try:
                    import zipfile
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        file_list = zip_ref.namelist()
                        # Check if contains Gerber files
                        gerber_files = [f for f in file_list if f.lower().endswith(('.ger', '.gbr', '.art', '.exc', '.drill'))]
                        if gerber_files:
                            return {
                                "success": True,
                                "format_type": "gerber",
                                "confidence": "high",
                                "note": f"ZIP contains {len(gerber_files)} Gerber/drill files"
                            }
                        # Check for ODB++ structure
                        odb_files = [f for f in file_list if any(odb in f.lower() for odb in ['steps', 'matrix', 'layers'])]
                        if odb_files:
                            return {
                                "success": True,
                                "format_type": "odbp",
                                "confidence": "high",
                                "note": "ZIP contains ODB++ structure"
                            }
                except:
                    pass
            # Default: assume ZIP contains Gerber files (most common case)
            return {
                "success": True,
                "format_type": "gerber",
                "confidence": "medium",
                "note": "ZIP file (assuming Gerber contents)"
            }
        
        # ODB++ formats (non-ZIP)
        if name_lower.endswith(('.tgz', '.tar.gz', '.odb')):
            return {
                "success": True,
                "format_type": "odbp",
                "confidence": "high"
            }
        
        # Gerber formats
        if name_lower.endswith(('.gbr', '.ger', '.art', '.drill', '.txt')):
            return {
                "success": True,
                "format_type": "gerber",
                "confidence": "high"
            }
        
        # Try to detect from file content if path provided
        if file_path and os.path.exists(file_path):
            # Check if it's a directory (ODB++ can be directory structure)
            if os.path.isdir(file_path):
                # Check for ODB++ structure files
                odb_files = ['steps', 'matrix', 'layers']
                if any(os.path.exists(os.path.join(file_path, f)) for f in odb_files):
                    return {
                        "success": True,
                        "format_type": "odbp",
                        "confidence": "medium"
                    }
            
            # Check file content for Gerber commands
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = f.read(1000)
                    if any(cmd in first_lines for cmd in ['G04', 'G01', 'D01', 'D02', 'D03', '%FS', '%MO']):
                        return {
                            "success": True,
                            "format_type": "gerber",
                            "confidence": "medium"
                        }
            except:
                pass
        
        return {
            "success": False,
            "error": "Could not detect file format",
            "format_type": "unknown"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to detect format: {str(e)}"
        }


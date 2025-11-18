"""Tool for parsing ODB++ files."""

import os
import tarfile
import zipfile
from typing import Dict, Any


def parse_odbp_file(archive_path: str = None, directory_path: str = None) -> Dict[str, Any]:
    """Parse an ODB++ archive and extract design information.
    
    Args:
        archive_path: Path to ODB++ archive (.tgz, .zip, .tar.gz)
        directory_path: Path to ODB++ directory structure
        
    Returns:
        Parsed data dictionary
    """
    try:
        extracted_path = None
        
        # Extract archive if provided
        if archive_path and os.path.exists(archive_path):
            # Create extraction directory
            extract_dir = archive_path + "_extracted"
            os.makedirs(extract_dir, exist_ok=True)
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.endswith(('.tgz', '.tar.gz')):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported archive format: {archive_path}"
                }
            
            extracted_path = extract_dir
        
        # Use directory path if provided
        if directory_path and os.path.exists(directory_path):
            extracted_path = directory_path
        
        if not extracted_path or not os.path.exists(extracted_path):
            return {
                "success": False,
                "error": "No valid ODB++ path provided"
            }
        
        # TODO: Implement actual ODB++ parsing using PyOdbDesignLib
        # For now, check for ODB++ structure files
        
        structure_info = {
            "extracted_path": extracted_path,
            "has_steps": os.path.exists(os.path.join(extracted_path, "steps")),
            "has_matrix": os.path.exists(os.path.join(extracted_path, "matrix")),
            "has_layers": os.path.exists(os.path.join(extracted_path, "layers")),
        }
        
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(extracted_path):
            file_count += len(files)
        
        return {
            "success": True,
            "extracted_path": extracted_path,
            "file_count": file_count,
            "structure": structure_info,
            "parsed": True,
            "note": "Basic structure detection implemented. Full parsing requires PyOdbDesignLib library."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse ODB++ file: {str(e)}"
        }


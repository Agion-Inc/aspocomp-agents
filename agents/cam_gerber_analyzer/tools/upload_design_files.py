"""Tool for uploading design files."""

import os
import base64
import zipfile
import tempfile
from typing import List, Dict, Any
from ..database import CamGerberDatabase
from ..models import DesignFile


def upload_design_files(
    files: List[Dict[str, Any]],
    project_name: str = None,
    board_name: str = None,
    user_id: str = "default"
) -> Dict[str, Any]:
    """Upload and store Gerber or ODB++ files for analysis.
    
    Args:
        files: List of file objects with 'filename', 'content' (base64), 'file_type'
        project_name: Project name (optional)
        board_name: Board name (optional)
        user_id: User identifier
        
    Returns:
        Dictionary with analysis_id and uploaded files info
    """
    try:
        # Initialize database
        db = CamGerberDatabase()
        
        # Create analysis session
        analysis_id = db.create_analysis(user_id, project_name, board_name)
        
        # Get upload directory from config
        upload_dir = os.path.join(
            os.path.dirname(__file__),
            '../../../data/cam_gerber_analyzer/uploads',
            str(analysis_id)
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        # Process each file
        for file_data in files:
            filename = file_data.get('filename', 'unknown')
            content = file_data.get('content', '')
            file_type = file_data.get('file_type', 'other')
            
            # Decode base64 content
            try:
                file_bytes = base64.b64decode(content)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to decode file {filename}: {str(e)}"
                }
            
            # Check if file is a ZIP archive
            if filename.lower().endswith('.zip'):
                # Extract ZIP file and process all contents
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
                        tmp_zip.write(file_bytes)
                        tmp_zip_path = tmp_zip.name
                    
                    with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                        zip_file_list = zip_ref.namelist()
                        
                        # Filter for Gerber and drill files
                        gerber_extensions = ('.ger', '.gbr', '.art', '.drill', '.exc', '.txt')
                        relevant_files = [f for f in zip_file_list if f.lower().endswith(gerber_extensions)]
                        
                        if not relevant_files:
                            return {
                                "success": False,
                                "error": f"ZIP file {filename} does not contain any Gerber or drill files"
                            }
                        
                        # Extract and process each file
                        for zip_filename in relevant_files:
                            # Skip directories
                            if zip_filename.endswith('/'):
                                continue
                            
                            # Extract file content
                            file_content = zip_ref.read(zip_filename)
                            
                            # Determine file type from filename
                            detected_type = "other"
                            zip_lower = zip_filename.lower()
                            if 'top' in zip_lower and ('copper' in zip_lower or 'elec' in zip_lower):
                                detected_type = "copper_top"
                            elif 'bottom' in zip_lower and ('copper' in zip_lower or 'elec' in zip_lower):
                                detected_type = "copper_bottom"
                            elif 'top' in zip_lower and 'silk' in zip_lower:
                                detected_type = "silk_top"
                            elif 'bottom' in zip_lower and 'silk' in zip_lower:
                                detected_type = "silk_bottom"
                            elif 'top' in zip_lower and ('stop' in zip_lower or 'mask' in zip_lower):
                                detected_type = "solder_mask_top"
                            elif ('bottom' in zip_lower or 'bot' in zip_lower) and ('stop' in zip_lower or 'mask' in zip_lower):
                                detected_type = "solder_mask_bottom"
                            elif 'top' in zip_lower and 'paste' in zip_lower:
                                detected_type = "paste_top"
                            elif 'drill' in zip_lower or zip_lower.endswith('.exc'):
                                detected_type = "drill"
                            elif 'routing' in zip_lower or 'outline' in zip_lower:
                                detected_type = "outline"
                            elif 'plating' in zip_lower:
                                detected_type = "plating"
                            elif 'elec' in zip_lower or 'inner' in zip_lower:
                                # Try to extract layer number
                                import re
                                layer_match = re.search(r'elec(\d+)', zip_lower)
                                if layer_match:
                                    layer_num = layer_match.group(1)
                                    detected_type = f"inner_layer_{layer_num}"
                                else:
                                    detected_type = "inner_layer"
                            
                            # Save extracted file
                            safe_filename = os.path.basename(zip_filename)
                            file_path = os.path.join(upload_dir, safe_filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                            
                            # Detect file format
                            file_format = "gerber"
                            if safe_filename.lower().endswith(('.exc', '.drill')):
                                file_format = "drill"
                            elif safe_filename.lower().endswith(('.gbr', '.ger', '.art', '.txt')):
                                file_format = "gerber"
                            
                            # Create design file record
                            design_file = DesignFile(
                                analysis_id=analysis_id,
                                filename=safe_filename,
                                file_format=file_format,
                                file_type=detected_type if detected_type != "other" else file_type,
                                file_path=file_path,
                                file_size=len(file_content)
                            )
                            
                            file_id = db.save_design_file(design_file)
                            uploaded_files.append({
                                "id": file_id,
                                "filename": safe_filename,
                                "file_format": file_format,
                                "file_type": detected_type,
                                "file_size": len(file_content)
                            })
                    
                    # Clean up temp file
                    os.unlink(tmp_zip_path)
                    
                except zipfile.BadZipFile:
                    return {
                        "success": False,
                        "error": f"File {filename} is not a valid ZIP archive"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to extract ZIP file {filename}: {str(e)}"
                    }
            else:
                # Regular file (not ZIP)
                # Save file
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                # Detect file format
                file_format = "gerber"
                if filename.endswith(('.tgz', '.tar.gz', '.odb')):
                    file_format = "odbp"
                elif filename.endswith(('.gbr', '.ger', '.art', '.drill', '.txt', '.exc')):
                    file_format = "gerber"
                
                # Create design file record
                design_file = DesignFile(
                    analysis_id=analysis_id,
                    filename=filename,
                    file_format=file_format,
                    file_type=file_type,
                    file_path=file_path,
                    file_size=len(file_bytes)
                )
                
                file_id = db.save_design_file(design_file)
                uploaded_files.append({
                    "id": file_id,
                    "filename": filename,
                    "file_format": file_format,
                    "file_size": len(file_bytes)
                })
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "uploaded_files": uploaded_files,
            "message": f"Successfully uploaded {len(uploaded_files)} file(s)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to upload files: {str(e)}"
        }


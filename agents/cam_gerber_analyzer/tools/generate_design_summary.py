"""Tool for generating PCB design summary."""

import json
from typing import Dict, Any
from ..database import CamGerberDatabase
from ..models import AnalysisResult


def generate_design_summary(analysis_id: int) -> Dict[str, Any]:
    """Generate comprehensive PCB design summary.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Design summary dictionary
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
                "error": "No design files found for this analysis"
            }
        
        # Detect format from files
        file_format = design_files[0].file_format if design_files else "gerber"
        
        # Parse all files and extract information
        from .parse_gerber_file import parse_gerber_file
        from .parse_odbp_file import parse_odbp_file
        from .parse_drill_file import parse_drill_file
        
        parsed_files = []
        board_dimensions = []
        layer_count = 0
        total_size = 0
        file_types = {}
        
        # Detailed statistics
        layer_details = {}
        drill_statistics = {}
        aperture_statistics = {}
        total_vias = 0
        total_pads = 0
        
        for df in design_files:
            file_types[df.file_type] = file_types.get(df.file_type, 0) + 1
            total_size += df.file_size
            
            # Parse file based on format
            if df.file_format == "gerber":
                parsed = parse_gerber_file(df.file_path, df.file_type)
                if parsed.get("success"):
                    parsed_files.append(parsed)
                    
                    # Store detailed layer information
                    layer_details[df.file_type] = {
                        "primitives_count": parsed.get("primitives_count", 0),
                        "apertures_count": parsed.get("apertures_count", 0),
                        "statements_count": parsed.get("statements_count", 0),
                        "lines_count": parsed.get("lines_count", 0),
                        "arcs_count": parsed.get("arcs_count", 0),
                        "regions_count": parsed.get("regions_count", 0),
                        "min_aperture_size": parsed.get("min_aperture_size"),
                        "max_aperture_size": parsed.get("max_aperture_size"),
                        "avg_aperture_size": parsed.get("avg_aperture_size"),
                        "aperture_sizes": parsed.get("aperture_sizes", [])[:10],  # Top 10 sizes
                    }
                    
                    # Collect aperture statistics
                    if parsed.get("apertures_count", 0) > 0:
                        aperture_statistics[df.file_type] = {
                            "count": parsed.get("apertures_count"),
                            "sizes": parsed.get("aperture_sizes", []),
                            "min": parsed.get("min_aperture_size"),
                            "max": parsed.get("max_aperture_size"),
                        }
                    
                    # Extract dimensions
                    width = parsed.get("width")
                    height = parsed.get("height")
                    
                    # If bounds available, use them for more accurate dimensions
                    if parsed.get("bounds"):
                        bounds = parsed["bounds"]
                        if bounds.get("max_x") is not None and bounds.get("max_y") is not None:
                            width = abs(bounds["max_x"] - bounds.get("min_x", 0))
                            height = abs(bounds["max_y"] - bounds.get("min_y", 0))
                    
                    if width and height and width > 0 and height > 0:
                        board_dimensions.append({
                            "width": width,
                            "height": height,
                            "file_type": df.file_type
                        })
                    # Count layers
                    if df.file_type in ["copper_top", "copper_bottom"]:
                        layer_count += 1
                    elif "inner_layer" in df.file_type or ("inner" in df.file_type and "layer" in df.file_type):
                        layer_count += 1
                    elif df.file_type.startswith("inner_layer_"):
                        layer_count += 1
            elif df.file_format == "drill":
                # Parse drill file
                parsed = parse_drill_file(df.file_path)
                if parsed.get("success"):
                    parsed_files.append(parsed)
                    drill_statistics[df.file_type] = {
                        "total_holes": parsed.get("total_holes", 0),
                        "tools_count": parsed.get("tools_count", 0),
                        "min_hole_size_mm": parsed.get("min_hole_size_mm"),
                        "max_hole_size_mm": parsed.get("max_hole_size_mm"),
                        "unique_hole_sizes": parsed.get("unique_hole_sizes", 0),
                        "hole_sizes_mm": parsed.get("hole_sizes_mm", []),
                        "hole_counts_by_size": parsed.get("hole_counts_by_size", {}),
                    }
                    total_vias += parsed.get("total_holes", 0)
            elif df.file_format == "odbp":
                parsed = parse_odbp_file(directory_path=df.file_path)
                if parsed.get("success"):
                    parsed_files.append(parsed)
        
        # Calculate average board dimensions (use largest dimensions found)
        board_width = None
        board_height = None
        if board_dimensions:
            valid_dims = [d for d in board_dimensions if d.get("width") and d.get("height")]
            if valid_dims:
                # Use the largest dimensions found (most accurate)
                max_width = max(d["width"] for d in valid_dims)
                max_height = max(d["height"] for d in valid_dims)
                board_width = round(max_width, 2)
                board_height = round(max_height, 2)
        
        # Detect panelization (multiple identical boards)
        # Simple heuristic: if we have multiple files with same dimensions, might be panelized
        is_panelized = False
        panel_count = 1
        boards_per_panel = 1
        total_boards = 1
        
        # Count copper layers to determine layer count
        # Count inner layers explicitly
        inner_layers = sum(1 for df in design_files if "inner_layer" in df.file_type)
        top_bottom_layers = sum(1 for df in design_files if df.file_type in ["copper_top", "copper_bottom"])
        
        # Total layer count = top + bottom + inner layers
        if inner_layers > 0 or top_bottom_layers > 0:
            layer_count = top_bottom_layers + inner_layers
            # If we have inner layers but no explicit top/bottom, assume 2-layer board
            if inner_layers > 0 and top_bottom_layers == 0:
                layer_count = inner_layers + 2  # inner layers + top + bottom
        
        # Calculate total pads (estimate from apertures)
        if aperture_statistics:
            total_pads = sum(stats.get("count", 0) for stats in aperture_statistics.values())
        
        # Create comprehensive summary
        summary = {
            "analysis_id": analysis_id,
            "file_format": file_format,
            "file_count": len(design_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "board_width": board_width,
            "board_height": board_height,
            "layer_count": layer_count if layer_count > 0 else None,
            "panel_count": panel_count,
            "boards_per_panel": boards_per_panel,
            "total_boards": total_boards,
            "is_panelized": is_panelized,
            "parsed_files_count": len(parsed_files),
            "status": "completed",
            # Detailed statistics
            "layer_details": layer_details,
            "drill_statistics": drill_statistics,
            "aperture_statistics": aperture_statistics,
            "total_vias": total_vias,
            "total_pads": total_pads,
            "total_holes": total_vias,  # Alias for vias
        }
        
        # Save to database
        result = AnalysisResult(
            analysis_id=analysis_id,
            board_width=board_width,
            board_height=board_height,
            layer_count=layer_count if layer_count > 0 else None,
            panel_count=panel_count,
            boards_per_panel=boards_per_panel,
            total_boards=total_boards,
            is_panelized=is_panelized,
            total_vias=total_vias,
            total_pads=total_pads,
        )
        db.save_analysis_result(result)
        
        # Get saved result for additional data
        result = db.get_analysis_result(analysis_id)
        if result:
            summary.update({
                "board_thickness": result.board_thickness,
                "laminate_type": result.laminate_type,
                "surface_finish": result.surface_finish,
                "total_vias": result.total_vias,
                "total_pads": result.total_pads,
            })
        
        # Update analysis status
        db.update_analysis_status(analysis_id, "completed", metadata=summary)
        
        return {
            "success": True,
            "summary": summary,
            "message": "Design summary generated successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate design summary: {str(e)}"
        }


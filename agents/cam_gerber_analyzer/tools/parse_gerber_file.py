"""Tool for parsing Gerber files."""

import os
from typing import Dict, Any, Optional


def parse_gerber_file(file_path: str, file_type: str = None) -> Dict[str, Any]:
    """Parse a Gerber file and extract layer information.
    
    Args:
        file_path: Path to Gerber file
        file_type: Type of file (copper_top, copper_bottom, solder_mask_top, drill, etc.)
        
    Returns:
        Parsed data dictionary
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        file_size = os.path.getsize(file_path)
        
        # Try to use python-gerber library for full parsing
        try:
            from gerber import read
            from gerber.rs274x import GerberFile
            
            # Read Gerber file
            gerber_file = read(file_path)
            
            # Extract basic information
            parsed_data = {
                "success": True,
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size,
                "format": "RS-274X",
                "parsed": True,
                "units": str(gerber_file.units) if hasattr(gerber_file, 'units') else None,
            }
            
            # Extract bounds if available
            if hasattr(gerber_file, 'bounds') and gerber_file.bounds:
                bounds = gerber_file.bounds
                if bounds:
                    try:
                        # python-gerber returns bounds as ((min_x, max_x), (min_y, max_y))
                        if isinstance(bounds, (list, tuple)) and len(bounds) >= 2:
                            x_bounds = bounds[0]
                            y_bounds = bounds[1]
                            
                            if isinstance(x_bounds, (list, tuple)) and len(x_bounds) >= 2:
                                min_x, max_x = x_bounds[0], x_bounds[1]
                            else:
                                min_x, max_x = 0, 0
                            
                            if isinstance(y_bounds, (list, tuple)) and len(y_bounds) >= 2:
                                min_y, max_y = y_bounds[0], y_bounds[1]
                            else:
                                min_y, max_y = 0, 0
                            
                            width = abs(max_x - min_x)
                            height = abs(max_y - min_y)
                            
                            if width > 0 and height > 0:
                                parsed_data.update({
                                    "bounds": {
                                        "min_x": min_x,
                                        "min_y": min_y,
                                        "max_x": max_x,
                                        "max_y": max_y,
                                    },
                                    "width": width,
                                    "height": height,
                                })
                    except Exception as e:
                        # If bounds extraction fails, fall through to coordinate parsing
                        pass
            
            # Count primitives and analyze types
            if hasattr(gerber_file, 'primitives'):
                primitives = gerber_file.primitives
                primitive_count = len(primitives) if primitives else 0
                
                # Analyze primitive types
                primitive_types = {}
                line_count = 0
                arc_count = 0
                region_count = 0
                
                for prim in primitives:
                    prim_type = type(prim).__name__
                    primitive_types[prim_type] = primitive_types.get(prim_type, 0) + 1
                    if 'Line' in prim_type:
                        line_count += 1
                    elif 'Arc' in prim_type:
                        arc_count += 1
                    elif 'Region' in prim_type:
                        region_count += 1
                
                parsed_data.update({
                    "primitives_count": primitive_count,
                    "primitive_types": primitive_types,
                    "lines_count": line_count,
                    "arcs_count": arc_count,
                    "regions_count": region_count,
                })
            
            # Extract detailed aperture information
            if hasattr(gerber_file, 'apertures'):
                apertures = gerber_file.apertures
                # Convert dict_values to dict if needed
                if hasattr(apertures, 'items'):
                    apertures_dict = apertures
                else:
                    # It's a dict_values object, convert to dict
                    apertures_dict = dict(apertures) if apertures else {}
                
                aperture_count = len(apertures_dict) if apertures_dict else 0
                
                # Analyze aperture sizes (these tell us pad sizes, trace widths)
                aperture_sizes = []
                circular_apertures = []
                rectangular_apertures = []
                oval_apertures = []
                
                if apertures_dict:
                    for ap_id, aperture in apertures_dict.items():
                        try:
                            # Extract size information
                            if hasattr(aperture, 'diameter'):
                                size = float(aperture.diameter)
                                aperture_sizes.append(size)
                                circular_apertures.append({"id": str(ap_id), "diameter": size})
                            elif hasattr(aperture, 'width') and hasattr(aperture, 'height'):
                                width = float(aperture.width)
                                height = float(aperture.height)
                                aperture_sizes.append(max(width, height))
                                if abs(width - height) < 0.001:  # Essentially equal
                                    circular_apertures.append({"id": str(ap_id), "diameter": width})
                                else:
                                    oval_apertures.append({"id": str(ap_id), "width": width, "height": height})
                            elif hasattr(aperture, 'width'):
                                width = float(aperture.width)
                                aperture_sizes.append(width)
                                rectangular_apertures.append({"id": str(ap_id), "width": width})
                            # Try to extract from string representation
                            else:
                                ap_str = str(aperture)
                                # Look for diameter or size in string
                                import re
                                dia_match = re.search(r'diameter[=:]?\s*([\d.]+)', ap_str, re.I)
                                if dia_match:
                                    size = float(dia_match.group(1))
                                    aperture_sizes.append(size)
                                    circular_apertures.append({"id": str(ap_id), "diameter": size})
                        except Exception as e:
                            # Skip apertures we can't parse
                            pass
                
                # Calculate statistics
                min_aperture = min(aperture_sizes) if aperture_sizes else None
                max_aperture = max(aperture_sizes) if aperture_sizes else None
                avg_aperture = sum(aperture_sizes) / len(aperture_sizes) if aperture_sizes else None
                
                parsed_data.update({
                    "apertures_count": aperture_count,
                    "aperture_sizes": sorted(set(aperture_sizes))[:20] if aperture_sizes else [],  # Unique sizes, top 20
                    "min_aperture_size": min_aperture,
                    "max_aperture_size": max_aperture,
                    "avg_aperture_size": avg_aperture,
                    "circular_apertures_count": len(circular_apertures),
                    "rectangular_apertures_count": len(rectangular_apertures),
                    "oval_apertures_count": len(oval_apertures),
                })
            
            # Extract statements count for file complexity
            if hasattr(gerber_file, 'statements'):
                statements = gerber_file.statements
                parsed_data.update({
                    "statements_count": len(statements) if statements else 0,
                })
            
            return parsed_data
            
        except ImportError:
            # Fallback to basic parsing if library not available
            pass
        except Exception as e:
            # If parsing fails, fall back to basic parsing
            pass
        
        # Basic parsing fallback
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # Read first 10KB
        
        # Detect if it's RS-274X format
        is_rs274x = '%FS' in content or '%MO' in content
        
        # Extract units
        units = "MM" if '%MOMM*%' in content or '%MO MM*%' in content else "IN" if '%MOIN*%' in content or '%MO IN*%' in content else None
        
        # Extract format specifier
        format_spec = None
        if '%FS' in content:
            fs_line = [line for line in content.split('\n') if '%FS' in line]
            if fs_line:
                format_spec = fs_line[0].strip()
        
        # Count basic commands
        draw_commands = content.count('D01') + content.count('D02') + content.count('D03')
        
        # Try to extract board dimensions from coordinates
        import re
        width = None
        height = None
        
        # Try combined X Y coordinates first (most common format)
        # Exclude format specifiers (lines starting with %)
        content_lines = [line for line in content.split('\n') if not line.strip().startswith('%')]
        content_filtered = '\n'.join(content_lines)
        
        coords_xy = re.findall(r'X(\d+)Y(\d+)', content_filtered)
        if coords_xy:
            try:
                x_coords = [int(c[0]) for c in coords_xy]
                y_coords = [int(c[1]) for c in coords_xy]
                if x_coords and y_coords:
                    min_x = min(x_coords)
                    max_x = max(x_coords)
                    min_y = min(y_coords)
                    max_y = max(y_coords)
                    # Convert to mm (assuming 5 decimal places, divide by 100000)
                    if units == "MM":
                        width = abs(max_x - min_x) / 100000.0
                        height = abs(max_y - min_y) / 100000.0
                    elif units == "IN":
                        width = abs(max_x - min_x) / 100000.0 * 25.4  # Convert inches to mm
                        height = abs(max_y - min_y) / 100000.0 * 25.4
                    else:
                        # Default to MM if units not specified
                        width = abs(max_x - min_x) / 100000.0
                        height = abs(max_y - min_y) / 100000.0
            except Exception:
                pass
        
        # Fallback: try separate X and Y coordinates
        if width is None or height is None:
            coords_x = re.findall(r'X(\d+)', content_filtered)
            coords_y = re.findall(r'Y(\d+)', content_filtered)
            if coords_x and coords_y:
                try:
                    x_coords = [int(x) for x in coords_x]
                    y_coords = [int(y) for y in coords_y]
                    if x_coords and y_coords:
                        min_x = min(x_coords)
                        max_x = max(x_coords)
                        min_y = min(y_coords)
                        max_y = max(y_coords)
                        # Convert to mm
                        if units == "MM":
                            width = abs(max_x - min_x) / 100000.0
                            height = abs(max_y - min_y) / 100000.0
                        elif units == "IN":
                            width = abs(max_x - min_x) / 100000.0 * 25.4
                            height = abs(max_y - min_y) / 100000.0 * 25.4
                        else:
                            width = abs(max_x - min_x) / 100000.0
                            height = abs(max_y - min_y) / 100000.0
                except Exception:
                    pass
        
        return {
            "success": True,
            "file_path": file_path,
            "file_type": file_type,
            "file_size": file_size,
            "format": "RS-274X" if is_rs274x else "RS-274D",
            "format_spec": format_spec,
            "units": units,
            "draw_commands": draw_commands,
            "width": width,
            "height": height,
            "parsed": True,
            "note": "Basic parsing completed. Install python-gerber for enhanced parsing."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse Gerber file: {str(e)}"
        }


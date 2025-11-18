"""Extract design rules from Gerber files: minimum spacing, trace width, annular ring."""

import os
import re
from typing import Dict, Any, List, Optional


def extract_trace_widths_and_spacing(file_path: str) -> Dict[str, Any]:
    """Extract trace widths and spacing from Gerber file.
    
    Args:
        file_path: Path to Gerber file
        
    Returns:
        Dictionary with trace width and spacing information
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Read file content first to determine units
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Determine units FIRST
        units = "IN"  # Default
        if '%MOMM' in content or '%MO MM' in content:
            units = "MM"
        elif '%MOIN' in content or '%MO IN' in content:
            units = "IN"
        
        # Extract aperture sizes from file content directly (most reliable)
        # Pattern: %ADD10C,0.100000*% (circular) or %ADD10R,0.1X0.2*% (rectangular)
        circular_pattern = r'%ADD\d+C,([\d.]+)'
        circular_sizes = re.findall(circular_pattern, content)
        
        rectangular_pattern = r'%ADD\d+R,([\d.]+)X([\d.]+)'
        rectangular_sizes = re.findall(rectangular_pattern, content)
        
        # Combine all aperture sizes
        file_sizes = []
        for size in circular_sizes:
            file_sizes.append(float(size))
        for width, height in rectangular_sizes:
            file_sizes.append(min(float(width), float(height)))  # Use smaller dimension
        
        # Convert to mm if needed
        if file_sizes:
            if units == "IN":
                aperture_sizes = [s * 25.4 for s in file_sizes]
            else:
                aperture_sizes = file_sizes
            
            # Filter out zero and very small values (likely errors)
            aperture_sizes = [s for s in aperture_sizes if s > 0.001]
        else:
            aperture_sizes = []
        
        # Filter out invalid sizes
        valid_sizes = [s for s in aperture_sizes if 0.001 < s < 100]  # Reasonable range
        
        # Calculate statistics
        min_aperture = min(valid_sizes) if valid_sizes else None
        max_aperture = max(valid_sizes) if valid_sizes else None
        
        # Estimate trace width (smallest non-zero aperture is often trace width)
        # Typically trace widths are in range 0.05mm - 0.5mm
        trace_width = None
        trace_width_candidates = [s for s in valid_sizes if 0.05 <= s <= 0.5]
        if trace_width_candidates:
            trace_width = min(trace_width_candidates)
        elif valid_sizes:
            # If no typical trace widths, use smallest
            trace_width = min_aperture
        
        # Estimate annular ring (difference between pad and via sizes)
        # Annular ring = (pad_diameter - via_diameter) / 2
        annular_ring = None
        if len(valid_sizes) >= 2:
            sorted_sizes = sorted(set(valid_sizes))
            # Pad sizes are typically > 0.5mm, via sizes < 0.5mm
            pad_sizes = [s for s in sorted_sizes if s >= 0.5]
            via_sizes = [s for s in sorted_sizes if s < 0.5]
            
            if pad_sizes and via_sizes:
                # Use smallest pad and largest via for conservative estimate
                smallest_pad = min(pad_sizes)
                largest_via = max(via_sizes)
                annular_ring = (smallest_pad - largest_via) / 2
            elif len(sorted_sizes) >= 2:
                # Fallback: use difference between largest and smallest
                annular_ring = (sorted_sizes[-1] - sorted_sizes[0]) / 2
        
        # Calculate minimum spacing
        # Method 1: Estimate from trace width (spacing is often 1-2x trace width)
        min_spacing = None
        if trace_width:
            min_spacing = trace_width * 1.2  # Conservative estimate
        
        # Method 2: Calculate from coordinates (if available and reasonable)
        coords_pattern = r'X([\d.]+)\s*Y([\d.]+)'
        coordinates = re.findall(coords_pattern, content)
        
        if len(coordinates) > 10:
            try:
                coords_list = [(float(x), float(y)) for x, y in coordinates[:5000]]  # Limit for performance
                min_distances = []
                # Check distances between nearby coordinates
                for i in range(min(500, len(coords_list))):
                    for j in range(i+1, min(i+50, len(coords_list))):
                        x1, y1 = coords_list[i]
                        x2, y2 = coords_list[j]
                        dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                        # Convert to mm if needed
                        if units == "IN":
                            dist = dist * 25.4
                        if 0.01 < dist < 5.0:  # Reasonable spacing range
                            min_distances.append(dist)
                if min_distances:
                    calculated_spacing = min(min_distances)
                    # Use the more conservative (smaller) estimate
                    if min_spacing:
                        min_spacing = min(min_spacing, calculated_spacing)
                    else:
                        min_spacing = calculated_spacing
            except:
                pass
        
        return {
            "success": True,
            "trace_width_mm": round(trace_width, 3) if trace_width else None,
            "min_spacing_mm": round(min_spacing, 3) if min_spacing else None,
            "annular_ring_mm": round(annular_ring, 3) if annular_ring else None,
            "aperture_sizes_mm": sorted(set([round(s, 3) for s in valid_sizes])) if valid_sizes else [],
            "min_aperture_mm": round(min_aperture, 3) if min_aperture else None,
            "max_aperture_mm": round(max_aperture, 3) if max_aperture else None,
            "units": units,
            "aperture_count": len(valid_sizes)
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract design rules: {str(e)}"
        }


def analyze_all_layers_for_design_rules(analysis_id: int) -> Dict[str, Any]:
    """Analyze all Gerber layers to find minimum design rules.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with overall design rules
    """
    try:
        from ..database import CamGerberDatabase
        
        db = CamGerberDatabase()
        design_files = db.get_design_files(analysis_id)
        
        all_trace_widths = []
        all_spacings = []
        all_annular_rings = []
        
        layer_results = {}
        
        for df in design_files:
            # Analyze copper layers (elec files or inner_layer files)
            is_copper_layer = (
                df.file_format == "gerber" and 
                ("elec" in df.file_type.lower() or "inner_layer" in df.file_type.lower())
            )
            
            if is_copper_layer:
                # Analyze copper layers for design rules
                result = extract_trace_widths_and_spacing(df.file_path)
                if result.get("success"):
                    layer_results[df.file_type] = result
                    trace = result.get("trace_width_mm")
                    spacing = result.get("min_spacing_mm")
                    annular = result.get("annular_ring_mm")
                    
                    if trace:
                        all_trace_widths.append(trace)
                    if spacing:
                        all_spacings.append(spacing)
                    if annular:
                        all_annular_rings.append(annular)
        
        # Find overall minimums
        min_trace_width = min(all_trace_widths) if all_trace_widths else None
        min_spacing = min(all_spacings) if all_spacings else None
        min_annular_ring = min(all_annular_rings) if all_annular_rings else None
        
        return {
            "success": True,
            "min_trace_width_mm": round(min_trace_width, 3) if min_trace_width else None,
            "min_spacing_mm": round(min_spacing, 3) if min_spacing else None,
            "min_annular_ring_mm": round(min_annular_ring, 3) if min_annular_ring else None,
            "layer_results": layer_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze design rules: {str(e)}"
        }

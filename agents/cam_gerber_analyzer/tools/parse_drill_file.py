"""Tool for parsing drill files (Excellon format)."""

import os
import re
from typing import Dict, Any, List


def parse_drill_file(file_path: str) -> Dict[str, Any]:
    """Parse an Excellon drill file and extract drill information.
    
    Args:
        file_path: Path to drill file (.exc, .drill, .txt)
        
    Returns:
        Parsed drill data dictionary
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse Excellon format
        # Format: T01C0.0250 (Tool number, diameter)
        # Holes: X12345Y67890 (coordinates)
        
        # Extract tool definitions
        tool_pattern = r'T(\d+)C([\d.]+)'
        tools = {}
        tool_matches = re.findall(tool_pattern, content)
        for tool_num, diameter in tool_matches:
            tools[tool_num] = float(diameter)
        
        # Extract hole coordinates
        # Format: X12345Y67890 or X12345 Y67890
        hole_pattern = r'X([\d.]+)\s*Y([\d.]+)'
        holes = re.findall(hole_pattern, content)
        
        # Count holes by tool
        tool_usage_pattern = r'T(\d+)'
        tool_usage = {}
        current_tool = None
        
        lines = content.split('\n')
        for line in lines:
            # Check for tool selection
            tool_match = re.search(r'T(\d+)', line)
            if tool_match:
                current_tool = tool_match.group(1)
                tool_usage[current_tool] = tool_usage.get(current_tool, 0)
            
            # Count holes for current tool
            if current_tool and ('X' in line and 'Y' in line):
                tool_usage[current_tool] = tool_usage.get(current_tool, 0) + 1
        
        # Calculate statistics
        hole_sizes = []
        hole_counts_by_size = {}
        
        for tool_num, diameter in tools.items():
            count = tool_usage.get(tool_num, 0)
            hole_sizes.append(diameter)
            hole_counts_by_size[diameter] = hole_counts_by_size.get(diameter, 0) + count
        
        total_holes = len(holes)
        min_hole_size = min(hole_sizes) if hole_sizes else None
        max_hole_size = max(hole_sizes) if hole_sizes else None
        
        # Determine units (usually inches for Excellon)
        units = "IN"  # Default
        if "METRIC" in content.upper() or "MM" in content:
            units = "MM"
        
        # Convert to mm if needed
        if units == "IN" and min_hole_size:
            min_hole_size_mm = min_hole_size * 25.4
            max_hole_size_mm = max_hole_size * 25.4 if max_hole_size else None
        else:
            min_hole_size_mm = min_hole_size
            max_hole_size_mm = max_hole_size
        
        return {
            "success": True,
            "file_path": file_path,
            "file_size": file_size,
            "format": "Excellon",
            "units": units,
            "tools_count": len(tools),
            "tools": tools,
            "total_holes": total_holes,
            "holes_by_tool": tool_usage,
            "hole_sizes_mm": sorted(set([h * 25.4 if units == "IN" else h for h in hole_sizes])) if hole_sizes else [],
            "min_hole_size_mm": min_hole_size_mm,
            "max_hole_size_mm": max_hole_size_mm,
            "hole_counts_by_size": {str(k): v for k, v in hole_counts_by_size.items()},
            "unique_hole_sizes": len(set(hole_sizes)) if hole_sizes else 0,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse drill file: {str(e)}"
        }


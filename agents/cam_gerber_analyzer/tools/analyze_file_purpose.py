"""Analyze Gerber file purpose based on filename and content patterns."""

import os
import re
from typing import Dict, Any


def analyze_file_purpose(filename: str, file_type: str, content_sample: str) -> Dict[str, Any]:
    """Analyze file purpose based on filename patterns and content.
    
    Args:
        filename: Filename
        file_type: Detected file type
        content_sample: Sample of file content
        
    Returns:
        Analysis dictionary
    """
    filename_lower = filename.lower()
    
    # Determine purpose from filename patterns
    purpose = "Unknown"
    manufacturing_function = "Unknown"
    category = "other"
    key_characteristics = []
    manufacturing_processes = []
    
    # Copper layers
    if 'elec' in filename_lower or 'inner_layer' in file_type.lower():
        if 'elec1' in filename_lower or 'layer_1' in file_type.lower():
            purpose = "Inner copper layer 1 (typically top-side copper)"
            category = "copper"
        elif 'elec2' in filename_lower or 'layer_2' in file_type.lower():
            purpose = "Inner copper layer 2"
            category = "copper"
        elif 'elec3' in filename_lower or 'layer_3' in file_type.lower():
            purpose = "Inner copper layer 3"
            category = "copper"
        elif 'elec4' in filename_lower or 'layer_4' in file_type.lower():
            purpose = "Inner copper layer 4 (typically bottom-side copper)"
            category = "copper"
        else:
            purpose = "Inner copper layer"
            category = "copper"
        
        manufacturing_function = "Defines copper traces, pads, and routing for this layer"
        manufacturing_processes = ["Etching", "Copper plating", "Lamination"]
        key_characteristics = ["Copper traces", "Pads", "Vias", "Routing patterns"]
    
    # Solder mask
    elif 'stop' in filename_lower or 'mask' in file_type.lower():
        if 'top' in filename_lower:
            purpose = "Top solder mask layer (solder stop)"
            category = "solder_mask"
        elif 'bot' in filename_lower or 'bottom' in filename_lower:
            purpose = "Bottom solder mask layer (solder stop)"
            category = "solder_mask"
        else:
            purpose = "Solder mask layer"
            category = "solder_mask"
        
        manufacturing_function = "Defines areas where solder mask should NOT be applied (exposes pads)"
        manufacturing_processes = ["Solder mask application", "UV curing", "Development"]
        key_characteristics = ["Pad openings", "Via openings", "Solder mask clearance"]
    
    # Silkscreen
    elif 'silk' in filename_lower:
        if 'top' in filename_lower:
            purpose = "Top silkscreen layer"
            category = "silkscreen"
        elif 'bot' in filename_lower or 'bottom' in filename_lower:
            purpose = "Bottom silkscreen layer"
            category = "silkscreen"
        else:
            purpose = "Silkscreen layer"
            category = "silkscreen"
        
        manufacturing_function = "Defines component labels, reference designators, and markings printed on PCB"
        manufacturing_processes = ["Screen printing", "Ink application"]
        key_characteristics = ["Component labels", "Reference designators", "Text markings", "Logo/Graphics"]
    
    # Solder paste
    elif 'paste' in filename_lower:
        if 'top' in filename_lower:
            purpose = "Top solder paste stencil layer"
            category = "paste"
        else:
            purpose = "Solder paste stencil layer"
            category = "paste"
        
        manufacturing_function = "Defines solder paste application areas for SMT component assembly"
        manufacturing_processes = ["Stencil fabrication", "Solder paste printing", "SMT assembly"]
        key_characteristics = ["SMT pad openings", "Paste volume control"]
    
    # Routing/Outline
    elif 'routing' in filename_lower or 'outline' in file_type.lower():
        purpose = "Board outline and routing layer"
        category = "outline"
        manufacturing_function = "Defines the physical board outline and cutout areas"
        manufacturing_processes = ["PCB routing", "V-scoring", "Panelization"]
        key_characteristics = ["Board outline", "Cutouts", "V-score lines", "Panel borders"]
    
    # Plating
    elif 'plating' in filename_lower:
        purpose = "Plating layer"
        category = "plating"
        manufacturing_function = "Defines areas requiring special plating treatment"
        manufacturing_processes = ["Electroplating", "Surface finish application"]
        key_characteristics = ["Plated areas", "Surface finish zones"]
    
    # Drill files
    elif 'drill' in filename_lower or 'exc' in filename_lower:
        if 'plated' in filename_lower or 'pth' in filename_lower:
            purpose = "Plated through-hole drill file"
            category = "drill"
            manufacturing_function = "Defines locations and sizes of plated through-holes (vias and component holes)"
            manufacturing_processes = ["Drilling", "Plating", "Via formation"]
        elif 'np' in filename_lower or 'non' in filename_lower:
            purpose = "Non-plated through-hole drill file"
            category = "drill"
            manufacturing_function = "Defines locations and sizes of non-plated holes (mounting holes, etc.)"
            manufacturing_processes = ["Drilling"]
        else:
            purpose = "Drill file"
            category = "drill"
            manufacturing_function = "Defines hole locations and sizes"
            manufacturing_processes = ["Drilling"]
        
        key_characteristics = ["Hole coordinates", "Hole diameters", "Tool definitions"]
    
    # Analyze content for additional characteristics
    if '%ADD' in content_sample:
        aperture_count = content_sample.count('%ADD')
        key_characteristics.append(f"{aperture_count} aperture definitions")
    
    if 'D01' in content_sample or 'D02' in content_sample:
        draw_count = content_sample.count('D01') + content_sample.count('D02')
        key_characteristics.append(f"{draw_count} draw commands (sample)")
    
    if 'D03' in content_sample:
        flash_count = content_sample.count('D03')
        key_characteristics.append(f"{flash_count} flash commands (pads)")
    
    return {
        "layer_purpose": purpose,
        "manufacturing_function": manufacturing_function,
        "key_characteristics": key_characteristics,
        "manufacturing_processes": manufacturing_processes,
        "file_category": category,
        "notable_features": f"RS-274X format, {len(content_sample)} characters analyzed"
    }


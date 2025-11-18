#!/usr/bin/env python3
"""Generate detailed file-by-file analysis report."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agents.cam_gerber_analyzer.database import CamGerberDatabase
from agents.cam_gerber_analyzer.tools.analyze_gerber_file_details import analyze_gerber_file_with_llm
from agents.cam_gerber_analyzer.tools.parse_drill_file import parse_drill_file

def main():
    analysis_id = 18
    
    db = CamGerberDatabase()
    files = db.get_design_files(analysis_id)
    
    print('=' * 80)
    print('DETAILED FILE-BY-FILE ANALYSIS')
    print('=' * 80)
    print()
    
    all_analyses = []
    
    for df in files:
        print(f'Analyzing: {df.filename}...', end=' ', flush=True)
        
        if df.file_format == "gerber":
            analysis = analyze_gerber_file_with_llm(df.file_path, df.filename, df.file_type)
            if analysis.get('success'):
                all_analyses.append(analysis)
                print('✓')
            else:
                print(f'✗ {analysis.get("error")}')
        elif df.file_format == "drill":
            drill_data = parse_drill_file(df.file_path)
            if drill_data.get('success'):
                all_analyses.append({
                    'filename': df.filename,
                    'file_type': df.file_type,
                    'file_size_kb': round(df.file_size / 1024, 2),
                    'format': 'Excellon',
                    'drill_data': drill_data,
                    'purpose': f'Drill file defining hole locations and sizes for {df.file_type}'
                })
                print('✓')
            else:
                print(f'✗ {drill_data.get("error")}')
    
    print()
    print('=' * 80)
    print('COMPREHENSIVE FILE ANALYSIS RESULTS')
    print('=' * 80)
    print()
    
    # Group files by category
    categories = {
        'Copper Layers': [],
        'Solder Mask': [],
        'Silkscreen': [],
        'Drill Files': [],
        'Other': []
    }
    
    for analysis in all_analyses:
        filename = analysis.get('filename', 'Unknown')
        file_type = analysis.get('file_type', 'Unknown')
        size_kb = analysis.get('file_size_kb', 0)
        
        # Categorize
        if 'elec' in filename.lower() or 'inner_layer' in file_type:
            category = 'Copper Layers'
        elif 'stop' in filename.lower() or 'mask' in file_type.lower():
            category = 'Solder Mask'
        elif 'silk' in filename.lower():
            category = 'Silkscreen'
        elif 'drill' in filename.lower() or 'exc' in filename.lower():
            category = 'Drill Files'
        else:
            category = 'Other'
        
        categories[category].append(analysis)
    
    # Print by category
    for category, files_list in categories.items():
        if files_list:
            print(f'\n📁 {category.upper()}')
            print('-' * 80)
            
            for analysis in files_list:
                filename = analysis.get('filename', 'Unknown')
                file_type = analysis.get('file_type', 'Unknown')
                size_kb = analysis.get('file_size_kb', 0)
                
                print(f'\n📄 {filename}')
                print(f'   Type: {file_type}')
                print(f'   Size: {size_kb:.2f} KB')
                
                # LLM Analysis
                if 'llm_analysis' in analysis:
                    llm = analysis.get('llm_analysis', {})
                    if llm and not llm.get('error'):
                        purpose = llm.get('layer_purpose', 'N/A')
                        function = llm.get('manufacturing_function', 'N/A')
                        category_name = llm.get('file_category', 'N/A')
                        
                        print(f'   Purpose: {purpose}')
                        print(f'   Manufacturing Function: {function}')
                        print(f'   Category: {category_name}')
                        
                        characteristics = llm.get('key_characteristics', [])
                        if characteristics:
                            print(f'   Key Characteristics:')
                            for char in characteristics[:5]:
                                print(f'     • {char}')
                        
                        processes = llm.get('manufacturing_processes', [])
                        if processes:
                            print(f'   Used In: {", ".join(processes[:3])}')
                
                # Drill Data
                if 'drill_data' in analysis:
                    drill = analysis.get('drill_data', {})
                    print(f'   Purpose: Drill file - defines hole locations and sizes')
                    print(f'   Total Holes: {drill.get("total_holes", 0)}')
                    print(f'   Drill Tools: {drill.get("tools_count", 0)}')
                    print(f'   Hole Size Range: {drill.get("min_hole_size_mm", 0):.3f}mm - {drill.get("max_hole_size_mm", 0):.3f}mm')
                    hole_sizes = drill.get('hole_sizes_mm', [])
                    if hole_sizes:
                        sizes_str = ', '.join([f'{s:.3f}mm' for s in hole_sizes])
                        print(f'   Hole Sizes: {sizes_str}')
                
                # File Statistics
                if 'aperture_definitions' in analysis:
                    print(f'   Aperture Definitions: {analysis.get("aperture_definitions", 0)}')
                if 'draw_commands_sample' in analysis:
                    print(f'   Draw Commands (sample): {analysis.get("draw_commands_sample", 0)}')
                if 'format' in analysis:
                    print(f'   Format: {analysis.get("format")}')
                if 'units' in analysis:
                    print(f'   Units: {analysis.get("units")}')
                if 'total_lines' in analysis:
                    print(f'   Total Lines: {analysis.get("total_lines", 0):,}')
    
    # Save detailed analysis
    report_dir = 'data/cam_gerber_analyzer/reports'
    os.makedirs(report_dir, exist_ok=True)
    detailed_file = os.path.join(report_dir, 'analysis_18_file_details.json')
    with open(detailed_file, 'w') as f:
        json.dump(all_analyses, f, indent=2)
    
    print()
    print('=' * 80)
    print(f'✅ Detailed file analysis saved to: {detailed_file}')
    print('=' * 80)

if __name__ == '__main__':
    main()


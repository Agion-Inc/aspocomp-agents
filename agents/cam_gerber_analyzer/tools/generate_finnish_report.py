"""Generate Finnish language report with specific PCB specifications."""

import os
from typing import Dict, Any
from ..database import CamGerberDatabase


def generate_finnish_report(analysis_id: int) -> Dict[str, Any]:
    """Generate Finnish report answering specific questions.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary with report path and content
    """
    try:
        from .generate_design_summary import generate_design_summary
        from .extract_design_rules import analyze_all_layers_for_design_rules
        from .parse_drill_file import parse_drill_file
        
        db = CamGerberDatabase()
        analysis = db.get_analysis(analysis_id)
        design_files = db.get_design_files(analysis_id)
        result = db.get_analysis_result(analysis_id)
        
        # Get summary
        summary_result = generate_design_summary(analysis_id)
        summary = summary_result.get('summary', {}) if summary_result.get('success') else {}
        
        # Get layer count
        layer_count = result.layer_count or summary.get('layer_count', 'N/A')
        
        # Get design rules
        design_rules = analyze_all_layers_for_design_rules(analysis_id)
        
        # Get drill statistics
        drill_stats = summary.get('drill_statistics', {})
        total_holes = sum(s.get('total_holes', 0) for s in drill_stats.values())
        
        # Generate Finnish report
        report_html = f"""<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PCB Analyysiraportti - Analysis {analysis_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.2em;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding: 15px;
            background: #ecf0f1;
            border-left: 5px solid #3498db;
            border-radius: 5px;
            font-size: 1.5em;
        }}
        .answer-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .answer-box .question {{
            font-size: 1.1em;
            margin-bottom: 15px;
            opacity: 0.9;
        }}
        .answer-box .answer {{
            font-size: 2em;
            font-weight: bold;
            margin-top: 10px;
        }}
        .answer-box .unit {{
            font-size: 0.6em;
            opacity: 0.8;
        }}
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        .details-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        .details-table td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        .details-table tr:hover {{
            background: #f8f9fa;
        }}
        .info-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .info-section h3 {{
            color: #555;
            margin-bottom: 15px;
        }}
        .info-section p {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 PCB Analyysiraportti</h1>
        
        <div style="margin-bottom: 30px;">
            <p><strong>Analyysi ID:</strong> {analysis_id}</p>
            <p><strong>Projekti:</strong> {analysis.project_name or 'N/A'}</p>
            <p><strong>Piirilevy:</strong> {analysis.board_name or 'N/A'}</p>
            <p><strong>Luotu:</strong> {analysis.created_at}</p>
        </div>
        
        <h2>1. Kuinka monta kerrosta?</h2>
        <div class="answer-box">
            <div class="question">Kerrosten määrä:</div>
            <div class="answer">{layer_count} <span class="unit">kerrosta</span></div>
        </div>
        
        <div class="info-section">
            <h3>Kerrosrakenne:</h3>
"""
        
        # Add layer breakdown
        inner_layers = sum(1 for df in design_files if "inner_layer" in df.file_type)
        if inner_layers > 0:
            report_html += f"            <p>• <strong>Yläkerros:</strong> Yläsivu (Top Layer)</p>\n"
            for i in range(1, inner_layers + 1):
                report_html += f"            <p>• <strong>Sisäkerros {i}:</strong> {i}. sisäkerros</p>\n"
            report_html += f"            <p>• <strong>Alakerros:</strong> Alasivu (Bottom Layer)</p>\n"
            report_html += f"            <p><strong>Yhteensä:</strong> {layer_count} kerrosta (ylä + {inner_layers} sisäkerrosta + ala)</p>\n"
        
        report_html += """
        </div>
        
        <h2>2. Minimi eristeväli, johdinleveys ja kaulus</h2>
"""
        
        if design_rules.get('success'):
            min_trace = design_rules.get('min_trace_width_mm')
            min_spacing = design_rules.get('min_spacing_mm')
            min_annular = design_rules.get('min_annular_ring_mm')
            
            report_html += f"""
        <div class="answer-box">
            <div class="question">Minimi johdinleveys:</div>
            <div class="answer">{min_trace if min_trace else 'N/A'} <span class="unit">mm</span></div>
        </div>
        
        <div class="answer-box">
            <div class="question">Minimi eristeväli:</div>
            <div class="answer">{min_spacing if min_spacing else 'N/A'} <span class="unit">mm</span></div>
        </div>
        
        <div class="answer-box">
            <div class="question">Minimi kaulus:</div>
            <div class="answer">{min_annular if min_annular else 'N/A'} <span class="unit">mm</span></div>
        </div>
        
        <div class="info-section">
            <h3>Mittausyksityiskohdat:</h3>
"""
            
            layer_results = design_rules.get('layer_results', {})
            if layer_results:
                report_html += """
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Kerros</th>
                        <th>Johdinleveys (mm)</th>
                        <th>Eristeväli (mm)</th>
                        <th>Kaulus (mm)</th>
                    </tr>
                </thead>
                <tbody>
"""
                for layer_name, layer_data in layer_results.items():
                    trace = layer_data.get('trace_width_mm', 'N/A')
                    spacing = layer_data.get('min_spacing_mm', 'N/A')
                    annular = layer_data.get('annular_ring_mm', 'N/A')
                    report_html += f"""
                    <tr>
                        <td>{layer_name}</td>
                        <td>{trace if trace else 'N/A'}</td>
                        <td>{spacing if spacing else 'N/A'}</td>
                        <td>{annular if annular else 'N/A'}</td>
                    </tr>
"""
                report_html += """
                </tbody>
            </table>
"""
        else:
            report_html += """
        <div class="info-section">
            <p><strong>Huomio:</strong> Tarkat mitat vaativat täydellisen Gerber-tiedostojen analyysin. 
            Perusanalyysi suoritettu, mutta tarkat minimimitat voivat vaatia syvempää analyysiä.</p>
        </div>
"""
        
        report_html += f"""
        </div>
        
        <h2>3. Porauksien määrä</h2>
        <div class="answer-box">
            <div class="question">Porauksien kokonaismäärä:</div>
            <div class="answer">{total_holes} <span class="unit">poraa</span></div>
        </div>
        
        <div class="info-section">
            <h3>Porausyksityiskohdat:</h3>
            <table class="details-table">
                <thead>
                    <tr>
                        <th>Porausaineisto</th>
                        <th>Porauksia</th>
                        <th>Porauskoko (mm)</th>
                        <th>Työkaluja</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for drill_type, stats in drill_stats.items():
            holes = stats.get('total_holes', 0)
            tools = stats.get('tools_count', 0)
            min_size = stats.get('min_hole_size_mm', 0)
            max_size = stats.get('max_hole_size_mm', 0)
            sizes = stats.get('hole_sizes_mm', [])
            
            type_name = "Platoidut reiät" if "Plated" in drill_type else "Ei-platoidut reiät" if "NP" in drill_type else drill_type
            
            sizes_str = ', '.join([f'{s:.3f}' for s in sizes[:5]])
            if len(sizes) > 5:
                sizes_str += f' ... (+{len(sizes)-5} muuta)'
            
            report_html += f"""
                    <tr>
                        <td>{type_name}</td>
                        <td><strong>{holes}</strong></td>
                        <td>{min_size:.3f} - {max_size:.3f} ({sizes_str})</td>
                        <td>{tools}</td>
                    </tr>
"""
        
        report_html += f"""
                </tbody>
            </table>
            
            <h3 style="margin-top: 20px;">Yhteenveto:</h3>
            <p>• <strong>Platoidut reiät:</strong> {sum(s.get('total_holes', 0) for s in drill_stats.values() if 'Plated' in str(s))} kpl</p>
            <p>• <strong>Ei-platoidut reiät:</strong> {sum(s.get('total_holes', 0) for s in drill_stats.values() if 'NP' in str(s))} kpl</p>
            <p>• <strong>Kokonaismäärä:</strong> {total_holes} poraa</p>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #ecf0f1; border-radius: 5px;">
            <h3>Lisätietoja:</h3>
            <p><strong>Piirilevyn koko:</strong> {result.board_width or summary.get('board_width', 'N/A')}mm × {result.board_height or summary.get('board_height', 'N/A')}mm</p>
            <p><strong>Analysoituja tiedostoja:</strong> {len(design_files)} kpl</p>
            <p><strong>Tiedostojen kokonaiskoko:</strong> {summary.get('total_size_mb', 0):.2f} MB</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save report
        report_dir = os.path.join(
            os.path.dirname(__file__),
            '../../../data/cam_gerber_analyzer/reports'
        )
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f'analysis_{analysis_id}_finnish.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return {
            "success": True,
            "report_path": report_path,
            "report_url": f"/reports/analysis_{analysis_id}_finnish.html",
            "answers": {
                "layer_count": layer_count,
                "min_trace_width_mm": design_rules.get('min_trace_width_mm') if design_rules.get('success') else None,
                "min_spacing_mm": design_rules.get('min_spacing_mm') if design_rules.get('success') else None,
                "min_annular_ring_mm": design_rules.get('min_annular_ring_mm') if design_rules.get('success') else None,
                "total_holes": total_holes
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate Finnish report: {str(e)}"
        }


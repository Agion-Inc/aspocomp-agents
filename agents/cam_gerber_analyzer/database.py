"""Database operations for CAM Gerber Analyzer Agent."""

import sqlite3
import os
import json
from typing import List, Optional
from datetime import datetime
from .models import Analysis, DesignFile, AnalysisResult, AnalysisIssue


class CamGerberDatabase:
    """Database operations for CAM Gerber Analyzer."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database. If None, uses default development path.
        """
        if db_path is None:
            # Default to development database
            data_dir = os.path.join(
                os.path.dirname(__file__),
                '../../data/cam_gerber_analyzer'
            )
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'analyses.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                project_name TEXT,
                board_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                report_path TEXT,
                metadata_json TEXT
            )
        ''')
        
        # Design files table (Gerber and ODB++)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS design_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_format TEXT NOT NULL,
                file_type TEXT NOT NULL,
                layer_number INTEGER,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        ''')
        
        # Analysis issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                issue_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                layer_name TEXT,
                location_x REAL,
                location_y REAL,
                description TEXT NOT NULL,
                recommendation TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        ''')
        
        # Analysis results summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL UNIQUE,
                board_width REAL,
                board_height REAL,
                board_thickness REAL,
                panel_count INTEGER DEFAULT 1,
                boards_per_panel INTEGER DEFAULT 1,
                total_boards INTEGER DEFAULT 1,
                is_panelized BOOLEAN DEFAULT 0,
                layer_count INTEGER,
                inner_layer_count INTEGER DEFAULT 0,
                laminate_type TEXT,
                prepreg_spec TEXT,
                copper_weights TEXT,
                surface_finish TEXT,
                total_vias INTEGER,
                total_pads INTEGER,
                via_types TEXT,
                min_trace_width REAL,
                min_spacing REAL,
                min_drill_size REAL,
                copper_area_percentage REAL,
                issues_critical INTEGER DEFAULT 0,
                issues_warning INTEGER DEFAULT 0,
                issues_info INTEGER DEFAULT 0,
                analysis_completed_at TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analyses_user_id 
            ON analyses(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analyses_status 
            ON analyses(status)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_design_files_analysis_id 
            ON design_files(analysis_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_issues_analysis_id 
            ON analysis_issues(analysis_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_analysis(self, user_id: str, project_name: str = None, board_name: str = None) -> int:
        """Create a new analysis session.
        
        Args:
            user_id: User identifier
            project_name: Project name (optional)
            board_name: Board name (optional)
            
        Returns:
            Analysis ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses (user_id, project_name, board_name, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_id, project_name, board_name))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis object or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return Analysis.from_dict(dict(row))
    
    def update_analysis_status(self, analysis_id: int, status: str, report_path: str = None, metadata: dict = None):
        """Update analysis status.
        
        Args:
            analysis_id: Analysis ID
            status: New status
            report_path: Path to report file (optional)
            metadata: Metadata dictionary (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            UPDATE analyses 
            SET status = ?, report_path = ?, metadata_json = ?
            WHERE id = ?
        ''', (status, report_path, metadata_json, analysis_id))
        
        conn.commit()
        conn.close()
    
    def save_design_file(self, design_file: DesignFile) -> int:
        """Save design file record.
        
        Args:
            design_file: DesignFile object
            
        Returns:
            File ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO design_files 
            (analysis_id, filename, file_format, file_type, layer_number, file_path, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            design_file.analysis_id,
            design_file.filename,
            design_file.file_format,
            design_file.file_type,
            design_file.layer_number,
            design_file.file_path,
            design_file.file_size
        ))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_design_files(self, analysis_id: int) -> List[DesignFile]:
        """Get design files for an analysis.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            List of DesignFile objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM design_files WHERE analysis_id = ?', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [DesignFile.from_dict(dict(row)) for row in rows]
    
    def save_analysis_result(self, result: AnalysisResult) -> int:
        """Save analysis result.
        
        Args:
            result: AnalysisResult object
            
        Returns:
            Result ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if result exists
        cursor.execute('SELECT id FROM analysis_results WHERE analysis_id = ?', (result.analysis_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute('''
                UPDATE analysis_results SET
                    board_width = ?, board_height = ?, board_thickness = ?,
                    panel_count = ?, boards_per_panel = ?, total_boards = ?, is_panelized = ?,
                    layer_count = ?, inner_layer_count = ?,
                    laminate_type = ?, prepreg_spec = ?, copper_weights = ?, surface_finish = ?,
                    total_vias = ?, total_pads = ?, via_types = ?,
                    min_trace_width = ?, min_spacing = ?, min_drill_size = ?,
                    copper_area_percentage = ?,
                    issues_critical = ?, issues_warning = ?, issues_info = ?,
                    analysis_completed_at = CURRENT_TIMESTAMP
                WHERE analysis_id = ?
            ''', (
                result.board_width, result.board_height, result.board_thickness,
                result.panel_count, result.boards_per_panel, result.total_boards, 1 if result.is_panelized else 0,
                result.layer_count, result.inner_layer_count,
                result.laminate_type, result.prepreg_spec, result.copper_weights, result.surface_finish,
                result.total_vias, result.total_pads, result.via_types,
                result.min_trace_width, result.min_spacing, result.min_drill_size,
                result.copper_area_percentage,
                result.issues_critical, result.issues_warning, result.issues_info,
                result.analysis_id
            ))
            result_id = existing[0]
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO analysis_results 
                (analysis_id, board_width, board_height, board_thickness,
                 panel_count, boards_per_panel, total_boards, is_panelized,
                 layer_count, inner_layer_count,
                 laminate_type, prepreg_spec, copper_weights, surface_finish,
                 total_vias, total_pads, via_types,
                 min_trace_width, min_spacing, min_drill_size,
                 copper_area_percentage,
                 issues_critical, issues_warning, issues_info,
                 analysis_completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                result.analysis_id, result.board_width, result.board_height, result.board_thickness,
                result.panel_count, result.boards_per_panel, result.total_boards, 1 if result.is_panelized else 0,
                result.layer_count, result.inner_layer_count,
                result.laminate_type, result.prepreg_spec, result.copper_weights, result.surface_finish,
                result.total_vias, result.total_pads, result.via_types,
                result.min_trace_width, result.min_spacing, result.min_drill_size,
                result.copper_area_percentage,
                result.issues_critical, result.issues_warning, result.issues_info
            ))
            result_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return result_id
    
    def get_analysis_result(self, analysis_id: int) -> Optional[AnalysisResult]:
        """Get analysis result.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            AnalysisResult object or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analysis_results WHERE analysis_id = ?', (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        data = dict(row)
        data['is_panelized'] = bool(data['is_panelized'])
        return AnalysisResult.from_dict(data)
    
    def save_analysis_issue(self, issue: AnalysisIssue) -> int:
        """Save analysis issue.
        
        Args:
            issue: AnalysisIssue object
            
        Returns:
            Issue ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_issues 
            (analysis_id, issue_type, severity, layer_name, location_x, location_y, description, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            issue.analysis_id,
            issue.issue_type,
            issue.severity,
            issue.layer_name,
            issue.location_x,
            issue.location_y,
            issue.description,
            issue.recommendation
        ))
        
        issue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return issue_id
    
    def get_analysis_issues(self, analysis_id: int) -> List[AnalysisIssue]:
        """Get analysis issues.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            List of AnalysisIssue objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analysis_issues WHERE analysis_id = ? ORDER BY severity DESC, id ASC', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [AnalysisIssue.from_dict(dict(row)) for row in rows]


"""Data models for CAM Gerber Analyzer Agent."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Analysis:
    """Analysis session model."""
    id: Optional[int] = None
    user_id: str = ""
    project_name: Optional[str] = None
    board_name: Optional[str] = None
    created_at: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    report_path: Optional[str] = None
    metadata_json: Optional[str] = None
    
    def to_dict(self, include_personal: bool = True) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id if include_personal else None,
            "project_name": self.project_name,
            "board_name": self.board_name,
            "created_at": self.created_at,
            "status": self.status,
            "report_path": self.report_path,
            "metadata": self.metadata_json
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Analysis':
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", ""),
            project_name=data.get("project_name"),
            board_name=data.get("board_name"),
            created_at=data.get("created_at"),
            status=data.get("status", "pending"),
            report_path=data.get("report_path"),
            metadata_json=data.get("metadata_json")
        )


@dataclass
class DesignFile:
    """Design file model."""
    id: Optional[int] = None
    analysis_id: int = 0
    filename: str = ""
    file_format: str = ""  # gerber, odbp
    file_type: str = ""  # copper_top, copper_bottom, solder_mask_top, drill, odbp_archive, etc.
    layer_number: Optional[int] = None
    file_path: str = ""
    file_size: int = 0
    uploaded_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "filename": self.filename,
            "file_format": self.file_format,
            "file_type": self.file_type,
            "layer_number": self.layer_number,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignFile':
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            analysis_id=data.get("analysis_id", 0),
            filename=data.get("filename", ""),
            file_format=data.get("file_format", ""),
            file_type=data.get("file_type", ""),
            layer_number=data.get("layer_number"),
            file_path=data.get("file_path", ""),
            file_size=data.get("file_size", 0),
            uploaded_at=data.get("uploaded_at")
        )


@dataclass
class AnalysisResult:
    """Analysis result summary model."""
    id: Optional[int] = None
    analysis_id: int = 0
    # Board dimensions
    board_width: Optional[float] = None
    board_height: Optional[float] = None
    board_thickness: Optional[float] = None
    # Panel information
    panel_count: int = 1
    boards_per_panel: int = 1
    total_boards: int = 1
    is_panelized: bool = False
    # Layer information
    layer_count: Optional[int] = None
    inner_layer_count: int = 0
    # Material information
    laminate_type: Optional[str] = None
    prepreg_spec: Optional[str] = None
    copper_weights: Optional[str] = None  # JSON string
    surface_finish: Optional[str] = None
    # Design characteristics
    total_vias: Optional[int] = None
    total_pads: Optional[int] = None
    via_types: Optional[str] = None  # JSON string
    min_trace_width: Optional[float] = None
    min_spacing: Optional[float] = None
    min_drill_size: Optional[float] = None
    copper_area_percentage: Optional[float] = None
    # Analysis results
    issues_critical: int = 0
    issues_warning: int = 0
    issues_info: int = 0
    analysis_completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "board_width": self.board_width,
            "board_height": self.board_height,
            "board_thickness": self.board_thickness,
            "panel_count": self.panel_count,
            "boards_per_panel": self.boards_per_panel,
            "total_boards": self.total_boards,
            "is_panelized": self.is_panelized,
            "layer_count": self.layer_count,
            "inner_layer_count": self.inner_layer_count,
            "laminate_type": self.laminate_type,
            "prepreg_spec": self.prepreg_spec,
            "copper_weights": self.copper_weights,
            "surface_finish": self.surface_finish,
            "total_vias": self.total_vias,
            "total_pads": self.total_pads,
            "via_types": self.via_types,
            "min_trace_width": self.min_trace_width,
            "min_spacing": self.min_spacing,
            "min_drill_size": self.min_drill_size,
            "copper_area_percentage": self.copper_area_percentage,
            "issues_critical": self.issues_critical,
            "issues_warning": self.issues_warning,
            "issues_info": self.issues_info,
            "analysis_completed_at": self.analysis_completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            analysis_id=data.get("analysis_id", 0),
            board_width=data.get("board_width"),
            board_height=data.get("board_height"),
            board_thickness=data.get("board_thickness"),
            panel_count=data.get("panel_count", 1),
            boards_per_panel=data.get("boards_per_panel", 1),
            total_boards=data.get("total_boards", 1),
            is_panelized=bool(data.get("is_panelized", False)),
            layer_count=data.get("layer_count"),
            inner_layer_count=data.get("inner_layer_count", 0),
            laminate_type=data.get("laminate_type"),
            prepreg_spec=data.get("prepreg_spec"),
            copper_weights=data.get("copper_weights"),
            surface_finish=data.get("surface_finish"),
            total_vias=data.get("total_vias"),
            total_pads=data.get("total_pads"),
            via_types=data.get("via_types"),
            min_trace_width=data.get("min_trace_width"),
            min_spacing=data.get("min_spacing"),
            min_drill_size=data.get("min_drill_size"),
            copper_area_percentage=data.get("copper_area_percentage"),
            issues_critical=data.get("issues_critical", 0),
            issues_warning=data.get("issues_warning", 0),
            issues_info=data.get("issues_info", 0),
            analysis_completed_at=data.get("analysis_completed_at")
        )


@dataclass
class AnalysisIssue:
    """Analysis issue model."""
    id: Optional[int] = None
    analysis_id: int = 0
    issue_type: str = ""
    severity: str = ""  # critical, warning, info
    layer_name: Optional[str] = None
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    description: str = ""
    recommendation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "layer_name": self.layer_name,
            "location_x": self.location_x,
            "location_y": self.location_y,
            "description": self.description,
            "recommendation": self.recommendation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisIssue':
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            analysis_id=data.get("analysis_id", 0),
            issue_type=data.get("issue_type", ""),
            severity=data.get("severity", ""),
            layer_name=data.get("layer_name"),
            location_x=data.get("location_x"),
            location_y=data.get("location_y"),
            description=data.get("description", ""),
            recommendation=data.get("recommendation")
        )


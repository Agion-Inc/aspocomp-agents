# CAM Gerber Analyzer Agent

## Overview

The CAM Gerber Analyzer Agent automatically performs CAM (Computer-Aided Manufacturing) analysis based on Gerber files and ODB++ format files. This agent helps Aspocomp's manufacturing team by automating the analysis of PCB design files, identifying potential manufacturing issues, and generating comprehensive CAM analysis reports.

The agent supports both **Gerber** (RS-274X) and **ODB++** formats, providing comprehensive PCB design summary and analysis regardless of the input format.

## Status

**Status**: Planned - Phase 3  
**Priority**: Medium  
**Agent ID**: `cam_gerber_analyzer`

## Goals

- **Primary Goal**: Generate comprehensive PCB design summary and analysis from Gerber and ODB++ files
  - Extract and summarize key design characteristics (panels, materials, dimensions, layer count)
  - Provide quick overview of PCB specifications for manufacturing planning
  - Support both Gerber (RS-274X) and ODB++ formats
- Automate CAM analysis based on Gerber and ODB++ files
- Identify potential manufacturing issues early in the process
- Generate comprehensive CAM analysis reports
- Save time and effort for manufacturing engineers
- Provide actionable insights for PCB design optimization

## Functional Requirements

### 1. PCB Design Summary and Analysis (Primary Feature)
- **Design Overview Extraction**:
  - **Panel Information**: Detect and count number of panels/boards in the design
  - **Board Dimensions**: Extract board width, height, and thickness
  - **Layer Count**: Identify total number of layers (including inner layers)
  - **Material Specifications**: Extract or infer material information:
    - Laminate type (FR4, High Tg FR4, Halogen-free, etc.)
    - Prepreg specifications
    - Copper weights per layer
    - Surface finish requirements
  - **Panelization**: Detect if design contains multiple panels/boards
  - **Board Count**: Count individual boards in panelized design
- **Design Characteristics**:
  - Via types (through-hole, blind, buried)
  - Pad types and sizes
  - Trace characteristics (typical widths, spacing)
  - Component density
  - Copper distribution per layer
- **Manufacturing Specifications**:
  - Minimum feature sizes
  - Drill hole sizes and counts
  - Solder mask and silkscreen presence
  - Surface finish type (if specified)

### 2. File Processing (Gerber and ODB++)

#### 2.1 Gerber File Processing
- **File Upload**: Accept Gerber files (.gbr, .ger, .art) and related PCB files
- **File Parsing**: Parse RS-274X Extended Gerber format files
- **Multi-Layer Support**: Process multiple Gerber files representing different PCB layers:
  - Copper layers (top, bottom, inner layers)
  - Solder mask layers
  - Silkscreen layers
  - Drill files (NC Drill, Excellon format)
  - Paste stencil layers
  - Panel/array files (if present)
- **File Validation**: Validate file format and completeness
- **Metadata Extraction**: Extract PCB specifications (board size, layer count, etc.)
- **Panel Detection**: Identify panelization patterns and count individual boards

#### 2.2 ODB++ File Processing
- **File Upload**: Accept ODB++ archive files (.tgz, .zip, .tar.gz) or ODB++ directory structures
- **File Parsing**: Parse ODB++ format files using PyOdbDesignLib or similar library
- **Comprehensive Data Access**: ODB++ provides structured access to:
  - Layer definitions and stackup information
  - Netlist and connectivity data
  - Component placement and orientation
  - Drill data and via information
  - Panelization data
  - Material specifications (often more detailed than Gerber)
  - Design rules and constraints
- **Advantages of ODB++**:
  - More structured format with better metadata
  - Often includes material specifications directly
  - Better panelization information
  - Netlist information for design verification
  - Component data for assembly planning
- **File Validation**: Validate ODB++ archive structure and required files
- **Metadata Extraction**: Extract comprehensive PCB specifications from ODB++ structure
- **Panel Detection**: Use ODB++ panelization data when available

#### 2.3 Format Detection and Routing
- **Automatic Format Detection**: Detect file format (Gerber vs ODB++) automatically
- **Unified Processing Pipeline**: Process both formats through unified analysis pipeline
- **Format-Specific Parsers**: Use appropriate parser based on detected format
- **Cross-Format Compatibility**: Ensure design summary output is consistent regardless of input format

### 3. CAM Analysis Capabilities
- **Design Rule Checks (DRC)**:
  - Minimum trace width verification
  - Minimum spacing between traces
  - Annular ring checks for vias and pads
  - Solder mask clearance verification
  - Silkscreen clearance checks
- **Manufacturing Feasibility**:
  - Detect features that may be difficult to manufacture
  - Identify potential etching issues
  - Check drill hole sizes and aspect ratios
  - Verify via-in-pad capabilities
- **Layer Alignment**:
  - Verify alignment between layers
  - Check registration marks
  - Detect layer-to-layer misalignment issues
- **Copper Analysis**:
  - Calculate copper area per layer
  - Identify copper balance issues
  - Detect potential warpage risks
- **Drill Analysis**:
  - Verify drill hole sizes
  - Check drill-to-copper clearance
  - Identify blind/buried via structures
- **Solder Mask Analysis**:
  - Verify solder mask openings
  - Check solder mask coverage
  - Identify potential solder bridging risks

### 4. Report Generation
- **Comprehensive Reports**: Generate detailed CAM analysis reports
- **Issue Categorization**: Categorize issues by severity (critical, warning, info)
- **Visual Annotations**: Provide visual representations of issues
- **Recommendations**: Suggest design improvements
- **Export Formats**: Support PDF, HTML, and JSON report formats

### 5. Integration Capabilities
- **File Storage**: Store uploaded Gerber files securely
- **Analysis History**: Maintain history of analyses
- **Comparison**: Compare analysis results over time
- **Workflow Integration**: Integrate with manufacturing workflow systems

## Technical Architecture

### API Endpoint

**Endpoint**: `/api/chat/cam_gerber_analyzer`

**Request Format**:
```json
{
    "message": "string",
    "conversation_id": "string (optional)",
    "context": {
        "user_id": "string",
        "department": "string",
        "role": "string"
    },
    "files": [
        {
            "filename": "string",
            "content": "base64_encoded_file_content",
            "file_type": "gerber|odbp|drill|other"
        }
    ]
}
```

**Response Format**:
```json
{
    "success": true,
    "response": "string",
    "agent_id": "cam_gerber_analyzer",
    "conversation_id": "string",
    "function_calls": [],
    "metadata": {
        "analysis_id": "string",
        "issues_found": 0,
        "report_url": "string"
    }
}
```

### Database Structure

**Development**: `data/cam_gerber_analyzer/analyses.db` (SQLite)  
**Production**: SharePoint list/database

#### Data Model Schema

```sql
-- Analysis sessions table
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    project_name TEXT,
    board_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    report_path TEXT,
    metadata_json TEXT  -- JSON with board specs, layer info, etc.
);

-- PCB design files table (Gerber and ODB++)
CREATE TABLE design_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_format TEXT NOT NULL,  -- gerber, odbp
    file_type TEXT NOT NULL,  -- copper_top, copper_bottom, solder_mask_top, drill, odbp_archive, etc.
    layer_number INTEGER,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

-- Analysis issues table
CREATE TABLE analysis_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    issue_type TEXT NOT NULL,  -- trace_width, spacing, annular_ring, etc.
    severity TEXT NOT NULL,  -- critical, warning, info
    layer_name TEXT,
    location_x REAL,
    location_y REAL,
    description TEXT NOT NULL,
    recommendation TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

-- Analysis results summary
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL UNIQUE,
    -- Board dimensions
    board_width REAL,
    board_height REAL,
    board_thickness REAL,
    -- Panel information
    panel_count INTEGER DEFAULT 1,
    boards_per_panel INTEGER DEFAULT 1,
    total_boards INTEGER DEFAULT 1,
    is_panelized BOOLEAN DEFAULT FALSE,
    -- Layer information
    layer_count INTEGER,
    inner_layer_count INTEGER DEFAULT 0,
    -- Material information
    laminate_type TEXT,  -- FR4, High Tg FR4, Halogen-free, etc.
    prepreg_spec TEXT,
    copper_weights TEXT,  -- JSON: {"top": "1oz", "inner": "0.5oz", "bottom": "1oz"}
    surface_finish TEXT,  -- HASL, ENIG, OSP, etc.
    -- Design characteristics
    total_vias INTEGER,
    total_pads INTEGER,
    via_types TEXT,  -- JSON: {"through": 100, "blind": 20, "buried": 10}
    min_trace_width REAL,
    min_spacing REAL,
    min_drill_size REAL,
    copper_area_percentage REAL,
    -- Analysis results
    issues_critical INTEGER DEFAULT 0,
    issues_warning INTEGER DEFAULT 0,
    issues_info INTEGER DEFAULT 0,
    analysis_completed_at TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
```

### Agent Tools/Functions

The agent has access to the following tools:

1. **`upload_design_files`**: Upload and store Gerber or ODB++ files for analysis
   - Parameters: files (list of file objects), project_name, board_name
   - Returns: analysis_id
   - Supports: Gerber files (.gbr, .ger, .art) and ODB++ archives (.tgz, .zip, .tar.gz)

2. **`detect_file_format`**: Automatically detect file format (Gerber vs ODB++)
   - Parameters: file_path or file content
   - Returns: format_type ("gerber" or "odbp")

3. **`parse_gerber_file`**: Parse a Gerber file and extract layer information
   - Parameters: file_path, file_type
   - Returns: Parsed data (apertures, primitives, layer info)

4. **`parse_odbp_file`**: Parse an ODB++ archive and extract design information
   - Parameters: archive_path or directory_path
   - Returns: Parsed data (layers, stackup, netlist, components, materials, panelization)

5. **`generate_design_summary`**: Generate comprehensive PCB design summary (PRIMARY TOOL)
   - Parameters: analysis_id
   - Returns: Design summary including:
     - Panel count and board count
     - Board dimensions (width, height, thickness)
     - Layer count and structure
     - Material specifications (laminate, prepreg, copper weights, surface finish)
     - Design characteristics (vias, pads, traces, drill holes)
     - Manufacturing specifications

6. **`perform_cam_analysis`**: Perform comprehensive CAM analysis
   - Parameters: analysis_id, analysis_options
   - Returns: Analysis results with issues and recommendations
   - Works with both Gerber and ODB++ formats

7. **`get_analysis_report`**: Generate and retrieve analysis report
   - Parameters: analysis_id, report_format (pdf|html|json)
   - Returns: Report file path or content

8. **`get_analysis_history`**: Retrieve analysis history for a project
   - Parameters: project_name, limit
   - Returns: List of previous analyses

9. **`compare_analyses`**: Compare two analysis results
   - Parameters: analysis_id_1, analysis_id_2
   - Returns: Comparison report

### System Prompt

The agent uses a specialized system prompt that:
- Explains the agent's role in CAM analysis
- Guides users through file upload process (supports both Gerber and ODB++ formats)
- Instructs agent to use tools for analysis
- Provides context about Aspocomp manufacturing capabilities
- Emphasizes accuracy and actionable insights
- Explains advantages of ODB++ format when available (better material specs, panelization data)

## Implementation Plan

### Phase 1: Research and Setup (Current Phase)
- [x] Research Gerber file format specifications
- [x] Identify Python libraries for Gerber parsing
- [x] Design agent architecture
- [ ] Select and test Gerber parsing library
- [ ] Create proof-of-concept parser

### Phase 2: Core Infrastructure
- [ ] Create agent directory structure
- [ ] Implement base agent class
- [ ] Create database schema and initialization
- [ ] Implement file upload and storage
- [ ] Set up file parsing pipeline

### Phase 3: File Parsing Implementation

#### 3.1 Gerber Parsing
- [ ] Implement RS-274X parser using selected library (PyGerber or python-gerber)
- [ ] Parse copper layers (top, bottom, inner)
- [ ] Parse solder mask layers
- [ ] Parse silkscreen layers
- [ ] Parse drill files (NC Drill/Excellon)
- [ ] Extract PCB metadata (board size, layer count)
- [ ] **Implement panel detection algorithm** (detect multiple boards in panel)
- [ ] **Extract material information** (from file names, attributes, or user input)

#### 3.2 ODB++ Parsing
- [ ] Evaluate and select ODB++ parsing library (PyOdbDesignLib recommended)
- [ ] Implement ODB++ archive extraction (.tgz, .zip, .tar.gz)
- [ ] Parse ODB++ directory structure
- [ ] Extract layer definitions and stackup information
- [ ] Extract netlist and connectivity data
- [ ] Extract component placement data
- [ ] Extract drill data and via information
- [ ] Extract panelization data (often more accurate than Gerber)
- [ ] Extract material specifications (laminate, prepreg, copper weights, surface finish)
- [ ] Extract design rules and constraints

#### 3.3 Format Detection and Unified Interface
- [ ] Implement automatic format detection (Gerber vs ODB++)
- [ ] Create unified parsing interface for both formats
- [ ] Ensure consistent data structure output regardless of input format
- [ ] Handle format-specific edge cases

### Phase 4: Design Summary Generation (Priority)
- [ ] **Implement panel counting algorithm** (detect and count individual boards)
- [ ] **Extract board dimensions** (from Gerber coordinates)
- [ ] **Calculate layer count** (from file structure)
- [ ] **Extract/infer material specifications**:
  - Laminate type detection (from file names or attributes)
  - Copper weight extraction (from layer files)
  - Surface finish detection
- [ ] **Generate design characteristics summary**:
  - Via counting and classification
  - Pad counting
  - Trace width/spacing statistics
  - Drill hole analysis
- [ ] **Create formatted design summary report**

### Phase 5: CAM Analysis Algorithms
- [ ] Implement Design Rule Checks (DRC)
- [ ] Implement manufacturing feasibility checks
- [ ] Implement layer alignment verification
- [ ] Implement copper analysis
- [ ] Implement drill analysis
- [ ] Implement solder mask analysis

### Phase 6: Report Generation
- [ ] Design report templates
- [ ] Implement PDF report generation
- [ ] Implement HTML report generation
- [ ] Implement JSON report export
- [ ] Add visual annotations and diagrams

### Phase 7: Integration
- [ ] Integrate with web chat backend
- [ ] Add agent to agent registry
- [ ] Implement file upload UI
- [ ] Test end-to-end flow
- [ ] Implement analysis history

### Phase 8: Production Readiness
- [ ] SharePoint integration (production database)
- [ ] Performance optimization
- [ ] Error handling and validation
- [ ] Security review (file upload security)
- [ ] Documentation and testing
- [ ] User training materials

## Python Libraries for File Parsing

### Gerber Parsing Libraries

#### Recommended: PyGerber
- **Package**: `pygerber` (version 3.0.0a3+)
- **Pros**:
  - Comprehensive toolkit for Gerber X3 files
  - Supports modern Gerber standard features
  - Includes implementations for deprecated functionalities
  - Good documentation
- **Cons**:
  - May be in alpha/beta stage
  - Need to verify RS-274X support

#### Alternative: python-gerber
- **Package**: `python-gerber`
- **Pros**:
  - Pure Python implementation
  - Supports all Gerber commands including deprecated ones
  - Well-established library
- **Cons**:
  - May have limited modern Gerber X3 support

#### Alternative: pcb-tools
- **Package**: `pcb-tools` (includes gerber-reader)
- **Pros**:
  - Part of broader PCB tools ecosystem
  - May include additional PCB analysis tools
- **Cons**:
  - Need to verify current maintenance status

**Gerber Recommendation**: Start with **PyGerber** for modern Gerber support, with **python-gerber** as fallback for RS-274X compatibility.

### ODB++ Parsing Libraries

#### Recommended: PyOdbDesignLib
- **Package**: `PyOdbDesignLib` or `pyodbdesignlib`
- **Pros**:
  - Thin Python 3 wrapper for C++ OdbDesignLib
  - Designed specifically for parsing ODB++ Design archives
  - Supports construction of netlist product models
  - May include REST API server (Docker image available)
- **Cons**:
  - Requires C++ OdbDesignLib dependency
  - May need additional setup

#### Alternative: py3odb
- **Package**: `py3odb`
- **Pros**:
  - Python 3.6+ compatible
  - SQL-like interface for processing ODB data
- **Cons**:
  - Primarily focused on observational data (ECMWF ODB API)
  - May not be suitable for PCB design ODB++ format
  - Requires libOdb from ODB API

**ODB++ Recommendation**: Start with **PyOdbDesignLib** as it's specifically designed for PCB ODB++ format. Evaluate py3odb if PyOdbDesignLib doesn't meet requirements.

### Library Evaluation Plan
1. Test PyGerber and python-gerber with sample Gerber files
2. Test PyOdbDesignLib with sample ODB++ archives
3. Evaluate parsing accuracy and performance
4. Determine best library combination for production use

## File Structure

```
agents/cam_gerber_analyzer/
├── README.md
├── agent.py                 # Main agent implementation
├── config.py                # Agent configuration
├── database.py              # Database operations
├── models.py                # Data models/schemas
├── gerber_parser.py          # Gerber file parsing logic
├── odbp_parser.py            # ODB++ file parsing logic
├── format_detector.py        # Automatic format detection (Gerber vs ODB++)
├── design_summarizer.py     # PCB design summary generation (PRIMARY)
├── cam_analyzer.py          # CAM analysis algorithms
├── report_generator.py      # Report generation
├── prompts/
│   └── system_prompt.txt    # LLM system prompt
├── tools/
│   ├── __init__.py
│   ├── upload_design_files.py
│   ├── detect_file_format.py
│   ├── parse_gerber_file.py
│   ├── parse_odbp_file.py
│   ├── generate_design_summary.py  # PRIMARY TOOL
│   ├── perform_cam_analysis.py
│   ├── get_analysis_report.py
│   └── get_analysis_history.py
└── tests/
    ├── __init__.py
    ├── test_gerber_parser.py
    ├── test_odbp_parser.py
    ├── test_format_detector.py
    ├── test_cam_analyzer.py
    └── test_cam_gerber_analyzer.py

data/
└── cam_gerber_analyzer/
    ├── analyses.db          # SQLite database (development)
    └── uploads/             # Uploaded Gerber files storage
        └── [analysis_id]/
            └── [gerber_files]

web_chat/frontend/agents/cam_gerber_analyzer/
├── index.html               # Agent UI with file upload
├── css/
│   └── styles.css
└── js/
    ├── app.js
    └── api.js
```

## Configuration

```python
AGENT_CONFIG = {
    "agent_id": "cam_gerber_analyzer",
    "name": "CAM Gerber Analyzer",
    "description": "Automatically performs CAM analysis based on Gerber files",
    "enabled": True,
    "model": "gemini-2.5-flash",
    "temperature": 0.3,  # Lower temperature for technical accuracy
    "max_iterations": 5,
    "database_path": "data/cam_gerber_analyzer/analyses.db",  # Development
    "sharepoint_list": "CAMAnalyses",  # Production
    "upload_directory": "data/cam_gerber_analyzer/uploads",
    "max_file_size_mb": 200,  # Larger for ODB++ archives
    "supported_file_types": [
        # Gerber files
        ".gbr", ".ger", ".art", ".drill", ".txt",
        # ODB++ files
        ".tgz", ".zip", ".tar.gz", ".odb"
    ],
    "supported_formats": ["gerber", "odbp"],
    "tools": [
        "upload_design_files",
        "detect_file_format",
        "parse_gerber_file",
        "parse_odbp_file",
        "generate_design_summary",  # PRIMARY TOOL
        "perform_cam_analysis",
        "get_analysis_report",
        "get_analysis_history",
        "compare_analyses"
    ],
    "system_prompt_path": "agents/cam_gerber_analyzer/prompts/system_prompt.txt",
    "cam_rules": {
        "min_trace_width": 0.1,  # mm
        "min_spacing": 0.1,  # mm
        "min_annular_ring": 0.05,  # mm
        "min_drill_size": 0.15,  # mm
        "min_solder_mask_clearance": 0.05  # mm
    }
}
```

## Usage Examples

### Example 1: Generate PCB Design Summary (Primary Use Case)

**User**: "Analysoi tämän piirilevyn tiedostot ja anna yhteenveto"

**Agent**: "Hei! Autan sinua piirilevyn analyysissa. Lähetä gerber-tiedostot tai ODB++-arkisto minulle, niin luon kattavan yhteenvedon suunnittelusta. Tuen sekä Gerber- että ODB++-muotoja." [waits for files]

**User**: [Uploads ODB++ archive]

**Agent**: "Kiitos! Olen vastaanottanut ODB++-arkiston. Tunnistan muodon automaattisesti. Luon nyt piirilevyn yhteenvedon..." [detects format, analyzes files]

**Agent**: "ODB++-muoto tarjoaa usein tarkemmat materiaalitiedot kuin Gerber-tiedostot, joten analyysi voi olla kattavampi."

**Agent**: "## Piirilevyn Yhteenveto

### Perustiedot
- **Projektin nimi**: ABC-123
- **Piirilevyn koko**: 100mm × 80mm
- **Paksuus**: 1.6mm
- **Kerroksia**: 4 (2 sisäkerrosta)

### Panelointi
- **Paneleita**: 1
- **Piirilevyjä paneelissa**: 4
- **Yhteensä piirilevyjä**: 4

### Materiaalit
- **Laminaatti**: FR4 High Tg (Tg 170°C)
- **Prepreg**: 2116, 0.12mm
- **Kupari**: 
  - Ylempi/alempi: 1oz (35μm)
  - Sisäkerrokset: 0.5oz (17.5μm)
- **Pintakäsittely**: ENIG (Electroless Nickel Immersion Gold)

### Suunnittelun ominaisuudet
- **Via-reikiä**: 245 (läpiviat: 200, sokeat: 30, piilotetut: 15)
- **Padeja**: 1,234
- **Minimijohdon leveys**: 0.1mm
- **Minimiväli**: 0.1mm
- **Porausreikien koko**: 0.2mm - 2.0mm
- **Kuparialue**: 
  - Ylempi: 42%
  - Alempi: 38%
  - Sisäkerrokset: 15-20%

### Valmistusominaisuudet
- Juotosmaski: Kyllä (vihreä)
- Silkscreen: Kyllä (valkoinen)
- Solder paste: Kyllä (stencil-tiedosto löytyy)

Haluatko nähdä yksityiskohtaisen CAM-analyysin tai PDF-raportin?"

### Example 2: Upload and Analyze Gerber Files with CAM Analysis

**User**: "Haluan analysoida uuden piirilevyn gerber-tiedostoja ja tarkistaa valmistettavuuden"

**Agent**: "Hei! Autan sinua CAM-analyysin tekemisessä. Voit lähettää gerber-tiedostot minulle. Tarvitsen seuraavat tiedostot:
- Ylempi kuparikerros (top copper)
- Alempi kuparikerros (bottom copper)
- Ylempi juotosmaski (top solder mask)
- Alempi juotosmaski (bottom solder mask)
- Poraus-tiedosto (drill file)

Voit lähettää tiedostot yksi kerrallaan tai kaikki kerralla. Mikä on projektin nimi?"

**User**: [Uploads files]

**Agent**: "Kiitos! Olen vastaanottanut 5 tiedostoa. Luon ensin piirilevyn yhteenvedon ja sitten CAM-analyysin..." [performs analysis]

**Agent**: "## Piirilevyn Yhteenveto
- **Koko**: 100mm × 80mm, 4 kerrosta
- **Paneleita**: 1, **Piirilevyjä**: 4
- **Materiaalit**: FR4 High Tg, 1oz kupari, ENIG pintakäsittely
- **Via-reikiä**: 245, **Padeja**: 1,234

## CAM-Analyysi
- **Kriittisiä ongelmia**: 2
  - Minimijohdon leveys 0.08mm (vaatii: 0.1mm) - löytyi 3 kohtaa
  - Porausreikä liian lähellä kuparia - löytyi 1 kohta
  
- **Varoituksia**: 5
  - Kuparitasapaino: ylempi kerros 45%, alempi 35% (suositus: max 10% ero)
  - ...

Haluatko nähdä yksityiskohtaisen raportin PDF-muodossa?"

### Example 3: Check Analysis History

**User**: "Näytä edelliset analyysit projektille 'ABC-123'"

**Agent**: [searches history]

**Agent**: "Löysin 3 edellistä analyysia projektille 'ABC-123':
1. 2024-03-15 - 2 kriittistä ongelmaa, 5 varoitusta
2. 2024-03-10 - 0 kriittistä ongelmaa, 3 varoitusta
3. 2024-03-05 - 1 kriittinen ongelma, 7 varoitusta

Haluatko nähdä jonkin näistä analyyseistä tarkemmin?"

## Challenges and Solutions

### Challenge 1: Gerber File Format Complexity
**Solution**: Use established Python libraries (PyGerber or python-gerber) rather than building custom parser from scratch.

### Challenge 2: Multi-Layer Analysis
**Solution**: Implement layer-by-layer parsing and cross-layer analysis algorithms.

### Challenge 3: Performance with Large Files
**Solution**: 
- Implement streaming parsing for large files
- Cache parsed data in database
- Optimize analysis algorithms

### Challenge 4: File Upload Security
**Solution**:
- Validate file types and sizes
- Scan for malicious content
- Store files in secure, isolated directory
- Implement access control

### Challenge 5: Integration with Manufacturing Systems
**Solution**: Design API endpoints that can be integrated with existing manufacturing workflow systems (Wise, etc.)

## Privacy and Security

- **File Storage**: Gerber files stored securely with access control
- **Data Retention**: Define retention policy for analysis data
- **Access Control**: Only authorized users can upload and analyze files
- **GDPR Compliance**: Handle any personal data according to GDPR
- **Confidentiality**: Customer design files must be kept confidential

## Testing

### Unit Tests
- Test Gerber file parsing
- Test CAM analysis algorithms
- Test report generation
- Test database operations

### Integration Tests
- Test file upload flow
- Test end-to-end analysis pipeline
- Test API endpoints
- Test error handling

### Sample Files
- Use Ucamco sample CAD jobs for testing
- Create test cases with known issues
- Test with various Gerber file versions

## References

- **General Requirements**: `docs/agent_requirements.md`
- **Framework Architecture**: `docs/agents_framework.md`
- **Implementation Guide**: `.cursor/rules/implement_agent.mdc`
- **Agent List**: `docs/agent_list.md`
- **Gerber Format Specification**: https://www.ucamco.com/en/gerber/standard-gerber
- **PyGerber Library**: https://pypi.org/project/pygerber/
- **python-gerber Library**: https://pypi.org/project/python-gerber/

## Next Steps

1. **Library Selection**: Test PyGerber and python-gerber with sample Gerber files
2. **Proof of Concept**: Create basic parser that can read a simple Gerber file
3. **Architecture Review**: Review plan with team before full implementation
4. **Sample Files**: Obtain sample Gerber files from Aspocomp manufacturing team
5. **Requirements Refinement**: Gather detailed requirements from manufacturing engineers


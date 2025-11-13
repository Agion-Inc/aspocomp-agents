# Aspocomp AI Agents - Complete List

This document contains the complete list of AI agents planned for development in the Aspocomp agents framework. Agents are organized by category and prioritized based on feasibility and business value.

## Agent Categories

- **Sales & Trading** - Customer-facing agents for sales, quotations, and trading
- **Manufacturing & Production** - Agents supporting PCB manufacturing processes
- **Operations & Logistics** - Agents for warehouse management, logistics, and operations
- **Quality & Technical** - Agents for quality assurance, technical support, and design
- **Administrative** - Agents for internal processes and administration
- **Integration & Automation** - Agents for system integration and automation tasks

---

## Sales & Trading Agents

### 1. Sales Agent (RFQ & Quotations)
**Status**: Planned - Phase 2  
**Priority**: High  
**Description**: Handles RFQ (Request for Quotation) requests, provides product information, generates quotations, and guides customers through the sales process.

**Capabilities**:
- Process RFQ requests
- Provide product information and specifications
- Generate quotations based on PCB specifications
- Answer sales-related questions
- Guide customers through sales process

**Integration Points**:
- Product catalog
- Pricing system
- Customer relationship management (CRM)

**Documentation**: `docs/agents/sales.md`

---

### 2. Trading Offer Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Quickly generates trading offers with Chinese prices and correct freight costs. Handles trading summium calculations.

**Challenges**:
- Freight prices are currently unknown when making offers
- Weight of upcoming shipment (freight costs) is not known
- Requires access to InvoiceReady's line-item data (currently not possible)

**Required Resources**:
- Access to Chinese supplier pricing
- Freight cost data
- InvoiceReady line-item data access

**Next Steps**:
- Investigate InvoiceReady API access for line-item data
- Develop freight cost estimation system
- Create pricing integration with Chinese suppliers

---

### 3. Trading Supplier Delivery Reliability Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Collects and analyzes data on delivery reliability from suppliers, including boards, deliveries (type of board, recipient, quantity, timing, method, price, freight, etc.).

**Challenges**:
- Data has not been collected; needs to be established
- Requires ETA information and Gerber package data collection
- Would benefit from AI access to InvoiceReady's line-item data (currently not possible)

**Required Resources**:
- Supplier delivery data collection system
- ETA tracking system
- Gerber package data
- InvoiceReady line-item data access

**Next Steps**:
- Design data collection system
- Establish supplier data feeds
- Develop reliability analysis algorithms

---

### 4. Trading Freight Prices Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Tracks and provides accurate freight cost information for trading offers.

**Challenges**:
- Data has not been collected; needs to be established
- Accurate tracking requires AI access to InvoiceReady's line-item data (currently not possible)

**Required Resources**:
- Freight invoice data
- InvoiceReady line-item data access
- Historical freight cost database

**Next Steps**:
- Investigate InvoiceReady API access
- Design freight cost tracking system
- Develop cost estimation algorithms

---

## Manufacturing & Production Agents

### 5. CAM Analysis Automation Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Performs CAM (Computer-Aided Manufacturing) analysis based on Gerber files automatically.

**Challenges**:
- How can the agent read Gerber and similar data formats?
- Requires specialized file format parsing capabilities

**Required Resources**:
- Gerber file parser
- CAM analysis algorithms
- Integration with manufacturing systems

**Next Steps**:
- Research Gerber file parsing libraries
- Develop CAM analysis algorithms
- Create integration with manufacturing workflow

---

### 6. DFM Report Agent
**Status**: Planned - Not Phase 1  
**Priority**: Low  
**Description**: Automatically generates DFM (Design for Manufacturability) reports. Includes production feedback integration.

**Challenges**:
- Can the agent access information from Wise?
- Can it copy images from Wise/M-files?
- Difficult to implement if batch memo texts cannot be extracted from Wise

**Required Resources**:
- Wise system access
- M-files integration
- Image extraction capabilities
- Production feedback data

**Next Steps**:
- Investigate Wise API capabilities
- Design DFM report generation system
- Develop image extraction from M-files

---

### 7. Etching Parameter Assistant Bot
**Status**: Planned  
**Priority**: Medium  
**Description**: Given job and copper thickness, reviews previous batches from the etching diary to report optimal etching speed and parameters. Reads optical feedback for necessary changes.

**Challenges**:
- If it's a new job, there is no existing data
- Logbook texts are not uniform across operators; entries should be standardized

**Required Resources**:
- Etching diary database
- Optical feedback system
- Standardized logbook format

**Next Steps**:
- Standardize etching logbook entries
- Develop parameter recommendation algorithms
- Create integration with optical feedback system

---

### 8. Speed Stack Build Automation Agent
**Status**: Planned  
**Priority**: Low  
**Description**: Builds a speed stack according to customer specifications automatically.

**Challenges**:
- Likely very difficult to implement
- Can the agent read information from images (PDF, Word, Excel) and transfer it to the speed stack?
- Problem is varied customer specification formats
- Data has not been collected
- Input data quality determines feasibility

**Required Resources**:
- Document parsing (PDF, Word, Excel)
- Image recognition capabilities
- Speed stack configuration system
- Customer specification database

**Next Steps**:
- Research document parsing solutions
- Develop specification extraction algorithms
- Create speed stack configuration system

---

### 9. Work Instructions Assistant Agent
**Status**: Planned - Phase 1  
**Priority**: High  
**Description**: Finds solutions from work instructions when asked about how to do something in a problem situation. Assists production staff with problem-solving. Provides real-time assistance in adhering to work instructions, process descriptions, and operating models.

**Goals**:
- Provide employees quick access to up-to-date work instructions
- Reduce errors in process adherence
- Enable interactive discussion about work instructions and processes
- Learn from user questions and improve answers over time

**User Requirements**:
- Support Finnish and English languages
- Clear responses with document references
- User feedback mechanism
- Web browser and mobile device support

**Functional Requirements**:
- Retrieve information from internal documents (PDF, Word, intranet pages, training portal)
- Recognize context (department, role) and adapt responses accordingly
- Suggest next steps or provide relevant links
- Log questions and answers for analytics purposes

**Non-Functional Requirements**:
- Response time: Under 3 seconds
- Availability: 24/7 (excluding scheduled maintenance)
- Data security: Encrypted data transfer, SSO authentication
- GDPR compliance: No personal data stored without explicit consent

**Limitations**:
- Will not make decisions on behalf of users
- Will not answer external questions (customer inquiries)
- Will not replace official documentation but will complement it

**Acceptance Criteria**:
- Correctly understand at least 90% of test questions
- User satisfaction at least 4/5 during pilot phase
- Integration with document system functions without errors
- Must not provide incorrect or misleading instructions

**Challenges**:
- Risk that AI cannot read work instructions
- All work instructions should be in the same format
- Requires standardized instruction format

**Benefits**:
- Quick access to solutions during production problems
- Consistent guidance based on latest instructions
- Reduces downtime
- Interactive assistance for process adherence

**Required Resources**:
- Standardized work instructions database
- Up-to-date instruction versions
- Clear instruction format
- Document retrieval system (PDF, Word, intranet, training portal)
- SSO authentication system
- Analytics and logging system

**Next Steps**:
- Standardize all work instructions format
- Ensure instructions are up-to-date and clear
- Develop instruction search and retrieval system
- Invest in instruction quality and detail
- Implement document system integration
- Set up SSO authentication
- Develop feedback mechanism

**Documentation**: `docs/agents/work_instructions.md`  
**Requirements**: See `docs/agent_requirements.md` for general requirements

---

### 10. Closing Productions from Axapta Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Automates closing productions that is currently a manual task. Handles cases where not all completed items can be closed if production is left open in Wise. Performs comparison in Excel.

**Challenges**:
- Is this already coming with WiseBooster implementation?

**Required Resources**:
- Wise and Axapta production order base
- Excel comparison logic
- Integration with WiseBooster

**Next Steps**:
- Check WiseBooster implementation status
- Develop production closing logic
- Create Axapta integration

---

### 11. Viafill Program Retrieval Agent
**Status**: Planned  
**Priority**: Low  
**Description**: Finds jobs in the queue that run with the same program.

**Note**: Currently handled manually by Santeri.

**Required Resources**:
- Production queue database
- Program matching system

**Next Steps**:
- Analyze current manual process
- Develop program matching algorithm
- Create queue search interface

---

## Operations & Logistics Agents

### 12. Kyreli Consignment Warehouse Management Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Manages Kyreli's warehouse, including balances, deliveries, stock transfers, and invoicing.

**Challenges**:
- Requires a precise description of what needs to be done
- Requires AI writing rights to Axapta

**Required Resources**:
- Axapta write access
- Warehouse management system
- Inventory tracking

**Next Steps**:
- Define precise requirements
- Obtain Axapta write permissions
- Develop warehouse management logic

---

### 13. Siricon Consignment Warehouse Management Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Manages Siricon's consignment warehouse, including balances, orders, in-transit information, deliveries, stock transfers, and invoicing.

**Challenges**:
- Requires a precise description of what needs to be done
- Requires AI writing rights to Axapta

**Required Resources**:
- Axapta write access
- Warehouse management system
- Inventory tracking

**Next Steps**:
- Define precise requirements
- Obtain Axapta write permissions
- Develop warehouse management logic

---

### 14. Intectiv Shipments and Invoices Consolidation Agent
**Status**: Planned  
**Priority**: High  
**Description**: Automates handling of Intectiv's separate delivery notes, invoices, and COC reports sent via email. Reads package/tracking numbers, invoices, notifies customers of shipments, and compiles comprehensive shipment reports.

**Benefits**:
- Brings order to unclear delivery and invoicing processes
- Enables comprehensive reports
- Customers always receive compiled documents (delivery note, invoice, COC report) in one package
- Accessible by order number without needing email attachments

**Required Resources**:
- Email parsing system
- Document consolidation system
- Customer notification system

**Next Steps**:
- Develop email parsing for Intectiv documents
- Create document consolidation system
- Build customer notification interface

**Documentation**: `docs/agents/intectiv_logistics.md`

---

### 15. Material Procurement Guidance Agent
**Status**: Planned  
**Priority**: High  
**Description**: When a sales order is created, calculates required material quantities and proposes procurement automatically.

**Benefits**:
- Automates currently manual process
- Ensures timely material procurement
- Reduces risk of material shortages

**Required Resources**:
- Axapta database
- Product build information
- Material calculation algorithms

**Next Steps**:
- Develop material calculation logic
- Create procurement proposal system
- Integrate with sales order creation

**Documentation**: `docs/agents/procurement.md`

---

## Quality & Technical Agents

### 16. Technical Support Agent
**Status**: Planned - Phase 2  
**Priority**: High  
**Description**: Provides technical support, design guidelines, technical specifications, and capability information to customers and internal staff.

**Capabilities**:
- Answer technical questions
- Provide design guidelines
- Explain PCB specifications
- Assist with technical documentation

**Integration Points**:
- Technical documentation database
- Design guidelines
- Product specifications

**Documentation**: `docs/agents/technical_support.md`

---

### 17. Quality Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Provides information about certifications, quality standards, testing procedures, and quality management.

**Capabilities**:
- Certification information (AS9100D, IATF 16949, ISO 9001, ISO 14001, Cyber Essentials)
- Quality standards guidance
- Testing procedure information
- Quality management system support

**Documentation**: `docs/agents/quality.md`

---

## Administrative Agents

### 18. AI Initiative Committee Assistant
**Status**: Planned - Phase 1 (First Test)  
**Priority**: High  
**Description**: Interactive chatbot that collects initiative information from users and checks for similar existing initiatives in its own database. Prevents duplicate initiatives by building a knowledge base over time.

**Key Features**:
- **Own Database**: Maintains its own SQLite database (development) or SharePoint (production)
- **Interactive Data Collection**: Chatbot guides users through providing initiative information
- **Similarity Detection**: Searches database for similar initiatives and reports findings
- **Privacy**: Personal information (creator details) stored but not exposed to chatbot

**Functional Requirements**:
- Collect initiative information through natural conversation:
  - Initiative title/name
  - Initiative description
  - Creator information (name, department, contact)
  - Initiative goals and objectives
  - Related processes or systems
  - Expected outcomes
- Search existing initiatives for similarities
- Report similar initiatives found with similarity reasons
- Store initiative information and feedback

**Technical Architecture**:
- **API Endpoint**: `/api/chat/initiative_assistant`
- **Database**: 
  - Development: `data/initiative_assistant/initiatives.db` (SQLite)
  - Production: SharePoint list/database
- **Data Model**: Includes initiatives, feedback, and similarity matches tables
- **Privacy**: Personal information (creator_name, creator_email, creator_contact) stored but NOT exposed to LLM
- **Tools**: 
  - `save_initiative` - Save collected initiative
  - `search_similar_initiatives` - Search for similar initiatives
  - `get_initiative_details` - Get initiative details
  - `save_feedback` - Save user feedback

**Benefits**:
- Easy to implement
- Suitable as first test for cursor workshop
- Prevents duplicate work
- Builds knowledge base over time
- No dependency on external systems (Wise)

**Implementation Approach**:
- **No Legacy Data**: Start fresh with own database, don't integrate with existing Wise data
- **Own Chatbot**: Dedicated chatbot interface for collecting initiative information
- **Database-First**: Build database from scratch with collected initiatives

**Required Resources**:
- SQLite database (development) or SharePoint (production)
- Database schema design
- Similarity search algorithm
- Chatbot conversation flow design

**Next Steps**:
- Create agent directory structure
- Design database schema
- Implement database operations
- Develop similarity search algorithm
- Create chatbot conversation flow
- Implement API endpoint integration

**Documentation**: `docs/agents/initiative_assistant.md`  
**Database Pattern**: See `docs/agent_database_pattern.md` for database implementation guidelines

---

### 19. Automatic Delay Email Agent
**Status**: Planned  
**Priority**: Medium  
**Description**: Generates pre-written emails about potential production delays. Requires access to Wise schedules and delivery dates.

**Challenges**:
- Can the agent access information from Wise?
- Main challenge is long-term forecasting

**Note**: Wise Booster is being implemented, which will partly help.

**Required Resources**:
- Wise schedule access
- Delivery date tracking
- Email template system

**Next Steps**:
- Integrate with Wise Booster
- Develop delay detection algorithms
- Create email generation system

**Documentation**: `docs/agents/delay_notification.md`

---

### 20. Guest Reception and Registration Agent
**Status**: Planned  
**Priority**: Low  
**Description**: Improves current manual guest registration process by automating data flow. Handles machine registration, FD approval, host notification, key logging, obliging key returns, and potentially activating/deactivating keys.

**Challenges**:
- Who can activate the cards?

**Required Resources**:
- New registration device for reception (including checkout)
- Card activation system
- Different system for repair personnel (e.g., weekly keys)

**Next Steps**:
- Design new registration system
- Develop card activation workflow
- Create notification system

---

## Integration & Automation Agents

### 21. ZF Forecast Consolidation Agent
**Status**: Planned  
**Priority**: High  
**Description**: Weekly ZF forecasts are automatically read, compiled, changes highlighted, and transferred to Axapta purchase and sales orders. Sends new order and forecast to supplier. Monitors order schedules, shipments, missing deliveries, and risks of out-of-frozen-zone orders.

**Challenges**:
- How to transfer orders to Axapta?
- AI permissions must be limited to prevent admin tasks beyond server reboots if necessary

**Process**:
- Transfer data from PDF to Excel
- Then to Axapta
- Consider changes and change times
- Monitor for risks

**Required Resources**:
- PDF parsing system
- Excel generation
- Axapta integration
- Monitoring system

**Next Steps**:
- Develop PDF to Excel conversion
- Create Axapta integration with limited permissions
- Build monitoring and alerting system
- Consider separate monitoring agent

**Documentation**: `docs/agents/zf_forecast.md`

---

### 22. Background Jobs Monitoring Agent
**Status**: Planned  
**Priority**: High  
**Description**: Monitors data transfer activity between applications and performs server reboots if necessary.

**Benefits**:
- Potentially very implementable
- Related to other similar "cleanup tasks" in Axapta (e.g., "tails" of sales orders)

**Challenges**:
- What permissions does AI need to reboot the server?

**Required Resources**:
- Server monitoring system
- Reboot permissions
- Data transfer monitoring

**Next Steps**:
- Define server reboot permissions
- Develop monitoring system
- Create automated reboot logic

**Documentation**: `docs/agents/system_monitoring.md`

---

### 23. Hierarchical Report Script Agent
**Status**: Planned  
**Priority**: Low  
**Description**: Removes Power Automate from use by automating hierarchical report generation.

**Note**: Not necessarily for AI; can be implemented by simply optimizing the work.

**Required Resources**:
- Report generation system
- Data aggregation logic

**Next Steps**:
- Analyze current Power Automate workflows
- Develop optimized report generation
- Migrate from Power Automate

---

## Implementation Priority Summary

### Phase 1 (Framework + First Agents)
1. **AI Initiative Committee Assistant** - Easy first test
2. **Sales Agent** - Core business function
3. **Work Instructions Assistant Agent** - High value, implementable

### Phase 2 (High Priority Agents)
4. **Technical Support Agent** - Customer-facing
5. **Intectiv Shipments Agent** - High business value
6. **Material Procurement Guidance Agent** - Automates manual process
7. **ZF Forecast Consolidation Agent** - Critical automation
8. **Background Jobs Monitoring Agent** - System reliability

### Phase 3 (Medium Priority Agents)
9. **Trading Offer Agent** - Requires data access
10. **Trading Supplier Delivery Reliability Agent** - Data collection needed
11. **Trading Freight Prices Agent** - Data collection needed
12. **CAM Analysis Automation Agent** - Technical challenge
13. **Etching Parameter Assistant Bot** - Standardization needed
14. **Kyreli/Siricon Warehouse Agents** - Requires Axapta write access
15. **Closing Productions Agent** - Check WiseBooster status
16. **Automatic Delay Email Agent** - Integrate with Wise Booster
17. **Quality Agent** - Documentation-focused

### Phase 4 (Lower Priority / Complex)
18. **DFM Report Agent** - Complex integration
19. **Speed Stack Build Agent** - Very difficult, data quality dependent
20. **Viafill Program Retrieval Agent** - Currently manual
21. **Guest Reception Agent** - Hardware requirements
22. **Hierarchical Report Script** - May not need AI

---

## Agent Status Legend

- **Planned** - Agent is planned but not yet implemented
- **Phase 1** - First phase of implementation
- **Phase 2** - Second phase of implementation
- **Not Phase 1** - Planned but not for initial implementation

## Priority Legend

- **High** - High business value, feasible implementation
- **Medium** - Good business value, some challenges to overcome
- **Low** - Lower priority or significant implementation challenges

---

## Related Documentation

- **Framework Architecture**: `docs/agents_framework.md`
- **Implementation Plan**: `docs/agents_implementation_plan.md`
- **Brand & Domain**: `docs/aspocomp_brand_domain.md`
- **Agent Implementation Guide**: `.cursor/rules/implement_agent.mdc`


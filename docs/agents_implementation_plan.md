# Aspocomp AI Agents Framework - Implementation Plan

## Overview

This document outlines the implementation plan for extending the current AI training project into a multi-agent framework for Aspocomp. The framework will support multiple specialized AI agents, each operating independently while being integrated with the main web chat system.

## Current State

### Existing Components
- **Main Web Chat**: Flask backend with web frontend (`web_chat/`)
- **Gemini Agent**: Core agent logic (`gemini_agent.py`)
- **CLI Tools**: Various tools accessible via npm scripts
- **Documentation**: Architecture, backend, frontend documentation

### What Needs to Be Built
- **Agents Framework**: Base infrastructure for multiple agents
- **Agent Registry**: System for discovering and managing agents
- **Agent Router**: Message routing to appropriate agents
- **Individual Agents**: Specialized agents for different business functions
- **Agent Documentation**: Comprehensive documentation for each agent

## Implementation Phases

### Phase 1: Framework Foundation (Not Started)

#### 1.1 Base Agent Infrastructure
- [ ] Create `agents/base/` directory structure
- [ ] Implement `BaseAgent` class with common interface
- [ ] Create agent utilities and helper functions
- [ ] Define agent configuration schema
- [ ] Implement agent discovery mechanism

**Files to Create:**
- `agents/base/__init__.py`
- `agents/base/agent_base.py`
- `agents/base/agent_interface.py`
- `agents/base/agent_utils.py`

#### 1.2 Agent Registry and Routing
- [ ] Create agent registry system
- [ ] Implement agent registration mechanism
- [ ] Build agent router for message routing
- [ ] Add intent detection for agent selection
- [ ] Implement fallback to general chat

**Files to Create/Modify:**
- `web_chat/backend/agent_registry.py` (new)
- `web_chat/backend/agent_router.py` (new)
- `web_chat/backend/app.py` (modify to integrate agent router)

#### 1.3 Framework Documentation
- [ ] Create framework README
- [ ] Document base agent interface
- [ ] Document agent development guidelines
- [ ] Create agent template/starter kit

**Files to Create:**
- `agents/README.md`
- `agents/TEMPLATE.md` (agent development template)

### Phase 2: First Agent Implementation (Not Started)

Based on `docs/agent_list.md`, Phase 1 includes:

#### 2.1 AI Initiative Committee Assistant
- [ ] Create `agents/initiative_assistant/` directory structure
- [ ] Implement Initiative Assistant Agent class
- [ ] Create initiative-specific system prompt
- [ ] Implement Wise system integration (if available)
- [ ] Add duplicate detection tools
- [ ] Add initiative assistant configuration
- [ ] Write initiative assistant tests
- [ ] Create initiative assistant documentation

**Files to Create:**
- `agents/initiative_assistant/agent.py`
- `agents/initiative_assistant/config.py`
- `agents/initiative_assistant/prompts/system_prompt.txt`
- `agents/initiative_assistant/tools/` (duplicate detection tools)
- `agents/initiative_assistant/tests/test_initiative_assistant.py`
- `docs/agents/initiative_assistant.md`

**Capabilities:**
- Check existing initiatives when new one is proposed
- Report if similar initiative already exists
- Prevent duplicate work

**Note**: Suitable as first test for cursor workshop - easy to implement.

#### 2.2 Sales Agent
- [ ] Create `agents/sales/` directory structure
- [ ] Implement Sales Agent class
- [ ] Create sales-specific system prompt
- [ ] Implement sales tools (quote generation, product info, etc.)
- [ ] Add sales agent configuration
- [ ] Write sales agent tests
- [ ] Create sales agent documentation

**Files to Create:**
- `agents/sales/agent.py`
- `agents/sales/config.py`
- `agents/sales/prompts/system_prompt.txt`
- `agents/sales/tools/` (various tools)
- `agents/sales/tests/test_sales_agent.py`
- `docs/agents/sales.md`

**Capabilities:**
- Handle RFQ (Request for Quotation) requests
- Provide product information
- Generate quotations
- Answer sales-related questions
- Guide customers through sales process

#### 2.3 Work Instructions Assistant Agent
- [ ] Create `agents/work_instructions/` directory structure
- [ ] Implement Work Instructions Assistant Agent class
- [ ] Create work instructions-specific system prompt
- [ ] Implement work instructions search tools
- [ ] Add standardized instruction format support
- [ ] Add work instructions agent configuration
- [ ] Write work instructions agent tests
- [ ] Create work instructions agent documentation

**Files to Create:**
- `agents/work_instructions/agent.py`
- `agents/work_instructions/config.py`
- `agents/work_instructions/prompts/system_prompt.txt`
- `agents/work_instructions/tools/` (instruction search tools)
- `agents/work_instructions/tests/test_work_instructions.py`
- `docs/agents/work_instructions.md`

**Capabilities:**
- Find solutions from work instructions for problem situations
- Assist production staff with problem-solving
- Provide quick access to solutions during production problems

**Note**: High value, implementable. Requires standardized instruction format.

#### 2.4 Integration Testing
- [ ] Test Initiative Assistant Agent with web chat
- [ ] Test Sales Agent with web chat
- [ ] Test Work Instructions Agent with web chat
- [ ] Test agent routing
- [ ] Test agent fallback mechanisms
- [ ] Test error handling

### Phase 3: High Priority Agents (Not Started)

Based on `docs/agent_list.md`, Phase 2 includes high-priority agents:

#### 3.1 Technical Support Agent
- [ ] Create `agents/technical_support/` structure
- [ ] Implement Technical Support Agent
- [ ] Create technical support tools
- [ ] Add design guidelines knowledge base
- [ ] Create technical support documentation

**Capabilities:**
- Answer technical questions
- Provide design guidelines
- Explain PCB specifications
- Assist with technical documentation

#### 3.2 Intectiv Shipments and Invoices Agent
- [ ] Create `agents/intectiv_logistics/` structure
- [ ] Implement Intectiv Logistics Agent
- [ ] Create email parsing tools
- [ ] Implement document consolidation
- [ ] Add customer notification system
- [ ] Create agent documentation

**Capabilities:**
- Parse Intectiv emails (delivery notes, invoices, COC reports)
- Consolidate documents by order number
- Notify customers of shipments
- Generate comprehensive shipment reports

#### 3.3 Material Procurement Guidance Agent
- [ ] Create `agents/procurement/` structure
- [ ] Implement Procurement Agent
- [ ] Create material calculation tools
- [ ] Integrate with Axapta sales orders
- [ ] Implement procurement proposal system
- [ ] Create agent documentation

**Capabilities:**
- Calculate required material quantities from sales orders
- Propose procurement automatically
- Reduce risk of material shortages

#### 3.4 ZF Forecast Consolidation Agent
- [ ] Create `agents/zf_forecast/` structure
- [ ] Implement ZF Forecast Agent
- [ ] Create PDF to Excel conversion tools
- [ ] Implement Axapta integration (with limited permissions)
- [ ] Add monitoring and alerting system
- [ ] Create agent documentation

**Capabilities:**
- Read weekly ZF forecasts
- Compile and highlight changes
- Transfer to Axapta purchase and sales orders
- Monitor order schedules and risks

#### 3.5 Background Jobs Monitoring Agent
- [ ] Create `agents/system_monitoring/` structure
- [ ] Implement System Monitoring Agent
- [ ] Create monitoring tools
- [ ] Implement server reboot logic (with proper permissions)
- [ ] Add alerting system
- [ ] Create agent documentation

**Capabilities:**
- Monitor data transfer activity
- Perform server reboots if necessary
- Handle cleanup tasks in Axapta

### Phase 4: Medium Priority Agents (Not Started)

See `docs/agent_list.md` for complete list of medium and low priority agents including:
- Trading Offer Agent
- Trading Supplier Delivery Reliability Agent
- Trading Freight Prices Agent
- CAM Analysis Automation Agent
- Etching Parameter Assistant Bot
- Warehouse Management Agents (Kyreli, Siricon)
- Automatic Delay Email Agent
- Quality Agent
- And more...

### Phase 5: Advanced Features (Not Started)

#### 5.1 Multi-Agent Collaboration
- [ ] Implement agent-to-agent communication
- [ ] Add multi-agent response aggregation
- [ ] Create agent orchestration system

#### 5.2 Enhanced Routing
- [ ] Implement advanced intent detection
- [ ] Add confidence scoring
- [ ] Create routing rules engine

#### 5.3 Monitoring and Analytics
- [ ] Add agent-specific metrics
- [ ] Implement agent performance tracking
- [ ] Create agent analytics dashboard

## Technical Specifications

### Agent Interface

All agents must implement:

```python
class BaseAgent:
    async def process_message(message, conversation_id, context) -> dict
    def get_capabilities() -> dict
    def get_system_prompt() -> str
    def is_enabled() -> bool
```

### Agent Configuration

Each agent requires:
- Agent ID (unique identifier)
- Name and description
- Enabled/disabled status
- Model configuration
- Tool definitions
- System prompt path

### Integration Points

1. **Web Chat Backend**: Routes messages to agents
2. **Agent Registry**: Manages agent lifecycle
3. **Agent Router**: Determines which agent(s) to use
4. **Conversation Manager**: Maintains conversation state
5. **Tool Execution**: Executes agent-specific tools

## File Structure

```
agents/
├── base/                    # Base agent infrastructure
│   ├── __init__.py
│   ├── agent_base.py
│   ├── agent_interface.py
│   └── agent_utils.py
├── sales/                   # Sales Agent
│   ├── agent.py
│   ├── config.py
│   ├── prompts/
│   ├── tools/
│   └── tests/
├── technical_support/       # Technical Support Agent
│   └── ...
└── customer_service/        # Customer Service Agent
    └── ...

web_chat/backend/
├── agent_registry.py        # Agent discovery and registration
├── agent_router.py          # Message routing logic
└── app.py                   # Modified to use agent router

docs/
├── agents/                  # Agent documentation
│   ├── README.md
│   ├── sales.md
│   └── ...
├── agents_framework.md      # Framework architecture
└── aspocomp_brand_domain.md # Brand and domain knowledge
```

## Dependencies

### New Python Packages
- None required initially (using existing Flask and Gemini libraries)
- May need additional packages for advanced routing (e.g., scikit-learn for intent classification)

### Configuration
- Environment variables for agent configuration
- Agent-specific API keys if needed
- Model selection per agent

## Testing Strategy

### Unit Tests
- Test base agent class
- Test individual agent implementations
- Test agent tools
- Test configuration loading

### Integration Tests
- Test agent registration
- Test message routing
- Test agent responses
- Test error handling

### E2E Tests
- Test full conversation flow
- Test agent switching
- Test multi-agent scenarios

## Documentation Requirements

### Framework Documentation
- ✅ `docs/agents_framework.md` - Framework architecture
- ✅ `docs/aspocomp_brand_domain.md` - Brand and domain knowledge
- ✅ `docs/agents/README.md` - Agents documentation overview
- [ ] `agents/README.md` - Framework setup guide
- [ ] `agents/TEMPLATE.md` - Agent development template

### Agent Documentation
- [ ] `docs/agents/sales.md` - Sales agent documentation
- [ ] `docs/agents/technical_support.md` - Technical support agent docs
- [ ] `docs/agents/customer_service.md` - Customer service agent docs

## Success Criteria

### Phase 1 Complete When:
- Base agent infrastructure is implemented
- Agent registry can discover and register agents
- Agent router can route messages to agents
- Framework documentation is complete

### Phase 2 Complete When:
- Sales Agent is fully implemented
- Sales Agent integrates with web chat
- Sales Agent documentation is complete
- Tests pass for Sales Agent

### Phase 3 Complete When:
- At least 3 agents are implemented
- All agents integrate with web chat
- Agent documentation is complete
- All tests pass

## Next Steps

1. **Review and Approve Plan**: Review this implementation plan
2. **Start Phase 1**: Begin framework foundation implementation
3. **Create Agent Template**: Develop starter template for new agents
4. **Implement First Agent**: Build Sales Agent as proof of concept
5. **Iterate and Improve**: Refine based on feedback and testing

## Agent Catalog

See `docs/agent_list.md` for the complete list of 23 planned agents, organized by category (Sales & Trading, Manufacturing & Production, Operations & Logistics, Quality & Technical, Administrative, Integration & Automation) and prioritized by feasibility and business value.

## References

- Agent List: `docs/agent_list.md` - Complete catalog of planned agents
- Framework Architecture: `docs/agents_framework.md`
- Brand and Domain: `docs/aspocomp_brand_domain.md`
- System Architecture: `docs/architecture.md`
- Backend API: `docs/backend.md`
- Frontend: `docs/frontend.md`


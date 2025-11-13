# Aspocomp AI Agents Documentation

This directory contains documentation for each AI agent in the Aspocomp AI framework.

## Overview

The Aspocomp AI Agents framework provides specialized AI agents for different business functions. Each agent operates independently while being integrated with the main web chat system.

## Complete Agent List

See `../agent_list.md` for the complete catalog of 23 planned agents, organized by category and priority.

## Framework Documentation

- **Agent Requirements**: `../agent_requirements.md` - General requirements for all agents
- **Agent List**: `../agent_list.md` - Complete catalog of all planned agents
- **Framework Architecture**: `../agents_framework.md` - Overall framework design
- **Brand and Domain**: `../aspocomp_brand_domain.md` - Aspocomp-specific knowledge
- **Implementation Plan**: `../agents_implementation_plan.md` - Implementation roadmap

## Agent Documentation

Each agent has its own documentation file in this directory:

### Phase 1 Agents (First Implementation)
- `initiative_assistant.md` - AI Initiative Committee Assistant
- `sales.md` - Sales Agent documentation
- `work_instructions.md` - Work Instructions Assistant Agent

### Phase 2 Agents (High Priority)
- `technical_support.md` - Technical Support Agent documentation
- `intectiv_logistics.md` - Intectiv Shipments and Invoices Agent
- `procurement.md` - Material Procurement Guidance Agent
- `zf_forecast.md` - ZF Forecast Consolidation Agent
- `system_monitoring.md` - Background Jobs Monitoring Agent

### Additional Agents
- `delay_notification.md` - Automatic Delay Email Agent
- `quality.md` - Quality Agent documentation
- `[agent_name].md` - Additional agent documentation files as they are developed

## Agent Development

When creating a new agent:

1. Create the agent implementation in `agents/[agent_name]/`
2. Create documentation in `docs/agents/[agent_name].md`
3. Update this README to include the new agent
4. Register the agent in the agent registry

## Documentation Structure

Each agent documentation should include:

- **Overview**: Purpose and capabilities
- **Configuration**: Setup and configuration options
- **System Prompt**: Agent-specific prompts and instructions
- **Tools**: Available tools and functions
- **Integration**: How the agent integrates with the main system
- **Testing**: Testing strategies and examples
- **Examples**: Usage examples and sample interactions

## Quick Links

- [Framework Architecture](../agents_framework.md)
- [Aspocomp Brand & Domain](../aspocomp_brand_domain.md)
- [System Architecture](../architecture.md)
- [Backend API](../backend.md)


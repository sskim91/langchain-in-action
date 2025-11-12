# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LangChain + Ollama** project implementing a personal assistant AI system using the **Skill Card Pattern**. The project demonstrates two execution approaches:
- **Static Execution Plan**: Predefined sequential workflow (Step 04-05)
- **Dynamic Agent**: LLM selects tools contextually (Step 06)

**Current Status**: Step 06 completed (Dynamic Agent implementation)

## Development Commands

### Running Examples

```bash
# Step 05: Real Tools Demo (LLM + DB + Logic tools with verbose debugging)
uv run python -m src.examples.08_real_tools_demo

# Step 06: Dynamic Agent (LLM selects tools)
uv run python -m src.examples.09_dynamic_agent

# Step 04: Skill Card Executor Demo
uv run python -m src.examples.05_skill_card_demo

# Quick test script
uv run python quick_test.py
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/core/test_skill_card_manager.py

# Run specific test
uv run pytest tests/core/test_skill_card_manager.py::test_skill_card_load
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Architecture

### Core Pattern: Skill Card System

The **Skill Card** is a JSON-based metadata pattern that defines Agent behavior:

```
User Query → SkillCardManager → SkillCardExecutor → Tools → Result
```

**Key Components:**

1. **SkillCard** (`src/core/skill_cards/schema.py`): Pydantic schema defining agent metadata
2. **SkillCardManager** (`src/core/skill_cards/manager.py`): Loads JSON files
3. **SkillCardExecutor** (`src/core/skill_cards/executor.py`): Executes the plan

**Execution Flow:**

```python
# 1. Load Skill Card from JSON
manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")

# 2. Register tools
executor = SkillCardExecutor(card, verbose=True)
executor.register_tool("parse_event_info", parse_event_info)
executor.register_tool("create_event", create_event)

# 3. Execute
result = executor.execute(
    user_query="내일 오후 2시에 팀 회의",
    context={"user_id": "user123"}
)
```

### Variable Substitution Pattern

Skill Cards use `${variable}` syntax for data flow between steps:

```json
{
  "step": 2,
  "action": "create_event",
  "input": {
    "title": "${event_data.title}",           // From step 1
    "start_time": "${free_slots.best_slot.start}"  // Nested access
  },
  "output_to": "created_event"
}
```

Implementation: `SkillCardExecutor._substitute_variables()` uses regex pattern `\$\{([^}]+)\}` to replace variables with actual values from `ExecutionContext.variables`.

### Tool Types

**1. LLM Tools** (Structured Output with Pydantic):
```python
from pydantic import BaseModel, Field

class EventInfo(BaseModel):
    title: str = Field(description="일정 제목")
    date: str = Field(description="날짜 (YYYY-MM-DD)")

@tool
def parse_event_info(query: str, verbose: bool = False) -> dict:
    llm = ChatOllama(model="gpt-oss:20b", temperature=0.0)
    structured_llm = llm.with_structured_output(EventInfo)
    result: EventInfo = structured_llm.invoke(prompt)
    return result.model_dump()
```

**2. DB Tools** (Database operations):
```python
@tool
def create_event(title: str, start_time: str) -> dict:
    event = {...}
    db.add_event(event)  # In-memory DB
    return {"success": True, "event": event}
```

**3. Logic Tools** (Business logic):
```python
@tool
def find_free_time(date: str, duration: int = 60) -> dict:
    # Complex scheduling logic
    busy_slots = get_busy_slots(date)
    available_slots = calculate_free_time(busy_slots)
    return {"available_slots": available_slots}
```

### Verbose Debugging System

The project uses a **two-level debugging** approach:

**Level 1: SkillCardExecutor verbose mode**
```python
executor = SkillCardExecutor(card, verbose=True)
# Prints step-by-step execution, variable substitution, timing
```

**Level 2: LangChain global debug**
```python
from langchain_core.globals import set_debug

if verbose:
    set_debug(True)  # Shows LLM prompts, responses, token counts
```

**Important**: Use `langchain_core.globals`, NOT `langchain.globals` (doesn't exist).

### Middleware System

Middleware pattern for pre/post processing:

```python
class BaseMiddleware:
    def pre_process(self, query: str) -> str:
        """Process before agent execution"""
        pass

    def post_process(self, result: str) -> str:
        """Process after agent execution"""
        pass
```

Current implementations:
- `PIIDetectionMiddleware`: Detects/masks phone, email, SSN
- `AuditLoggingMiddleware`: JSON Lines format logging

## Project Structure

```
src/
├── core/                       # Framework layer
│   ├── agents/
│   │   └── base_agent.py      # Base agent class (not actively used)
│   ├── skill_cards/           # ⭐ Core pattern
│   │   ├── schema.py          # Pydantic models
│   │   ├── manager.py         # Load JSON
│   │   └── executor.py        # Execute plan
│   └── middleware/            # Middleware system
│
├── personal_assistant/        # Application layer
│   ├── agents/
│   │   └── schedule_manager.py  # Dynamic agent (Step 06)
│   ├── tools/
│   │   └── schedule_tools.py    # LLM/DB/Logic tools
│   ├── database/
│   │   └── memory_db.py         # In-memory DB
│   └── skill_cards/
│       └── schedule_card.json   # Static plan definition
│
└── examples/                  # Runnable demos
    ├── 08_real_tools_demo.py  # Step 05: Skill Card + Real Tools
    └── 09_dynamic_agent.py    # Step 06: Dynamic tool selection
```

## Key Concepts

### Static vs Dynamic Execution

| Aspect | Static Plan | Dynamic Agent |
|--------|-------------|---------------|
| Tool Selection | Predefined in JSON | LLM decides |
| Execution Order | Always same | Context-dependent |
| Predictability | High | Low |
| Flexibility | Low | High |
| Use Case | Compliance-critical | User experience |

**Static** (Step 04-05): `SkillCardExecutor` executes JSON execution_plan sequentially
**Dynamic** (Step 06): `ScheduleManagerAgent` uses LangChain's tool calling

See `docs/personal-assistant/patterns.md` for detailed comparison.

### Ollama Integration

**Model**: `gpt-oss:20b` (GPT-Oss-20B from Shallowmind)

**Setup:**
```bash
ollama pull gpt-oss:20b
ollama serve  # Must be running
```

**Usage:**
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0.0,  # Deterministic for parsing
)
```

**Troubleshooting**: If "Could not connect to Ollama" error, run `ollama serve` in separate terminal.

## Testing Patterns

### Test Structure

```python
# tests/conftest.py automatically sets working directory to project root
# No need for sys.path manipulation

def test_example():
    from core.skill_cards import SkillCardManager

    manager = SkillCardManager()
    card = manager.get("SC_SCHEDULE_001")

    assert card is not None
    assert card.skill_id == "SC_SCHEDULE_001"
```

### Pytest Configuration

`pyproject.toml` sets:
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

This means imports work from `src/` root without relative paths.

## Common Patterns

### Creating a New Tool

```python
from langchain_core.tools import tool

@tool
def my_new_tool(param: str, verbose: bool = False) -> dict:
    """
    Tool description for LLM

    Args:
        param: Parameter description
        verbose: Enable debug output

    Returns:
        dict: Result with success/error keys
    """
    if verbose:
        print(f"[DEBUG] my_new_tool: {param}")

    try:
        result = do_something(param)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Adding to Skill Card

```json
{
  "execution_plan": [
    {
      "step": N,
      "action": "my_new_tool",
      "input": {
        "param": "${previous_step.field}"
      },
      "output_to": "my_result",
      "on_error": "fail"  // or "skip"
    }
  ]
}
```

### Register in Executor

```python
from personal_assistant.tools.my_tools import my_new_tool

executor.register_tool("my_new_tool", my_new_tool)
```

## Documentation

Comprehensive docs in `docs/` organized hierarchically:

**Quick Start:**
1. `docs/README.md` - Navigation hub
2. `docs/personal-assistant/README.md` - Project intro
3. `docs/personal-assistant/concepts.md` - Core concepts (10 min read)

**Implementation:**
- `docs/personal-assistant/implementation-guide.md` - Tool creation, verbose debugging, best practices
- `docs/personal-assistant/patterns.md` - Static vs Dynamic detailed comparison
- `docs/personal-assistant/step-by-step/` - Step-by-step implementation guides

**General Learning:**
- `docs/learning-guide.md` - LangChain learning roadmap
- `docs/package-guide.md` - Python package structure guide

## Important Notes

### Import Paths

Always use absolute imports from `src/`:
```python
# ✅ Correct
from core.skill_cards import SkillCardManager
from personal_assistant.tools.schedule_tools import create_event

# ❌ Wrong
from ..core.skill_cards import SkillCardManager
```

### LangChain Versions

This project uses **LangChain 1.0.5** split packages:
- `langchain-core`: Core abstractions
- `langchain-community`: Community integrations
- `langchain-ollama`: Ollama specific

**Note**: Some examples use `langchain_classic.agents` for compatibility with tool calling pattern.

### Database

Currently uses **in-memory database** (`src/personal_assistant/database/memory_db.py`). Data doesn't persist between runs. This is intentional for demo purposes.

### Korean Language

All user-facing messages and documentation are in Korean. LLM system prompts include `항상 한국어로 응답하세요.`

## Next Steps

Roadmap in `docs/personal-assistant/roadmap.md`:

**Step 07** (Next): VectorDB integration for semantic Skill Card matching
**Step 08-09**: TodoManager and KnowledgeManager agents
**Step 10**: Supervisor agent for multi-agent routing
**Step 11+**: FastAPI, caching, logging, monitoring

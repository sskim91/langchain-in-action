# Step 07: LangGraph Supervisor 패턴 구현

> Multi-Agent 시스템의 핵심 - Supervisor가 적절한 Agent를 선택하여 작업 위임

## 🎯 학습 목표

1. **LangGraph 기본 개념** 이해
2. **TodoAgent** 구현 (ScheduleManagerAgent 패턴 참고)
3. **SupervisorAgent** 구현 (LangGraph StateGraph 활용)
4. **Agent 간 라우팅** 로직 구현

---

## 📊 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query                                │
│              "내일 회의 잡아줘" / "장보기 추가해줘"            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 SupervisorAgent                              │
│            (LangGraph StateGraph)                            │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Router    │ -> │  Executor   │ -> │  Finalizer  │     │
│  │  (LLM 판단) │    │ (Agent 실행)│    │ (응답 정리) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Schedule │ │   Todo   │ │  (확장)  │
    │  Agent   │ │  Agent   │ │  Agent   │
    └──────────┘ └──────────┘ └──────────┘
```

---

## 🗂️ 구현 파일 구조

```
src/multi_agent_lab/
├── domains/
│   └── personal_assistant/
│       ├── agents/
│       │   ├── schedule_manager.py   # 기존 (수정 없음)
│       │   ├── todo_manager.py       # 🆕 새로 생성
│       │   └── supervisor.py         # 🆕 새로 생성 (LangGraph)
│       └── tools/
│           ├── schedule_tools.py     # 기존 (수정 없음)
│           └── todo_tools.py         # 🆕 새로 생성
│
└── examples/
    └── 10_langgraph_supervisor.py    # 🆕 데모 파일
```

---

## 📋 구현 계획

### Phase 1: 환경 설정

#### 1.1 LangGraph 의존성 추가

```bash
uv add langgraph
```

**pyproject.toml 변경:**
```toml
dependencies = [
    ...
    "langgraph>=1.0.2",
]
```

---

### Phase 2: TodoAgent 구현

#### 2.1 todo_tools.py 생성

**위치:** `src/multi_agent_lab/domains/personal_assistant/tools/todo_tools.py`

**구현할 Tool 목록:**

| Tool | 설명 | 입력 | 출력 |
|------|------|------|------|
| `add_task` | 새 할일 추가 | title, priority, due_date | task dict |
| `list_tasks` | 할일 목록 조회 | status (optional) | tasks list |
| `complete_task` | 할일 완료 처리 | task_id | success bool |
| `delete_task` | 할일 삭제 | task_id | success bool |

**코드 구조:**
```python
from langchain_core.tools import tool
from multi_agent_lab.domains.personal_assistant.storage import db

@tool
def add_task(title: str, priority: str = "medium", due_date: str | None = None) -> dict:
    """새로운 할일을 추가합니다."""
    ...

@tool
def list_tasks(status: str | None = None) -> dict:
    """할일 목록을 조회합니다."""
    ...

@tool
def complete_task(task_id: str) -> dict:
    """할일을 완료 처리합니다."""
    ...
```

#### 2.2 todo_manager.py 생성

**위치:** `src/multi_agent_lab/domains/personal_assistant/agents/todo_manager.py`

**ScheduleManagerAgent 패턴 따르기:**
- `__init__`: LLM, Tools, Prompt, Agent, Executor 초기화
- `chat(query)`: 메인 인터페이스
- `invoke(query)`: 직접 실행

**System Prompt:**
```
당신은 할일 관리 전문가입니다.

사용자의 할일을 효율적으로 관리하고, 다음 작업을 수행합니다:

1. **할일 추가**: 새로운 할일을 등록합니다.
2. **할일 조회**: 전체 또는 상태별 할일을 조회합니다.
3. **할일 완료**: 완료된 할일을 처리합니다.
4. **할일 삭제**: 불필요한 할일을 삭제합니다.

항상 한국어로 응답하세요.
```

---

### Phase 3: SupervisorAgent 구현 (LangGraph)

#### 3.1 LangGraph 핵심 개념

**StateGraph 구조:**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. State 정의
class AgentState(TypedDict):
    query: str                    # 사용자 질문
    agent_type: str              # 선택된 Agent 타입
    agent_response: str          # Agent 응답
    final_response: str          # 최종 응답

# 2. Node 함수 정의
def router(state: AgentState) -> AgentState:
    """LLM이 적절한 Agent 선택"""
    ...

def executor(state: AgentState) -> AgentState:
    """선택된 Agent 실행"""
    ...

def finalizer(state: AgentState) -> AgentState:
    """응답 정리"""
    ...

# 3. Graph 구성
graph = StateGraph(AgentState)
graph.add_node("router", router)
graph.add_node("executor", executor)
graph.add_node("finalizer", finalizer)

graph.add_edge("router", "executor")
graph.add_edge("executor", "finalizer")
graph.add_edge("finalizer", END)

graph.set_entry_point("router")

# 4. 컴파일
app = graph.compile()
```

#### 3.2 supervisor.py 구현

**위치:** `src/multi_agent_lab/domains/personal_assistant/agents/supervisor.py`

**핵심 구현:**

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

from .schedule_manager import ScheduleManagerAgent
from .todo_manager import TodoManagerAgent


class SupervisorState(TypedDict):
    """Supervisor의 상태"""
    query: str
    agent_type: Literal["schedule", "todo", "unknown"]
    response: str


class PersonalAssistantSupervisor:
    """
    LangGraph 기반 Supervisor Agent

    사용자 질문을 분석하여 적절한 Agent에게 작업을 위임합니다.
    """

    def __init__(self, model_name: str = "gpt-oss:20b"):
        self.llm = ChatOllama(model=model_name, temperature=0.0)

        # Sub-Agents
        self.schedule_agent = ScheduleManagerAgent()
        self.todo_agent = TodoManagerAgent()

        # Graph 구성
        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """LangGraph 구성"""
        graph = StateGraph(SupervisorState)

        # Node 추가
        graph.add_node("router", self._router)
        graph.add_node("schedule_executor", self._execute_schedule)
        graph.add_node("todo_executor", self._execute_todo)
        graph.add_node("fallback", self._fallback)

        # 조건부 Edge
        graph.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "schedule": "schedule_executor",
                "todo": "todo_executor",
                "unknown": "fallback",
            }
        )

        # 종료 Edge
        graph.add_edge("schedule_executor", END)
        graph.add_edge("todo_executor", END)
        graph.add_edge("fallback", END)

        graph.set_entry_point("router")

        return graph

    def _router(self, state: SupervisorState) -> SupervisorState:
        """LLM이 Agent 유형 판단"""
        ...

    def _route_decision(self, state: SupervisorState) -> str:
        """라우팅 결정"""
        return state["agent_type"]

    def _execute_schedule(self, state: SupervisorState) -> SupervisorState:
        """ScheduleAgent 실행"""
        response = self.schedule_agent.chat(state["query"])
        return {**state, "response": response}

    def _execute_todo(self, state: SupervisorState) -> SupervisorState:
        """TodoAgent 실행"""
        response = self.todo_agent.chat(state["query"])
        return {**state, "response": response}

    def _fallback(self, state: SupervisorState) -> SupervisorState:
        """알 수 없는 요청 처리"""
        return {**state, "response": "죄송합니다. 해당 요청을 처리할 수 없습니다."}

    def chat(self, query: str) -> str:
        """메인 인터페이스"""
        result = self.app.invoke({"query": query, "agent_type": "", "response": ""})
        return result["response"]
```

---

### Phase 4: 데모 파일 생성

#### 4.1 10_langgraph_supervisor.py

**위치:** `src/examples/10_langgraph_supervisor.py`

**데모 시나리오:**
```python
"""
LangGraph Supervisor Demo - Multi-Agent 라우팅

🎯 목표:
- Supervisor가 질문을 분석하여 적절한 Agent 선택
- Schedule 관련 → ScheduleAgent
- Todo 관련 → TodoAgent

실행:
    uv run python -m src.examples.10_langgraph_supervisor
"""

from multi_agent_lab.domains.personal_assistant.agents.supervisor import (
    PersonalAssistantSupervisor,
)
from multi_agent_lab.domains.personal_assistant.storage import db


def main():
    print("=" * 80)
    print("  🤖 LangGraph Supervisor - Multi-Agent 라우팅")
    print("=" * 80)

    # DB 초기화
    db.clear()

    # Supervisor 생성
    supervisor = PersonalAssistantSupervisor()

    # 테스트 시나리오
    test_queries = [
        ("📅 일정 관련", "내일 오후 2시에 팀 회의 잡아줘"),
        ("✅ 할일 관련", "장보기 할일 추가해줘"),
        ("📅 일정 조회", "이번 주 일정 보여줘"),
        ("✅ 할일 조회", "오늘 할일 목록 알려줘"),
    ]

    for category, query in test_queries:
        print(f"\n{category}")
        print(f"질문: {query}")
        print("-" * 40)
        response = supervisor.chat(query)
        print(f"응답: {response}")

    print("\n✨ 완료!")


if __name__ == "__main__":
    main()
```

---

## 🧪 테스트 계획

### 단위 테스트

**파일:** `tests/domains/personal_assistant/test_todo_agent.py`

```python
def test_add_task():
    """할일 추가 테스트"""
    ...

def test_list_tasks():
    """할일 조회 테스트"""
    ...

def test_complete_task():
    """할일 완료 테스트"""
    ...
```

**파일:** `tests/domains/personal_assistant/test_supervisor.py`

```python
def test_route_to_schedule():
    """일정 관련 질문 라우팅"""
    ...

def test_route_to_todo():
    """할일 관련 질문 라우팅"""
    ...

def test_unknown_query():
    """알 수 없는 질문 처리"""
    ...
```

---

## 📝 문서화 계획

### 1. 코드 문서화
- 모든 클래스/함수에 docstring 추가
- 타입 힌트 완전 적용

### 2. 학습 문서
- `docs/personal-assistant/step-by-step/step-07-langgraph-supervisor.md` (현재 문서)
- LangGraph 핵심 개념 설명 추가

### 3. 아키텍처 문서 업데이트
- `docs/ARCHITECTURE.md` 로드맵 업데이트
- Phase 2 진행 상황 반영

---

## ⏱️ 구현 순서

| 순서 | 작업 | 파일 |
|------|------|------|
| 1 | LangGraph 의존성 추가 | `pyproject.toml` |
| 2 | Todo Tools 구현 | `tools/todo_tools.py` |
| 3 | TodoAgent 구현 | `agents/todo_manager.py` |
| 4 | SupervisorAgent 구현 | `agents/supervisor.py` |
| 5 | 데모 파일 생성 | `examples/10_langgraph_supervisor.py` |
| 6 | 테스트 작성 | `tests/` |
| 7 | 문서 업데이트 | `docs/` |

---

## 🎓 학습 포인트

### LangGraph 핵심 개념

1. **StateGraph**: 상태 기반 그래프
2. **Node**: 작업 단위 (함수)
3. **Edge**: Node 간 연결
4. **Conditional Edge**: 조건부 분기
5. **Compile**: 실행 가능한 앱으로 변환

### Multi-Agent 패턴

1. **Supervisor Pattern**: 중앙 관리자가 작업 분배
2. **Router**: 질문 분석 및 Agent 선택
3. **State Management**: Agent 간 상태 공유

---

## 📚 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph Multi-Agent 예제](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)
- [LangChain Agent 문서](https://python.langchain.com/docs/modules/agents/)

---

**작성일:** 2025-11-14
**프로젝트:** Multi-Agent Lab
**버전:** Step 07

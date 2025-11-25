"""
PersonalAssistantSupervisor - LangGraph 기반 Multi-Agent Supervisor

Supervisor 패턴을 사용하여 사용자 질문을 분석하고
적절한 Agent(Schedule/Todo)에게 작업을 위임합니다.

사용 예시:
    from multi_agent_lab.domains.personal_assistant.agents.supervisor import (
        PersonalAssistantSupervisor,
    )

    supervisor = PersonalAssistantSupervisor()
    response = supervisor.chat("내일 오후 2시에 회의 잡아줘")
    print(response)

실행:
    uv run python -m src.examples.10_langgraph_supervisor

아키텍처:
    ┌─────────────────────────────────────────┐
    │              User Query                  │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │          Router (LLM 판단)               │
    │   "일정" → schedule / "할일" → todo      │
    └─────────────────┬───────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Schedule │ │   Todo   │ │ Fallback │
    │  Agent   │ │  Agent   │ │          │
    └──────────┘ └──────────┘ └──────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │            Final Response               │
    └─────────────────────────────────────────┘
"""

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from .schedule_manager import ScheduleManagerAgent
from .todo_manager import TodoManagerAgent

# =============================================================================
# State 정의
# =============================================================================


class SupervisorState(TypedDict):
    """
    Supervisor의 상태를 정의하는 TypedDict

    LangGraph v1+에서 Node 간 데이터를 전달하는 데 사용됩니다.
    (Pydantic BaseModel은 deprecated)

    Attributes:
        query: 사용자 질문
        agent_type: 선택된 Agent 유형 (schedule, todo, unknown)
        response: Agent 응답
    """

    query: str
    agent_type: Literal["schedule", "todo", "unknown"]
    response: str


# =============================================================================
# Supervisor Agent
# =============================================================================


class PersonalAssistantSupervisor:
    """
    LangGraph 기반 Multi-Agent Supervisor

    사용자 질문을 분석하여 적절한 Agent에게 작업을 위임합니다.

    LangGraph 핵심 개념:
        - StateGraph: 상태 기반 그래프
        - Node: 작업 단위 (함수)
        - Edge: Node 간 연결
        - Conditional Edge: 조건부 분기
        - Compile: 실행 가능한 앱으로 변환

    Attributes:
        model_name: 사용할 Ollama 모델명
        llm: LLM 인스턴스 (라우팅용)
        schedule_agent: 일정 관리 Agent
        todo_agent: 할일 관리 Agent
        graph: LangGraph StateGraph
        app: 컴파일된 그래프 앱

    Example:
        >>> supervisor = PersonalAssistantSupervisor()
        >>> response = supervisor.chat("장보기 할일 추가해줘")
        >>> print(response)
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        verbose: bool = True,
    ):
        """
        Args:
            model_name: Ollama 모델명
            verbose: 상세 로그 출력 여부
        """
        self.model_name = model_name
        self.verbose = verbose

        # 라우팅용 LLM (빠른 판단을 위해 temperature=0)
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.0,
        )

        # Sub-Agents 초기화
        if self.verbose:
            print("🔧 Sub-Agents 초기화 중...")

        self.schedule_agent = ScheduleManagerAgent(model_name=model_name)
        self.todo_agent = TodoManagerAgent(model_name=model_name)

        if self.verbose:
            print("   ✅ ScheduleManagerAgent 준비 완료")
            print("   ✅ TodoManagerAgent 준비 완료")

        # LangGraph 구성
        if self.verbose:
            print("🔧 LangGraph 구성 중...")

        self.graph = self._build_graph()
        self.app = self.graph.compile()

        if self.verbose:
            print("   ✅ StateGraph 컴파일 완료")

    def _build_graph(self) -> StateGraph:
        """
        LangGraph StateGraph 구성

        그래프 구조:
            START → router → (schedule_executor | todo_executor | fallback) → END

        Returns:
            StateGraph: 구성된 그래프
        """

        # StateGraph 생성 (TypedDict 사용 - LangGraph v1+ 권장)
        graph = StateGraph(SupervisorState)

        # Node 추가
        graph.add_node("router", self._router)
        graph.add_node("schedule_executor", self._execute_schedule)
        graph.add_node("todo_executor", self._execute_todo)
        graph.add_node("fallback", self._fallback)

        # Entry Point 설정
        graph.set_entry_point("router")

        # Conditional Edge: router → (schedule | todo | fallback)
        graph.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "schedule": "schedule_executor",
                "todo": "todo_executor",
                "unknown": "fallback",
            },
        )

        # 종료 Edge
        graph.add_edge("schedule_executor", END)
        graph.add_edge("todo_executor", END)
        graph.add_edge("fallback", END)

        return graph

    def _router(self, state: SupervisorState) -> dict:
        """
        Router Node: LLM이 Agent 유형 판단

        사용자 질문을 분석하여 적절한 Agent 유형을 결정합니다.

        Args:
            state: 현재 상태

        Returns:
            dict: 업데이트된 상태 (agent_type 포함)
        """
        if self.verbose:
            print("\n🔀 Router: 질문 분석 중...")
            print(f"   질문: {state.query}")

        # 라우팅 프롬프트
        routing_prompt = """당신은 질문 분류 전문가입니다.

사용자 질문을 분석하여 다음 중 하나로 분류하세요:

- schedule: 일정, 회의, 약속, 캘린더, 시간 관련 질문
  예: "내일 회의 잡아줘", "이번 주 일정 보여줘", "오후 3시에 약속 있어?"

- todo: 할일, 작업, 태스크, 목록 관련 질문
  예: "장보기 추가해줘", "오늘 할일 뭐야?", "숙제 완료 처리해줘"

- unknown: 위 두 가지에 해당하지 않는 질문

반드시 schedule, todo, unknown 중 하나만 응답하세요. 다른 말은 하지 마세요."""

        messages = [
            SystemMessage(content=routing_prompt),
            HumanMessage(content=f"질문: {state.query}"),
        ]

        # LLM 호출
        response = self.llm.invoke(messages)
        agent_type = response.content.strip().lower()

        # 유효성 검증
        if agent_type not in ["schedule", "todo", "unknown"]:
            # 키워드 기반 폴백
            query_lower = state.query.lower()
            if any(
                kw in query_lower for kw in ["일정", "회의", "약속", "캘린더", "시간"]
            ):
                agent_type = "schedule"
            elif any(
                kw in query_lower for kw in ["할일", "태스크", "작업", "추가", "완료"]
            ):
                agent_type = "todo"
            else:
                agent_type = "unknown"

        if self.verbose:
            print(f"   → Agent 유형: {agent_type}")

        return {"agent_type": agent_type}

    def _route_decision(self, state: SupervisorState) -> str:
        """
        라우팅 결정 함수

        Conditional Edge에서 사용되어 다음 Node를 결정합니다.

        Args:
            state: 현재 상태

        Returns:
            str: 다음 Node 이름 (schedule, todo, unknown)
        """
        return state.agent_type

    def _execute_schedule(self, state: SupervisorState) -> dict:
        """
        Schedule Agent 실행 Node

        Args:
            state: 현재 상태

        Returns:
            dict: 업데이트된 상태 (response 포함)
        """
        if self.verbose:
            print("\n📅 ScheduleAgent 실행 중...")

        try:
            response = self.schedule_agent.chat(state.query)
        except Exception as e:
            response = f"일정 처리 중 오류가 발생했습니다: {e}"

        if self.verbose:
            print("   ✅ 완료")

        return {"response": response}

    def _execute_todo(self, state: SupervisorState) -> dict:
        """
        Todo Agent 실행 Node

        Args:
            state: 현재 상태

        Returns:
            dict: 업데이트된 상태 (response 포함)
        """
        if self.verbose:
            print("\n✅ TodoAgent 실행 중...")

        try:
            response = self.todo_agent.chat(state.query)
        except Exception as e:
            response = f"할일 처리 중 오류가 발생했습니다: {e}"

        if self.verbose:
            print("   ✅ 완료")

        return {"response": response}

    def _fallback(self, state: SupervisorState) -> dict:
        """
        Fallback Node: 알 수 없는 요청 처리

        Args:
            state: 현재 상태

        Returns:
            dict: 업데이트된 상태 (response 포함)
        """
        if self.verbose:
            print("\n❓ Fallback: 처리할 수 없는 요청")

        response = """죄송합니다. 해당 요청을 처리할 수 없습니다.

현재 지원하는 기능:
- 📅 일정 관리: 일정 생성, 조회, 빈 시간 찾기
- ✅ 할일 관리: 할일 추가, 조회, 완료 처리

예시:
- "내일 오후 2시에 팀 회의 잡아줘"
- "장보기 할일 추가해줘"
- "오늘 할일 목록 보여줘"
"""
        return {"response": response}

    def chat(self, query: str) -> str:
        """
        메인 인터페이스

        사용자 질문을 받아 적절한 Agent에게 위임하고 결과를 반환합니다.

        Args:
            query: 사용자 질문

        Returns:
            str: Agent 응답
        """
        if self.verbose:
            print("\n" + "=" * 60)
            print("🤖 Supervisor: 새 요청 수신")
            print("=" * 60)

        # 초기 상태 생성 (TypedDict는 모든 필드 명시)
        initial_state: SupervisorState = {
            "query": query,
            "agent_type": "unknown",
            "response": "",
        }

        # 그래프 실행
        result = self.app.invoke(initial_state)

        if self.verbose:
            print("\n" + "=" * 60)
            print("🏁 처리 완료")
            print("=" * 60)

        return result["response"]

    def invoke(self, query: str) -> dict:
        """
        상세 결과 반환용 인터페이스

        Args:
            query: 사용자 질문

        Returns:
            dict: 전체 상태 (query, agent_type, response)
        """
        initial_state: SupervisorState = {
            "query": query,
            "agent_type": "unknown",
            "response": "",
        }
        return self.app.invoke(initial_state)

    def get_mermaid(self) -> str:
        """Mermaid 다이어그램반환"""
        return self.app.get_graph().draw_mermaid()

    def save_graph_image(self, output_path: str = "graph.png") -> None:
        """그래프를 PNG 이미지로 저장"""
        self.app.get_graph().draw_mermaid_png(output_file_path=output_path)

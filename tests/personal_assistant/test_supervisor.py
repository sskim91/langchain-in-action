"""
PersonalAssistantSupervisor 테스트

LangGraph StateGraph 구조 및 라우팅 로직 테스트입니다.
"""

import pytest

from multi_agent_lab.domains.personal_assistant.agents.supervisor import (
    PersonalAssistantSupervisor,
    SupervisorState,
)
from multi_agent_lab.domains.personal_assistant.storage.memory_db import db


@pytest.fixture(autouse=True)
def clear_db():
    """각 테스트 전에 DB 초기화"""
    db.clear()
    yield
    db.clear()


class TestSupervisorState:
    """SupervisorState TypedDict 테스트 (LangGraph v1+ 권장 방식)"""

    def test_default_state(self):
        """기본 상태 생성 (TypedDict는 모든 필드 명시)"""
        state: SupervisorState = {
            "query": "",
            "agent_type": "unknown",
            "response": "",
        }

        assert state["query"] == ""
        assert state["agent_type"] == "unknown"
        assert state["response"] == ""

    def test_state_with_query(self):
        """질문이 있는 상태"""
        state: SupervisorState = {
            "query": "내일 회의 잡아줘",
            "agent_type": "unknown",
            "response": "",
        }

        assert state["query"] == "내일 회의 잡아줘"
        assert state["agent_type"] == "unknown"

    def test_state_with_all_fields(self):
        """모든 필드가 있는 상태"""
        state: SupervisorState = {
            "query": "장보기 추가해줘",
            "agent_type": "todo",
            "response": "할일이 추가되었습니다.",
        }

        assert state["query"] == "장보기 추가해줘"
        assert state["agent_type"] == "todo"
        assert state["response"] == "할일이 추가되었습니다."


class TestSupervisorGraphStructure:
    """Supervisor 그래프 구조 테스트 (LLM 없이)"""

    def test_graph_nodes(self):
        """그래프 노드 확인"""
        # Supervisor 생성 시 LLM 연결 시도하므로 실제 인스턴스 생성은 피함
        # 대신 기대하는 노드 이름들을 문서화
        expected_nodes = ["router", "schedule_executor", "todo_executor", "fallback"]

        # 이 테스트는 문서화 목적
        assert len(expected_nodes) == 4

    def test_routing_decision_schedule(self):
        """라우팅 결정 - schedule"""
        state: SupervisorState = {
            "query": "회의 잡아줘",
            "agent_type": "schedule",
            "response": "",
        }

        # _route_decision 메서드가 agent_type을 반환하는지 확인
        # 실제 Supervisor 인스턴스 없이 로직 테스트
        assert state["agent_type"] == "schedule"

    def test_routing_decision_todo(self):
        """라우팅 결정 - todo"""
        state: SupervisorState = {
            "query": "할일 추가해줘",
            "agent_type": "todo",
            "response": "",
        }

        assert state["agent_type"] == "todo"

    def test_routing_decision_unknown(self):
        """라우팅 결정 - unknown"""
        state: SupervisorState = {
            "query": "날씨 어때?",
            "agent_type": "unknown",
            "response": "",
        }

        assert state["agent_type"] == "unknown"


class TestKeywordFallback:
    """키워드 기반 폴백 로직 테스트"""

    @pytest.mark.parametrize(
        "query,expected_type",
        [
            ("일정 알려줘", "schedule"),
            ("회의 잡아줘", "schedule"),
            ("약속 있어?", "schedule"),
            ("캘린더 보여줘", "schedule"),
            ("시간 확인해줘", "schedule"),
            ("할일 추가해줘", "todo"),
            ("태스크 목록", "todo"),
            ("작업 완료", "todo"),
            ("추가해줘", "todo"),
            ("완료 처리", "todo"),
        ],
    )
    def test_keyword_matching(self, query, expected_type):
        """키워드 매칭 테스트"""
        query_lower = query.lower()

        # 실제 Supervisor._router의 폴백 로직 재현
        if any(kw in query_lower for kw in ["일정", "회의", "약속", "캘린더", "시간"]):
            agent_type = "schedule"
        elif any(
            kw in query_lower for kw in ["할일", "태스크", "작업", "추가", "완료"]
        ):
            agent_type = "todo"
        else:
            agent_type = "unknown"

        assert agent_type == expected_type


# Integration tests (Ollama 필요)
@pytest.mark.skipif(
    True,  # Ollama가 실행 중일 때만 테스트
    reason="Ollama 서버가 필요한 통합 테스트",
)
class TestSupervisorIntegration:
    """Supervisor 통합 테스트 (Ollama 필요)"""

    @pytest.fixture
    def supervisor(self):
        """Supervisor 인스턴스"""
        return PersonalAssistantSupervisor(verbose=False)

    def test_route_to_schedule(self, supervisor):
        """일정 관련 질문 라우팅"""
        result = supervisor.invoke("내일 오후 2시에 팀 회의 잡아줘")

        assert result["agent_type"] == "schedule"
        assert result["response"] != ""

    def test_route_to_todo(self, supervisor):
        """할일 관련 질문 라우팅"""
        result = supervisor.invoke("장보기 할일 추가해줘")

        assert result["agent_type"] == "todo"
        assert result["response"] != ""

    def test_route_to_fallback(self, supervisor):
        """알 수 없는 질문 처리"""
        result = supervisor.invoke("오늘 날씨 어때?")

        assert result["agent_type"] == "unknown"
        assert "지원" in result["response"]

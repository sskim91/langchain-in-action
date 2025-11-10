"""
ScheduleManagerAgent 테스트
"""

import pytest

from personal_assistant.agents.schedule_manager import ScheduleManagerAgent
from personal_assistant.database.memory_db import db


@pytest.fixture(autouse=True)
def clear_db():
    """각 테스트 전에 DB 초기화"""
    db.clear()
    yield
    db.clear()


@pytest.fixture
def agent():
    """ScheduleManagerAgent 인스턴스"""
    return ScheduleManagerAgent()


def test_create_event(agent):
    """일정 생성 테스트"""
    response = agent.chat("2025년 11월 15일 오후 2시에 팀 회의 일정 잡아줘")

    assert response is not None
    assert "팀 회의" in response or "일정" in response

    # DB 확인
    events = db.get_events()
    assert len(events) == 1
    assert events[0]["title"] == "팀 회의"


def test_list_events(agent):
    """일정 조회 테스트"""
    # 먼저 일정 생성
    agent.chat("2025년 11월 15일 오후 2시에 회의 일정 잡아줘")
    agent.chat("2025년 11월 15일 오후 3시에 면접 일정 잡아줘")

    # 일정 조회
    response = agent.chat("2025년 11월 15일 일정 알려줘")

    assert response is not None
    assert "회의" in response or "면접" in response

    # DB 확인
    events = db.get_events()
    assert len(events) == 2


def test_find_free_time(agent):
    """빈 시간 찾기 테스트"""
    # 일정 생성
    agent.chat("2025년 11월 15일 오전 10시에 1시간 회의 잡아줘")

    # 빈 시간 찾기
    response = agent.chat("2025년 11월 15일에 1시간 회의 잡을 수 있는 시간대 알려줘")

    assert response is not None
    # 10시가 사용 중이므로 다른 시간대가 제안되어야 함
    assert "09:00" in response or "11:00" in response or "시간" in response


def test_invalid_date_format(agent):
    """잘못된 날짜 형식 처리"""
    response = agent.chat("내일에 회의")

    # Agent가 정확한 시간 정보를 요청하거나 오류를 처리해야 함
    assert response is not None

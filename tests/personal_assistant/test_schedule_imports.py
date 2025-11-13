"""
ScheduleManagerAgent import 테스트 (빠른 테스트)
"""

import sys
from pathlib import Path


def test_imports():
    """Import 테스트"""
    # PYTHONPATH에 src 추가
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

    from multi_agent_lab.domains.personal_assistant.agents.schedule_manager import (
        ScheduleManagerAgent,
    )
    from multi_agent_lab.domains.personal_assistant.storage.memory_db import db
    from multi_agent_lab.domains.personal_assistant.tools.schedule_tools import (
        create_event,
        find_free_time,
        list_events,
    )

    assert ScheduleManagerAgent is not None
    assert db is not None
    assert create_event is not None
    assert list_events is not None
    assert find_free_time is not None


def test_agent_initialization():
    """Agent 초기화 테스트"""
    # PYTHONPATH에 src 추가
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

    from multi_agent_lab.domains.personal_assistant.agents.schedule_manager import (
        ScheduleManagerAgent,
    )

    agent = ScheduleManagerAgent()
    assert agent is not None
    assert agent.llm is not None
    assert len(agent.tools) == 3

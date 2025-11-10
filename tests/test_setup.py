"""환경 설정 테스트"""

import sys
from pathlib import Path


def test_python_version():
    """Python 버전 확인"""
    assert sys.version_info >= (3, 11), "Python 3.11 이상이 필요합니다"


def test_langchain_import():
    """LangChain 임포트 확인"""
    try:
        from langchain_core.tools import tool
        from langchain_ollama import ChatOllama

        assert tool is not None
        assert ChatOllama is not None
    except ImportError as e:
        raise AssertionError(f"LangChain 라이브러리를 찾을 수 없습니다: {e}")


def test_personal_assistant_structure():
    """프로젝트 구조 확인"""
    project_root = Path(__file__).parent.parent
    personal_assistant = project_root / "src" / "personal_assistant"

    assert personal_assistant.exists(), "personal_assistant 모듈이 없습니다"
    assert (personal_assistant / "agents").exists(), "agents 디렉토리가 없습니다"
    assert (personal_assistant / "tools").exists(), "tools 디렉토리가 없습니다"
    assert (personal_assistant / "models").exists(), "models 디렉토리가 없습니다"
    assert (personal_assistant / "database").exists(), "database 디렉토리가 없습니다"


def test_memory_db_import():
    """MemoryDB 임포트 확인"""
    # PYTHONPATH에 src 추가
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from personal_assistant.database import MemoryDB, db

    assert MemoryDB is not None
    assert db is not None


def test_memory_db_basic_operations():
    """MemoryDB 기본 동작 확인"""
    # PYTHONPATH에 src 추가
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from personal_assistant.database import db

    # 초기화
    db.clear()

    # 이벤트 추가
    event = db.add_event({"title": "테스트 일정", "start_time": "2025-11-15 14:00"})
    assert event["id"] == "EVT001"
    assert event["title"] == "테스트 일정"

    # 이벤트 조회
    events = db.get_events()
    assert len(events) == 1
    assert events[0]["id"] == "EVT001"

    # 태스크 추가
    task = db.add_task({"title": "테스트 할일", "completed": False})
    assert task["id"] == "TASK001"

    # 노트 추가
    note = db.add_note({"title": "테스트 메모", "content": "내용"})
    assert note["id"] == "NOTE001"

    # 정리
    db.clear()

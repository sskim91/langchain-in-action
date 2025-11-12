# Step 01: 프로젝트 구조 설정

## 목표

개인비서 Agent 구현을 위한 프로젝트 디렉토리 구조를 설정하고, 필요한 의존성을 설치합니다.

## 현재 상태 확인

```bash
# 프로젝트 루트 확인
pwd
# /Users/sskim/dev/langchain-in-action

# 현재 구조
tree -L 2 -I '__pycache__|*.pyc|.venv|.git'
```

현재 구조:
```
langchain-in-action/
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
├── docs/
│   ├── AGENT_CONCEPTS.md
│   ├── PROJECT_ROADMAP.md
│   ├── SKILL_CARD_GUIDE.md
│   └── implementation/
└── src/
    ├── __init__.py
    ├── agents/
    ├── tools/
    ├── utils/
    ├── examples/
    └── tests/
```

## 1. 디렉토리 구조 확장

개인비서 Agent를 위한 디렉토리를 추가로 생성합니다:

```bash
# src/ 하위에 개인비서 관련 디렉토리 생성
mkdir -p src/personal_assistant/agents
mkdir -p src/personal_assistant/tools
mkdir -p src/personal_assistant/skill_cards
mkdir -p src/personal_assistant/models
mkdir -p src/personal_assistant/database

# 테스트 디렉토리
mkdir -p tests/personal_assistant
```

### 최종 디렉토리 구조

```
src/
├── __init__.py
├── agents/                      # 기존 BaseAgent 등
│   ├── __init__.py
│   ├── base.py
│   └── factory.py
├── tools/                       # 기존 basic tools
│   ├── __init__.py
│   ├── basic.py
│   └── file_tools.py
├── utils/                       # 공통 유틸리티
│   ├── __init__.py
│   ├── config.py
│   └── helpers.py
├── personal_assistant/          # ← 새로 추가
│   ├── __init__.py
│   ├── agents/                  # 개인비서 Agent들
│   │   ├── __init__.py
│   │   ├── schedule_manager.py
│   │   ├── todo_manager.py
│   │   └── knowledge_manager.py
│   ├── tools/                   # 개인비서 Tools
│   │   ├── __init__.py
│   │   ├── schedule_tools.py
│   │   ├── todo_tools.py
│   │   └── knowledge_tools.py
│   ├── skill_cards/             # Skill Card JSON
│   │   ├── __init__.py
│   │   ├── schedule_card.json
│   │   ├── todo_card.json
│   │   └── knowledge_card.json
│   ├── models/                  # 데이터 모델 (Pydantic)
│   │   ├── __init__.py
│   │   ├── event.py
│   │   ├── task.py
│   │   └── note.py
│   └── database/                # 인메모리 DB (나중에 SQLite)
│       ├── __init__.py
│       └── memory_db.py
├── examples/                    # 사용 예제
│   ├── __init__.py
│   ├── 01_basic_agent.py
│   └── 02_file_agent.py
└── tests/                       # 테스트
    ├── __init__.py
    └── personal_assistant/
        ├── __init__.py
        ├── test_schedule_agent.py
        ├── test_todo_agent.py
        └── test_knowledge_agent.py
```

## 2. 필요한 의존성 추가

```bash
# LangChain 관련
uv add langchain-core
uv add langchain-ollama
uv add langchain-community

# 데이터 모델
uv add pydantic

# 날짜/시간 처리
uv add python-dateutil

# 테스트
uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev pytest-cov

# 타입 체크
uv add --dev mypy
uv add --dev ruff
```

## 3. 기본 파일 생성

### 3.1 `src/personal_assistant/__init__.py`

```python
"""
Personal Assistant AI Agent System

일정 관리, 할 일 관리, 지식 관리를 제공하는 개인비서 Agent 시스템
"""

__version__ = "0.1.0"

from src.personal_assistant.agents.schedule_manager import ScheduleManagerAgent
from src.personal_assistant.agents.todo_manager import TodoManagerAgent
from src.personal_assistant.agents.knowledge_manager import KnowledgeManagerAgent

__all__ = [
    "ScheduleManagerAgent",
    "TodoManagerAgent",
    "KnowledgeManagerAgent",
]
```

### 3.2 `src/personal_assistant/models/__init__.py`

```python
"""
Data models for Personal Assistant
"""

from src.personal_assistant.models.event import Event, EventCreate
from src.personal_assistant.models.task import Task, TaskCreate
from src.personal_assistant.models.note import Note, NoteCreate

__all__ = [
    "Event",
    "EventCreate",
    "Task",
    "TaskCreate",
    "Note",
    "NoteCreate",
]
```

### 3.3 `src/personal_assistant/database/memory_db.py`

```python
"""
In-memory database for development and testing
나중에 SQLite나 PostgreSQL로 교체 가능
"""

from typing import Any


class MemoryDB:
    """간단한 인메모리 데이터베이스"""

    def __init__(self):
        self._events: list[dict[str, Any]] = []
        self._tasks: list[dict[str, Any]] = []
        self._notes: list[dict[str, Any]] = []

    def add_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """일정 추가"""
        event["id"] = f"EVT{len(self._events) + 1:03d}"
        self._events.append(event)
        return event

    def get_events(self) -> list[dict[str, Any]]:
        """모든 일정 조회"""
        return self._events.copy()

    def add_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """할 일 추가"""
        task["id"] = f"TASK{len(self._tasks) + 1:03d}"
        self._tasks.append(task)
        return task

    def get_tasks(self, completed: bool | None = None) -> list[dict[str, Any]]:
        """할 일 조회"""
        if completed is None:
            return self._tasks.copy()
        return [t for t in self._tasks if t.get("completed") == completed]

    def add_note(self, note: dict[str, Any]) -> dict[str, Any]:
        """메모 추가"""
        note["id"] = f"NOTE{len(self._notes) + 1:03d}"
        self._notes.append(note)
        return note

    def search_notes(self, query: str) -> list[dict[str, Any]]:
        """메모 검색 (단순 텍스트 매칭)"""
        query_lower = query.lower()
        return [
            n for n in self._notes
            if query_lower in n.get("title", "").lower()
            or query_lower in n.get("content", "").lower()
        ]

    def clear(self):
        """모든 데이터 삭제 (테스트용)"""
        self._events.clear()
        self._tasks.clear()
        self._notes.clear()


# 전역 DB 인스턴스 (싱글톤)
db = MemoryDB()
```

## 4. 설정 파일 업데이트

### 4.1 `pyproject.toml` 확인

기존 `pyproject.toml`에 다음 내용이 있는지 확인:

```toml
[project]
name = "langchain-in-action"
version = "0.1.0"
description = "LangChain + Ollama Personal Assistant Agent"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "langchain-core>=1.0.0",
    "langchain-ollama>=1.0.0",
    "langchain-community>=1.0.0",
    "pydantic>=2.0.0",
    "python-dateutil>=2.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

## 5. 환경 확인

### 5.1 Python 버전 확인

```bash
python --version
# Python 3.11.x 이상이어야 함
```

### 5.2 Ollama 실행 확인

```bash
# Ollama 서버 실행 확인
ollama list

# gpt-oss:20b 모델 확인
ollama pull gpt-oss:20b

# 테스트 실행
ollama run gpt-oss:20b "안녕하세요"
```

### 5.3 의존성 설치 확인

```bash
# uv로 의존성 동기화
uv sync

# 설치된 패키지 확인
uv pip list | grep langchain
```

## 6. 테스트 실행

간단한 테스트를 작성하여 환경이 제대로 설정되었는지 확인:

### `tests/test_setup.py`

```python
"""환경 설정 테스트"""

def test_python_version():
    """Python 버전 확인"""
    import sys
    assert sys.version_info >= (3, 11)


def test_langchain_import():
    """LangChain 임포트 확인"""
    from langchain_core.tools import tool
    from langchain_ollama import ChatOllama

    assert tool is not None
    assert ChatOllama is not None


def test_personal_assistant_structure():
    """프로젝트 구조 확인"""
    import os
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    personal_assistant = project_root / "src" / "personal_assistant"

    assert personal_assistant.exists()
    assert (personal_assistant / "agents").exists()
    assert (personal_assistant / "tools").exists()
    assert (personal_assistant / "models").exists()
    assert (personal_assistant / "database").exists()
```

### 테스트 실행

```bash
# 테스트 실행
pytest tests/test_setup.py -v

# 결과:
# test_setup.py::test_python_version PASSED
# test_setup.py::test_langchain_import PASSED
# test_setup.py::test_personal_assistant_structure PASSED
```

## 7. Git 커밋

```bash
# 변경사항 확인
git status

# 새 파일 추가
git add src/personal_assistant/
git add tests/test_setup.py
git add docs/implementation/

# 커밋
git commit -m "Step 01: Set up project structure for personal assistant

- Create personal_assistant module structure
- Add agents, tools, models, database directories
- Add memory database implementation
- Add setup tests
- Update dependencies in pyproject.toml"

# 푸시
git push origin main
```

## ✅ 체크리스트

완료한 항목을 체크하세요:

- [ ] 디렉토리 구조 생성 완료
- [ ] 필요한 의존성 설치 완료
- [ ] `src/personal_assistant/__init__.py` 생성
- [ ] `src/personal_assistant/database/memory_db.py` 생성
- [ ] Ollama 실행 확인
- [ ] 테스트 실행 성공
- [ ] Git 커밋 완료

## 다음 단계

모든 체크리스트 항목이 완료되었다면:

👉 **[Step 02: ScheduleManager Agent 구현](./02-schedule-manager-agent.md)** 으로 이동하세요!

## 트러블슈팅

### 문제: `uv` 명령어를 찾을 수 없음

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는
pip install uv
```

### 문제: Python 버전이 3.11 미만

```bash
# pyenv로 Python 3.11 설치
pyenv install 3.11.6
pyenv local 3.11.6
```

### 문제: Ollama 연결 안 됨

```bash
# Ollama 서버 시작
ollama serve

# 다른 터미널에서
ollama pull gpt-oss:20b
```

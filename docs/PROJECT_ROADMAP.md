# 프로젝트 로드맵

> 개인 비서 AI System - LangChain + Ollama Agent 학습 프로젝트

## 프로젝트 목표

**Multi-Agent 개인 비서 시스템을 구축하면서 Agent 개념 완전 마스터하기**

- ✅ Skill Card 개념 이해 및 구현
- ✅ Multi-Agent 시스템 구축 (일정/할일/메모 관리)
- ✅ Supervisor Agent로 자동 라우팅
- ✅ MCP Server 연동
- ✅ 실전 수준의 Agent 프레임워크 완성

---

## 현재 상태: Step 06 완료 ✅

### ✅ 완료된 것

#### Step 01-03: 기본 환경 구축
- [x] Ollama 설치 및 모델 다운로드 (`gpt-oss:20b`)
- [x] LangChain 1.0 환경 구축
- [x] BaseAgent 클래스 구현
- [x] 기본 Tool 구현 (basic.py, file_tools.py)
- [x] 간단한 Agent 실행 예제
- [x] Skill Card 시스템 구현

#### Step 04: Skill Card Executor (Static Execution Plan)
- [x] SkillCardExecutor 구현
- [x] Variable Substitution (`${variable}`)
- [x] Execution Plan 순차 실행
- [x] schedule_card.json 작성
- [x] 실습: `src/examples/07_skill_card_demo.py`

#### Step 05: Real Tool Integration
- [x] **LLM Tools**: parse_event_info (Structured Output with Pydantic)
- [x] **DB Tools**: get_calendar_events, create_event, send_notification
- [x] **Logic Tools**: find_free_time (비즈니스 로직)
- [x] **Verbose 시스템**: SkillCardExecutor verbose 모드, Tool verbose 파라미터
- [x] **Memory DB**: 간단한 in-memory 데이터베이스 구현
- [x] 실습: `src/examples/08_real_tools_demo.py`

#### Step 06: Dynamic Agent
- [x] ScheduleManagerAgent 구현
- [x] LLM이 Tool을 상황에 맞게 선택
- [x] Static vs Dynamic 비교 분석
- [x] Hybrid 접근 방법 설계
- [x] 실습: `src/examples/09_dynamic_agent.py`
- [x] 문서: `docs/static-vs-dynamic.md`

### 📁 현재 프로젝트 구조

```
langchain-in-action/
├── src/
│   ├── core/
│   │   └── skill_cards/
│   │       ├── executor.py         ✅ SkillCardExecutor (Step 04)
│   │       └── manager.py          ✅ SkillCardManager (Step 04)
│   ├── personal_assistant/
│   │   ├── agents/
│   │   │   └── schedule_manager.py ✅ ScheduleManagerAgent (Step 06)
│   │   ├── tools/
│   │   │   └── schedule_tools.py   ✅ Real Tools (Step 05)
│   │   ├── database/
│   │   │   └── memory_db.py        ✅ In-memory DB (Step 05)
│   │   └── skill_cards/
│   │       └── schedule_card.json  ✅ Skill Card 정의 (Step 04)
│   ├── examples/
│   │   ├── 01-06_*.py              ✅ 기본 예제들
│   │   ├── 07_skill_card_demo.py   ✅ Step 04 실습
│   │   ├── 08_real_tools_demo.py   ✅ Step 05 실습
│   │   └── 09_dynamic_agent.py     ✅ Step 06 실습
│   └── tests/
├── docs/
│   ├── AGENT_CONCEPTS.md           ✅ Agent 개념 (+ Dynamic Agent)
│   ├── SKILL_CARD_GUIDE.md         ✅ Skill Card 가이드 (+ Verbose)
│   ├── LEARNING_PATH.md            ✅ 학습 로드맵 (Step 05, 06 추가)
│   ├── PROJECT_ROADMAP.md          ✅ 프로젝트 계획 (현재 문서)
│   ├── static-vs-dynamic.md        ✅ Static vs Dynamic 비교
│   └── IMPLEMENTATION_SUMMARY.md   ✅ Step 05-06 구현 요약
└── README.md
```

---

## Phase 1: 기본 Agent 구현 (1주)

### 목표
- 단일 Agent의 동작 원리 완전 이해
- Tool 작성 및 연동
- Skill Card 개념 적용

---

### 1.1 단일 Agent 구현 (2-3일) ⭐

**목표:** 일정 관리 Agent 만들기

#### 구현할 Agent

```python
# src/agents/schedule_manager.py
class ScheduleManagerAgent(BaseAgent):
    """일정 관리 전문가 Agent"""

    def __init__(self):
        super().__init__(
            model_name="gpt-oss:20b",
            temperature=0.1,
            system_prompt="""
당신은 개인 비서의 일정 관리 전문가입니다.
사용자의 일정을 생성, 조회, 수정하고 알림을 설정합니다.
항상 시간 형식(YYYY-MM-DD HH:MM)을 정확히 지켜주세요.
            """,
            tools=[create_event, find_free_time, set_reminder, list_events]
        )
```

#### 구현할 Tool (4개)

**1. create_event(title, start_time, duration, location)**
```python
@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60,
    location: str = None
) -> dict:
    """
    일정 생성

    Args:
        title: 일정 제목
        start_time: 시작 시간 (YYYY-MM-DD HH:MM)
        duration: 소요 시간 (분 단위, 기본 60분)
        location: 장소 (선택)

    Returns:
        생성된 일정 정보

    Example:
        >>> create_event("팀 회의", "2025-11-11 14:00", 90, "회의실 A")
        {
            "id": "EVT001",
            "title": "팀 회의",
            "start_time": "2025-11-11 14:00",
            "end_time": "2025-11-11 15:30",
            "location": "회의실 A",
            "created": True
        }
    """
    from datetime import datetime, timedelta

    # 시간 파싱
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end = start + timedelta(minutes=duration)

    # 가짜 DB에 저장 (실전에서는 실제 DB 사용)
    event = {
        "id": f"EVT{len(EVENTS_DB) + 1:03d}",
        "title": title,
        "start_time": start_time,
        "end_time": end.strftime("%Y-%m-%d %H:%M"),
        "duration": duration,
        "location": location,
        "created": True
    }

    EVENTS_DB.append(event)
    return event
```

**2. find_free_time(date, duration)**
```python
@tool
def find_free_time(date: str, duration: int = 60) -> list[dict]:
    """
    빈 시간 찾기

    Args:
        date: 날짜 (YYYY-MM-DD)
        duration: 필요한 시간 (분 단위)

    Returns:
        사용 가능한 시간대 리스트

    Example:
        >>> find_free_time("2025-11-11", 60)
        [
            {"start": "09:00", "end": "10:00"},
            {"start": "11:00", "end": "12:00"},
            {"start": "15:00", "end": "16:00"}
        ]
    """
    # 해당 날짜의 일정 조회
    day_events = [e for e in EVENTS_DB if e["start_time"].startswith(date)]

    # 9시~18시 중 빈 시간 찾기
    free_slots = []
    work_hours = range(9, 18)

    for hour in work_hours:
        slot_start = f"{hour:02d}:00"
        slot_end = f"{hour + 1:02d}:00"

        # 겹치는 일정 확인
        is_free = True
        for event in day_events:
            event_hour = int(event["start_time"].split()[1].split(":")[0])
            if event_hour == hour:
                is_free = False
                break

        if is_free:
            free_slots.append({
                "start": slot_start,
                "end": slot_end
            })

    return free_slots
```

**3. set_reminder(event_id, minutes_before)**
```python
@tool
def set_reminder(event_id: str, minutes_before: int = 10) -> dict:
    """
    알림 설정

    Args:
        event_id: 일정 ID
        minutes_before: 몇 분 전 알림 (기본 10분)

    Returns:
        알림 설정 정보
    """
    event = next((e for e in EVENTS_DB if e["id"] == event_id), None)

    if not event:
        return {"error": f"일정 {event_id}를 찾을 수 없습니다"}

    from datetime import datetime, timedelta

    start = datetime.strptime(event["start_time"], "%Y-%m-%d %H:%M")
    reminder_time = start - timedelta(minutes=minutes_before)

    reminder = {
        "event_id": event_id,
        "event_title": event["title"],
        "reminder_time": reminder_time.strftime("%Y-%m-%d %H:%M"),
        "message": f"{event['title']} {minutes_before}분 전입니다"
    }

    REMINDERS_DB.append(reminder)
    return reminder
```

**4. list_events(date)**
```python
@tool
def list_events(date: str = None) -> list[dict]:
    """
    일정 목록 조회

    Args:
        date: 날짜 (YYYY-MM-DD, None이면 모든 일정)

    Returns:
        일정 목록
    """
    if date:
        return [e for e in EVENTS_DB if e["start_time"].startswith(date)]
    return EVENTS_DB
```

#### 가짜 데이터베이스

```python
# src/tools/schedule_tools.py

# 가짜 DB (메모리에만 저장)
EVENTS_DB = [
    {
        "id": "EVT001",
        "title": "프로젝트 회의",
        "start_time": "2025-11-11 10:00",
        "end_time": "2025-11-11 11:00",
        "duration": 60,
        "location": "회의실 A"
    },
    {
        "id": "EVT002",
        "title": "점심 약속",
        "start_time": "2025-11-11 12:30",
        "end_time": "2025-11-11 13:30",
        "duration": 60,
        "location": "강남역 식당"
    }
]

REMINDERS_DB = []
```

#### 테스트 시나리오

```python
# tests/test_schedule_agent.py
import asyncio
from agents.schedule_manager import ScheduleManagerAgent

async def main():
    agent = ScheduleManagerAgent()

    # 테스트 1: 일정 생성
    print("=== 테스트 1: 일정 생성 ===")
    result = agent.chat("내일 오후 3시에 팀 회의 일정 잡아줘")
    print(result)

    # 테스트 2: 빈 시간 찾기
    print("\n=== 테스트 2: 빈 시간 찾기 ===")
    result = agent.chat("2025-11-11에 1시간짜리 회의 잡을 수 있는 시간 알려줘")
    print(result)

    # 테스트 3: 알림 설정
    print("\n=== 테스트 3: 알림 설정 ===")
    result = agent.chat("EVT001 일정 10분 전에 알림 설정해줘")
    print(result)

    # 테스트 4: 일정 목록
    print("\n=== 테스트 4: 일정 목록 ===")
    result = agent.chat("오늘 일정 알려줘")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 체크리스트

- [ ] `src/agents/` 폴더 생성
- [ ] `src/tools/` 폴더 생성
- [ ] `ScheduleManagerAgent` 클래스 작성
- [ ] Tool 4개 구현 (create_event, find_free_time, set_reminder, list_events)
- [ ] 가짜 DB 구현 (EVENTS_DB, REMINDERS_DB)
- [ ] 테스트 스크립트 작성 및 실행
- [ ] Tool 호출 로그 확인 (어떤 Tool이 언제 호출되는지)

**예상 소요 시간:** 2-3일

---

### 1.2 Skill Card 개념 적용 (2일)

**목표:** JSON 파일로 Agent 동작 제어하기

#### Skill Card 작성

```json
// skill_cards/SC_SCHEDULE_001.json
{
  "id": "SC_SCHEDULE_001",
  "version": "1.0.0",
  "agent_name": "일정 관리 전문가",
  "agent_type": "schedule",
  "description": "사용자의 일정을 생성, 조회, 수정하고 알림을 설정합니다",

  "trigger": {
    "keywords": ["일정", "스케줄", "미팅", "회의", "약속", "calendar"],
    "examples": [
      "내일 오후 3시에 회의 잡아줘",
      "이번 주 금요일 빈 시간 알려줘",
      "다음주 월요일 일정 알려줘"
    ],
    "similarity_threshold": 0.85
  },

  "tools": [
    {
      "name": "create_event",
      "required": false,
      "timeout_ms": 3000,
      "retry": 1
    },
    {
      "name": "find_free_time",
      "required": false,
      "timeout_ms": 2000,
      "retry": 0
    },
    {
      "name": "set_reminder",
      "required": false,
      "timeout_ms": 2000,
      "retry": 0
    },
    {
      "name": "list_events",
      "required": false,
      "timeout_ms": 2000,
      "retry": 0
    }
  ],

  "constraints": {
    "time_format": "YYYY-MM-DD HH:MM",
    "max_response_length": 500,
    "tone": "friendly",
    "language": "ko"
  },

  "llm_config": {
    "model": "gpt-oss:20b",
    "temperature": 0.1,
    "max_tokens": 300
  },

  "examples": [
    {
      "user": "내일 오후 3시에 팀 회의 잡아줘",
      "expected_tool": "create_event",
      "expected_params": {
        "title": "팀 회의",
        "start_time": "2025-11-12 15:00",
        "duration": 60
      }
    },
    {
      "user": "내일 빈 시간 알려줘",
      "expected_tool": "find_free_time",
      "expected_params": {
        "date": "2025-11-12"
      }
    }
  ]
}
```

#### Skill Card Manager 구현

```python
# src/skill_cards/skill_card_manager.py
import json
from pathlib import Path
from typing import Optional

class SkillCardManager:
    """Skill Card 로드 및 관리"""

    def __init__(self, cards_dir: str = "skill_cards"):
        self.cards_dir = Path(cards_dir)
        self.cards = {}
        self._load_all_cards()

    def _load_all_cards(self):
        """모든 Skill Card 로드"""
        if not self.cards_dir.exists():
            self.cards_dir.mkdir(parents=True)
            return

        for card_file in self.cards_dir.glob("*.json"):
            with open(card_file, encoding='utf-8') as f:
                card = json.load(f)
                self.cards[card["id"]] = card

    def get(self, card_id: str) -> Optional[dict]:
        """Skill Card 조회"""
        return self.cards.get(card_id)

    def validate(self, card: dict) -> bool:
        """Skill Card 유효성 검증"""
        required_fields = ["id", "agent_name", "agent_type", "tools"]

        for field in required_fields:
            if field not in card:
                print(f"Missing required field: {field}")
                return False

        return True

    def list_all(self) -> list[dict]:
        """모든 Skill Card 목록"""
        return [
            {
                "id": card["id"],
                "name": card["agent_name"],
                "type": card["agent_type"],
                "description": card.get("description", "")
            }
            for card in self.cards.values()
        ]
```

#### 체크리스트

- [ ] `skill_cards/` 폴더 생성
- [ ] `SC_SCHEDULE_001.json` 작성
- [ ] `SkillCardManager` 클래스 구현
- [ ] Skill Card 로드 테스트
- [ ] Skill Card 유효성 검증 테스트

**예상 소요 시간:** 2일

---

### 1.3 Tool 고도화 (2일)

**목표:** 나머지 2개 Agent의 Tool 구현

#### TodoManager Agent Tools

```python
# src/tools/todo_tools.py
from datetime import datetime
from langchain_core.tools import tool

TODO_DB = [
    {
        "id": "TODO001",
        "title": "프로젝트 문서 작성",
        "description": "Agent 개념 정리 문서 작성하기",
        "priority": "high",
        "status": "pending",
        "due_date": "2025-11-15",
        "created_at": "2025-11-10"
    }
]

@tool
def add_task(title: str, description: str = "", priority: str = "medium", due_date: str = None) -> dict:
    """
    할 일 추가

    Args:
        title: 작업 제목
        description: 작업 설명
        priority: 우선순위 (low/medium/high)
        due_date: 마감일 (YYYY-MM-DD)

    Returns:
        생성된 작업 정보
    """
    task = {
        "id": f"TODO{len(TODO_DB) + 1:03d}",
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "due_date": due_date,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    TODO_DB.append(task)
    return task

@tool
def list_tasks(status: str = None, priority: str = None) -> list[dict]:
    """
    할 일 목록 조회

    Args:
        status: 상태 필터 (pending/done/all)
        priority: 우선순위 필터 (low/medium/high)

    Returns:
        작업 목록
    """
    tasks = TODO_DB

    if status and status != "all":
        tasks = [t for t in tasks if t["status"] == status]

    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]

    return tasks

@tool
def complete_task(task_id: str) -> dict:
    """작업 완료 처리"""
    task = next((t for t in TODO_DB if t["id"] == task_id), None)

    if not task:
        return {"error": f"작업 {task_id}를 찾을 수 없습니다"}

    task["status"] = "done"
    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return task

@tool
def prioritize_tasks() -> list[dict]:
    """
    우선순위 기반 작업 정렬

    Returns:
        정렬된 작업 목록 (high → medium → low, 마감일 빠른 순)
    """
    priority_order = {"high": 0, "medium": 1, "low": 2}

    pending_tasks = [t for t in TODO_DB if t["status"] == "pending"]

    sorted_tasks = sorted(
        pending_tasks,
        key=lambda t: (
            priority_order[t["priority"]],
            t.get("due_date", "9999-12-31")
        )
    )

    return sorted_tasks
```

#### KnowledgeManager Agent Tools

```python
# src/tools/knowledge_tools.py
from datetime import datetime
from langchain_core.tools import tool

NOTES_DB = [
    {
        "id": "NOTE001",
        "title": "Agent 개념",
        "content": "Agent = LLM + Tools + Memory + 실행 로직",
        "tags": ["ai", "agent", "concept"],
        "created_at": "2025-11-10 10:00"
    }
]

@tool
def save_note(title: str, content: str, tags: list[str] = None) -> dict:
    """
    메모 저장

    Args:
        title: 메모 제목
        content: 메모 내용
        tags: 태그 리스트

    Returns:
        저장된 메모 정보
    """
    note = {
        "id": f"NOTE{len(NOTES_DB) + 1:03d}",
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": None
    }
    NOTES_DB.append(note)
    return note

@tool
def search_notes(keyword: str) -> list[dict]:
    """
    메모 검색

    Args:
        keyword: 검색 키워드 (제목, 내용, 태그에서 검색)

    Returns:
        검색된 메모 목록
    """
    keyword_lower = keyword.lower()

    results = []
    for note in NOTES_DB:
        if (keyword_lower in note["title"].lower() or
            keyword_lower in note["content"].lower() or
            any(keyword_lower in tag.lower() for tag in note["tags"])):
            results.append(note)

    return results

@tool
def list_notes_by_tag(tag: str) -> list[dict]:
    """태그별 메모 조회"""
    return [n for n in NOTES_DB if tag in n["tags"]]

@tool
def update_note(note_id: str, title: str = None, content: str = None, tags: list[str] = None) -> dict:
    """메모 수정"""
    note = next((n for n in NOTES_DB if n["id"] == note_id), None)

    if not note:
        return {"error": f"메모 {note_id}를 찾을 수 없습니다"}

    if title:
        note["title"] = title
    if content:
        note["content"] = content
    if tags:
        note["tags"] = tags

    note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return note
```

#### 체크리스트

- [ ] `src/tools/todo_tools.py` 작성 (4개 함수)
- [ ] `src/tools/knowledge_tools.py` 작성 (4개 함수)
- [ ] 각 Tool별 단위 테스트
- [ ] Tool Docstring 작성 (LLM이 이해하기 쉽게)

**예상 소요 시간:** 2일

---

## Phase 2: Multi-Agent 시스템 (1주)

### 목표
- 3개 Agent 모두 구현
- Supervisor Agent로 자동 라우팅
- Agent 간 역할 분담

---

### 2.1 Agent 3개 구현 (3일)

**작업 내용:**

```python
# 1. ScheduleManagerAgent (Phase 1에서 완성)
# 2. TodoManagerAgent (새로 구현)
# 3. KnowledgeManagerAgent (새로 구현)
```

#### TodoManagerAgent

```python
# src/agents/todo_manager.py
from .base import BaseAgent
from ..tools.todo_tools import add_task, list_tasks, complete_task, prioritize_tasks

class TodoManagerAgent(BaseAgent):
    """할 일 관리 Agent"""

    def __init__(self):
        super().__init__(
            model_name="gpt-oss:20b",
            temperature=0.2,
            system_prompt="""
당신은 개인 비서의 할 일 관리 전문가입니다.
사용자의 작업을 추가, 조회, 완료 처리하고 우선순위를 관리합니다.
항상 마감일을 고려하여 우선순위를 제안하세요.
            """,
            tools=[add_task, list_tasks, complete_task, prioritize_tasks]
        )
```

#### KnowledgeManagerAgent

```python
# src/agents/knowledge_manager.py
from .base import BaseAgent
from ..tools.knowledge_tools import save_note, search_notes, list_notes_by_tag, update_note

class KnowledgeManagerAgent(BaseAgent):
    """메모/지식 관리 Agent"""

    def __init__(self):
        super().__init__(
            model_name="gpt-oss:20b",
            temperature=0.5,  # 더 창의적인 메모 작성
            system_prompt="""
당신은 개인 비서의 지식 관리 전문가입니다.
사용자의 메모를 저장, 검색, 정리하고 태그를 자동으로 추천합니다.
메모를 저장할 때는 핵심 내용을 요약하여 저장하세요.
            """,
            tools=[save_note, search_notes, list_notes_by_tag, update_note]
        )
```

#### 각 Agent별 Skill Card

**SC_TODO_001.json:**
```json
{
  "id": "SC_TODO_001",
  "agent_name": "할 일 관리 전문가",
  "agent_type": "todo",
  "trigger": {
    "keywords": ["할일", "작업", "태스크", "todo", "완료", "우선순위"],
    "examples": [
      "프로젝트 문서 작성을 할 일에 추가해줘",
      "오늘 할 일 알려줘",
      "TODO001 완료 처리해줘"
    ]
  },
  "tools": ["add_task", "list_tasks", "complete_task", "prioritize_tasks"]
}
```

**SC_KNOWLEDGE_001.json:**
```json
{
  "id": "SC_KNOWLEDGE_001",
  "agent_name": "메모/지식 관리 전문가",
  "agent_type": "knowledge",
  "trigger": {
    "keywords": ["메모", "노트", "기록", "저장", "검색", "note"],
    "examples": [
      "Python Agent 개념을 메모해줘",
      "AI 관련 메모 찾아줘",
      "학습한 내용 정리해줘"
    ]
  },
  "tools": ["save_note", "search_notes", "list_notes_by_tag", "update_note"]
}
```

#### 체크리스트

- [ ] `TodoManagerAgent` 구현
- [ ] `KnowledgeManagerAgent` 구현
- [ ] `SC_TODO_001.json` 작성
- [ ] `SC_KNOWLEDGE_001.json` 작성
- [ ] 각 Agent 개별 테스트

**예상 소요 시간:** 3일

---

### 2.2 Supervisor Agent 구현 (2-3일)

**목표:** 질의를 분석하여 자동으로 적절한 Agent 선택

#### Supervisor Agent 구현

```python
# src/supervisor/supervisor_agent.py
from typing import Optional

class SupervisorAgent:
    """Agent 선택 및 실행 관리자"""

    def __init__(self):
        from agents.schedule_manager import ScheduleManagerAgent
        from agents.todo_manager import TodoManagerAgent
        from agents.knowledge_manager import KnowledgeManagerAgent

        # 모든 Agent 인스턴스화
        self.agents = {
            "schedule": ScheduleManagerAgent(),
            "todo": TodoManagerAgent(),
            "knowledge": KnowledgeManagerAgent()
        }

    def classify_query(self, query: str) -> str:
        """
        질의 분류 (간단한 키워드 기반)

        나중에 VectorDB + Embedding으로 업그레이드 예정
        """
        query_lower = query.lower()

        # 일정 관련 키워드
        schedule_keywords = ["일정", "스케줄", "미팅", "회의", "약속", "calendar", "알림"]
        if any(keyword in query_lower for keyword in schedule_keywords):
            return "schedule"

        # 할 일 관련 키워드
        todo_keywords = ["할일", "작업", "태스크", "todo", "완료", "우선순위"]
        if any(keyword in query_lower for keyword in todo_keywords):
            return "todo"

        # 메모 관련 키워드
        knowledge_keywords = ["메모", "노트", "기록", "저장", "검색", "note", "정리"]
        if any(keyword in query_lower for keyword in knowledge_keywords):
            return "knowledge"

        # 기본값 (일정 관리)
        return "schedule"

    async def route(self, query: str, context: dict = {}) -> dict:
        """
        질의 라우팅 및 실행

        Args:
            query: 사용자 질의
            context: 컨텍스트 정보

        Returns:
            {
                "agent_type": str,
                "query": str,
                "answer": str,
                "tools_used": list[str]
            }
        """
        # 1. Agent 분류
        agent_type = self.classify_query(query)
        print(f"[Supervisor] Selected Agent: {agent_type}")

        # 2. Agent 선택
        agent = self.agents[agent_type]

        # 3. Agent 실행
        answer = agent.chat(query)

        return {
            "agent_type": agent_type,
            "query": query,
            "answer": answer,
            "tools_used": []  # 나중에 추적 기능 추가
        }
```

#### 테스트 시나리오

```python
# tests/test_supervisor.py
import asyncio
from supervisor.supervisor_agent import SupervisorAgent

async def main():
    supervisor = SupervisorAgent()

    test_cases = [
        # 일정 관리
        ("내일 오후 3시에 팀 회의 잡아줘", "schedule"),
        ("이번 주 금요일 빈 시간 알려줘", "schedule"),

        # 할 일 관리
        ("프로젝트 문서 작성을 할 일에 추가해줘", "todo"),
        ("오늘 할 일 알려줘", "todo"),

        # 메모/지식 관리
        ("Python Agent 개념을 메모해줘", "knowledge"),
        ("AI 관련 메모 찾아줘", "knowledge")
    ]

    for query, expected_agent in test_cases:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Expected Agent: {expected_agent}")
        print(f"{'='*60}")

        result = await supervisor.route(query)

        print(f"Selected Agent: {result['agent_type']}")
        print(f"Answer: {result['answer']}")

        # 검증
        assert result['agent_type'] == expected_agent, \
            f"Expected {expected_agent}, but got {result['agent_type']}"

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 체크리스트

- [ ] `SupervisorAgent` 클래스 구현
- [ ] 키워드 기반 분류 로직
- [ ] Agent 선택 및 실행 로직
- [ ] 6가지 테스트 케이스 실행
- [ ] 로그 출력 (어떤 Agent가 선택되었는지)

**예상 소요 시간:** 2-3일

---

### 2.3 FastAPI 통합 (1-2일)

**목표:** REST API로 서비스 제공

#### FastAPI 애플리케이션

```python
# src/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from supervisor.supervisor_agent import SupervisorAgent
import time

app = FastAPI(
    title="개인 비서 AI System",
    description="Multi-Agent 기반 일정/할일/메모 관리 시스템",
    version="1.0.0"
)

supervisor = SupervisorAgent()

class ChatRequest(BaseModel):
    query: str
    context: dict = {}

class ChatResponse(BaseModel):
    agent_type: str
    query: str
    answer: str
    tools_used: list[str] = []
    execution_time: float

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 엔드포인트

    사용자 질의를 분석하여 적절한 Agent에게 라우팅합니다.
    """
    start = time.time()

    # Supervisor 실행
    result = await supervisor.route(request.query, request.context)

    execution_time = time.time() - start

    return ChatResponse(
        agent_type=result["agent_type"],
        query=request.query,
        answer=result["answer"],
        tools_used=result.get("tools_used", []),
        execution_time=execution_time
    )

@app.get("/agents")
async def list_agents():
    """사용 가능한 Agent 목록"""
    return {
        "agents": [
            {
                "type": "schedule",
                "name": "일정 관리 전문가",
                "description": "일정 생성, 조회, 알림 설정",
                "keywords": ["일정", "스케줄", "미팅", "회의"]
            },
            {
                "type": "todo",
                "name": "할 일 관리 전문가",
                "description": "작업 추가, 조회, 우선순위 관리",
                "keywords": ["할일", "작업", "태스크", "완료"]
            },
            {
                "type": "knowledge",
                "name": "메모/지식 관리 전문가",
                "description": "메모 저장, 검색, 태그 관리",
                "keywords": ["메모", "노트", "기록", "검색"]
            }
        ]
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 테스트

```bash
# 서버 실행
python src/main.py

# 테스트 1: 일정 생성
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "내일 오후 3시에 팀 회의 잡아줘"}'

# 테스트 2: 할 일 추가
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "프로젝트 문서 작성을 할 일에 추가해줘"}'

# 테스트 3: 메모 저장
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Agent는 LLM과 Tools의 조합이다 라고 메모해줘"}'

# Agent 목록 조회
curl http://localhost:8000/agents
```

#### 체크리스트

- [ ] FastAPI 앱 구현
- [ ] `/chat` 엔드포인트
- [ ] `/agents` 엔드포인트
- [ ] `/health` 엔드포인트
- [ ] Request/Response 모델 정의
- [ ] 실행 시간 측정
- [ ] curl 테스트

**예상 소요 시간:** 1-2일

---

## Phase 3: Skill Card 고도화 (1주)

### 3.1 VectorDB 연동 (3일)
### 3.2 Execution Plan 구현 (2일)
### 3.3 Constraints 적용 (2일)

**상세 내용은 Phase 3 착수 시 작성 예정**

---

## Phase 4: 실전 기능 (2주)

### 4.1 캐싱 (Redis) (3일)
### 4.2 로깅 (Trace ID) (3일)
### 4.3 모니터링 (Prometheus) (3-4일)
### 4.4 간단한 Admin 페이지 (3-4일)

**상세 내용은 Phase 4 착수 시 작성 예정**

---

## Phase 5: RAG 구현 (1주)

### 5.1 문서 로드 및 임베딩 (3일)
### 5.2 RAG Tool 작성 (2일)
### 5.3 Agent에 RAG 통합 (2일)

**상세 내용은 Phase 5 착수 시 작성 예정**

---

## 예상 일정

| Phase | 기간 | 주요 내용 | 상태 |
|-------|------|----------|------|
| **Step 01-03** | 완료 | 기본 환경 구축, BaseAgent, 기본 Tool | ✅ **완료** |
| **Step 04** | 완료 | Skill Card Executor, Static Execution Plan | ✅ **완료** |
| **Step 05** | 완료 | Real Tool Integration (LLM/DB/Logic Tools, Verbose) | ✅ **완료** |
| **Step 06** | 완료 | Dynamic Agent (vs Static 비교) | ✅ **완료** |
| **Step 07** | 예정 | VectorDB 연동 (Skill Card 검색) | 🎯 **다음** |
| **Step 08** | 예정 | Multi-Agent System (Todo, Knowledge Agent 추가) | ⏳ 대기 |
| **Step 09** | 예정 | Supervisor Agent (자동 라우팅) | ⏳ 대기 |
| **Step 10+** | 예정 | 캐싱, 로깅, 모니터링, Admin | ⏳ 대기 |

---

## 다음 단계: Step 07 - VectorDB 연동 🎯

**현재 위치:** Step 06 완료 → Step 07 대기 중

**Step 07 목표:**
- VectorDB (FAISS 또는 ChromaDB) 설정
- Skill Card 임베딩 생성
- 유사도 기반 Skill Card 검색
- 키워드 매칭 → 의미 기반 매칭으로 업그레이드

**완료된 기반 작업:**
1. ✅ Skill Card 시스템 구현 (Step 04)
2. ✅ Real Tool Integration (Step 05)
3. ✅ Dynamic Agent 구현 (Step 06)
4. ✅ Static vs Dynamic 비교 분석

**다음 학습 주제:** RAG (Retrieval-Augmented Generation)

---

**프로젝트:** 개인 비서 AI System 🤖
**작성일:** 2025-11-10
**버전:** 1.0.0

# Step 02: ScheduleManager Agent 구현

## 목표

일정 관리 기능을 제공하는 `ScheduleManagerAgent`를 구현합니다.

## 사전 준비

- [Step 01: 프로젝트 구조 설정](./01-project-setup.md) 완료
- Ollama 실행 중 (`gpt-oss:20b` 모델 준비)

## 1. 데이터 모델 정의

먼저 일정(Event) 데이터 모델을 정의합니다.

### `src/personal_assistant/models/event.py`

```python
"""
Event 데이터 모델
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EventBase(BaseModel):
    """Event 기본 모델"""

    title: str = Field(..., min_length=1, max_length=200, description="일정 제목")
    start_time: str = Field(..., description="시작 시간 (YYYY-MM-DD HH:MM)")
    duration: int = Field(60, gt=0, le=1440, description="소요 시간 (분)")
    location: Optional[str] = Field(None, max_length=200, description="장소")
    description: Optional[str] = Field(None, max_length=1000, description="상세 설명")

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        """시작 시간 형식 검증"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
            return v
        except ValueError:
            raise ValueError("시작 시간은 'YYYY-MM-DD HH:MM' 형식이어야 합니다")


class EventCreate(EventBase):
    """Event 생성 요청"""

    pass


class Event(EventBase):
    """Event (DB에 저장된)"""

    id: str = Field(..., description="일정 ID")
    end_time: str = Field(..., description="종료 시간 (YYYY-MM-DD HH:MM)")
    created_at: str = Field(..., description="생성 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "EVT001",
                "title": "팀 회의",
                "start_time": "2025-11-15 14:00",
                "end_time": "2025-11-15 15:00",
                "duration": 60,
                "location": "회의실 A",
                "description": "프로젝트 진행 상황 공유",
                "created_at": "2025-11-10 10:30:00",
            }
        }
```

## 2. 일정 관리 Tools 작성

이 부분은 다음 단계([Step 03](./03-schedule-tools.md))에서 자세히 다루므로, 여기서는 간단한 버전만 작성합니다.

### `src/personal_assistant/tools/schedule_tools.py`

```python
"""
일정 관리 Tools
"""

from datetime import datetime, timedelta
from typing import Optional

from langchain_core.tools import tool

from src.personal_assistant.database.memory_db import db


@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60,
    location: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    새로운 일정 생성

    Args:
        title: 일정 제목
        start_time: 시작 시간 (YYYY-MM-DD HH:MM 형식)
        duration: 소요 시간 (분, 기본값: 60)
        location: 장소 (선택)
        description: 상세 설명 (선택)

    Returns:
        dict: 생성된 일정 정보

    Example:
        >>> event = create_event(
        ...     title="팀 회의",
        ...     start_time="2025-11-15 14:00",
        ...     duration=60
        ... )
        >>> print(event["id"])
        'EVT001'
    """
    # 시작 시간 파싱
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    end = start + timedelta(minutes=duration)

    # 일정 데이터 생성
    event = {
        "title": title,
        "start_time": start_time,
        "end_time": end.strftime("%Y-%m-%d %H:%M"),
        "duration": duration,
        "location": location,
        "description": description,
        "created_at": datetime.now().isoformat(),
    }

    # DB에 저장
    saved_event = db.add_event(event)

    return {
        "success": True,
        "event": saved_event,
        "message": f"일정 '{title}'이(가) {start_time}에 생성되었습니다.",
    }


@tool
def list_events(
    date: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    일정 목록 조회

    Args:
        date: 특정 날짜 (YYYY-MM-DD 형식, None이면 전체)
        limit: 최대 조회 개수 (기본값: 10)

    Returns:
        dict: 일정 목록

    Example:
        >>> events = list_events(date="2025-11-15")
        >>> print(len(events["events"]))
        3
    """
    all_events = db.get_events()

    # 날짜 필터링
    if date:
        all_events = [
            e for e in all_events if e["start_time"].startswith(date)
        ]

    # 시작 시간 순으로 정렬
    all_events.sort(key=lambda x: x["start_time"])

    # 제한
    events = all_events[:limit]

    return {
        "total": len(all_events),
        "count": len(events),
        "events": events,
    }


@tool
def find_free_time(date: str, duration: int = 60) -> dict:
    """
    특정 날짜의 비어있는 시간대 찾기

    Args:
        date: 날짜 (YYYY-MM-DD 형식)
        duration: 필요한 시간 (분)

    Returns:
        dict: 사용 가능한 시간대 목록

    Example:
        >>> slots = find_free_time(date="2025-11-15", duration=60)
        >>> print(slots["available_slots"][0])
        '09:00-10:00'
    """
    # 해당 날짜의 일정 조회
    events = db.get_events()
    date_events = [e for e in events if e["start_time"].startswith(date)]

    # 업무 시간 (09:00 ~ 18:00)
    work_start = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
    work_end = datetime.strptime(f"{date} 18:00", "%Y-%m-%d %H:%M")

    # 사용 중인 시간대 수집
    busy_slots = []
    for event in date_events:
        start = datetime.strptime(event["start_time"], "%Y-%m-%d %H:%M")
        end = datetime.strptime(event["end_time"], "%Y-%m-%d %H:%M")
        busy_slots.append((start, end))

    # 비어있는 시간대 찾기
    available_slots = []
    current = work_start

    busy_slots.sort()  # 시작 시간 순 정렬

    for busy_start, busy_end in busy_slots:
        if (busy_start - current).total_seconds() >= duration * 60:
            slot_end = current + timedelta(minutes=duration)
            available_slots.append(
                f"{current.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
            )
        current = max(current, busy_end)

    # 마지막 여유 시간
    if (work_end - current).total_seconds() >= duration * 60:
        slot_end = current + timedelta(minutes=duration)
        available_slots.append(
            f"{current.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
        )

    return {
        "date": date,
        "duration": duration,
        "available_slots": available_slots,
        "count": len(available_slots),
    }
```

## 3. ScheduleManagerAgent 구현

### `src/personal_assistant/agents/schedule_manager.py`

```python
"""
일정 관리 Agent
"""

from typing import Any, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.personal_assistant.tools.schedule_tools import (
    create_event,
    find_free_time,
    list_events,
)


class ScheduleManagerAgent:
    """
    일정 관리 전문 Agent

    사용자의 일정을 생성, 조회하고 비어있는 시간대를 찾아주는 Agent입니다.
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
    ):
        """
        Args:
            model_name: Ollama 모델명
            temperature: 생성 온도 (0.0 ~ 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature

        # LLM 초기화
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
        )

        # Tools 설정
        self.tools = [create_event, list_events, find_free_time]

        # System Prompt
        self.system_prompt = """당신은 일정 관리 전문가입니다.

사용자의 일정을 효율적으로 관리하고, 다음 작업을 수행합니다:

1. **일정 생성**: 사용자가 요청한 일정을 생성합니다.
2. **일정 조회**: 특정 날짜 또는 전체 일정을 조회합니다.
3. **빈 시간 찾기**: 회의나 약속을 잡을 수 있는 시간대를 찾아줍니다.

**주의사항:**
- 시작 시간은 반드시 'YYYY-MM-DD HH:MM' 형식으로 파싱하세요.
- 과거 날짜에는 일정을 생성하지 마세요.
- 비어있는 시간대를 제안할 때는 구체적으로 알려주세요.

항상 한국어로 응답하세요."""

        # Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Agent 생성
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        # Agent Executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    def chat(self, message: str) -> str:
        """
        간단한 채팅 인터페이스

        Args:
            message: 사용자 메시지

        Returns:
            str: Agent 응답

        Example:
            >>> agent = ScheduleManagerAgent()
            >>> response = agent.chat("내일 오후 2시에 팀 회의 일정 잡아줘")
            >>> print(response)
            '일정 "팀 회의"가 2025-11-15 14:00에 생성되었습니다.'
        """
        result = self.executor.invoke({"input": message})
        return result["output"]

    def invoke(self, message: str, **kwargs) -> dict[str, Any]:
        """
        Agent 실행 (상세 결과 포함)

        Args:
            message: 사용자 메시지
            **kwargs: 추가 파라미터

        Returns:
            dict: Agent 실행 결과
        """
        return self.executor.invoke({"input": message}, **kwargs)
```

## 4. 테스트 작성

### `tests/personal_assistant/test_schedule_agent.py`

```python
"""
ScheduleManagerAgent 테스트
"""

import pytest

from src.personal_assistant.agents.schedule_manager import ScheduleManagerAgent
from src.personal_assistant.database.memory_db import db


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
    response = agent.chat("내일 오후 2시에 팀 회의 일정 잡아줘")

    assert response is not None
    assert "팀 회의" in response or "일정" in response

    # DB 확인
    events = db.get_events()
    assert len(events) == 1
    assert events[0]["title"] == "팀 회의"


def test_list_events(agent):
    """일정 조회 테스트"""
    # 먼저 일정 생성
    agent.chat("11월 15일 오후 2시에 회의 일정 잡아줘")
    agent.chat("11월 15일 오후 3시에 면접 일정 잡아줘")

    # 일정 조회
    response = agent.chat("11월 15일 일정 알려줘")

    assert response is not None
    assert "회의" in response or "면접" in response

    # DB 확인
    events = db.get_events()
    assert len(events) == 2


def test_find_free_time(agent):
    """빈 시간 찾기 테스트"""
    # 일정 생성
    agent.chat("11월 15일 오전 10시에 1시간 회의 잡아줘")

    # 빈 시간 찾기
    response = agent.chat("11월 15일에 1시간 회의 잡을 수 있는 시간대 알려줘")

    assert response is not None
    # 10시가 사용 중이므로 다른 시간대가 제안되어야 함
    assert "09:00" in response or "11:00" in response or "시간" in response


def test_invalid_date_format(agent):
    """잘못된 날짜 형식 처리"""
    response = agent.chat("내일에 회의")

    # Agent가 정확한 시간 정보를 요청하거나 오류를 처리해야 함
    assert response is not None
```

## 5. 실행 예제 작성

### `src/examples/03_schedule_agent.py`

```python
"""
일정 관리 Agent 사용 예제
"""

from src.personal_assistant.agents.schedule_manager import ScheduleManagerAgent


def main():
    """ScheduleManagerAgent 예제"""
    print("=" * 60)
    print("일정 관리 Agent 데모")
    print("=" * 60)
    print()

    # Agent 생성
    agent = ScheduleManagerAgent()

    # 테스트 질의들
    queries = [
        "2025년 11월 15일 오후 2시에 팀 회의 일정 잡아줘. 회의실 A에서 1시간 동안 해.",
        "2025년 11월 15일 일정 보여줘",
        "2025년 11월 15일에 1시간 회의 잡을 수 있는 시간대 알려줘",
        "내일 오전 10시에 고객 미팅 일정 추가해줘",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"[질문 {i}] {query}")
        print(f"{'='*60}")

        try:
            response = agent.chat(query)
            print(f"\n[답변]\n{response}")
        except Exception as e:
            print(f"\n[오류] {e}")

        print()

    print("=" * 60)
    print("데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

## 6. 실행 및 테스트

### 테스트 실행

```bash
# 단위 테스트 실행
pytest tests/personal_assistant/test_schedule_agent.py -v

# 커버리지 포함
pytest tests/personal_assistant/test_schedule_agent.py --cov=src/personal_assistant/agents
```

### 예제 실행

```bash
# Ollama 실행 확인
ollama list | grep gpt-oss

# 예제 실행
python -m src.examples.03_schedule_agent
```

## 7. Git 커밋

```bash
git add src/personal_assistant/models/event.py
git add src/personal_assistant/tools/schedule_tools.py
git add src/personal_assistant/agents/schedule_manager.py
git add tests/personal_assistant/test_schedule_agent.py
git add src/examples/03_schedule_agent.py

git commit -m "Step 02: Implement ScheduleManagerAgent

- Add Event data model with Pydantic validation
- Implement schedule management tools (create, list, find_free_time)
- Create ScheduleManagerAgent with LangChain
- Add comprehensive tests
- Add usage example

Closes: Personal Assistant Phase 1 - Schedule Management"

git push origin main
```

## ✅ 체크리스트

- [ ] `Event` 모델 정의 완료
- [ ] 일정 관리 Tools 구현 완료
- [ ] `ScheduleManagerAgent` 구현 완료
- [ ] 테스트 작성 및 통과
- [ ] 예제 코드 실행 성공
- [ ] Git 커밋 완료

## 다음 단계

👉 **[Step 03: 일정 관리 Tools 개발](./03-schedule-tools.md)** 에서 더 고급 기능을 추가하세요!

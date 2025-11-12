# 개인비서 AI 구현 가이드

> 실전에서 바로 사용할 수 있는 구현 가이드입니다.

## 목차

1. [Tool 작성 가이드](#tool-작성-가이드)
2. [Verbose 디버깅](#verbose-디버깅)
3. [Skill Card 작성](#skill-card-작성)
4. [Agent 구현](#agent-구현)
5. [베스트 프랙티스](#베스트-프랙티스)

---

## Tool 작성 가이드

### 1. LLM Tool: 정보 추출

LLM을 활용하여 자연어에서 구조화된 정보 추출

```python
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from datetime import datetime

class EventInfo(BaseModel):
    """일정 정보 구조"""
    title: str = Field(description="일정 제목")
    date: str = Field(description="날짜 (YYYY-MM-DD)")
    time: str = Field(description="시간 (HH:MM, 24시간제)")
    duration: int = Field(default=60, description="소요 시간 (분)")

@tool
def parse_event_info(query: str, verbose: bool = False) -> dict:
    """
    자연어에서 일정 정보 추출

    Args:
        query: 사용자 질의 (예: "내일 오후 2시에 팀 회의")
        verbose: 디버깅 정보 출력 여부

    Returns:
        추출된 일정 정보
    """
    # verbose 모드 설정
    if verbose:
        from langchain_core.globals import set_debug
        set_debug(True)

    # LLM + Structured Output
    llm = ChatOllama(model="gpt-oss:20b", temperature=0.0)
    structured_llm = llm.with_structured_output(EventInfo)

    # 현재 날짜 제공 (상대적 날짜 파싱용)
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    prompt = f"""오늘 날짜: {today_str}

사용자 요청: {query}

위 요청에서 일정 정보를 추출하세요.
- "내일" = 오늘 +1일
- "오후 2시" = 14:00
- 시간 미지정 시 09:00
"""

    result: EventInfo = structured_llm.invoke(prompt)
    return result.model_dump()
```

### 2. DB Tool: 데이터 조작

데이터베이스 조회/저장 (현재는 in-memory, 실전에서는 PostgreSQL 등)

```python
from datetime import datetime, timedelta

# 가상 DB (메모리)
EVENTS_DB = []

@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60,
    location: str | None = None
) -> dict:
    """
    새로운 일정 생성

    Args:
        title: 일정 제목
        start_time: 시작 시간 (YYYY-MM-DD HH:MM)
        duration: 소요 시간 (분, 기본 60)
        location: 장소 (선택)

    Returns:
        생성된 일정 정보
    """
    # 시간 파싱
    try:
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except ValueError as e:
        return {
            "success": False,
            "error": f"잘못된 시간 형식: {start_time}"
        }

    end = start + timedelta(minutes=duration)

    # 일정 생성
    event = {
        "id": f"EVT{len(EVENTS_DB) + 1:03d}",
        "title": title,
        "start_time": start_time,
        "end_time": end.strftime("%Y-%m-%d %H:%M"),
        "duration": duration,
        "location": location,
        "created_at": datetime.now().isoformat()
    }

    EVENTS_DB.append(event)

    return {
        "success": True,
        "event": event,
        "message": f"일정 '{title}'이(가) 생성되었습니다."
    }

@tool
def list_events(date: str | None = None) -> dict:
    """
    일정 목록 조회

    Args:
        date: 날짜 (YYYY-MM-DD, None이면 전체)

    Returns:
        일정 목록
    """
    events = EVENTS_DB

    if date:
        events = [e for e in events if e["start_time"].startswith(date)]

    # 시작 시간 순 정렬
    events.sort(key=lambda x: x["start_time"])

    return {
        "total": len(events),
        "events": events
    }
```

### 3. Logic Tool: 비즈니스 로직

복잡한 계산이나 비즈니스 로직 실행

```python
@tool
def find_free_time(date: str, duration: int = 60) -> dict:
    """
    비어있는 시간대 찾기

    Args:
        date: 날짜 (YYYY-MM-DD)
        duration: 필요한 시간 (분)

    Returns:
        사용 가능한 시간대 목록
    """
    # 해당 날짜의 일정 조회
    events = [e for e in EVENTS_DB if e["start_time"].startswith(date)]

    # 업무 시간 (09:00 ~ 18:00)
    work_start = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
    work_end = datetime.strptime(f"{date} 18:00", "%Y-%m-%d %H:%M")

    # 사용 중인 시간대
    busy_slots = []
    for event in events:
        start = datetime.strptime(event["start_time"], "%Y-%m-%d %H:%M")
        end = datetime.strptime(event["end_time"], "%Y-%m-%d %H:%M")
        busy_slots.append((start, end))

    # 빈 시간 찾기
    available_slots = []
    current = work_start

    busy_slots.sort()

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

    # 첫 번째 슬롯을 best_slot으로 선택
    best_slot = None
    if available_slots:
        first_slot = available_slots[0]
        start_time, end_time = first_slot.split("-")
        best_slot = {
            "start": f"{date} {start_time}",
            "end": f"{date} {end_time}"
        }

    return {
        "date": date,
        "duration": duration,
        "available_slots": available_slots,
        "count": len(available_slots),
        "best_slot": best_slot
    }
```

### Tool 작성 체크리스트

- [ ] **명확한 Docstring**: LLM이 이해하기 쉽게
- [ ] **타입 힌트**: 모든 파라미터와 리턴값에 타입 지정
- [ ] **에러 처리**: try-except로 예외 처리
- [ ] **검증 로직**: 입력값 검증
- [ ] **verbose 지원**: 디버깅용 verbose 파라미터 (선택)

---

## Verbose 디버깅

### 1. SkillCardExecutor에서 사용

```python
from core.skill_cards import SkillCardExecutor, SkillCardManager

# Skill Card 로드
manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")

# verbose=True로 Executor 생성
executor = SkillCardExecutor(card, verbose=True)

# 실행
result = executor.execute(
    user_query="내일 오후 2시에 팀 회의",
    context={"user_id": "user123"}
)
```

### 2. 출력 예시

```
================================================================================
  🚀 Skill Card Executor 시작
================================================================================
📋 Skill Card: SC_SCHEDULE_001 v1.0.0
👤 질의: "내일 오후 2시에 팀 회의"
📦 컨텍스트: {'user_id': 'user123'}
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📍 Step 1/5: parse_event_info
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 실행: parse_event_info(
  query = "내일 오후 2시에 팀 회의"
)

✅ 성공!
💾 저장: variables['event_data'] = {
  'title': '팀 회의',
  'date': '2025-11-13',
  'time': '14:00',
  'duration': 60
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📍 Step 2/5: get_calendar_events
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 실행: get_calendar_events(
  date = "2025-11-13"  ← ${event_data.date}
)

✅ 성공!
💾 저장: variables['existing_events'] = [...]

[... Step 3, 4, 5 ...]

================================================================================
  ✨ 실행 완료!
================================================================================
⏱️  총 소요 시간: 3.24초
✅ 성공 Step: 5개
❌ 실패 Step: 0개
================================================================================
```

### 3. 디버깅 레벨

| 레벨 | 출력 내용 | 사용 시기 |
|------|-----------|----------|
| `verbose=False` | 결과만 | 프로덕션 |
| `verbose=True` | Step 실행 + Tool 호출 | 개발/테스트 |
| LangChain Debug | LLM 내부 프롬프트까지 | 심층 디버깅 |

**LangChain Debug 활성화:**
```python
from langchain_core.globals import set_debug

set_debug(True)  # 전역 설정
```

### 4. 실전 활용

**개발 중:**
```python
# 새 Tool 개발 시 verbose로 확인
executor = SkillCardExecutor(card, verbose=True)
result = executor.execute(query)
# → 각 Step 성공/실패, 전달된 데이터 확인
```

**프로덕션:**
```python
# 기본은 verbose=False
executor = SkillCardExecutor(card, verbose=False)

# 에러 시만 verbose=True로 재실행
try:
    result = executor.execute(query)
except Exception as e:
    logger.error(f"실행 실패: {e}")
    result = executor.execute(query, verbose=True)
    # 로그 저장
```

**단위 테스트:**
```python
def test_schedule_creation():
    """일정 생성 테스트"""
    executor = SkillCardExecutor(card, verbose=True)

    result = executor.execute(
        user_query="내일 오후 2시에 회의"
    )

    assert result["success"] is True
    assert result["event"]["title"] == "회의"
```

---

## Skill Card 작성

### 기본 구조

```json
{
  "id": "SC_SCHEDULE_001",
  "version": "1.0.0",
  "agent_name": "일정 관리 전문가",
  "description": "일정 생성, 조회, 수정, 삭제",

  "tools": [
    "parse_event_info",
    "get_calendar_events",
    "find_free_time",
    "create_event",
    "send_notification"
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "parse_event_info",
      "input": {"query": "${user_query}"},
      "output_to": "event_data"
    },
    {
      "step": 2,
      "action": "find_free_time",
      "input": {
        "date": "${event_data.date}",
        "duration": "${event_data.duration}"
      },
      "output_to": "free_slots"
    },
    {
      "step": 3,
      "action": "create_event",
      "input": {
        "title": "${event_data.title}",
        "start_time": "${free_slots.best_slot.start}",
        "duration": "${event_data.duration}"
      },
      "output_to": "created_event"
    }
  ],

  "constraints": {
    "validation": [
      "과거 날짜 일정 생성 금지",
      "일정 제목 필수"
    ]
  }
}
```

### Variable Substitution

`${변수명}` 또는 `${변수명.필드명}` 형태로 이전 Step 결과 참조

```json
{
  "step": 2,
  "action": "create_event",
  "input": {
    "title": "${event_data.title}",        // Step 1 결과의 title
    "start_time": "${event_data.date}",    // Step 1 결과의 date
    "duration": "${event_data.duration}"   // Step 1 결과의 duration
  }
}
```

---

## Agent 구현

### Dynamic Agent (추천)

```python
from personal_assistant.agents.schedule_manager import ScheduleManagerAgent

# Agent 생성
agent = ScheduleManagerAgent()

# 실행
response = agent.chat("내일 오후 2시에 팀 회의 잡아줘")
print(response)

# LLM이 필요한 Tool만 선택적으로 사용
```

### Static Agent (Skill Card Executor)

```python
from core.skill_cards import SkillCardExecutor, SkillCardManager

# Skill Card 로드
manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")

# Executor 생성
executor = SkillCardExecutor(card, verbose=False)

# 실행
result = executor.execute(
    user_query="내일 오후 2시에 팀 회의",
    context={"user_id": "user123"}
)
```

---

## 베스트 프랙티스

### 1. Tool Docstring 작성

```python
@tool
def create_event(title: str, start_time: str) -> dict:
    """
    새로운 일정 생성  ← 1줄 요약 (LLM이 Tool 선택 시 참고)

    이 함수는 사용자가 요청한 일정을 생성합니다.  ← 상세 설명
    시작 시간과 제목이 필수입니다.

    Args:  ← 파라미터 설명 (LLM이 파라미터 추론 시 참고)
        title: 일정 제목 (예: "팀 회의", "점심 약속")
        start_time: 시작 시간 (형식: YYYY-MM-DD HH:MM)

    Returns:  ← 리턴값 설명
        dict: 생성된 일정 정보
        {
            "id": "EVT001",
            "title": "팀 회의",
            "start_time": "2025-11-13 14:00"
        }

    Example:  ← 사용 예시
        >>> create_event("팀 회의", "2025-11-13 14:00")
        {'id': 'EVT001', 'title': '팀 회의', ...}
    """
```

### 2. 에러 처리

```python
@tool
def create_event(title: str, start_time: str) -> dict:
    """일정 생성"""
    try:
        # 시간 파싱
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except ValueError:
        # 에러를 dict로 반환 (LLM이 이해 가능)
        return {
            "success": False,
            "error": "잘못된 시간 형식입니다. 'YYYY-MM-DD HH:MM' 형식으로 입력해주세요."
        }

    # 성공 시
    return {
        "success": True,
        "event": {...}
    }
```

### 3. 일관된 리턴 형식

```python
# ✅ 좋은 예: 일관된 구조
{
    "success": True/False,
    "data": {...},      // success=True일 때
    "error": "...",     // success=False일 때
    "message": "..."
}

# ❌ 나쁜 예: 비일관적
True  # 성공
"에러 발생"  # 실패
```

### 4. Verbose 파라미터 추가

```python
@tool
def my_tool(param: str, verbose: bool = False) -> dict:
    """도구 설명"""
    if verbose:
        print(f"[DEBUG] my_tool 호출: param={param}")

    # 로직 실행
    result = do_something(param)

    if verbose:
        print(f"[DEBUG] my_tool 결과: {result}")

    return result
```

### 5. 단위 테스트 작성

```python
def test_create_event():
    """일정 생성 테스트"""
    result = create_event(
        title="테스트 회의",
        start_time="2025-11-13 14:00"
    )

    assert result["success"] is True
    assert result["event"]["title"] == "테스트 회의"

def test_create_event_invalid_time():
    """잘못된 시간 형식 테스트"""
    result = create_event(
        title="테스트",
        start_time="잘못된 형식"
    )

    assert result["success"] is False
    assert "error" in result
```

---

## 다음 단계

- **[concepts.md](./concepts.md)** - 핵심 개념 복습
- **[patterns.md](./patterns.md)** - Static vs Dynamic 패턴 비교
- **[step-by-step/](./step-by-step/)** - 단계별 구현 가이드
- **[roadmap.md](./roadmap.md)** - 프로젝트 로드맵

---

**작성일:** 2025-11-12
**프로젝트:** 개인비서 AI System

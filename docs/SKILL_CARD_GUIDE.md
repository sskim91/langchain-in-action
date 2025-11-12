# Skill Card 완전 가이드 및 Agent 개발자 역할

## 목차

1. [Skill Card란?](#skill-card란)
2. [왜 Skill Card가 필요한가?](#왜-skill-card가-필요한가)
3. [Skill Card vs 기존 AI Agent 패턴](#skill-card-vs-기존-ai-agent-패턴)
4. [Skill Card 구조](#skill-card-구조)
5. [Verbose 디버깅 시스템](#verbose-디버깅-시스템)
6. [Skill Card 생명주기](#skill-card-생명주기)
7. [Agent 개발자가 실제로 해야 할 일](#agent-개발자가-실제로-해야-할-일)
8. [개발 워크플로우](#개발-워크플로우)
9. [실전 예제](#실전-예제)

---

## Skill Card란?

### 정의

**Skill Card**는 AI Agent의 행동을 정의하고 관리하기 위한 **메타데이터 구조**입니다.

### 한 문장 요약

> Agent가 "무엇을 할 수 있는지", "어떻게 할 것인지", "무엇을 해서는 안 되는지"를 **JSON/DB 형태로 정의**한 것

### 기존 용어와의 관계

```
Skill Card =
  System Prompt (역할 정의)
  + Tool Schema (사용 가능 도구)
  + Workflow DAG (실행 순서)
  + Constraints (제약사항)
  + Metadata (관리 정보)
```

| 기존 AI Agent 용어 | Skill Card에서의 역할 |
|------------------|---------------------|
| System Prompt | Agent의 역할, 제약사항 정의 |
| Function Schema | 사용 가능한 Tool 목록 |
| Routing Rules | 어떤 질의에 이 Agent를 사용할지 |
| Execution Plan | Tool 호출 순서 가이드 |
| Few-shot Examples | 실행 예시 |

### 핵심 특징

✅ **코드가 아닌 데이터** - JSON/DB로 저장되어 동적 관리 가능
✅ **통제 가능** - LLM이 임의로 동작하지 않도록 제어
✅ **버전 관리** - 변경 이력 추적 및 롤백 가능
✅ **동적 선택** - VectorDB에서 유사도 기반 자동 선택
✅ **Admin 페이지에서 관리** - 코드 수정 없이 GUI로 편집

---

## 왜 Skill Card가 필요한가?

### 문제: LLM의 불확실성

#### 일반적인 Agent 구현의 문제점

```python
# 문제가 있는 방식
response = llm.chat([
    {"role": "system", "content": "너는 개인 비서야. 일정을 관리해줘."},
    {"role": "user", "content": "내일 회의 일정 추가해줘"}
])
```

**발생하는 문제:**
- 🔴 LLM이 **매번 다르게 동작**
- 🔴 어떤 Tool을 호출할지 **예측 불가**
- 🔴 추적/감사 **어려움**
- 🔴 품질 관리 **불가능**

### 해결: Skill Card로 통제

```python
# Skill Card 기반 방식
skill_card = {
    "name": "일정 관리 Agent",
    "tools": ["create_event", "find_free_time", "set_reminder"],
    "execution_plan": [
        "1. 일정 정보 파싱",
        "2. 시간대 중복 확인",
        "3. 일정 생성",
        "4. 알림 설정"
    ],
    "constraints": [
        "과거 날짜 일정 생성 금지",
        "중복 일정 경고 필수",
        "시간대 검증 필수"
    ]
}

response = agent.execute(
    query="내일 회의 일정 추가해줘",
    skill_card=skill_card
)
```

**해결된 부분:**
- ✅ **통제 가능**: 정해진 순서대로만 실행
- ✅ **예측 가능**: 항상 같은 Tool 사용
- ✅ **감사 가능**: Skill Card ID로 추적
- ✅ **버전 관리**: 변경 이력 관리
- ✅ **품질 보장**: 제약사항 강제 적용

---

## Skill Card vs 기존 AI Agent 패턴

### 1. ReAct (Reason + Act) Pattern

#### ReAct 방식

```
User: 내일 회의 일정 잡아줘

LLM: [생각] 일정 정보가 필요하다
     [행동] parse_event_info()

LLM: [생각] 시간대 확인이 필요하다
     [행동] check_availability()

LLM: [생각] 일정을 생성하자
     [행동] create_event()
```

**문제점:**
- 🔴 LLM이 매번 "생각"하므로 **비용 높음** (토큰 많이 사용)
- 🔴 **순서가 보장 안 됨** (매번 다를 수 있음)
- 🔴 **중간에 실패** 가능 (잘못된 판단)

#### Skill Card 방식

```
User: 내일 회의 일정 잡아줘

[Skill Card로 미리 정의된 실행 계획]
1. parse_event_info() ✓
2. check_availability() ✓
3. create_event() ✓
4. set_reminder() ✓

→ LLM은 최종 답변 생성만 담당 (1회 호출)
```

**장점:**
- ✅ **순서 보장**: 항상 1→2→3→4
- ✅ **비용 절감**: LLM 호출 최소화
- ✅ **안정성**: 실패 지점 명확
- ✅ **예측 가능**: 디버깅 용이

### 비교 요약

| 패턴 | 유연성 | 통제성 | 비용 | 예측성 | 실용성 |
|-----|-------|-------|-----|-------|--------|
| ReAct | ⭐⭐⭐⭐⭐ | ⭐ | 높음 | 낮음 | ⚠️ |
| Function Calling | ⭐⭐⭐⭐ | ⭐⭐ | 중간 | 중간 | ✅ |
| LangGraph | ⭐⭐⭐ | ⭐⭐⭐⭐ | 낮음 | 높음 | ✅ |
| **Skill Card** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **낮음** | **높음** | **✅✅** |

---

## Skill Card 구조

### 전체 스키마

```json
{
  "id": "SC_SCHEDULE_001",
  "version": "1.0.0",
  "agent_name": "일정 관리 전문가",
  "description": "사용자의 일정을 생성, 조회, 수정, 삭제하고 시간 관리를 도와주는 Agent",

  "trigger": {
    "keywords": ["일정", "스케줄", "약속", "회의", "미팅"],
    "intent": "일정 관리",
    "similarity_threshold": 0.85
  },

  "tools": [
    {
      "name": "create_event",
      "required": true,
      "timeout_ms": 3000,
      "retry": 2
    },
    {
      "name": "find_free_time",
      "required": false,
      "timeout_ms": 2000,
      "retry": 1
    },
    {
      "name": "set_reminder",
      "required": false,
      "timeout_ms": 1000,
      "retry": 0
    }
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "parse_event_info",
      "input": {
        "query": "${user_query}"
      },
      "output_to": "event_data",
      "on_error": "fail"
    },
    {
      "step": 2,
      "action": "find_free_time",
      "input": {
        "date": "${event_data.date}",
        "duration": "${event_data.duration}"
      },
      "output_to": "available_slots",
      "on_error": "skip"
    },
    {
      "step": 3,
      "action": "create_event",
      "input": {
        "title": "${event_data.title}",
        "start_time": "${event_data.start_time}",
        "duration": "${event_data.duration}"
      },
      "output_to": "created_event",
      "on_error": "fail"
    }
  ],

  "constraints": {
    "validation": [
      "과거 날짜 일정 생성 금지",
      "종료 시간이 시작 시간보다 앞설 수 없음",
      "일정 제목 필수"
    ],
    "output_format": "markdown",
    "max_response_length": 500,
    "language": "ko-KR"
  },

  "fallback_strategy": {
    "type": "default_response",
    "message": "죄송합니다. 일정 생성에 실패했습니다. 다시 시도해 주세요.",
    "actions": ["log_failure", "notify_user"]
  },

  "llm_config": {
    "model": "gpt-oss:20b",
    "temperature": 0.1,
    "max_tokens": 500,
    "system_prompt": "당신은 사용자의 개인 비서입니다. 일정을 효율적으로 관리하고 시간 관리를 도와주세요."
  },

  "metadata": {
    "created_at": "2025-11-10T09:00:00Z",
    "created_by": "admin",
    "last_updated": "2025-11-10T09:00:00Z",
    "updated_by": "admin",
    "usage_count": 0,
    "success_count": 0,
    "avg_success_rate": 0.0,
    "avg_response_time_ms": 0,
    "tags": ["schedule", "calendar", "time-management"]
  }
}
```

---

## Verbose 디버깅 시스템

### 개요

Skill Card 실행 시 내부 동작을 상세히 확인할 수 있는 디버깅 시스템입니다.

### 왜 필요한가?

**문제: Agent의 블랙박스 문제**
```python
# 무엇이 일어나는지 알 수 없음
result = executor.execute(user_query="내일 회의 잡아줘")
# → 성공? 실패? 어떤 Tool 호출? 무슨 데이터 전달?
```

**해결: Verbose 모드로 투명하게**
```python
# 모든 실행 과정 출력
result = executor.execute(
    user_query="내일 회의 잡아줘",
    verbose=True  # ⭐ 핵심
)
```

### 사용 방법

#### 1. SkillCardExecutor에서 사용

```python
from core.skill_cards import SkillCardExecutor, SkillCardManager

# Skill Card 로드
manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")

# Executor 생성 (verbose=True)
executor = SkillCardExecutor(card, verbose=True)

# 실행
result = executor.execute(
    user_query="내일 오후 2시에 팀 회의",
    context={"user_id": "user123"}
)
```

#### 2. Tool 내부에서 사용

```python
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

class EventInfo(BaseModel):
    title: str = Field(description="일정 제목")
    date: str = Field(description="날짜 (YYYY-MM-DD)")
    time: str = Field(description="시간 (HH:MM)")

@tool
def parse_event_info(query: str, verbose: bool = False) -> dict:
    """
    자연어에서 일정 정보 추출 (LLM 사용)

    Args:
        query: 사용자 질의
        verbose: 디버깅 정보 출력 여부
    """
    # verbose 모드일 때 LangChain 디버그 활성화
    if verbose:
        from langchain_core.globals import set_debug
        set_debug(True)

    llm = ChatOllama(model="gpt-oss:20b", temperature=0.0)
    structured_llm = llm.with_structured_output(EventInfo)

    if verbose:
        print("\n" + "=" * 80)
        print("🤖 LLM 호출 (LangChain verbose=True)")
        print("=" * 80)

    try:
        result: EventInfo = structured_llm.invoke(prompt)

        if verbose:
            print("\n✅ LLM 응답 (Structured Output):")
            print(f"  • title: {result.title}")
            print(f"  • date: {result.date}")
            print(f"  • time: {result.time}")
            print("=" * 80 + "\n")

        return result.model_dump()

    except Exception as e:
        if verbose:
            print(f"\n❌ LLM 호출 실패: {e}")
            print("=" * 80 + "\n")

        return {"error": f"일정 정보 추출 실패: {str(e)}"}
```

### Verbose 출력 예시

#### Step-by-Step 실행 추적

```
================================================================================
  🚀 Skill Card Executor 시작
================================================================================
📋 Skill Card: SC_SCHEDULE_001 v1.0.0
📝 설명: 일정 생성/조회/수정 Agent
👤 질의: "내일 오후 2시에 팀 회의"
📦 컨텍스트: {'user_id': 'user123'}
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📍 Step 1/5: parse_event_info
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 실행: parse_event_info(
  query = "내일 오후 2시에 팀 회의"
)

================================================================================
🤖 LLM 호출 (LangChain verbose=True)
================================================================================
[LangChain 내부 로그...]
Invoking: `ChatOllama` with `You are an assistant...`

✅ LLM 응답 (Structured Output):
  • title: 팀 회의
  • date: 2025-11-13
  • time: 14:00
  • duration: 60분
================================================================================

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
💾 저장: variables['existing_events'] = [
  {'id': 'EVT001', 'title': '기존 회의', 'start_time': '2025-11-13 10:00'}
]

[... Step 3, 4, 5 계속 ...]

================================================================================
  ✨ 실행 완료!
================================================================================
⏱️  총 소요 시간: 3.24초
✅ 성공 Step: 5개
❌ 실패 Step: 0개
📊 실행 결과:
  • 일정 ID: EVT002
  • 제목: 팀 회의
  • 시작: 2025-11-13 14:00
  • 알림: 전송 완료
================================================================================
```

### 디버깅 레벨

Verbose 모드는 3가지 레벨로 제공:

| 레벨 | 출력 내용 | 사용 시기 |
|-----|----------|---------|
| **False** (기본) | 결과만 | 프로덕션 |
| **True** | Step 실행 + Tool 호출 | 개발/테스트 |
| **LangChain Debug** | LLM 내부 프롬프트까지 | 디버깅 |

#### LangChain Debug 활성화

```python
from langchain_core.globals import set_debug

# 전역 설정
set_debug(True)

# Tool 실행
result = executor.execute(
    user_query="내일 회의 잡아줘",
    verbose=True
)
```

**추가 출력 내용:**
- LLM에게 전달된 실제 프롬프트
- LLM의 내부 생각 과정 (ReAct)
- Tool 선택 이유
- 각 Step의 토큰 사용량

### 실전 활용 예시

#### 예시 1: 개발 중 디버깅

```python
# 새로운 Tool 개발 중
executor = SkillCardExecutor(card, verbose=True)

# 실행하면서 각 Step 확인
result = executor.execute(
    user_query="테스트 질의",
    context={}
)

# verbose 출력을 보며 문제 지점 파악:
# - 어떤 Step에서 실패?
# - 어떤 데이터가 전달?
# - 변수 치환이 제대로 동작?
```

#### 예시 2: 프로덕션 모니터링

```python
# 프로덕션에서는 verbose=False
executor = SkillCardExecutor(card, verbose=False)

# 하지만 에러 발생 시 자동으로 verbose=True로 재실행
try:
    result = executor.execute(user_query=query, context=ctx)
except Exception as e:
    # 재실행 with verbose
    logger.error(f"실행 실패, verbose 모드로 재실행: {e}")
    result = executor.execute(user_query=query, context=ctx, verbose=True)
    # verbose 로그를 로그 파일에 저장
```

#### 예시 3: 단위 테스트

```python
def test_schedule_creation():
    """일정 생성 테스트 (verbose로 각 Step 검증)"""
    executor = SkillCardExecutor(card, verbose=True)

    result = executor.execute(
        user_query="내일 오후 2시에 회의",
        context={"user_id": "test_user"}
    )

    # verbose 출력으로 각 Step 성공 확인
    assert result["success"] is True
    assert result["event"]["title"] == "회의"
    assert result["event"]["start_time"] == "2025-11-13 14:00"
```

### 장점

✅ **투명성**: 블랙박스가 아닌 화이트박스
✅ **디버깅**: 문제 지점 즉시 파악
✅ **학습**: Agent 내부 동작 이해
✅ **테스트**: 각 Step 검증 가능
✅ **모니터링**: 프로덕션 이슈 추적

### 주의사항

⚠️ **성능**: verbose=True는 실행 속도 느림 (로그 출력 비용)
⚠️ **보안**: 민감한 데이터가 로그에 노출될 수 있음
⚠️ **로그 크기**: LLM 프롬프트 전체가 출력되어 용량 큼

**권장 사항:**
- 개발/테스트: verbose=True
- 프로덕션: verbose=False (에러 시만 True)
- 민감 데이터: 로그 마스킹 적용

---

## 실전 예제

### 예제 1: "할 일 관리 Agent" 개발

#### 1단계: Skill Card 설계

```json
{
  "id": "SC_TODO_001",
  "version": "1.0.0",
  "agent_name": "할 일 관리자",
  "description": "사용자의 할 일 목록을 관리하고 우선순위를 설정하며 완료 상태를 추적합니다.",

  "trigger": {
    "keywords": ["할일", "TODO", "작업", "태스크", "완료"],
    "intent": "할 일 관리",
    "similarity_threshold": 0.85
  },

  "tools": [
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "prioritize_tasks"
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "parse_task_info",
      "input": {"query": "${user_query}"},
      "output_to": "task_data",
      "timeout_ms": 1000,
      "on_error": "fail"
    },
    {
      "step": 2,
      "action": "add_task",
      "input": {
        "title": "${task_data.title}",
        "priority": "${task_data.priority}",
        "due_date": "${task_data.due_date}"
      },
      "output_to": "new_task",
      "timeout_ms": 2000,
      "on_error": "fail"
    },
    {
      "step": 3,
      "action": "prioritize_tasks",
      "input": {"task_id": "${new_task.id}"},
      "output_to": "updated_priorities",
      "timeout_ms": 2000,
      "on_error": "skip"
    }
  ],

  "constraints": {
    "validation": [
      "작업 제목 필수",
      "우선순위는 1-5 사이",
      "마감일은 현재 또는 미래 날짜"
    ],
    "output_format": "markdown",
    "max_response_length": 500
  },

  "llm_config": {
    "model": "gpt-oss:20b",
    "temperature": 0.1,
    "max_tokens": 400
  }
}
```

#### 2단계: Tool 구현

```python
from langchain_core.tools import tool
from datetime import datetime
from typing import Optional

# 메모리 DB (실제로는 SQLite나 PostgreSQL 사용)
TASKS_DB = []

@tool
def add_task(
    title: str,
    priority: int = 3,
    due_date: Optional[str] = None,
    description: str = ""
) -> dict:
    """
    새로운 할 일 추가

    Args:
        title: 작업 제목 (필수)
        priority: 우선순위 (1=높음, 5=낮음)
        due_date: 마감일 (YYYY-MM-DD 형식)
        description: 작업 설명

    Returns:
        dict: 생성된 작업 정보

    Example:
        >>> task = add_task("프로젝트 문서 작성", priority=1, due_date="2025-11-15")
        >>> print(task["id"])
        'TASK_001'
    """
    task_id = f"TASK_{len(TASKS_DB) + 1:03d}"

    task = {
        "id": task_id,
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

    TASKS_DB.append(task)

    return {
        "id": task_id,
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "message": f"작업 '{title}'이(가) 추가되었습니다."
    }


@tool
def list_tasks(
    status: str = "all",
    priority: Optional[int] = None
) -> dict:
    """
    할 일 목록 조회

    Args:
        status: 상태 필터 ("all", "pending", "completed")
        priority: 우선순위 필터 (1-5)

    Returns:
        dict: 작업 목록
    """
    filtered_tasks = TASKS_DB.copy()

    # 상태 필터
    if status == "pending":
        filtered_tasks = [t for t in filtered_tasks if not t["completed"]]
    elif status == "completed":
        filtered_tasks = [t for t in filtered_tasks if t["completed"]]

    # 우선순위 필터
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]

    # 우선순위와 마감일로 정렬
    filtered_tasks.sort(key=lambda x: (x["priority"], x["due_date"] or "9999-12-31"))

    return {
        "total": len(filtered_tasks),
        "tasks": filtered_tasks
    }


@tool
def complete_task(task_id: str) -> dict:
    """
    할 일 완료 표시

    Args:
        task_id: 작업 ID

    Returns:
        dict: 완료된 작업 정보
    """
    for task in TASKS_DB:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            return {
                "id": task_id,
                "title": task["title"],
                "message": f"작업 '{task['title']}'을(를) 완료했습니다!"
            }

    raise ValueError(f"작업 ID {task_id}를 찾을 수 없습니다.")


@tool
def prioritize_tasks(task_list: list[dict]) -> dict:
    """
    작업 우선순위 자동 조정

    Args:
        task_list: 작업 목록

    Returns:
        dict: 우선순위가 조정된 작업 목록
    """
    # 마감일이 가까운 순으로 우선순위 자동 조정
    today = datetime.now().date()

    for task in task_list:
        if task.get("due_date"):
            due = datetime.fromisoformat(task["due_date"]).date()
            days_left = (due - today).days

            if days_left < 0:
                task["priority"] = 1  # 마감 지남
            elif days_left <= 1:
                task["priority"] = min(task["priority"], 2)  # 오늘/내일
            elif days_left <= 3:
                task["priority"] = min(task["priority"], 3)  # 이번 주

    return {
        "updated_count": len(task_list),
        "tasks": sorted(task_list, key=lambda x: x["priority"])
    }
```

#### 3단계: Agent 실행 예제

```python
from src import create_simple_agent
from src.tools import add_task, list_tasks, complete_task, prioritize_tasks

# Agent 생성
agent = create_simple_agent(
    model_name="gpt-oss:20b",
    temperature=0.1,
    tools=[add_task, list_tasks, complete_task, prioritize_tasks],
    system_prompt="""당신은 할 일 관리 전문가입니다.
사용자의 작업을 효율적으로 관리하고 우선순위를 제안해주세요.
항상 한국어로 응답하세요."""
)

# 사용 예시
print("=" * 60)
print("할 일 관리 Agent 실행")
print("=" * 60)

# 1. 할 일 추가
response1 = agent.chat("프로젝트 문서 작성 작업 추가해줘. 마감일은 11월 15일이야.")
print(f"\n[응답 1]\n{response1}\n")

# 2. 할 일 목록 조회
response2 = agent.chat("현재 내 할 일 목록 보여줘")
print(f"\n[응답 2]\n{response2}\n")

# 3. 할 일 완료
response3 = agent.chat("TASK_001 완료했어")
print(f"\n[응답 3]\n{response3}\n")
```

### 예제 2: "메모/지식 관리 Agent"

#### Skill Card 설계

```json
{
  "id": "SC_NOTE_001",
  "version": "1.0.0",
  "agent_name": "메모/지식 관리자",
  "description": "사용자의 메모를 저장, 검색, 정리하고 지식 베이스를 구축합니다.",

  "trigger": {
    "keywords": ["메모", "노트", "기록", "저장", "검색"],
    "intent": "메모 관리",
    "similarity_threshold": 0.85
  },

  "tools": [
    "save_note",
    "search_notes",
    "organize_notes",
    "tag_note",
    "delete_note"
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "save_note",
      "description": "메모 저장"
    },
    {
      "step": 2,
      "action": "tag_note",
      "description": "자동 태그 추가"
    },
    {
      "step": 3,
      "action": "organize_notes",
      "description": "카테고리별 정리"
    }
  ],

  "constraints": {
    "validation": [
      "메모 내용 필수",
      "태그는 최대 10개",
      "제목은 100자 이내"
    ],
    "output_format": "markdown"
  },

  "llm_config": {
    "model": "gpt-oss:20b",
    "temperature": 0.2,
    "max_tokens": 600
  }
}
```

---

## 체크리스트

### Skill Card 설계 체크리스트

- [ ] Agent 역할이 명확히 정의되었는가?
- [ ] Trigger keywords가 충분한가?
- [ ] 필요한 Tool이 모두 리스트업되었는가?
- [ ] Execution Plan이 논리적인가?
- [ ] 에러 처리 전략이 수립되었는가?
- [ ] Constraints가 적절한가?
- [ ] Fallback 전략이 있는가?
- [ ] LLM 설정이 적절한가?

### Tool 개발 체크리스트

- [ ] Docstring이 명확한가?
- [ ] 함수명이 의미를 잘 전달하는가?
- [ ] 입출력 타입이 명확한가?
- [ ] 에러 케이스가 정의되었는가?
- [ ] 데이터 검증 로직이 있는가?
- [ ] 단위 테스트가 작성되었는가?

### Agent 로직 체크리스트

- [ ] Tool 실행 순서가 올바른가?
- [ ] 에러 처리가 적절한가?
- [ ] 사용자 피드백이 명확한가?
- [ ] 로깅이 적절히 되는가?

---

## 참고 자료

### 프로젝트 문서
- docs/AGENT_CONCEPTS.md
- docs/PROJECT_ROADMAP.md
- docs/LEARNING_PATH.md

### 관련 패키지
- LangChain 1.0
- LangGraph
- Ollama (Local LLM)

---

## 버전 정보

- **문서명**: Skill Card 완전 가이드 (개인비서 도메인)
- **버전**: 1.0.0
- **작성일**: 2025-11-10
- **작성자**: Claude Code

# 개인비서 AI 핵심 개념

> LangChain Agent를 활용한 개인비서 시스템의 핵심 개념을 간결하게 설명합니다.

## Agent란?

**Agent = LLM + Tools + Logic**

```python
Agent = {
    "LLM": "언어 모델 (사고)",
    "Tools": "사용할 수 있는 도구들 (행동)",
    "Logic": "실행 방식 (전략)"
}
```

### 예시

```python
class ScheduleManagerAgent:
    """일정 관리 Agent"""

    llm = ChatOllama(model="gpt-oss:20b")
    tools = [create_event, find_free_time, set_reminder]

    def execute(self, query: str):
        return self.llm.invoke(query, tools=self.tools)
```

**Agent는 사용자 질의를 받아 적절한 Tool을 선택하고 실행하여 답변을 생성합니다.**

---

## Skill Card란?

**Skill Card = Agent의 행동 명세서 (JSON/DB)**

Agent가 "무엇을", "어떻게", "무엇을 하면 안 되는지"를 정의한 메타데이터입니다.

### 왜 필요한가?

**문제: LLM의 불확실성**
```python
# ❌ LLM에게 자유롭게 맡기면
llm.chat("일정 잡아줘")
→ 매번 다른 Tool 호출
→ 예측 불가
→ 디버깅 어려움
```

**해결: Skill Card로 통제**
```json
{
  "id": "SC_SCHEDULE_001",
  "tools": ["create_event", "find_free_time"],
  "execution_plan": [
    {"step": 1, "action": "find_free_time"},
    {"step": 2, "action": "create_event"}
  ],
  "constraints": ["과거 날짜 금지"]
}
```

**장점:**
- ✅ 예측 가능: 항상 같은 순서
- ✅ 제어 가능: 제약사항 강제
- ✅ 관리 용이: JSON으로 버전 관리

---

## Static vs Dynamic Agent

### Static Execution Plan

**특징:** Skill Card에 실행 순서를 미리 정의

```json
{
  "execution_plan": [
    {"step": 1, "action": "parse_event_info"},
    {"step": 2, "action": "get_calendar_events"},
    {"step": 3, "action": "create_event"}
  ]
}
```

**장점:** 예측 가능, 감사 추적 용이, 비용 효율적
**단점:** 유연성 부족, 불필요한 실행 가능
**사용:** 금융/의료 등 규정 준수가 중요한 도메인

### Dynamic Agent

**특징:** LLM이 상황을 보고 Tool 선택

```python
agent = ScheduleManagerAgent()
agent.chat("내일 회의 잡아줘")
# LLM이 필요한 Tool만 선택적으로 사용
```

**장점:** 유연함, 효율적 (필요한 Tool만 실행)
**단점:** 예측 불가, LLM 비용 높음
**사용:** 챗봇, 개인비서 등 다양한 질의 처리

### Hybrid 접근

```
1. Dynamic Agent로 의도 분류
   → "일정 생성" vs "조회" vs "수정"

2. 분류 결과에 따라 Static Plan 선택
   → schedule_creation.json 실행

3. 예측 가능 + 유연성
```

**자세한 비교:** [patterns.md](./patterns.md)

---

## Multi-Agent 시스템

### 왜 여러 Agent?

**역할(Role)이 다르기 때문**

```python
# Agent 1: 일정 관리
ScheduleManagerAgent(
    tools=[create_event, find_free_time],
    system_prompt="일정 관리 전문가"
)

# Agent 2: 할 일 관리
TodoManagerAgent(
    tools=[add_task, complete_task],
    system_prompt="할 일 관리 전문가"
)

# Agent 3: 메모 관리
KnowledgeManagerAgent(
    tools=[save_note, search_notes],
    system_prompt="지식 관리 전문가"
)
```

### Supervisor Agent

여러 Agent를 관리하고 적절한 Agent를 선택하는 라우터

```python
class SupervisorAgent:
    def route(self, query: str):
        # 1. 질의 분석
        intent = self.classify(query)

        # 2. Agent 선택
        agent = self.agents[intent]

        # 3. 실행
        return agent.execute(query)
```

---

## Tool이란?

Agent가 사용할 수 있는 **함수**

### Tool 작성 예시

```python
from langchain_core.tools import tool

@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60
) -> dict:
    """
    새로운 일정 생성

    Args:
        title: 일정 제목
        start_time: 시작 시간 (YYYY-MM-DD HH:MM)
        duration: 소요 시간 (분)

    Returns:
        생성된 일정 정보
    """
    # 구현
    event = {
        "id": generate_id(),
        "title": title,
        "start_time": start_time,
        "duration": duration
    }
    db.save(event)
    return event
```

**Tool 3가지 유형:**
1. **LLM Tool**: LLM을 활용한 정보 추출/분석
2. **DB Tool**: 데이터베이스 조회/저장
3. **Logic Tool**: 비즈니스 로직 실행

**자세한 가이드:** [implementation-guide.md](./implementation-guide.md)

---

## Verbose 디버깅

Agent 실행 과정을 상세히 확인

```python
executor = SkillCardExecutor(card, verbose=True)
result = executor.execute(user_query="내일 회의 잡아줘")
```

**출력:**
```
📍 Step 1/3: parse_event_info
🔧 실행: parse_event_info(query="내일 회의 잡아줘")
✅ 성공! → {'title': '회의', 'date': '2025-11-13', 'time': '14:00'}

📍 Step 2/3: find_free_time
🔧 실행: find_free_time(date="2025-11-13")
✅ 성공! → ['09:00-10:00', '14:00-15:00']

📍 Step 3/3: create_event
🔧 실행: create_event(title="회의", start_time="2025-11-13 14:00")
✅ 성공! → {'id': 'EVT001', 'created': True}
```

**자세한 사용법:** [implementation-guide.md](./implementation-guide.md#verbose-디버깅)

---

## 핵심 정리

| 개념 | 설명 | 비유 |
|------|------|------|
| **Agent** | LLM + Tools + Logic | 전문가 |
| **Skill Card** | Agent 행동 명세 | 업무 매뉴얼 |
| **Tool** | Agent가 사용하는 함수 | 도구 |
| **Static Plan** | 고정된 실행 순서 | 레시피 |
| **Dynamic Agent** | LLM이 Tool 선택 | 즉흥 요리 |
| **Supervisor** | Agent 라우터 | 매니저 |

---

## 다음 단계

1. **[implementation-guide.md](./implementation-guide.md)** - 실전 구현 가이드
2. **[patterns.md](./patterns.md)** - Static vs Dynamic 상세 비교
3. **[roadmap.md](./roadmap.md)** - 프로젝트 로드맵
4. **[step-by-step/](./step-by-step/)** - 단계별 구현 가이드

---

**작성일:** 2025-11-12
**프로젝트:** 개인비서 AI System

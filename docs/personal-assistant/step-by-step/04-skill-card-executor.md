# Step 04: Skill Card Executor 구현

## 📌 현재 상태 (2025-11-11)

### ✅ 완료된 것

1. **SkillCardExecutor 기본 구조** (`src/core/skill_cards/executor.py`)
   - Execution Plan을 순서대로 실행하는 엔진
   - 변수 치환 기능 (`${variable}` → 실제 값)
   - Step 간 데이터 전달 (output_to → input)
   - 에러 처리 (fail/skip)

2. **실행 예제** (`src/examples/07_executor_demo.py`)
   - Mock Tool로 전체 흐름 시연
   - 5단계 Execution Plan 실행 확인

3. **LLM 연결 확인** (`src/examples/06_simple_llm.py`)
   - Ollama 정상 동작 확인
   - LangChain 연결 테스트

### ⏳ 다음에 할 것

**실제 Tools 연결하기** (현재는 Mock 데이터)
- `parse_event_info`: LLM으로 자연어 파싱
- `create_event`: 실제 DB에 저장
- `find_free_time`: 실제 로직 구현

---

## 🎯 이 단계의 목표

**Skill Card의 Execution Plan을 "실제로 실행"하는 엔진 만들기**

### 핵심 개념

```
Skill Card (레시피) + Executor (요리사) = 실제 동작!

사용자: "내일 2시 회의"
  ↓
Executor: Execution Plan 실행
  Step 1 → Step 2 → Step 3 → ...
  ↓
결과: 실제로 캘린더에 일정 추가됨!
```

---

## 📂 파일 구조

```
src/core/skill_cards/
├── __init__.py          # SkillCardExecutor export 추가
├── schema.py            # Pydantic 모델 (기존)
├── manager.py           # Skill Card 로드 (기존)
└── executor.py          # ⭐ NEW! Execution Plan 실행 엔진

src/examples/
├── 06_simple_llm.py     # ⭐ NEW! LLM 연결 테스트
└── 07_executor_demo.py  # ⭐ NEW! Executor 데모
```

---

## 🔧 구현 설명

### 1. ExecutionContext (실행 컨텍스트)

**역할**: Step 실행 중 생성된 변수들을 저장하고 관리

```python
class ExecutionContext:
    def __init__(self, initial_data: dict):
        self.variables = initial_data  # 변수 저장소
        self.step_results = []         # 실행 결과 기록

    def set(self, key: str, value: Any):
        """변수 저장: event_data = {...}"""
        self.variables[key] = value

    def get(self, key: str) -> Any:
        """변수 조회: event_data 가져오기"""
        return self.variables.get(key)
```

**예시**:
```python
ctx = ExecutionContext({"user_query": "내일 회의"})
ctx.set("event_data", {"title": "회의", "date": "2025-11-12"})
ctx.get("event_data")  # {"title": "회의", ...}
```

---

### 2. SkillCardExecutor (실행 엔진)

#### 핵심 메서드

##### `execute()` - 전체 실행

```python
def execute(self, user_query: str, context: dict | None = None) -> dict:
    """
    Skill Card 실행

    Args:
        user_query: "내일 오후 2시에 팀 회의 일정 잡아줘"
        context: {"user_id": "user123", ...}

    Returns:
        {
            "success": True,
            "variables": {...},      # 모든 저장된 변수
            "step_results": [...]    # Step 실행 기록
        }
    """
```

##### `_execute_step()` - 단일 Step 실행

```python
def _execute_step(self, step: ExecutionStep, ctx: ExecutionContext):
    """
    1. Input 변수 치환: ${variable} → 실제 값
    2. Action 실행: Tool 호출
    3. Output 저장: output_to 변수에 저장
    """
```

##### `_resolve_variables()` - 변수 치환

```python
def _resolve_variables(self, data: Any, ctx: ExecutionContext) -> Any:
    """
    변수 치환 로직

    Input:  {"date": "${event_data.date}"}
    Output: {"date": "2025-11-12"}

    - 재귀적으로 dict, list 모두 처리
    - 중첩 경로 지원: event_data.title, available_slots.best_slot.start
    """
```

**변수 치환 예시**:
```python
# Step 1 실행 후
ctx.set("event_data", {"title": "팀 회의", "date": "2025-11-12"})

# Step 2 input
input_data = {"date": "${event_data.date}"}

# 치환 후
resolved = {"date": "2025-11-12"}  # ✅
```

##### `_execute_action()` - Action 실행

**현재 (Mock 버전)**:
```python
def _execute_action(self, action: str, input_data: dict) -> Any:
    """
    하드코딩된 Mock 데이터 반환

    parse_event_info → {"title": "팀 회의", ...}
    create_event → {"id": "evt_12345", "created": True}
    """
    mock_results = {
        "parse_event_info": {...},
        "create_event": {...},
    }
    return mock_results.get(action)
```

**다음 단계 (실제 Tool 연결)**:
```python
def _execute_action(self, action: str, input_data: dict) -> Any:
    """
    실제 Tool 호출

    self.tools["parse_event_info"](input_data)
    self.tools["create_event"](input_data)
    """
    tool = self.tools.get(action)
    if tool:
        return tool.invoke(input_data)  # ← 실제 실행!
    else:
        raise ValueError(f"Tool '{action}'을 찾을 수 없습니다")
```

---

## 🚀 사용 방법

### 예제 1: 기본 실행

```python
from core.skill_cards import SkillCardManager, SkillCardExecutor

# 1. Skill Card 로드
manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")

# 2. Executor 생성
executor = SkillCardExecutor(card)

# 3. 실행!
result = executor.execute(
    user_query="내일 오후 2시에 팀 회의 일정 잡아줘",
    context={"user_id": "user123"}
)

# 4. 결과 확인
print(result["success"])           # True
print(result["variables"])         # 모든 변수
print(result["step_results"])      # Step 실행 기록
```

### 예제 2: 데모 실행

```bash
# 전체 실행 과정 확인
uv run python -m src.examples.07_executor_demo

# 결과:
# Step 1: parse_event_info 실행
# Step 2: get_calendar_events 실행
# ...
# ✅ 완료!
```

---

## 🔍 실행 흐름 (상세)

### 시나리오: "내일 오후 2시에 팀 회의 일정 잡아줘"

```
┌─────────────────────────────────────────────────┐
│ 1. Executor 초기화                               │
├─────────────────────────────────────────────────┤
│ ctx.variables = {                               │
│   "user_query": "내일 오후 2시에...",           │
│   "user_id": "user123"                          │
│ }                                               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. Step 1: parse_event_info                     │
├─────────────────────────────────────────────────┤
│ Input:  {"query": "내일 오후 2시에..."}         │
│ Action: parse_event_info 실행                   │
│ Output: {"title": "팀 회의", "date": "...", ... }│
│ 저장:   ctx.set("event_data", {...})            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Step 2: get_calendar_events                  │
├─────────────────────────────────────────────────┤
│ Input (원본):                                   │
│   {"date": "${event_data.date}", ...}           │
│                                                 │
│ 변수 치환:                                      │
│   "${event_data.date}" → "2025-11-12"           │
│                                                 │
│ Input (치환 후):                                │
│   {"date": "2025-11-12", ...}                   │
│                                                 │
│ Action: get_calendar_events 실행                │
│ Output: [{"title": "기존 회의", ...}]           │
│ 저장:   ctx.set("existing_events", [...])       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. Step 3: find_free_time                       │
├─────────────────────────────────────────────────┤
│ Input (원본):                                   │
│   {                                             │
│     "duration": "${event_data.duration}",       │
│     "existing_events": "${existing_events}"     │
│   }                                             │
│                                                 │
│ 변수 치환:                                      │
│   "${event_data.duration}" → 60                 │
│   "${existing_events}" → [...]                  │
│                                                 │
│ Action: find_free_time 실행                     │
│ Output: {"best_slot": {"start": "14:00", ...}}  │
│ 저장:   ctx.set("available_slots", {...})       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 5. Step 4: create_event                         │
├─────────────────────────────────────────────────┤
│ Input (치환 후):                                │
│   {                                             │
│     "title": "팀 회의",                         │
│     "start_time": "14:00",                      │
│     "end_time": "15:00"                         │
│   }                                             │
│                                                 │
│ Action: create_event 실행                       │
│ Output: {"id": "evt_12345", "created": True}    │
│ 저장:   ctx.set("created_event", {...})         │
│                                                 │
│ 🎉 여기서 실제로 일정이 생성됨!                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 6. Step 5: send_notification                    │
├─────────────────────────────────────────────────┤
│ Input: {"event": {...}, "message": "..."}       │
│ Action: send_notification 실행                  │
│ Output: {"sent": True}                          │
│ 저장:   ctx.set("notification_result", {...})   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 7. 최종 결과 반환                               │
├─────────────────────────────────────────────────┤
│ {                                               │
│   "success": True,                              │
│   "variables": {                                │
│     "event_data": {...},                        │
│     "existing_events": [...],                   │
│     "available_slots": {...},                   │
│     "created_event": {...},                     │
│     "notification_result": {...}                │
│   },                                            │
│   "step_results": [...]                         │
│ }                                               │
└─────────────────────────────────────────────────┘
```

---

## 🧪 테스트 방법

### 1. LLM 연결 테스트

```bash
uv run python -m src.examples.06_simple_llm

# 예상 출력:
# 🤖 LLM 연결 테스트
# ✅ 연결 완료!
# 응답: 안녕하세요! ...
```

### 2. Executor 테스트

```bash
uv run python -m src.examples.07_executor_demo

# 예상 출력:
# 🚀 Execution Plan 시작
# ▶ Step 1: parse_event_info
# ▶ Step 2: get_calendar_events
# ...
# ✅ Execution Plan 완료!
```

### 3. 전체 테스트 실행

```bash
uv run pytest tests/ -v

# 현재 34개 테스트 모두 통과 예상
```

---

## 📊 현재 구조 vs 최종 목표

### 현재 상태

```python
# Mock Tool 사용
executor = SkillCardExecutor(card)
result = executor.execute("내일 회의")

# _execute_action()에서 하드코딩된 값 반환
"parse_event_info" → {"title": "팀 회의"}  # Mock!
"create_event" → {"created": True}         # Mock!
```

### 최종 목표

```python
# 실제 Tools 등록
executor = SkillCardExecutor(card)
executor.register_tool("parse_event_info", parse_event_info_tool)
executor.register_tool("create_event", create_event_tool)
executor.register_tool("find_free_time", find_free_time_tool)

# 실행 → 실제 Tool 호출
result = executor.execute("내일 회의")

# 실제 동작:
# 1. LLM이 질의 파싱
# 2. DB에서 기존 일정 조회
# 3. 빈 시간 계산
# 4. DB에 일정 저장  ← 실제로 저장됨!
```

---

## 🎯 다음 단계 (Step 05)

### 목표: 실제 Tools 연결

1. **parse_event_info Tool 만들기**
   ```python
   @tool
   def parse_event_info(query: str) -> dict:
       """LLM을 사용해서 자연어에서 정보 추출"""
       llm = ChatOllama(model="gpt-oss:20b")
       prompt = f"다음 질의에서 일정 정보를 추출해주세요: {query}"
       response = llm.invoke(prompt)
       return parse_response(response)
   ```

2. **create_event Tool 만들기**
   ```python
   @tool
   def create_event(title: str, start_time: str, ...) -> dict:
       """실제 DB에 저장"""
       from personal_assistant.database import db
       event = db.add_event({
           "title": title,
           "start_time": start_time,
           ...
       })
       return event
   ```

3. **Executor에 Tool 등록**
   ```python
   executor.register_tool("parse_event_info", parse_event_info)
   executor.register_tool("create_event", create_event)
   ```

4. **_execute_action() 수정**
   ```python
   def _execute_action(self, action: str, input_data: dict) -> Any:
       tool = self.tools.get(action)
       if not tool:
           raise ValueError(f"Tool '{action}'을 찾을 수 없습니다")
       return tool.invoke(input_data)  # 실제 실행!
   ```

---

## 📝 중요 노트

### Mock vs Real 구분

**현재 (Mock)**:
- ✅ Execution Plan 흐름 검증
- ✅ 변수 치환 동작 확인
- ✅ Step 간 데이터 전달 확인
- ❌ 실제 LLM 사용 안 함
- ❌ 실제 DB 저장 안 함

**다음 (Real)**:
- ✅ 실제 LLM 호출
- ✅ 실제 DB 저장
- ✅ 실제 로직 실행

### 에러 처리

```python
# Skill Card JSON에서 설정
{
  "step": 2,
  "action": "get_calendar_events",
  "on_error": "skip"  # ← 실패해도 계속 진행
}

{
  "step": 4,
  "action": "create_event",
  "on_error": "fail"  # ← 실패하면 전체 중단
}
```

**동작**:
- `on_error: "skip"`: 에러 발생 시 해당 Step 건너뛰고 계속 진행
- `on_error: "fail"`: 에러 발생 시 즉시 중단하고 예외 발생

---

## 🔗 관련 파일

### 구현 파일
- `src/core/skill_cards/executor.py` - Executor 구현
- `src/core/skill_cards/schema.py` - ExecutionStep 정의
- `src/core/skill_cards/manager.py` - Skill Card 로드

### 예제 파일
- `src/examples/06_simple_llm.py` - LLM 연결 테스트
- `src/examples/07_executor_demo.py` - Executor 데모

### Skill Card
- `src/personal_assistant/skill_cards/schedule_card.json` - 일정 관리 Skill Card

### 이전 문서
- [Step 03: Skill Card 시스템](03-skill-card-system.md)

### 다음 문서
- Step 05: 실제 Tools 연결 (작성 예정)

---

## 💡 트러블슈팅

### Q: Executor 실행 시 "Skill Card를 찾을 수 없습니다" 에러

**원인**: Skill Card JSON 파일 경로 문제

**해결**:
```bash
# 파일 존재 확인
ls src/personal_assistant/skill_cards/schedule_card.json

# 없으면 Step 03 문서 참고해서 생성
```

### Q: 변수 치환이 안 됨 (${variable} 그대로 출력)

**원인**: 변수가 컨텍스트에 저장되지 않음

**확인**:
```python
# 이전 Step에서 output_to 설정 확인
{
  "step": 1,
  "action": "parse_event_info",
  "output_to": "event_data"  # ← 이게 있어야 함
}

# 다음 Step에서 사용
{
  "step": 2,
  "input": {"date": "${event_data.date}"}  # ← 매칭되어야 함
}
```

### Q: Step 실행 순서가 이상함

**원인**: Execution Plan의 step 번호가 연속적이지 않음

**해결**:
```json
// ❌ 잘못된 예
[
  {"step": 1, ...},
  {"step": 3, ...},  // 2를 건너뜀!
  {"step": 5, ...}
]

// ✅ 올바른 예
[
  {"step": 1, ...},
  {"step": 2, ...},
  {"step": 3, ...}
]
```

---

## 🎓 학습 포인트

### 1. 왜 Executor가 필요한가?

**일반 LLM Agent**:
```
사용자: "내일 회의"
  ↓
LLM: "음... 뭐 해야 하지?" (매번 다르게 생각)
  ↓
Tool A 호출 → LLM 다시 생각 → Tool B 호출 → ...
  ↓
결과: 매번 다름, 예측 불가능
```

**Skill Card + Executor**:
```
사용자: "내일 회의"
  ↓
Executor: Execution Plan 확인
  ↓
Step 1 → Step 2 → Step 3 (정해진 순서)
  ↓
결과: 항상 같음, 예측 가능, 신뢰할 수 있음
```

### 2. 변수 치환의 힘

**없으면**:
```python
# 각 Step마다 이전 결과를 수동으로 전달
step1_result = execute_step1()
step2_result = execute_step2(step1_result)  # 수동
step3_result = execute_step3(step2_result)  # 수동
```

**있으면**:
```python
# JSON에 선언만 하면 자동으로 전달
{
  "step": 2,
  "input": {"date": "${event_data.date}"}  # 자동!
}
```

### 3. Execution Plan = 논리적 사고 전개

**사람이 일정을 잡는 과정**:
1. 언제 뭐 하자는지 파악
2. 그날 일정 확인
3. 빈 시간 찾기
4. 일정 등록
5. 알림 보내기

**Execution Plan**:
```json
[
  {"step": 1, "action": "parse_event_info"},
  {"step": 2, "action": "get_calendar_events"},
  {"step": 3, "action": "find_free_time"},
  {"step": 4, "action": "create_event"},
  {"step": 5, "action": "send_notification"}
]
```

→ **똑같음!** 사람의 사고 과정을 코드로 표현한 것!

---

## 🚀 빠른 시작 (집에서 다시 시작할 때)

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/sskim/dev/langchain-in-action

# 2. 현재 상태 확인
git status
git log --oneline -5

# 3. 테스트 실행 (모든 게 정상인지 확인)
uv run pytest tests/ -v

# 4. Executor 데모 실행
uv run python -m src.examples.07_executor_demo

# 5. 다음 작업 시작
# docs/implementation/05-tool-integration.md 참고 (아직 없음, 만들 예정)
```

---

## ✅ 체크리스트

작업 시작 전 확인:

- [ ] 모든 테스트 통과 (`uv run pytest tests/ -v`)
- [ ] Executor 데모 정상 실행 (`uv run python -m src.examples.07_executor_demo`)
- [ ] LLM 연결 확인 (`uv run python -m src.examples.06_simple_llm`)
- [ ] 문서 읽음 (이 파일)
- [ ] 다음 할 일 파악 (Step 05: 실제 Tools 연결)

---

**작성일**: 2025-11-11
**상태**: ✅ 완료 (Mock 버전)
**다음 단계**: Step 05 - 실제 Tools 연결

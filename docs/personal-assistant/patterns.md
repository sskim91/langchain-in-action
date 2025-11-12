# Static Execution Plan vs Dynamic Agent

## 개요

LangChain Agent를 구축하는 두 가지 주요 패턴을 비교합니다.

## 비교표

| 특징 | Static Execution Plan | Dynamic Agent |
|------|---------------------|---------------|
| **Tool 선택** | JSON에 미리 정의 | LLM이 매번 판단 |
| **실행 순서** | 항상 동일 | 상황에 따라 변경 |
| **예측 가능성** | 높음 ⭐⭐⭐⭐⭐ | 낮음 ⭐⭐ |
| **유연성** | 낮음 ⭐⭐ | 높음 ⭐⭐⭐⭐⭐ |
| **효율성** | 보통 (불필요한 Tool도 실행) | 높음 (필요한 Tool만 실행) |
| **LLM 비용** | 낮음 (Tool 내부만) | 높음 (매번 판단) |
| **디버깅** | 쉬움 | 어려움 |
| **구현 난이도** | 중간 | 낮음 (LangChain 내장) |
| **적용 사례** | 금융, 의료 규정 준수 | 챗봇, 개인비서 |

## Static Execution Plan (Step 04-05)

### 구조

```json
{
  "execution_plan": [
    {"step": 1, "action": "parse_event_info"},
    {"step": 2, "action": "get_calendar_events"},
    {"step": 3, "action": "find_free_time"},
    {"step": 4, "action": "create_event"},
    {"step": 5, "action": "send_notification"}
  ]
}
```

### 실행 흐름

```
사용자 질의
    ↓
SkillCardExecutor가 JSON 읽기
    ↓
Step 1 실행 → 변수 저장
    ↓
Step 2 실행 → 변수 저장
    ↓
Step 3 실행 → 변수 저장
    ↓
...
    ↓
모든 Step 완료
```

### 장점

✅ **예측 가능한 실행**: 항상 같은 순서  
✅ **감사 추적 용이**: 모든 Step 기록  
✅ **규정 준수**: 금융/의료 등 규제 산업  
✅ **디버깅 쉬움**: 문제 발생 Step 명확  
✅ **비용 효율적**: LLM 판단 비용 없음

### 단점

⚠️ **불필요한 실행**: 조회만 해도 5 Step 모두 실행  
⚠️ **유연성 부족**: 새로운 케이스 대응 어려움  
⚠️ **JSON 수정 필요**: 순서 변경 시 JSON 수정

### 사용 사례

- **금융 거래 승인**: 반드시 AML → KYC → 리스크 평가 → 승인 순서
- **의료 진단 프로세스**: 문진 → 검사 → 판독 → 처방 (순서 고정)
- **제조 공정**: 반복적이고 예측 가능한 워크플로우

## Dynamic Agent (Step 06)

### 구조

```python
agent = ScheduleManagerAgent()
response = agent.chat("내일 회의 잡아줘")
# LLM이 상황을 보고 Tool 선택
```

### 실행 흐름

```
사용자 질의
    ↓
LLM: "어떤 Tool이 필요한가?" 판단
    ↓
Tool 1 선택 → 실행 → 결과 확인
    ↓
LLM: "충분한가? 다음은?" 판단
    ↓
Tool 2 선택 → 실행 → 결과 확인
    ↓
...
    ↓
LLM: "충분하다" 판단 → 최종 답변
```

### 장점

✅ **효율적**: 필요한 Tool만 사용  
✅ **유연함**: 다양한 질의 타입 처리  
✅ **대화형**: 추가 정보 요청 가능  
✅ **확장성**: 새 Tool 추가만으로 기능 확장  
✅ **자연스러움**: 사람처럼 판단

### 단점

⚠️ **예측 불가**: 실행 경로 미리 알 수 없음  
⚠️ **비용 증가**: 매번 LLM 판단 필요  
⚠️ **디버깅 어려움**: 왜 그 Tool을 선택했는지 불명확  
⚠️ **잘못된 선택**: LLM이 틀린 Tool 선택 가능  
⚠️ **규정 준수 어려움**: 감사 추적 복잡

### 사용 사례

- **챗봇**: 다양한 질의 ("날씨", "일정", "검색" 등)
- **개인비서**: 유연한 대응 필요
- **고객지원**: 상황별 다른 Tool 조합

## 실제 비교 예시

### 예시 1: "내일 회의 잡아줘"

**Static Plan:**
```
Step 1: parse_event_info ✅ (필요)
Step 2: get_calendar_events ✅ (필요)
Step 3: find_free_time ✅ (필요)
Step 4: create_event ✅ (필요)
Step 5: send_notification ✅ (필요)
→ 5개 Tool 모두 실행
```

**Dynamic Agent:**
```
LLM: "일정 생성이니 create_event만"
→ create_event ✅
→ 1개 Tool만 실행 (80% 절감!)
```

### 예시 2: "내 일정 보여줘"

**Static Plan:**
```
Step 1: parse_event_info ❌ (불필요)
Step 2: get_calendar_events ❌ (불필요)
Step 3: find_free_time ❌ (불필요)
Step 4: create_event ❌ (불필요)
Step 5: send_notification ❌ (불필요)
→ 5개 Step 실행하지만 조회만 필요
```

**Dynamic Agent:**
```
LLM: "조회니까 list_events만"
→ list_events ✅
→ 1개 Tool만 실행 (효율적!)
```

## 하이브리드 접근

두 패턴의 장점을 결합:

```
1. Dynamic Agent로 질의 분류
   "일정 생성"? "조회"? "수정"?
   
2. 분류 결과에 따라 Static Plan 선택
   - 생성 → schedule_creation.json 실행
   - 조회 → schedule_query.json 실행
   - 수정 → schedule_update.json 실행
   
3. Static Plan 실행
   - 예측 가능한 순서
   - 규정 준수
   - 감사 추적
```

**장점:**
- ✅ 유연성 (Dynamic) + 예측성 (Static)
- ✅ 비용 최적화 (1번만 LLM 판단)
- ✅ 감사 추적 가능

## 선택 가이드

### Static Execution Plan을 선택하세요:

- ✅ 워크플로우가 반복적이고 예측 가능
- ✅ 규정 준수가 중요 (금융, 의료)
- ✅ 감사 추적이 필수
- ✅ 비용 최적화가 중요
- ✅ 실행 순서가 논리적으로 고정

### Dynamic Agent를 선택하세요:

- ✅ 질의 타입이 다양
- ✅ 대화형 서비스 (챗봇)
- ✅ 유연성이 중요
- ✅ 빠른 프로토타이핑
- ✅ 사용자 경험 우선

## 구현 코드

### Static Plan 실행

```python
from core.skill_cards import SkillCardExecutor, SkillCardManager

manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")
executor = SkillCardExecutor(card, verbose=True)

result = executor.execute(
    user_query="내일 오후 2시에 팀 회의",
    context={"user_id": "user123"}
)
```

### Dynamic Agent 실행

```python
from personal_assistant.agents import ScheduleManagerAgent

agent = ScheduleManagerAgent()
response = agent.chat("내일 오후 2시에 팀 회의")
```

## 결론

- **Static Plan**: 예측 가능성, 규정 준수가 중요한 엔터프라이즈
- **Dynamic Agent**: 유연성, 사용자 경험이 중요한 소비자 서비스
- **Hybrid**: 두 장점 결합, 실무에서 가장 효과적

프로젝트 요구사항에 맞게 선택하거나, Hybrid 방식으로 시작하는 것을 권장합니다.

# LangChain Personal Assistant

LangChain과 Ollama를 사용한 개인 비서 Agent 시스템입니다. Skill Card 패턴을 사용하여 확장 가능한 Agent 아키텍처를 구현합니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [요구사항](#요구사항)
- [설치](#설치)
- [프로젝트 구조](#프로젝트-구조)
- [Contributor Guide](#-contributor-guide)
- [구현 단계](#구현-단계)
- [사용법](#사용법)
- [주요 개념](#주요-개념)
- [문제해결](#문제해결)

## 🎯 프로젝트 개요

이 프로젝트는 **Skill Card 패턴**을 사용하여 LLM Agent를 체계적으로 구축하는 방법을 보여줍니다.

### 핵심 특징

- **Skill Card Pattern**: JSON 기반 메타데이터로 Agent 행동 정의
- **Static Execution Plan**: 예측 가능한 워크플로우 실행
- **Real Tool Integration**: LLM과 실제 DB/API가 연동된 Tool
- **Middleware System**: PII 탐지, 감사 로깅 등 프로덕션 기능
- **Structured Output**: Pydantic을 사용한 타입 안전한 LLM 응답

### 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                  User Query                         │
│          "내일 오후 2시에 팀 회의 잡아줘"               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Skill Card Manager                     │
│  - Skill Card 로드 (schedule_card.json)             │
│  - Execution Plan 파싱                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│           Skill Card Executor                       │
│  - Step 1: parse_event_info (LLM Tool)             │
│  - Step 2: get_calendar_events (DB Tool)           │
│  - Step 3: find_free_time (Logic Tool)             │
│  - Step 4: create_event (DB Tool)                  │
│  - Step 5: send_notification (Notify Tool)         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                   Result                            │
│  - DB에 일정 생성됨                                  │
│  - 알림 전송됨                                       │
│  - 실행 결과 반환                                    │
└─────────────────────────────────────────────────────┘
```

## 📦 요구사항

### 필수 사항

- **Python 3.13+**
- **Ollama** 설치 및 실행
- **gpt-oss:20b** 모델 설치

### Ollama 설치

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 모델 다운로드
ollama pull gpt-oss:20b

# Ollama 서버 시작
ollama serve
```

## 🚀 설치

```bash
# 1. 저장소 클론
git clone <repository-url>
cd langchain-in-action

# 2. UV를 사용한 패키지 설치 (권장)
uv sync

# 또는 pip 사용
pip install -e .

# 3. Ollama 모델 확인
ollama list
```

## 📁 프로젝트 구조

```
langchain-in-action/
├── src/
│   ├── core/                          # 핵심 프레임워크
│   │   ├── agents/                    # Agent 베이스 클래스
│   │   │   ├── __init__.py
│   │   │   └── base_agent.py
│   │   ├── skill_cards/              # ⭐ Skill Card 시스템
│   │   │   ├── __init__.py
│   │   │   ├── schema.py             # Skill Card 스키마 (Pydantic)
│   │   │   ├── manager.py            # Skill Card 로드/관리
│   │   │   └── executor.py           # Execution Plan 실행 엔진
│   │   └── middleware/               # 미들웨어 시스템
│   │       ├── __init__.py
│   │       ├── base.py               # BaseMiddleware
│   │       ├── pii_detection.py      # PII 마스킹
│   │       └── audit_logging.py      # 감사 로깅
│   │
│   ├── personal_assistant/           # 개인 비서 Agent
│   │   ├── __init__.py
│   │   ├── agent.py                  # ScheduleManagerAgent
│   │   ├── skill_cards/              # ⭐ Skill Card 정의 (JSON)
│   │   │   └── schedule_card.json    # 일정 관리 Skill Card
│   │   ├── tools/                    # ⭐ Real Tools
│   │   │   └── schedule_tools.py     # 일정 관리 도구들
│   │   └── database/                 # In-Memory DB
│   │       └── memory_db.py
│   │
│   └── examples/                     # 예제 및 데모
│       ├── 01_basic_agent.py         # Step 01: 기본 Agent
│       ├── 02_schedule_agent.py      # Step 02: 일정 관리 Agent
│       ├── 03_middleware.py          # Step 03: 미들웨어 통합
│       ├── 04_skill_card_executor.py # Step 04: Skill Card Executor
│       ├── 05_skill_card_demo.py     # Step 04: Skill Card 데모
│       ├── 06_simple_llm.py          # LLM 시스템 프롬프트 비교
│       └── 08_real_tools_demo.py     # ⭐ Step 05: Real Tools 데모
│
├── tests/                            # 테스트
│   ├── conftest.py                   # Pytest 설정
│   ├── core/                         # 코어 테스트
│   └── personal_assistant/           # 개인 비서 테스트
│
├── docs/                             # 문서
│   └── implementation/               # 구현 문서
│
├── pyproject.toml                    # 프로젝트 설정
├── uv.lock                           # UV 잠금 파일
└── README.md                         # 이 파일
```

## 🧑‍💻 Contributor Guide

- 새로 합류했다면 `AGENTS.md`의 **Repository Guidelines**를 먼저 읽고 브랜치 전략, 테스트 우선순위, Skill Card 작성 요령을 익혀주세요.
- 문서에는 `uv` 기반 빌드/테스트 명령, Ruff 포맷 규칙, Skill Card/미들웨어 확장 팁, 그리고 PR 템플릿 기대치가 압축되어 있습니다.
- PR 설명에는 실행한 명령과 결과를 붙여야 하므로, 가이드의 체크리스트를 따라 증빙을 준비하세요.

## 🎓 구현 단계

### ✅ Step 01: Basic Agent
- LangChain Agent 기본 구조 이해
- Tool Calling 패턴 학습
- Ollama LLM 연동

### ✅ Step 02: Schedule Manager Agent
- 일정 관리 도구 구현 (Mock 데이터)
- Agent가 여러 도구 사용하는 패턴
- 대화형 Agent 구현

### ✅ Step 03: Middleware System
- BaseMiddleware 추상 클래스
- PII 탐지 및 마스킹 (전화번호, 이메일, SSN 등)
- 감사 로깅 (JSON Lines 포맷)
- Agent와 미들웨어 통합

### ✅ Step 04: Skill Card System
- **Skill Card 스키마 정의** (Pydantic)
  - Agent 메타데이터
  - Execution Plan (순차 실행 계획)
  - Variable Substitution (`${variable}` 패턴)
- **SkillCardManager**: JSON에서 Skill Card 로드
- **SkillCardExecutor**: Execution Plan 실행 엔진
  - Step별 실행
  - 변수 치환 및 저장
  - 에러 핸들링 (fail/skip)

### ✅ Step 05: Real Tool Integration ⭐ 최신!
- **LLM Tool**: `parse_event_info`
  - 자연어 → 구조화된 데이터 (Structured Output)
  - Pydantic 모델로 타입 안전성 보장
  - 상대적 날짜 파싱 ("내일" → "2025-11-13")
- **DB Tools**:
  - `get_calendar_events`: 특정 날짜 일정 조회
  - `create_event`: 새 일정 DB 저장
  - `send_notification`: 알림 전송
- **Logic Tool**: `find_free_time`
  - 기존 일정 분석
  - 빈 시간대 계산
  - 최적 시간 추천
- **Verbose 디버깅**:
  - SkillCardExecutor verbose 모드
  - LangChain `set_debug(True)` 통합
  - Tool 호출 추적, 성능 지표

### ✅ Step 06: Dynamic Agent ⭐ 최신!
- **Dynamic Tool Selection**: LLM이 상황을 보고 필요한 Tool만 선택
- **효율성**: 불필요한 Tool 실행 안 함 (비용/시간 절감)
- **유연성**: 같은 Agent로 다양한 질의 타입 처리
- **비교**: Static Plan은 항상 5 Step, Dynamic은 필요한 만큼만
- **실제 예시**:
  - "일정 생성" → create_event만 사용 (1개 Tool)
  - "조회만" → list_events만 사용 (1개 Tool)
  - Static Plan이었다면 둘 다 5개 Tool 실행
- **Trade-off 분석**: [Static vs Dynamic 비교](docs/static-vs-dynamic.md)

## 💻 사용법

### 1. 기본 예제 실행

```bash
# Step 01: 기본 Agent
uv run python -m src.examples.01_basic_agent

# Step 02: 일정 관리 Agent
uv run python -m src.examples.02_schedule_agent

# Step 03: 미들웨어
uv run python -m src.examples.03_middleware

# Step 04: Skill Card 데모
uv run python -m src.examples.05_skill_card_demo
```

### 2. ⭐ Real Tools 데모 (Step 05)

```bash
# 전체 워크플로우 실행 (verbose 모드)
uv run python -m src.examples.08_real_tools_demo
```

**실행 결과:**
```
================================================================================
  🚀 Real Tools Demo - LLM이 실제로 작동합니다!
================================================================================

사용자: 내일 오후 2시에 팀 회의 일정 잡아줘

🚀 Execution Plan 시작: 일정 관리 전문가

▶ Step 1: parse_event_info
  🔧 Tool 호출: parse_event_info

[llm/start] Entering LLM run with input:
{
  "prompts": ["Human: 당신은 일정 정보를 추출하는 전문가입니다..."]
}

[llm/end] [5.70s] Exiting LLM run with output:
{
  "text": "{\n  \"title\": \"팀 회의\",\n  \"date\": \"2025-11-13\",\n  \"time\": \"14:00\"\n}"
}

✅ LLM 응답 (Structured Output):
  • title: 팀 회의
  • date: 2025-11-13
  • time: 14:00
  • duration: 60분

▶ Step 2: get_calendar_events
  ✅ 기존 일정 2개 발견

▶ Step 3: find_free_time
  ✅ 빈 시간: 09:00-10:00, 11:00-12:00, 13:00-14:00

▶ Step 4: create_event
  ✅ 일정 생성: EVT003

▶ Step 5: send_notification
  ✅ 알림 전송

📅 실제 DB 확인:
  • EVT001: 기존 회의 (2025-11-13 10:00 ~ 11:00)
  • EVT002: 점심 약속 (2025-11-13 12:00 ~ 13:00)
  • EVT003: 팀 회의 (2025-11-13 09:00 ~ 10:00) ← 새로 생성됨!
```

### 3. LLM 시스템 프롬프트 비교

```bash
# Ollama.app GUI vs LangChain 동작 차이 확인
uv run python -m src.examples.06_simple_llm
```

### 4. 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# verbose 모드
uv run pytest -v

# 특정 테스트만
uv run pytest tests/core/test_skill_card_manager.py
```

### 5. 빠른 테스트 (개발용)

```bash
# quick_test.py 사용
uv run python quick_test.py
```

## 🧩 주요 개념

### 1. Skill Card Pattern

**Skill Card**는 Agent의 행동을 JSON으로 정의하는 패턴입니다.

```json
{
  "skill_id": "SC_SCHEDULE_001",
  "agent_name": "일정 관리 전문가",
  "execution_plan": [
    {
      "step": 1,
      "action": "parse_event_info",
      "description": "사용자 요청에서 이벤트 정보 추출",
      "input": {
        "query": "${user_query}"
      },
      "output_to": "event_data",
      "on_error": "fail"
    }
  ]
}
```

**장점:**
- ✅ Agent 로직과 정의 분리
- ✅ 비개발자도 Agent 행동 수정 가능
- ✅ 버전 관리 및 테스트 용이
- ✅ 예측 가능한 실행 흐름

### 2. Static vs Dynamic Execution Plan

| 특징 | Static Plan (현재) | Dynamic Plan (Step 06) |
|------|-------------------|----------------------|
| Tool 선택 | JSON에 미리 정의 | LLM이 매번 판단 |
| 순서 | 항상 같음 | 상황에 따라 다름 |
| 예측성 | 높음 | 낮음 |
| 유연성 | 낮음 | 높음 |
| 비유 | 요리 레시피 | 요리사 |

### 3. Structured Output (Pydantic)

LLM 응답을 타입 안전하게 파싱:

```python
class EventInfo(BaseModel):
    title: str = Field(description="일정 제목")
    date: str = Field(description="날짜 (YYYY-MM-DD 형식)")
    time: str = Field(description="시간 (HH:MM 형식)")

# LLM이 자동으로 JSON 생성
llm = ChatOllama(model="gpt-oss:20b")
structured_llm = llm.with_structured_output(EventInfo)
result: EventInfo = structured_llm.invoke(prompt)
```

### 4. Variable Substitution

Execution Plan에서 변수 치환:

```json
{
  "input": {
    "title": "${event_data.title}",           // 이전 Step 결과 참조
    "start_time": "${available_slots.best_slot.start}"  // 중첩 참조
  }
}
```

### 5. Verbose Debugging

LangChain 실행 흐름 전체 추적:

```python
from langchain_core.globals import set_debug

if verbose:
    set_debug(True)  # 프롬프트, 응답, 성능 지표 모두 출력

executor = SkillCardExecutor(card, verbose=True)
result = executor.execute(user_query="...")
```

**출력 예시:**
```
[llm/start] Entering LLM run...
[llm/end] [5.70s] Exiting LLM run...
  - prompt_eval_count: 534 tokens
  - eval_count: 33 tokens
  - total_duration: 5699324375 ns

[tool/start] Entering Tool run...
[tool/end] [1ms] Exiting Tool run...
```

## 🛠️ 문제해결

### Ollama 연결 실패

```
Error: Could not connect to Ollama
```

**해결:**
```bash
# Ollama 서버 시작
ollama serve

# 다른 터미널에서
ollama list  # 모델 확인
```

### 모델 미설치

```
Error: model 'gpt-oss:20b' not found
```

**해결:**
```bash
ollama pull gpt-oss:20b
```

### PyCharm 테스트 실패

Working directory 문제로 테스트 실패 시:
- `tests/conftest.py`가 자동으로 프로젝트 루트로 변경
- PyCharm에서 직접 실행 가능

### LangChain verbose 로그가 안 나올 때

```python
# langchain.globals (X) - 이 경로는 없음
# langchain_core.globals (O) - 올바른 경로

from langchain_core.globals import set_debug
set_debug(True)
```

## 📚 참고 자료

### 공식 문서
- [LangChain 공식 문서](https://docs.langchain.com/)
- [Ollama 공식 사이트](https://ollama.ai/)
- [Pydantic 문서](https://docs.pydantic.dev/)

### 주요 개념
- [Structured Output](https://python.langchain.com/docs/how_to/structured_output/)
- [Tool Calling](https://python.langchain.com/docs/how_to/tool_calling/)
- [Agent Types](https://python.langchain.com/docs/concepts/agents/)

### 프로젝트 참고
- 신한은행 자산관리 Agent (`.reviews/` 참조)
- Skill Card Pattern 설계

## 🔮 다음 단계

- [ ] **Step 07**: VectorDB 통합 (RAG 패턴)
- [ ] **Step 08**: Multi-Agent 시스템
- [ ] **Step 09**: 프로덕션 배포 (FastAPI + Docker)

## 📄 라이선스

MIT License

---

**Made with ❤️ using LangChain + Ollama**

🤖 Step 05 완료: Real Tool Integration with LLM + DB + Verbose Debugging

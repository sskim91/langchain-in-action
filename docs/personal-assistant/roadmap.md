# 개인비서 AI 프로젝트 로드맵

> Multi-Agent 개인비서 시스템 구축 프로젝트

## 🎯 프로젝트 목표

**LangChain + Ollama로 실전 수준의 Multi-Agent 시스템 구축**

- 일정/할일/메모 관리 Agent 3개
- Skill Card 기반 동적 Agent 관리
- Supervisor Agent로 자동 라우팅
- FastAPI REST API 제공

---

## 📊 현재 상태: Step 07 완료 ✅

### 완료된 작업

#### Step 01-03: 기본 환경
- [x] Ollama + LangChain 1.0 환경 구축
- [x] BaseAgent 클래스 구현
- [x] 기본 Tool 작성

#### Step 04: Skill Card Executor
- [x] SkillCardExecutor 구현
- [x] Variable Substitution (`${variable}`)
- [x] Static Execution Plan 순차 실행
- [x] 실습: `src/examples/07_skill_card_demo.py`

#### Step 05: Real Tool Integration
- [x] **LLM Tools**: parse_event_info (Structured Output)
- [x] **DB Tools**: get_calendar_events, create_event
- [x] **Logic Tools**: find_free_time
- [x] **Verbose 시스템**: 단계별 실행 추적
- [x] 실습: `src/examples/08_real_tools_demo.py`

#### Step 06: Dynamic Agent
- [x] ScheduleManagerAgent 구현
- [x] LLM이 Tool을 스스로 선택
- [x] Static vs Dynamic 비교 분석
- [x] 실습: `src/examples/09_dynamic_agent.py`

#### Step 07: LangGraph Supervisor 🆕
- [x] **LangGraph 의존성 추가**
- [x] **TodoManagerAgent 구현**: 할일 관리 전문 Agent
- [x] **todo_tools.py**: add_task, list_tasks, complete_task, delete_task
- [x] **PersonalAssistantSupervisor**: LangGraph StateGraph 기반 라우팅
- [x] **테스트 작성**: 32개 테스트 통과
- [x] 실습: `src/examples/10_langgraph_supervisor.py`

---

## 🗺️ 전체 로드맵

| Step | 내용 | 상태 |
|------|------|------|
| **01-03** | 기본 환경 구축 | ✅ 완료 |
| **04** | Skill Card Executor | ✅ 완료 |
| **05** | Real Tool Integration | ✅ 완료 |
| **06** | Dynamic Agent | ✅ 완료 |
| **07** | LangGraph Supervisor | ✅ 완료 |
| **08** | VectorDB 연동 | 🎯 다음 |
| **09** | KnowledgeManager Agent | ⏳ 대기 |
| **10** | FastAPI 통합 | ⏳ 대기 |
| **11+** | 캐싱, 로깅, 모니터링 | ⏳ 대기 |

---

## 🎯 Step 08: VectorDB 연동 (다음 단계)

### 목표

Supervisor의 라우팅을 키워드 매칭에서 의미 기반 매칭으로 업그레이드

### 구현 내용

1. **VectorDB 선택 및 설정**
   - FAISS 또는 ChromaDB 선택
   - Ollama Embeddings 설정

2. **Agent 설명 임베딩**
   - 각 Agent의 description 임베딩
   - VectorDB에 저장

3. **의미 기반 라우팅**
   - 사용자 질의 임베딩
   - 유사도 계산하여 Agent 선택

4. **Supervisor 통합**
   - LLM 기반 라우팅 → VectorDB 기반으로 대체 (옵션)

### 예상 효과

```python
# Before (LLM 기반 라우팅)
response = llm.invoke("일정? 할일? 분류해줘")

# After (의미 기반)
query_embedding = embeddings.embed_query("내일 팀 미팅")
similar_agents = vectordb.similarity_search(query_embedding, k=1)
return similar_agents[0]  # → schedule_agent
```

**장점:**
- ✅ 더 빠른 라우팅 (LLM 호출 없이)
- ✅ 유연한 질의 처리 ("미팅" → "일정" 매칭)
- ✅ Agent 추가 시 자동 반영

---

## 📁 현재 프로젝트 구조

```
langchain-in-action/
├── src/multi_agent_lab/
│   ├── platform/
│   │   └── skill_card/
│   │       ├── executor.py          # SkillCardExecutor
│   │       └── manager.py           # SkillCardManager
│   ├── domains/
│   │   └── personal_assistant/
│   │       ├── agents/
│   │       │   ├── schedule_manager.py  # ScheduleManagerAgent
│   │       │   ├── todo_manager.py      # TodoManagerAgent 🆕
│   │       │   └── supervisor.py        # PersonalAssistantSupervisor 🆕
│   │       ├── tools/
│   │       │   ├── schedule_tools.py    # LLM/DB/Logic Tools
│   │       │   └── todo_tools.py        # Todo Tools 🆕
│   │       └── storage/
│   │           └── memory_db.py         # In-memory DB
├── src/examples/
│   ├── 07_skill_card_demo.py        # Step 04
│   ├── 08_real_tools_demo.py        # Step 05
│   ├── 09_dynamic_agent.py          # Step 06
│   └── 10_langgraph_supervisor.py   # Step 07 🆕
├── tests/
│   └── personal_assistant/
│       ├── test_todo_tools.py       # 🆕
│       └── test_supervisor.py       # 🆕
└── docs/
    └── personal-assistant/
        ├── concepts.md
        ├── implementation-guide.md
        ├── patterns.md
        ├── roadmap.md (현재 문서)
        └── step-by-step/
            └── step-07-langgraph-supervisor.md  # 🆕
```

---

## 🔮 향후 계획

### Phase 2: Multi-Agent 시스템

**Step 08-10: Agent 추가**
- TodoManager Agent (할 일 관리)
- KnowledgeManager Agent (메모/지식 관리)
- Supervisor Agent (자동 라우팅)

**기대 효과:**
```python
supervisor = SupervisorAgent()

# 자동으로 적절한 Agent 선택
supervisor.chat("내일 회의 잡아줘")      # → ScheduleManager
supervisor.chat("프로젝트 문서 작성 추가")  # → TodoManager
supervisor.chat("Python 개념 메모")     # → KnowledgeManager
```

### Phase 3: 프로덕션화

**Step 11: FastAPI 통합**
- REST API 제공
- 요청/응답 모델 정의
- 에러 처리

**Step 12+: 엔터프라이즈 기능**
- 캐싱 (Redis)
- 로깅 (Structured Logging)
- 모니터링 (Prometheus)
- Admin 페이지

### Phase 4: RAG 구현

**Step 13-14: 지식 기반 강화**
- 문서 로드 및 임베딩
- RAG Tool 작성
- KnowledgeManager에 RAG 통합

---

## 💡 학습 순서 (추천)

### 1. 기본 개념 이해
- **[concepts.md](./concepts.md)** 읽기
- Agent, Skill Card, Tool 개념 파악

### 2. 패턴 학습
- **[patterns.md](./patterns.md)** 읽기
- Static vs Dynamic 비교 이해

### 3. 실전 구현
- **[step-by-step/](./step-by-step/)** 따라하기
- 각 Step별 구현 실습

### 4. 응용 및 확장
- **[implementation-guide.md](./implementation-guide.md)** 참고
- 자신만의 Agent/Tool 작성

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
cd langchain-in-action

# 의존성 설치
uv sync

# Ollama 모델 다운로드
ollama pull gpt-oss:20b
```

### 2. 예제 실행

```bash
# Step 04: Skill Card Executor
uv run python -m src.examples.07_skill_card_demo

# Step 05: Real Tools
uv run python -m src.examples.08_real_tools_demo

# Step 06: Dynamic Agent
uv run python -m src.examples.09_dynamic_agent
```

### 3. 직접 사용해보기

```python
from personal_assistant.agents import ScheduleManagerAgent

# Agent 생성
agent = ScheduleManagerAgent()

# 실행
response = agent.chat("내일 오후 2시에 팀 회의 잡아줘")
print(response)
```

---

## 📚 참고 자료

### 프로젝트 문서
- [concepts.md](./concepts.md) - 핵심 개념
- [implementation-guide.md](./implementation-guide.md) - 구현 가이드
- [patterns.md](./patterns.md) - 패턴 비교
- [step-by-step/](./step-by-step/) - 단계별 가이드

### 외부 문서
- [LangChain 공식 문서](https://python.langchain.com/)
- [Ollama 공식 문서](https://ollama.ai/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

---

## 📈 진행 상황 체크리스트

**완료된 Step:**
- [x] Step 01-03: 기본 환경 구축
- [x] Step 04: Skill Card Executor
- [x] Step 05: Real Tool Integration
- [x] Step 06: Dynamic Agent
- [x] Step 07: LangGraph Supervisor

**다음 Step:**
- [ ] Step 08: VectorDB 연동
- [ ] Step 09: KnowledgeManager Agent
- [ ] Step 10: FastAPI 통합

---

**작성일:** 2025-11-12
**프로젝트:** 개인비서 AI System
**버전:** 1.1.0 (간소화)

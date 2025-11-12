# 개인비서 AI 프로젝트

> LangChain + Ollama로 만드는 Multi-Agent 개인비서 시스템

## 🎯 프로젝트 소개

일정/할일/메모를 관리하는 3개의 전문 Agent가 협업하는 개인비서 AI 시스템입니다.

**핵심 기능:**
- 📅 **일정 관리**: 회의, 약속 생성/조회/수정
- ✅ **할 일 관리**: 작업 추가/완료/우선순위 관리
- 📝 **메모 관리**: 지식 저장/검색/태그 관리
- 🤖 **자동 라우팅**: Supervisor가 적절한 Agent 선택

**기술 스택:**
- LangChain 1.0 (Agent 프레임워크)
- Ollama (Local LLM: `gpt-oss:20b`)
- FastAPI (REST API)
- FAISS/ChromaDB (VectorDB)

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
# Dynamic Agent 예제
uv run python -m src.examples.09_dynamic_agent
```

### 3. 직접 사용하기

```python
from personal_assistant.agents import ScheduleManagerAgent

# Agent 생성
agent = ScheduleManagerAgent()

# 실행
response = agent.chat("내일 오후 2시에 팀 회의 잡아줘")
print(response)
```

---

## 📚 문서 구조

### 시작하기

1. **[concepts.md](./concepts.md)** - 핵심 개념 (10분) ⭐ 필수
   - Agent, Skill Card, Tool이란?
   - Static vs Dynamic 개요
   - Multi-Agent 시스템

2. **[patterns.md](./patterns.md)** - 패턴 비교 (15분)
   - Static Execution Plan 상세
   - Dynamic Agent 상세
   - 실제 비교 예시

3. **[implementation-guide.md](./implementation-guide.md)** - 구현 가이드 (30분)
   - Tool 작성 방법
   - Verbose 디버깅
   - 베스트 프랙티스

4. **[step-by-step/](./step-by-step/)** - 단계별 실습 (5-10시간)
   - Step 01-04: 기초부터 차근차근

5. **[roadmap.md](./roadmap.md)** - 프로젝트 로드맵
   - 완료된 작업
   - 다음 단계

### 추천 학습 순서

```
concepts.md 읽기 (개념 이해)
    ↓
patterns.md 읽기 (패턴 비교)
    ↓
step-by-step/ 따라하기 (실습)
    ↓
implementation-guide.md 참고 (심화)
```

---

## 🏗️ 프로젝트 구조

```
langchain-in-action/
├── src/
│   ├── core/
│   │   └── skill_cards/        # Skill Card 시스템
│   │       ├── executor.py     # Static Execution Plan
│   │       └── manager.py      # Skill Card 관리
│   ├── personal_assistant/
│   │   ├── agents/             # Agent들
│   │   │   └── schedule_manager.py
│   │   ├── tools/              # Tool들
│   │   │   └── schedule_tools.py
│   │   ├── database/           # DB
│   │   │   └── memory_db.py
│   │   └── skill_cards/        # Skill Card 정의
│   │       └── schedule_card.json
│   ├── examples/               # 실행 가능한 예제
│   │   ├── 07_skill_card_demo.py
│   │   ├── 08_real_tools_demo.py
│   │   └── 09_dynamic_agent.py
│   └── tests/
└── docs/
    └── personal-assistant/     # 현재 위치
```

---

## 📊 현재 진행 상황

### ✅ 완료 (Step 01-06)

- [x] 기본 환경 구축
- [x] Skill Card Executor (Static Plan)
- [x] Real Tool Integration (LLM/DB/Logic)
- [x] Verbose 디버깅 시스템
- [x] Dynamic Agent 구현
- [x] Static vs Dynamic 비교 분석

### 🎯 진행 중

- [ ] Step 07: VectorDB 연동 (다음 단계)

### ⏳ 예정

- [ ] Step 08-09: TodoManager, KnowledgeManager Agent
- [ ] Step 10: Supervisor Agent
- [ ] Step 11: FastAPI 통합

---

## 💡 핵심 개념 (요약)

### Agent = LLM + Tools + Logic

```python
Agent = {
    "LLM": "사고 (언어 모델)",
    "Tools": "행동 (함수들)",
    "Logic": "전략 (실행 방식)"
}
```

### Skill Card = Agent 행동 명세

JSON/DB로 Agent의 "무엇을", "어떻게", "제약사항"을 정의

```json
{
  "id": "SC_SCHEDULE_001",
  "tools": ["create_event", "find_free_time"],
  "execution_plan": [...],
  "constraints": [...]
}
```

### Static vs Dynamic

| Static Plan | Dynamic Agent |
|-------------|---------------|
| 고정된 순서 | LLM이 선택 |
| 예측 가능 | 유연함 |
| 비용 효율 | 효율적 |

**자세한 내용:** [concepts.md](./concepts.md)

---

## 🛠️ 실행 예제

### Step 04: Skill Card Executor (Static Plan)

```bash
uv run python -m src.examples.07_skill_card_demo
```

**특징:**
- Skill Card에 정의된 순서대로 Tool 실행
- 예측 가능, 감사 추적 용이

### Step 05: Real Tools

```bash
uv run python -m src.examples.08_real_tools_demo
```

**특징:**
- LLM Tool: 자연어 → 구조화 데이터
- DB Tool: 데이터베이스 조작
- Logic Tool: 비즈니스 로직
- Verbose 디버깅 시스템

### Step 06: Dynamic Agent

```bash
uv run python -m src.examples.09_dynamic_agent
```

**특징:**
- LLM이 상황을 보고 Tool 선택
- 필요한 Tool만 실행 (효율적)

---

## 📖 참고 자료

### 프로젝트 문서
- [concepts.md](./concepts.md) - 핵심 개념
- [patterns.md](./patterns.md) - 패턴 비교
- [implementation-guide.md](./implementation-guide.md) - 구현 가이드
- [step-by-step/](./step-by-step/) - 단계별 가이드
- [roadmap.md](./roadmap.md) - 프로젝트 로드맵

### 외부 문서
- [LangChain 공식 문서](https://python.langchain.com/)
- [Ollama 공식 문서](https://ollama.ai/)

---

## 🤔 FAQ

**Q: Agent가 여러 개 = 프로세스가 여러 개?**
A: 아닙니다. 하나의 프로세스 안에 여러 Agent 클래스가 있는 것입니다. (Java의 여러 @Service와 같음)

**Q: Dynamic Agent와 Static Plan 중 뭘 선택해야 하나요?**
A:
- 규정 준수/감사 필요 → Static Plan
- 유연성/사용자 경험 중요 → Dynamic Agent
- 실전에서는 Hybrid (둘 다 사용)

**Q: Verbose 모드는 언제 사용하나요?**
A:
- 개발/테스트: `verbose=True` (항상)
- 프로덕션: `verbose=False` (에러 시만 True)

---

## 🎓 다음 학습

1. **개념 이해**: [concepts.md](./concepts.md) 읽기
2. **패턴 학습**: [patterns.md](./patterns.md) 읽기
3. **실습 시작**: [step-by-step/](./step-by-step/) 따라하기

**준비되셨나요? [concepts.md](./concepts.md)부터 시작하세요!** 🚀

---

**작성일:** 2025-11-12
**프로젝트:** 개인비서 AI System
**현재 버전:** Step 06 완료

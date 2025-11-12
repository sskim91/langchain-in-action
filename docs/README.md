# 문서 가이드

LangChain + Ollama를 활용한 AI Agent 학습 프로젝트 문서입니다.

## 📚 문서 구조

```
docs/
├── README.md (현재 문서)
├── learning-guide.md           # LangChain 학습 로드맵 (범용)
├── package-guide.md            # Python 패키지 구조 가이드 (범용)
└── personal-assistant/         # 개인비서 AI 프로젝트
    ├── README.md               # 프로젝트 소개
    ├── concepts.md             # 핵심 개념
    ├── implementation-guide.md # 구현 가이드
    ├── patterns.md             # Static vs Dynamic 패턴 비교
    ├── roadmap.md              # 프로젝트 로드맵
    └── step-by-step/           # 단계별 구현 가이드
```

## 🎯 학습 경로

### 1. LangChain 기초 학습

**범용 LangChain 학습 (모든 프로젝트 공통)**

- **[learning-guide.md](./learning-guide.md)** - LangChain + Ollama 학습 로드맵
  - Level 1: 기본기 (Agent, Tool, Memory)
  - Level 2: Tool 활용 마스터
  - Level 3: Memory & Context 관리
  - Level 4: RAG (Retrieval-Augmented Generation)
  - Level 5: LangGraph & Multi-Agent

- **[package-guide.md](./package-guide.md)** - Python 패키지 구조 가이드
  - 모듈화, 계층 구조, import 시스템
  - 프로젝트 구조 설계 원칙

### 2. 개인비서 AI 프로젝트 (실습)

**실전 프로젝트로 Agent 개념 완전 마스터**

📁 **[personal-assistant/](./personal-assistant/)**

#### 시작하기

1. **[README.md](./personal-assistant/README.md)** - 프로젝트 소개 및 빠른 시작
2. **[concepts.md](./personal-assistant/concepts.md)** - 핵심 개념 (10분)
   - Agent, Skill Card, Tool이란?
   - Static vs Dynamic 개요
   - Multi-Agent 시스템
3. **[patterns.md](./personal-assistant/patterns.md)** - 패턴 비교 (15분)
   - Static Execution Plan 상세
   - Dynamic Agent 상세
   - Hybrid 접근 방법
4. **[implementation-guide.md](./personal-assistant/implementation-guide.md)** - 구현 가이드 (30분)
   - Tool 작성 방법 (LLM/DB/Logic)
   - Verbose 디버깅 시스템
   - Skill Card 작성
   - 베스트 프랙티스
5. **[step-by-step/](./personal-assistant/step-by-step/)** - 단계별 실습 (5-10시간)
   - Step 01: 프로젝트 구조 설정
   - Step 02: ScheduleManager Agent 구현
   - Step 03: Skill Card 시스템
   - Step 04: Skill Card Executor

#### 추천 학습 순서

```
1. concepts.md 읽기 (핵심 개념 이해)
   ↓
2. patterns.md 읽기 (패턴 비교)
   ↓
3. step-by-step/ 따라하기 (실습)
   ↓
4. implementation-guide.md 참고 (심화)
   ↓
5. roadmap.md 확인 (다음 단계)
```

---

## 🚀 빠른 시작

### 프로젝트가 처음이라면

1. **[learning-guide.md](./learning-guide.md)** 에서 Level 1-2 학습
2. **[personal-assistant/README.md](./personal-assistant/README.md)** 읽고 환경 설정
3. **[personal-assistant/concepts.md](./personal-assistant/concepts.md)** 로 개념 파악
4. **[personal-assistant/step-by-step/](./personal-assistant/step-by-step/)** 으로 실습 시작

### Agent 개념만 빠르게 이해하려면

1. **[personal-assistant/concepts.md](./personal-assistant/concepts.md)** (10분)
2. **[personal-assistant/patterns.md](./personal-assistant/patterns.md)** (15분)

### 바로 구현하려면

1. **[personal-assistant/implementation-guide.md](./personal-assistant/implementation-guide.md)** 로 시작
2. **[personal-assistant/step-by-step/](./personal-assistant/step-by-step/)** 에서 코드 확인

---

## 📖 주요 문서

### 범용 학습 자료

| 문서 | 설명 | 소요 시간 |
|------|------|----------|
| [learning-guide.md](./learning-guide.md) | LangChain + Ollama 학습 로드맵 | 읽기: 20분 |
| [package-guide.md](./package-guide.md) | Python 패키지 구조 가이드 | 읽기: 15분 |

### 개인비서 AI 프로젝트

| 문서 | 설명 | 소요 시간 |
|------|------|----------|
| [personal-assistant/README.md](./personal-assistant/README.md) | 프로젝트 소개 | 읽기: 5분 |
| [personal-assistant/concepts.md](./personal-assistant/concepts.md) | 핵심 개념 | 읽기: 10분 |
| [personal-assistant/patterns.md](./personal-assistant/patterns.md) | 패턴 비교 | 읽기: 15분 |
| [personal-assistant/implementation-guide.md](./personal-assistant/implementation-guide.md) | 구현 가이드 | 읽기: 30분 |
| [personal-assistant/roadmap.md](./personal-assistant/roadmap.md) | 프로젝트 로드맵 | 읽기: 10분 |
| [personal-assistant/step-by-step/](./personal-assistant/step-by-step/) | 단계별 실습 | 실습: 5-10시간 |

---

## 💡 학습 팁

### 1. 순서대로 진행
각 단계는 이전 단계를 기반으로 하므로 순서대로 학습하세요.

### 2. 실습 중심
문서만 읽지 말고 반드시 코드를 직접 작성하며 실습하세요.

### 3. 커밋 단위 관리
각 Step 완료 시 Git 커밋으로 진행 상황을 관리하세요.

### 4. 문서화 습관
구현한 내용은 주석과 docstring으로 문서화하세요.

---

## 🔗 외부 자료

### 공식 문서
- [LangChain 공식 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Ollama 공식 문서](https://ollama.ai/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

### 추천 자료
- [LangChain YouTube 채널](https://www.youtube.com/@LangChain)
- [Ollama 모델 라이브러리](https://ollama.ai/library)

---

## ❓ 자주 묻는 질문

### Q1. 어떤 문서부터 읽어야 하나요?

**A:**
1. 처음이라면: `learning-guide.md` → `personal-assistant/README.md`
2. Agent 개념만: `personal-assistant/concepts.md`
3. 바로 구현: `personal-assistant/implementation-guide.md`

### Q2. 실습 환경이 필요한가요?

**A:** 네, 다음이 필요합니다:
- Python 3.11+
- Ollama (Local LLM)
- uv (패키지 관리자)

자세한 설정: [personal-assistant/README.md](./personal-assistant/README.md#환경-설정)

### Q3. 코드 예제는 어디서 확인하나요?

**A:** `src/examples/` 폴더에서 확인 가능:
- `07_skill_card_demo.py` (Step 04)
- `08_real_tools_demo.py` (Step 05)
- `09_dynamic_agent.py` (Step 06)

---

**작성일:** 2025-11-12
**프로젝트:** LangChain + Ollama Agent 학습

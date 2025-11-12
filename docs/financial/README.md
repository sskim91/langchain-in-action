# 금융 투자 분석 Agent 프로젝트

> LangChain + Ollama로 만드는 실전 금융 AI Agent 시스템

## 🎯 프로젝트 소개

실제 금융 API를 활용하여 종목 분석, 포트폴리오 관리, 시황 분석을 수행하는 AI Agent 시스템입니다.

**핵심 기능:**
- 📊 **종목 분석**: 재무제표, 밸류에이션, 뉴스 기반 투자 의견
- 💼 **포트폴리오 분석**: 보유 자산 분석 및 리밸런싱 제안
- 📈 **시황 분석**: 시장 동향, 섹터 분석, 경제 지표
- 🤖 **자동 라우팅**: Supervisor가 적절한 Agent 선택

**기술 스택:**
- LangChain 1.0 (Agent 프레임워크)
- Ollama (Local LLM: `gpt-oss:20b`)
- yfinance/FinanceDataReader (금융 데이터 API)
- Core Skill Card System (재사용)

**아키텍처:**
```
신한은행 스타일 Skill Card 기반 설계
- Skill Card로 Agent 행동 정의
- RDB/API Tool로 구조화 데이터 조회
- VectorDB는 Skill Card 라우팅용 (문서 검색 없음)
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 루트에서
cd langchain-in-action

# 의존성 설치
uv sync

# 금융 데이터 라이브러리 추가
uv add yfinance finance-datareader

# Ollama 모델 다운로드
ollama pull gpt-oss:20b
```

### 2. 예제 실행

```bash
# Step 07: 금융 API Tool 예제
uv run python -m src.examples.10_financial_tools_demo

# Step 08: Skill Card 라우팅 예제
uv run python -m src.examples.11_skill_card_routing

# Step 09: Multi-Agent 시스템
uv run python -m src.examples.12_multi_agent_financial
```

### 3. 직접 사용하기

```python
from financial.agents import StockAnalysisAgent

# Agent 생성
agent = StockAnalysisAgent()

# 실행
response = agent.chat("삼성전자 최근 실적 분석하고 투자 의견 줘")
print(response)
```

---

## 📚 문서 구조

### 시작하기

1. **[README.md](./README.md)** - 프로젝트 소개 (현재 문서)
2. **[architecture.md](./architecture.md)** - 시스템 아키텍처
3. **[step-by-step/](./step-by-step/)** - 단계별 구현 가이드
   - Step 07: 금융 API Tool 작성
   - Step 08: Skill Card 라우팅
   - Step 09: Multi-Agent 시스템
   - Step 10: 실전 기능 추가

### 추천 학습 순서

```
architecture.md 읽기 (시스템 설계 이해)
    ↓
step-by-step/07-financial-tools.md (Tool 작성)
    ↓
step-by-step/08-skill-card-routing.md (라우팅)
    ↓
step-by-step/09-multi-agent.md (Multi-Agent)
    ↓
step-by-step/10-advanced-features.md (실전 기능)
```

---

## 🏗️ 프로젝트 구조

```
langchain-in-action/
├── src/
│   ├── core/                    # 공통 (기존)
│   │   └── skill_cards/
│   │       ├── executor.py      # Skill Card 실행기
│   │       └── manager.py       # Skill Card 관리자
│   ├── personal_assistant/      # 개인비서 (기존)
│   └── financial/               # 금융 (NEW)
│       ├── agents/
│       │   ├── stock_analysis_agent.py
│       │   ├── portfolio_agent.py
│       │   └── supervisor_agent.py
│       ├── tools/
│       │   ├── financial_data_tools.py
│       │   ├── analysis_tools.py
│       │   └── report_tools.py
│       ├── database/
│       │   └── memory_db.py
│       └── skill_cards/
│           ├── stock_analysis.json
│           └── portfolio_analysis.json
├── docs/
│   ├── personal-assistant/      # 개인비서 문서
│   └── financial/               # 금융 문서 (현재 위치)
│       ├── README.md
│       ├── architecture.md
│       └── step-by-step/
└── tests/
    └── financial/
```

---

## 📊 현재 진행 상황

### ✅ 완료 (기본 환경)

- [x] 프로젝트 구조 설정
- [x] 문서 초기화
- [x] Core Skill Card 시스템 (재사용)

### 🎯 진행 예정

- [ ] Step 07: 금융 API Tool 작성
- [ ] Step 08: Skill Card 라우팅
- [ ] Step 09: Multi-Agent 시스템
- [ ] Step 10: 실전 기능 추가

---

## 💡 핵심 개념

### Agent = LLM + Tools + Skill Card

```python
Agent = {
    "LLM": "사고 (언어 모델)",
    "Tools": "행동 (금융 API)",
    "Skill Card": "전략 (분석 프로세스)"
}
```

### Skill Card 기반 설계 (신한은행 스타일)

```json
{
  "id": "SC_STOCK_001",
  "name": "종목 분석",
  "tools": ["get_stock_price", "get_financial_statement"],
  "execution_plan": [
    {"step": 1, "action": "get_stock_price"},
    {"step": 2, "action": "get_financial_statement"},
    {"step": 3, "action": "analyze_valuation"}
  ]
}
```

### 데이터 소스 = RDB/API (RAG 없음)

```python
# ✅ 금융 데이터는 구조화되어 있음
get_stock_price("005930")       # yfinance API
get_financial_statement("삼성전자")  # FinanceDataReader

# ❌ 문서 임베딩/검색은 필요 없음
# VectorDB는 Skill Card 라우팅에만 사용
```

---

## 🎓 학습 목표

### Step 07: 금융 API Tool 작성
- yfinance로 주가 데이터 조회
- FinanceDataReader로 재무제표 조회
- Tool 작성 패턴 (LLM/DB/Logic)

### Step 08: Skill Card 라우팅
- Skill Card JSON 작성
- 키워드 기반 라우팅 구현
- SkillCardManager 활용

### Step 09: Multi-Agent 시스템
- 3개 전문 Agent 구현
- Supervisor Agent 라우팅
- Agent 간 협업

### Step 10: 실전 기능 추가
- 백테스팅 Tool
- 리포트 생성 (Markdown/PDF)
- 차트 생성 (matplotlib)

---

## 🔗 참고 자료

### 프로젝트 문서
- [architecture.md](./architecture.md) - 시스템 아키텍처
- [step-by-step/](./step-by-step/) - 단계별 가이드

### 외부 자료
- [yfinance 문서](https://github.com/ranaroussi/yfinance)
- [FinanceDataReader 문서](https://github.com/FinanceData/FinanceDataReader)
- [LangChain 공식 문서](https://python.langchain.com/)

### 관련 프로젝트
- [Personal Assistant](../personal-assistant/README.md) - Skill Card 개념 참고
- [신한은행 자산관리 Agent](.reviews/KT) - 실전 아키텍처 참고

---

## 🤔 FAQ

**Q: personal_assistant와 financial의 차이점은?**

A:
- **personal_assistant**: 일정/할일/메모 관리 (CRUD 중심)
- **financial**: 금융 데이터 분석 (API 연동 + 분석 중심)
- **공통**: `core/skill_cards` 시스템 재사용

**Q: RAG는 사용 안 하나요?**

A:
- 금융 데이터는 이미 구조화되어 있어 RAG 불필요
- VectorDB는 Skill Card 라우팅에만 사용 (신한은행 방식)
- 실시간 API 조회가 더 정확하고 최신 데이터 보장

**Q: 어떤 LLM을 사용하나요?**

A:
- Local: Ollama `gpt-oss:20b` (개발/테스트)
- Cloud: OpenAI/Claude (프로덕션 옵션)

---

## 🚀 다음 단계

1. **[architecture.md](./architecture.md)** 읽고 전체 설계 파악
2. **[step-by-step/07-financial-tools.md](./step-by-step/07-financial-tools.md)** 로 Tool 작성 시작
3. 단계별로 구현하며 실습

**준비되셨나요? [architecture.md](./architecture.md)부터 시작하세요!** 🚀

---

**작성일:** 2025-11-12
**프로젝트:** 금융 투자 분석 AI Agent System
**현재 버전:** Step 07 준비 중

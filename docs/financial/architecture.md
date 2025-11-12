# 금융 투자 분석 Agent 아키텍처

> 섭섭은행 스타일 Skill Card 기반 실전 금융 AI 시스템 설계

## 🎯 설계 철학

### 핵심 원칙

1. **Skill Card 기반 통제 가능한 AI**
   - LLM의 불확실성을 Skill Card로 제어
   - 예측 가능하고 감사 추적 가능한 실행

2. **구조화 데이터 우선**
   - 금융 데이터는 이미 구조화되어 있음
   - RAG(문서 검색) 대신 API/DB 직접 조회

3. **Core 재사용**
   - `core/skill_cards` 시스템 재사용
   - `personal_assistant`에서 검증된 패턴 활용

---

## 🏗️ 전체 시스템 아키텍처

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                     User Query                       │
│         "삼성전자 최근 실적 분석하고 투자 의견 줘"      │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              Supervisor Agent                        │
│  - Skill Card 선택 (키워드/의미 기반)                  │
│  - 적절한 전문 Agent로 라우팅                          │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   종목분석   │ │ 포트폴리오  │ │   시황분석   │
│    Agent    │ │   Agent     │ │    Agent    │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│           Skill Card Executor (Core)                 │
│  - Skill Card 로드 및 파싱                            │
│  - Tool 순차 실행                                    │
│  - 변수 치환 (${variable})                           │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  LLM Tools  │ │  API Tools  │ │ Logic Tools │
└─────────────┘ └─────────────┘ └─────────────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              External Data Sources                   │
│  - yfinance (주가 데이터)                            │
│  - FinanceDataReader (재무제표)                      │
│  - News API (뉴스 크롤링)                            │
│  - Memory DB (사용자 포트폴리오)                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 패키지 구조

### 디렉토리 레이아웃

```
src/
├── core/                           # 공통 (재사용)
│   └── skill_cards/
│       ├── executor.py             # SkillCardExecutor
│       └── manager.py              # SkillCardManager
│
├── personal_assistant/             # 개인비서 (기존)
│   ├── agents/
│   ├── tools/
│   └── skill_cards/
│
└── financial/                      # 금융 (NEW)
    ├── __init__.py
    ├── agents/                     # Agent 구현
    │   ├── __init__.py
    │   ├── base_agent.py           # BaseFinancialAgent
    │   ├── stock_analysis_agent.py # 종목 분석
    │   ├── portfolio_agent.py      # 포트폴리오 분석
    │   ├── market_agent.py         # 시황 분석
    │   └── supervisor_agent.py     # 라우터
    │
    ├── tools/                      # Tool 구현
    │   ├── __init__.py
    │   ├── financial_data_tools.py # 금융 데이터 조회
    │   ├── analysis_tools.py       # 분석 로직
    │   └── report_tools.py         # 리포트 생성
    │
    ├── database/                   # 데이터베이스
    │   ├── __init__.py
    │   └── memory_db.py            # In-memory DB
    │
    └── skill_cards/                # Skill Card 정의
        ├── __init__.py
        ├── stock_analysis.json     # 종목 분석
        ├── portfolio_analysis.json # 포트폴리오 분석
        └── market_analysis.json    # 시황 분석
```

---

## 🎴 Skill Card 기반 설계

### Skill Card란?

Agent의 행동을 JSON으로 정의한 메타데이터

```json
{
  "id": "SC_STOCK_001",
  "name": "종목 분석",
  "description": "개별 종목의 재무, 밸류에이션, 뉴스를 종합 분석",
  "keywords": ["종목", "주식", "분석", "실적", "재무제표"],
  "tools": [
    "get_stock_price",
    "get_financial_statement",
    "calculate_valuation",
    "get_analyst_reports"
  ],
  "execution_plan": [
    {
      "step": 1,
      "action": "get_stock_price",
      "params": {"ticker": "${user_input.ticker}"}
    },
    {
      "step": 2,
      "action": "get_financial_statement",
      "params": {"ticker": "${user_input.ticker}"}
    },
    {
      "step": 3,
      "action": "calculate_valuation",
      "params": {
        "price": "${step1.current_price}",
        "eps": "${step2.eps}"
      }
    }
  ],
  "constraints": [
    "과거 데이터만 사용 (미래 예측 금지)",
    "금융감독원 규정 준수"
  ]
}
```

### Skill Card 실행 흐름

```
1. Supervisor가 사용자 질의 분석
   "삼성전자 분석해줘" → "종목 분석" Skill Card 선택

2. SkillCardExecutor가 Skill Card 로드
   stock_analysis.json 파싱

3. Execution Plan 순차 실행
   Step 1: get_stock_price("005930")
   Step 2: get_financial_statement("005930")
   Step 3: calculate_valuation(...)

4. 변수 치환
   ${step1.current_price} → 75000
   ${step2.eps} → 5000

5. 최종 결과 생성
   LLM이 Tool 결과를 자연어로 요약
```

---

## 🛠️ Tool 아키텍처

### Tool 3가지 유형

#### 1. API Tools (외부 데이터 조회)

```python
from langchain_core.tools import tool
import yfinance as yf

@tool
def get_stock_price(ticker: str) -> dict:
    """
    주가 데이터 조회

    Args:
        ticker: 종목 코드 (예: "005930" 또는 "AAPL")

    Returns:
        현재가, 52주 최고/최저, 거래량 등
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "current_price": info.get("currentPrice"),
        "high_52w": info.get("fiftyTwoWeekHigh"),
        "low_52w": info.get("fiftyTwoWeekLow"),
        "volume": info.get("volume"),
    }
```

#### 2. Logic Tools (비즈니스 로직)

```python
@tool
def calculate_valuation(
    current_price: float,
    eps: float,
    industry_avg_per: float = 15.0
) -> dict:
    """
    밸류에이션 분석

    Args:
        current_price: 현재 주가
        eps: 주당순이익 (EPS)
        industry_avg_per: 업종 평균 PER

    Returns:
        PER, 적정가, 투자 의견
    """
    per = current_price / eps
    fair_value = eps * industry_avg_per

    if per < industry_avg_per * 0.8:
        opinion = "매수"
    elif per > industry_avg_per * 1.2:
        opinion = "매도"
    else:
        opinion = "중립"

    return {
        "per": per,
        "fair_value": fair_value,
        "opinion": opinion
    }
```

#### 3. LLM Tools (자연어 처리)

```python
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

class InvestmentOpinion(BaseModel):
    rating: str = Field(description="투자 의견 (매수/중립/매도)")
    target_price: int = Field(description="목표 주가")
    reason: str = Field(description="투자 의견 근거")

@tool
def generate_investment_opinion(
    financial_data: dict,
    valuation_data: dict
) -> dict:
    """
    투자 의견 생성 (LLM 활용)
    """
    llm = ChatOllama(model="gpt-oss:20b")
    structured_llm = llm.with_structured_output(InvestmentOpinion)

    prompt = f"""
    다음 데이터를 바탕으로 투자 의견을 제시하세요:

    재무 데이터: {financial_data}
    밸류에이션: {valuation_data}
    """

    result = structured_llm.invoke(prompt)
    return result.model_dump()
```

### Tool 등록 및 실행

```python
from core.skill_cards.executor import SkillCardExecutor
from financial.tools.financial_data_tools import get_stock_price
from financial.tools.analysis_tools import calculate_valuation

# Executor 생성
executor = SkillCardExecutor(skill_card_path="stock_analysis.json")

# Tool 등록
executor.register_tool("get_stock_price", get_stock_price)
executor.register_tool("calculate_valuation", calculate_valuation)

# 실행
result = executor.execute(
    user_query="삼성전자 분석해줘",
    context={"ticker": "005930"}
)
```

---

## 🤖 Agent 아키텍처

### Agent 계층 구조

```
BaseFinancialAgent (추상 클래스)
    ├── StockAnalysisAgent (종목 분석)
    ├── PortfolioAgent (포트폴리오 분석)
    ├── MarketAgent (시황 분석)
    └── SupervisorAgent (라우터)
```

### BaseFinancialAgent

```python
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama

class BaseFinancialAgent(ABC):
    """금융 Agent 기본 클래스"""

    def __init__(self):
        self.llm = ChatOllama(model="gpt-oss:20b", temperature=0.0)
        self.tools = []
        self.skill_card_path = None

    @abstractmethod
    def chat(self, query: str) -> str:
        """사용자 질의 처리"""
        pass

    def execute_skill_card(self, context: dict) -> dict:
        """Skill Card 실행"""
        from core.skill_cards.executor import SkillCardExecutor

        executor = SkillCardExecutor(self.skill_card_path)
        for tool in self.tools:
            executor.register_tool(tool.__name__, tool)

        return executor.execute(
            user_query=context.get("query"),
            context=context
        )
```

### StockAnalysisAgent

```python
class StockAnalysisAgent(BaseFinancialAgent):
    """종목 분석 Agent"""

    def __init__(self):
        super().__init__()
        self.skill_card_path = "financial/skill_cards/stock_analysis.json"
        self.tools = [
            get_stock_price,
            get_financial_statement,
            calculate_valuation,
        ]

    def chat(self, query: str) -> str:
        # 1. 종목 코드 추출
        ticker = self._extract_ticker(query)

        # 2. Skill Card 실행
        result = self.execute_skill_card({
            "query": query,
            "ticker": ticker
        })

        # 3. LLM으로 자연어 응답 생성
        return self._generate_response(result)
```

### SupervisorAgent

```python
class SupervisorAgent:
    """Agent 라우터"""

    def __init__(self):
        self.agents = {
            "stock_analysis": StockAnalysisAgent(),
            "portfolio": PortfolioAgent(),
            "market": MarketAgent(),
        }

    def route(self, query: str) -> str:
        # 1. 키워드 기반 라우팅
        if any(kw in query for kw in ["종목", "주식", "분석"]):
            agent = self.agents["stock_analysis"]
        elif any(kw in query for kw in ["포트폴리오", "자산"]):
            agent = self.agents["portfolio"]
        else:
            agent = self.agents["market"]

        # 2. 선택된 Agent 실행
        return agent.chat(query)
```

---

## 🔄 데이터 흐름

### 전체 데이터 흐름

```
User Query
    ↓
Supervisor Agent (라우팅)
    ↓
전문 Agent (종목/포트폴리오/시황)
    ↓
Skill Card Executor
    ↓
Tools (API/Logic/LLM)
    ↓
External Data Sources
    ├── yfinance (주가)
    ├── FinanceDataReader (재무제표)
    ├── News API (뉴스)
    └── Memory DB (사용자 데이터)
    ↓
결과 수집 및 변수 치환
    ↓
LLM 응답 생성
    ↓
Final Answer (자연어)
```

### 예시: "삼성전자 분석해줘" 실행 흐름

```
1. SupervisorAgent.route("삼성전자 분석해줘")
   → "종목" 키워드 감지 → StockAnalysisAgent 선택

2. StockAnalysisAgent.chat("삼성전자 분석해줘")
   → 종목 코드 추출: "005930"
   → Skill Card 실행 요청

3. SkillCardExecutor.execute(context={"ticker": "005930"})
   → stock_analysis.json 로드

4. Step 1: get_stock_price("005930")
   → yfinance API 호출
   → {"current_price": 75000, "high_52w": 85000, ...}

5. Step 2: get_financial_statement("005930")
   → FinanceDataReader API 호출
   → {"eps": 5000, "revenue": 1000000000, ...}

6. Step 3: calculate_valuation(price=75000, eps=5000)
   → 비즈니스 로직 실행
   → {"per": 15.0, "fair_value": 75000, "opinion": "중립"}

7. 결과 취합 및 변수 치환
   → context = {step1: {...}, step2: {...}, step3: {...}}

8. LLM 응답 생성
   → ChatOllama로 자연어 요약
   → "삼성전자(005930) 현재가 75,000원, PER 15배로 적정 수준입니다..."
```

---

## 🎯 섭섭은행과의 차이점

### 유사점

- ✅ Skill Card 기반 통제 가능한 AI
- ✅ 구조화 데이터 우선 (API/DB 조회)
- ✅ VectorDB는 라우팅용 (문서 검색 X)
- ✅ Multi-Agent 시스템

### 차이점

| 항목 | 섭섭은행 | 우리 프로젝트 |
|------|---------|-------------|
| **규모** | 엔터프라이즈급 | 학습 프로젝트 |
| **데이터** | 행내 Vertica, EAI | yfinance, FinanceDataReader |
| **인프라** | 클라우드, MCP 서버 | 로컬 Ollama |
| **라우팅** | VectorDB (Semantic Search) | 키워드 기반 (단순) |
| **UI** | SuperSOL, AI One | CLI (추후 FastAPI) |

---

## 📊 성능 고려사항

### 최적화 전략

1. **Tool 실행 병렬화**
   - 독립적인 Tool은 동시 실행
   - 예: 주가 조회 + 뉴스 조회 병렬 처리

2. **캐싱**
   - 동일한 API 요청 결과 캐싱 (5분)
   - 예: `get_stock_price("005930")` 결과 캐싱

3. **LLM 호출 최소화**
   - Skill Card로 Tool 순서 고정 → LLM 호출 1회
   - 변수 치환으로 중간 결과 활용

---

## 🔐 보안 고려사항

### 규정 준수

1. **금융 데이터 보호**
   - 사용자 포트폴리오 데이터 암호화
   - 로그에 민감 정보 제외

2. **LLM 출력 검증**
   - 투자 권유 표현 제한
   - "투자 판단은 본인 책임" 명시

3. **API 키 관리**
   - 환경 변수로 API 키 관리
   - .env 파일 git ignore

---

## 🚀 확장 계획

### Phase 1: 기본 기능 (Step 07-09)
- 금융 API Tool 작성
- Skill Card 라우팅
- Multi-Agent 시스템

### Phase 2: 실전 기능 (Step 10)
- 백테스팅 Tool
- 리포트 생성 (PDF)
- 차트 생성 (plotly)

### Phase 3: VectorDB 라우팅
- Skill Card 임베딩
- Semantic Search 기반 라우팅

### Phase 4: FastAPI 통합
- REST API 제공
- 웹 UI 연동

---

**작성일:** 2025-11-12
**프로젝트:** 금융 투자 분석 AI Agent System
**버전:** 1.0.0

# Agent 개념 완전 가이드

> Java Spring 개발자를 위한 AI Agent 핵심 개념 설명
>
> **실습 프로젝트: 개인 비서 AI System** 🤖

## 목차

1. [Agent란 무엇인가?](#agent란-무엇인가)
2. [Skill Card 개념](#skill-card-개념)
3. [Multi-Agent 시스템](#multi-agent-시스템)
4. [Agent vs Java Spring 비교](#agent-vs-java-spring-비교)
5. [실전 예제: 개인 비서 Agent](#실전-예제-개인-비서-agent)

---

## Agent란 무엇인가?

### 정의

**Agent = LLM + Tools + Memory + 실행 로직**

```python
Agent = {
    "LLM": "언어 모델 (GPT, Llama, etc.)",
    "Tools": "사용할 수 있는 도구들 (함수, API)",
    "Memory": "대화 기록 및 컨텍스트",
    "Logic": "실행 방식 (ReAct, Plan & Execute, etc.)"
}
```

### Java Spring과 비교

| Python Agent | Java Spring | 설명 |
|--------------|-------------|------|
| `BaseAgent` | `abstract class Service` | 추상 클래스 |
| `InvestmentAgent` | `@Service InvestmentService` | 구체 구현 |
| `SupervisorAgent` | `@Controller` | 라우팅 |
| `Tool` | `@Repository` / External API | 데이터 접근 |
| `SkillCard` | `application.yml` + Config | 설정 |
| `execute()` | `process()` | 비즈니스 로직 |

### 간단한 예제

```python
# Agent 정의
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model_name="gpt-oss:20b",        # LLM 선택
            temperature=0.1,                  # 생성 온도
            system_prompt="You are helpful", # 역할 정의
            tools=[calculator, search_web]    # 사용 가능 도구
        )

    def execute(self, query: str) -> str:
        # Agent 실행 로직
        return self.agent.invoke(query)
```

---

## Skill Card 개념

### 정의

**Skill Card = Agent가 "무엇을", "어떻게" 할지 정의한 메타데이터**

### 왜 필요한가?

**문제: LLM의 불확실성**
```python
# ❌ 문제가 있는 방식
llm.chat("펀드 추천해줘")
# → 매번 다르게 동작
# → 어떤 Tool을 호출할지 예측 불가
# → 컴플라이언스 위반 가능성
```

**해결: Skill Card로 통제**
```python
# ✅ Skill Card 기반
skill_card = {
    "name": "투자 상품 추천 Agent",
    "tools": ["get_customer_profile", "search_funds"],
    "execution_plan": [
        "1. 고객 프로필 조회",
        "2. 투자 성향 분석",
        "3. 적합 상품 검색",
        "4. 추천 생성"
    ],
    "constraints": [
        "투자 권유 표현 금지",
        "수익률 보장 언급 금지"
    ]
}

agent.execute(query, skill_card)
# → 항상 같은 순서로 실행
# → 제약사항 자동 적용
# → 예측 가능
```

### Skill Card 구조

```json
{
  "id": "SC_INVEST_001",
  "version": "1.0.0",
  "agent_name": "투자 상품 전문가",
  "description": "고객 투자 성향 기반 펀드/ETF 추천",

  "trigger": {
    "keywords": ["펀드", "ETF", "추천", "상품"],
    "similarity_threshold": 0.85
  },

  "tools": [
    "get_customer_profile",
    "search_investment_products",
    "calculate_risk"
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "get_customer_profile",
      "input": {"customer_id": "${context.customer_id}"},
      "output_to": "customer_data"
    },
    {
      "step": 2,
      "action": "search_investment_products",
      "input": {
        "tendency": "${customer_data.tendency}",
        "risk_level": "${customer_data.risk_tolerance}"
      },
      "output_to": "products"
    }
  ],

  "constraints": {
    "compliance": [
      "투자 권유 표현 금지",
      "수익률 보장 언급 금지"
    ],
    "output_format": "markdown",
    "max_response_length": 1000
  },

  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 800
  }
}
```

### Java Config와 비교

```java
// Spring의 application.yml과 유사
@Configuration
public class AgentConfig {

    @Bean
    public InvestmentService investmentService() {
        return InvestmentService.builder()
            .name("투자 상품 전문가")
            .tools(Arrays.asList(
                customerProfileTool,
                productSearchTool
            ))
            .constraints(Constraints.builder()
                .maxResponseLength(1000)
                .complianceRules(Arrays.asList(
                    "투자 권유 금지"
                ))
                .build()
            )
            .build();
    }
}
```

**차이점:**
- Java: 코드로 정의 → 변경 시 재컴파일/재배포 필요
- Skill Card: JSON/DB로 정의 → 런타임 변경 가능, Admin 페이지에서 수정

---

## Multi-Agent 시스템

### Agent가 여러 개인 이유

#### 1. 역할(Role)이 다르다 ⭐ (가장 중요)

```python
# Agent 1: 일정 관리자
class ScheduleManagerAgent(BaseAgent):
    system_prompt = "당신은 일정 관리 전문가입니다."
    tools = [create_event, find_free_time, set_reminder]

# Agent 2: 할 일 관리자
class TodoManagerAgent(BaseAgent):
    system_prompt = "당신은 할 일 관리 전문가입니다."
    tools = [add_task, prioritize_tasks, track_completion]

# Agent 3: 메모/지식 관리자
class KnowledgeManagerAgent(BaseAgent):
    system_prompt = "당신은 지식 관리 전문가입니다."
    tools = [save_note, search_notes, organize_knowledge]
```

**Java 비유:**
```java
@Service
class ScheduleService { }    // 일정 관리

@Service
class TodoService { }        // 할 일 관리

@Service
class KnowledgeService { }   // 메모/지식 관리
```

#### 2. 사용하는 LLM이 다를 수 있다

```python
# Agent 1: 복잡한 분석 → 큰 모델
class ComplexAnalysisAgent(BaseAgent):
    model_name = "gpt-4"  # 비싸지만 똑똑함

# Agent 2: 간단한 요약 → 작은 모델
class SimpleSummaryAgent(BaseAgent):
    model_name = "gpt-3.5-turbo"  # 싸고 빠름

# Agent 3: 한국어 특화 → 로컬 모델
class KoreanChatAgent(BaseAgent):
    model_name = "llama3-korean:8b"  # Ollama 로컬
```

#### 3. 사용하는 Tool이 다르다

```python
# Agent 1: 일정 관련 Tool만
schedule_agent = Agent(tools=[
    create_event,
    find_free_time,
    set_reminder
])

# Agent 2: 할 일 관련 Tool만
todo_agent = Agent(tools=[
    add_task,
    complete_task,
    list_tasks
])

# Agent 3: 메모 관련 Tool만
knowledge_agent = Agent(tools=[
    save_note,
    search_notes,
    tag_note
])
```

#### 4. 실행 방식이 다르다

```python
# Agent 1: 한 번에 실행 (Single-shot)
class QuickAnswerAgent:
    def execute(self, query):
        return self.llm.invoke(query)

# Agent 2: 계획 후 실행 (Plan & Execute)
class PlannerAgent:
    def execute(self, query):
        plan = self.create_plan(query)
        results = [self.execute_step(s) for s in plan]
        return self.synthesize(results)

# Agent 3: 대화형 (Interactive)
class ConversationalAgent:
    def execute(self, query, history):
        messages = history + [{"role": "user", "content": query}]
        return self.llm.invoke(messages)
```

#### 5. 제약사항이 다르다

```python
# Agent 1: 컴플라이언스 엄격 (대고객용)
class CustomerFacingAgent:
    def execute(self, query):
        result = super().execute(query)
        if self.contains_investment_advice(result):
            return "투자 권유는 제공할 수 없습니다."
        return result

# Agent 2: 제약 없음 (내부 직원용)
class InternalAgent:
    def execute(self, query):
        return super().execute(query)  # 자유롭게
```

### 정리: Agent 여러 개 = 전문가 여러 명

| 구분 | Agent 1 | Agent 2 | Agent 3 |
|------|---------|---------|---------|
| **역할** | 일정 관리 | 할 일 관리 | 메모/지식 관리 |
| **LLM** | GPT-4 | GPT-3.5 | Llama3-Korean |
| **Tool** | 일정생성, 알림설정 | 작업추가, 우선순위 | 메모저장, 검색 |
| **온도** | 0.1 (정확) | 0.2 (중간) | 0.5 (창의적) |
| **제약** | 시간형식 엄격 | 중간 | 자유로운 메모 |

---

## Agent vs Java Spring 비교

### 프로세스 수

**❌ 잘못된 이해:**
```bash
# Agent를 여러 프로세스로 띄우는 게 아닙니다!
python agent1.py &  # PID 1001
python agent2.py &  # PID 1002
python agent3.py &  # PID 1003
```

**✅ 올바른 이해:**
```bash
# 하나의 프로세스 (Spring Boot처럼)
python main.py  # PID 1001 (모든 Agent 포함)
```

```python
# main.py 내부
agents = {
    "investment": InvestmentAdvisorAgent(),
    "portfolio": PortfolioAnalyzerAgent(),
    "market": MarketAnalysisAgent()
}

# 요청마다 적절한 Agent 선택
selected_agent = agents[skill_card.agent_type]
result = await selected_agent.execute(query)
```

### 프로젝트 구조

**Java Spring:**
```
spring-boot-app/
├── src/main/java/
│   ├── controller/
│   │   └── AssistantController.java
│   ├── service/
│   │   ├── ScheduleService.java
│   │   ├── TodoService.java
│   │   └── KnowledgeService.java
│   └── repository/
│       └── EventRepository.java
└── application.yml
```

**Python Agent:**
```
langchain-in-action/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── schedule_manager.py
│   │   ├── todo_manager.py
│   │   └── knowledge_manager.py
│   ├── tools/
│   │   ├── schedule_tools.py
│   │   ├── todo_tools.py
│   │   └── knowledge_tools.py
│   ├── supervisor/
│   │   └── supervisor_agent.py
│   └── main.py  # FastAPI app
└── skill_cards/
    ├── SC_SCHEDULE_001.json
    ├── SC_TODO_001.json
    └── SC_KNOWLEDGE_001.json
```

### 실행 흐름 비교

**Java Spring:**
```
Client Request
    ↓
DispatcherServlet
    ↓
@Controller
    ↓
@Service (선택)
    ↓
비즈니스 로직 실행
```

**Python Agent:**
```
Client Request
    ↓
FastAPI Router
    ↓
Supervisor Agent
    ↓
Skill Card 검색 (VectorDB)
    ↓
Agent 선택 & 인스턴스화
    ↓
Agent.execute() (Skill Card 기반)
```

### 용어 매핑

| Python Agent | Java Spring | 역할 |
|--------------|-------------|------|
| `BaseAgent` | `interface Service` | 추상화 |
| `ScheduleManagerAgent` | `@Service ScheduleService` | 구현체 |
| `SupervisorAgent` | `@Controller + Router` | 라우팅 |
| `Tool` | `@Repository` / External API | 데이터 접근 |
| `SkillCard` | `@Configuration` + yml | 설정 |
| `await agent.execute()` | `service.process()` | 비즈니스 로직 |
| `FastAPI app` | `@SpringBootApplication` | 애플리케이션 |

---

## 실전 예제: 개인 비서 Agent

### 1. 단일 Agent 구현

```python
# src/agents/schedule_manager.py
from .base import BaseAgent
from ..tools.schedule_tools import create_event, find_free_time, set_reminder

class ScheduleManagerAgent(BaseAgent):
    """일정 관리 Agent"""

    def __init__(self):
        super().__init__(
            model_name="gpt-oss:20b",
            temperature=0.1,
            system_prompt="""
당신은 개인 비서의 일정 관리 전문가입니다.
사용자의 일정을 생성, 조회, 수정하고 알림을 설정합니다.
항상 시간 형식(YYYY-MM-DD HH:MM)을 정확히 지켜주세요.
            """,
            tools=[create_event, find_free_time, set_reminder]
        )
```

### 2. Supervisor Agent 구현

```python
# src/supervisor/supervisor_agent.py
class SupervisorAgent:
    """Agent 선택 및 실행"""

    def __init__(self):
        # 모든 Agent 인스턴스 생성
        self.agents = {
            "schedule": ScheduleManagerAgent(),
            "todo": TodoManagerAgent(),
            "knowledge": KnowledgeManagerAgent()
        }
        self.skill_card_selector = SkillCardSelector()

    async def route(self, query: str, context: dict = {}) -> dict:
        # 1. 적절한 Skill Card 검색
        skill_card = await self.skill_card_selector.select(query)

        # 2. Agent 선택
        agent = self.agents[skill_card.agent_type]

        # 3. Agent 실행
        result = await agent.execute(query, context)

        return result
```

### 3. FastAPI 애플리케이션

```python
# src/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
supervisor = SupervisorAgent()

class ChatRequest(BaseModel):
    query: str
    context: dict = {}

@app.post("/chat")
async def chat(request: ChatRequest):
    """채팅 엔드포인트"""
    result = await supervisor.route(
        query=request.query,
        context=request.context
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. 사용 예시

```bash
# 서버 실행
python src/main.py

# 요청 1: 일정 생성 → ScheduleManagerAgent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "내일 오후 3시에 회의 일정 잡아줘"}'

# 요청 2: 할 일 추가 → TodoManagerAgent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "프로젝트 문서 작성하기를 할 일에 추가해줘"}'

# 요청 3: 메모 저장 → KnowledgeManagerAgent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Python Agent 개념을 메모해줘"}'
```

---

## 핵심 개념 정리

### Q&A

**Q1. Agent가 여러 개 = 프로세스가 여러 개?**
- ❌ 아닙니다. 하나의 프로세스 안에 여러 Agent 클래스가 있는 것입니다.
- Java Spring에서 여러 @Service가 하나의 애플리케이션 안에 있는 것과 같습니다.

**Q2. Agent가 여러 개 = LLM이 다른 것?**
- ⚠️ 다를 *수도* 있습니다 (선택사항)
- 더 중요한 건: 역할, Tool, 제약사항이 다릅니다.
- 같은 LLM을 사용하더라도 system_prompt와 tools가 다르면 전혀 다른 Agent입니다.

**Q3. Skill Card는 Agent를 호출하나?**
- ❌ 아닙니다.
- ✅ Supervisor Agent가 Skill Card를 선택하고, 해당 Agent를 실행합니다.

**Q4. Skill Card vs Java Config?**
- Java Config: 코드로 정의, 변경 시 재배포
- Skill Card: JSON/DB로 정의, 런타임 변경 가능

**Q5. 언제 프로세스를 여러 개 띄우나?**
- 대규모 분산 시스템에서만 (선택사항)
- 학습/POC 단계에서는 단일 프로세스로 충분합니다.

---

## 다음 단계

### Phase 1: 기본 Agent 구현 (현재 단계)
- [ ] BaseAgent 이해
- [ ] 단일 Agent 구현 (ScheduleManagerAgent)
- [ ] Tool 2-3개 작성
- [ ] 간단한 실행 테스트

### Phase 2: Multi-Agent 시스템
- [ ] Agent 3개 구현 (Schedule, Todo, Knowledge)
- [ ] Supervisor Agent 구현
- [ ] Skill Card 3개 작성
- [ ] 자동 Agent 선택 테스트

### Phase 3: Skill Card 고도화
- [ ] VectorDB 연동 (Skill Card 검색)
- [ ] Execution Plan 구현
- [ ] Constraints 적용
- [ ] 품질 평가

### Phase 4: 실전 기능
- [ ] 캐싱 (Redis)
- [ ] 로깅 (trace_id 기반)
- [ ] 모니터링 (Prometheus)
- [ ] Admin 페이지

---

## 참고 자료

- [프로젝트 로드맵](./PROJECT_ROADMAP.md) - 6주 실습 계획
- [학습 경로](./LEARNING_PATH.md) - LangChain 학습 가이드
- [LangChain 공식 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)

---

**프로젝트:** 개인 비서 AI System 🤖
**작성일:** 2025-11-10
**버전:** 1.0.0

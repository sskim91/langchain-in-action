# Multi-Agent Lab Architecture

## 개요

**Multi-Agent Lab**은 학습과 실전 적용을 모두 고려한 Multi-Agent 시스템 프레임워크입니다.

## 설계 원칙

### 1. Domain-First Design
- 비즈니스 도메인을 최상위 조직 단위로 사용
- 각 도메인은 독립적으로 실행 가능
- 도메인 간 명확한 경계와 인터페이스

### 2. 학습 중심 구조
- 복잡도를 최소화하여 학습 곡선 완화
- 실전 적용 가능한 패턴 사용
- 확장 가능하지만 과도하지 않은 추상화

### 3. 계층적 Agent 구조
```
MasterAgent (Orchestrator)
    └── Domain Supervisors
            └── Specialized Agents
                    └── Tools
```

## 디렉토리 구조

```
src/multi_agent_lab/
├── core/                   # 프레임워크 핵심 (Agent 기반 클래스, 미들웨어)
│   ├── agents/
│   │   └── base_agent.py
│   └── middleware/
│       ├── base.py
│       ├── pii_detection.py
│       └── audit_logging.py
│
├── platform/               # 실행 플랫폼 (LangChain 어댑터, Skill Card)
│   ├── langchain_adapter/
│   └── skill_card/         # Skill Card 패턴 구현
│       ├── schema.py
│       ├── manager.py
│       └── executor.py
│
├── domains/                # 비즈니스 도메인 (독립적인 Agent 시스템)
│   ├── personal_assistant/
│   │   ├── agents/         # 도메인별 Agent 구현
│   │   ├── tools/          # 도메인별 Tool 정의
│   │   ├── workflows/      # 복합 워크플로우
│   │   ├── storage/        # 도메인 데이터 저장
│   │   └── supervisor.py   # (예정) 도메인 조율자
│   │
│   ├── financial/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── workflows/
│   │   └── storage/
│   │
│   └── research/           # (예정) 리서치 도메인
│
├── infra/                  # 인프라스트럭처 (외부 시스템 연동)
│   ├── llm/                # LLM 프로바이더
│   ├── database/           # 데이터베이스
│   │   ├── elasticsearch/
│   │   ├── redis/
│   │   └── postgres/
│   └── cache/              # 캐시 레이어
│
├── shared/                 # 공유 컴포넌트
│   ├── types/              # 공통 타입 정의
│   ├── utils/              # 유틸리티 함수
│   └── tools/              # 범용 Tools (calculator, get_current_time 등)
│
├── app/                    # 애플리케이션 조합 (예정)
│   ├── personal_assistant_app.py
│   └── financial_app.py
│
└── interfaces/             # 외부 인터페이스 (예정)
    ├── cli.py
    └── api.py
```

## Agent 계층

### Level 1: Specialized Agents (전문 Agent)
개별 작업을 수행하는 가장 하위 Agent

**예시:**
- `ScheduleManagerAgent`: 일정 관리
- `TodoAgent`: 할일 관리 (예정)
- `PortfolioAgent`: 포트폴리오 관리 (예정)

**위치:** `domains/{domain}/agents/`

### Level 2: Domain Supervisors (도메인 감독자)
도메인 내 Agent들을 조율

**예시:**
- `PersonalAssistantSupervisor` (예정)
- `FinancialSupervisor` (예정)
- `ResearchSupervisor` (예정)

**위치:** `domains/{domain}/supervisor.py`

### Level 3: Master Agent (마스터 Agent)
도메인 간 라우팅 및 협업 조율

**위치:** `app/master_agent.py` (예정)

## 핵심 패턴

### 1. Skill Card Pattern
JSON 기반 Agent 행동 정의

**장점:**
- 예측 가능한 실행
- 버전 관리 용이
- 컴플라이언스 요구사항 충족

**위치:** `platform/skill_card/`

**사용 예:**
```python
from multi_agent_lab.platform.skill_card import SkillCardManager, SkillCardExecutor

manager = SkillCardManager()
card = manager.get("SC_SCHEDULE_001")
executor = SkillCardExecutor(card)
result = executor.execute(user_query="내일 오후 2시에 회의")
```

### 2. Domain Pattern
비즈니스 도메인별 독립적 구성

**구조:**
```
domains/{domain_name}/
├── agents/         # Agent 구현
├── tools/          # 도메인 특화 Tool
├── workflows/      # 복합 워크플로우
├── storage/        # 데이터 저장
└── supervisor.py   # 도메인 조율자
```

### 3. Middleware Pattern
횡단 관심사 처리

**구현된 미들웨어:**
- `PIIDetectionMiddleware`: 개인정보 탐지/마스킹
- `AuditLoggingMiddleware`: 감사 로깅

**위치:** `core/middleware/`

## 통신 패턴

### 1. Supervisor Pattern
Supervisor가 하위 Agent에게 작업 위임

### 2. Collaboration Pattern
Agent들이 순차적으로 협업하여 작업 완료

### 3. Event-Driven Pattern
Message Bus를 통한 비동기 이벤트 처리 (예정)

## 기술 스택

### Agent Framework
- **LangChain**: Agent 프레임워크
- **LangGraph**: 복잡한 Agent 워크플로우 (예정)

### LLM
- **Ollama**: 로컬 LLM 실행
- **모델**: gpt-oss:20b (GPT-Oss-20B from Shallowmind)

### 데이터 저장
- **Elasticsearch**: Vector Search
- **Redis**: Cache, Session (예정)
- **In-Memory DB**: 현재 개발용

### 관찰성
- **LangSmith**: Agent 디버깅 (예정)
- **Custom Tracing**: 자체 추적 시스템 (예정)

## 개발 로드맵

### Phase 1: 기본 Agent 구현 ✅
- [x] Skill Card 패턴 구현
- [x] 기본 Agent (Schedule, File, Basic)
- [x] Middleware 시스템
- [x] Elasticsearch 연동

### Phase 2: 도메인 확장 (진행 중)
- [x] Multi-Agent Lab 구조 마이그레이션
- [x] LangGraph 기반 Supervisor 구현 (PersonalAssistantSupervisor)
- [x] TodoManagerAgent 구현
- [ ] 도메인별 Agent 추가 (Knowledge)
- [ ] Financial 도메인 구현

### Phase 3: 고급 기능 (예정)
- [ ] MasterAgent 구현
- [ ] Message Bus 구현
- [ ] Redis 캐싱
- [ ] LangSmith 통합

### Phase 4: 프로덕션 준비 (예정)
- [ ] FastAPI 인터페이스
- [ ] 모니터링 시스템
- [ ] 배포 자동화
- [ ] 성능 최적화

## 참고 문서

- [개인 비서 가이드](./personal-assistant/README.md)
- [학습 가이드](./learning-guide.md)
- [패키지 구조 가이드](./package-guide.md)

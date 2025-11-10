# 개인비서 Agent 구현 가이드

이 폴더는 개인비서 AI Agent 시스템을 단계별로 구현하기 위한 가이드 문서를 포함합니다.

## 📚 학습 순서

구현은 다음 순서로 진행됩니다:

### Phase 1: 기본 구조 (1주)
1. [Step 01: 프로젝트 구조 설정](./01-project-setup.md)
2. [Step 02: ScheduleManager Agent 구현](./02-schedule-manager-agent.md)
3. [Step 03: 일정 관리 Tools 개발](./03-schedule-tools.md)
4. [Step 04: 테스트 작성](./04-testing.md)

### Phase 2: 멀티 Agent 시스템 (1주)
5. [Step 05: TodoManager Agent 구현](./05-todo-manager-agent.md)
6. [Step 06: KnowledgeManager Agent 구현](./06-knowledge-manager-agent.md)
7. [Step 07: Supervisor Agent 구현](./07-supervisor-agent.md)
8. [Step 08: FastAPI 연동](./08-fastapi-integration.md)

### Phase 3: Skill Card & VectorDB (1주)
9. [Step 09: Skill Card 시스템](./09-skill-card-system.md)
10. [Step 10: VectorDB 연동](./10-vectordb-integration.md)
11. [Step 11: 동적 Agent 선택](./11-dynamic-agent-selection.md)

### Phase 4: 고급 기능 (2주)
12. [Step 12: 캐싱 시스템](./12-caching-system.md)
13. [Step 13: 로깅 & 모니터링](./13-logging-monitoring.md)
14. [Step 14: Admin 페이지](./14-admin-page.md)
15. [Step 15: 성능 최적화](./15-performance-optimization.md)

### Phase 5: RAG 구현 (1주)
16. [Step 16: RAG 기본 구조](./16-rag-basics.md)
17. [Step 17: KnowledgeManager에 RAG 적용](./17-rag-integration.md)

## 🎯 학습 목표

이 가이드를 완료하면 다음을 할 수 있게 됩니다:

- ✅ LangChain 1.0으로 Multi-Agent 시스템 구축
- ✅ Ollama로 로컬 LLM 활용
- ✅ Skill Card 기반 동적 Agent 관리
- ✅ VectorDB로 의미 기반 검색
- ✅ FastAPI로 REST API 제공
- ✅ 프로덕션 수준의 모니터링 및 로깅
- ✅ RAG로 지식 기반 답변 생성

## 📋 사전 준비사항

### 1. 개발 환경
- Python 3.11+
- uv (패키지 관리자)
- Ollama (Local LLM)
- VS Code 또는 PyCharm

### 2. 필수 지식
- Python 기본 문법
- 비동기 프로그래밍 (async/await)
- REST API 개념
- Git 기본 사용법

### 3. 선행 학습 문서
이 구현 가이드를 시작하기 전에 다음 문서를 먼저 읽어보세요:

- [AGENT_CONCEPTS.md](../AGENT_CONCEPTS.md) - Agent 개념 이해
- [PROJECT_ROADMAP.md](../PROJECT_ROADMAP.md) - 전체 로드맵
- [SKILL_CARD_GUIDE.md](../SKILL_CARD_GUIDE.md) - Skill Card 개념

## 🚀 시작하기

### 현재 프로젝트 상태 확인

```bash
# 프로젝트 루트로 이동
cd /Users/sskim/dev/langchain-in-action

# 디렉토리 구조 확인
tree -L 2 -I '__pycache__|*.pyc|.venv'

# 결과:
# .
# ├── LICENSE
# ├── README.md
# ├── docs/
# │   ├── AGENT_CONCEPTS.md
# │   ├── LEARNING_PATH.md
# │   ├── PACKAGE_GUIDE.md
# │   ├── PROJECT_ROADMAP.md
# │   ├── SKILL_CARD_GUIDE.md
# │   └── implementation/    ← 현재 위치
# ├── pyproject.toml
# ├── src/
# │   ├── agents/
# │   ├── examples/
# │   ├── tests/
# │   ├── tools/
# │   └── utils/
# └── uv.lock
```

### 첫 번째 단계 시작

[Step 01: 프로젝트 구조 설정](./01-project-setup.md) 문서를 열어 시작하세요!

## 💡 학습 팁

### 1. 순서대로 진행하기
각 단계는 이전 단계를 기반으로 하므로, 반드시 순서대로 진행하세요.

### 2. 실습 위주로 학습
문서를 읽기만 하지 말고, 직접 코드를 작성하면서 실습하세요.

### 3. 테스트 먼저 작성 (TDD)
각 기능을 구현할 때 테스트를 먼저 작성하는 습관을 들이세요.

### 4. 커밋 단위 관리
각 Step이 완료되면 Git 커밋을 하여 진행 상황을 관리하세요.

```bash
# 예시
git add .
git commit -m "Complete Step 01: Project setup"
```

### 5. 문서화
구현한 내용은 주석과 docstring으로 잘 문서화하세요.

## 🔧 트러블슈팅

### Ollama 연결 오류
```bash
# Ollama 서버 실행 확인
ollama list

# 모델 다운로드
ollama pull gpt-oss:20b
```

### Import 오류
```bash
# 가상환경 활성화 확인
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 의존성 설치 확인
uv sync
```

### 테스트 실행 오류
```bash
# pytest 설치 확인
uv add pytest pytest-asyncio

# 테스트 실행
pytest -v
```

## 📞 도움 받기

### 참고 자료
- [LangChain 공식 문서](https://python.langchain.com/)
- [Ollama 공식 문서](https://ollama.ai/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

### 코드 예제
각 단계의 완성된 코드는 `src/examples/` 폴더에서 확인할 수 있습니다.

## 📈 진행 상황 추적

각 단계를 완료하면 체크해주세요:

- [ ] Step 01: 프로젝트 구조 설정
- [ ] Step 02: ScheduleManager Agent 구현
- [ ] Step 03: 일정 관리 Tools 개발
- [ ] Step 04: 테스트 작성
- [ ] Step 05: TodoManager Agent 구현
- [ ] Step 06: KnowledgeManager Agent 구현
- [ ] Step 07: Supervisor Agent 구현
- [ ] Step 08: FastAPI 연동
- [ ] Step 09: Skill Card 시스템
- [ ] Step 10: VectorDB 연동
- [ ] Step 11: 동적 Agent 선택
- [ ] Step 12: 캐싱 시스템
- [ ] Step 13: 로깅 & 모니터링
- [ ] Step 14: Admin 페이지
- [ ] Step 15: 성능 최적화
- [ ] Step 16: RAG 기본 구조
- [ ] Step 17: RAG 통합

---

**준비가 되셨나요? [Step 01부터 시작하세요!](./01-project-setup.md)** 🚀

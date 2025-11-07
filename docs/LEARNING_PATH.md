# LangChain + Ollama 학습 로드맵

현재 위치: ✅ **기본 Agent 생성 완료**

---

## 🎯 학습 단계별 가이드

### Level 1: 기본기 (현재 완료 ✅)

- [x] Ollama 모델 설치 및 실행
- [x] LangChain 1.0 설치
- [x] 기본 Agent 생성 (`create_agent`)
- [x] Agent 실행 (`invoke`)
- [x] 에러 처리 (UTF-8 인코딩 이슈)

---

## Level 2: Tool 활용 마스터하기 (추천 🌟)

### 2.1 Custom Tool 만들기

**목표:** 실용적인 도구들을 Agent에 추가

```python
# examples/02_custom_tools.py

@tool
def search_web(query: str) -> str:
    """웹 검색 시뮬레이션"""
    return f"'{query}'에 대한 검색 결과입니다..."

@tool
def save_to_file(content: str, filename: str) -> str:
    """파일에 내용 저장"""
    with open(filename, 'w') as f:
        f.write(content)
    return f"'{filename}'에 저장되었습니다."

@tool
def read_from_file(filename: str) -> str:
    """파일에서 내용 읽기"""
    with open(filename, 'r') as f:
        return f.read()
```

**연습 과제:**
- [ ] 날씨 조회 도구 (가짜 데이터)
- [ ] 할 일 관리 도구 (추가/조회/삭제)
- [ ] 간단한 데이터베이스 조회 도구

### 2.2 여러 Tool을 조합하기

```python
# 3개 이상의 도구를 사용하는 복잡한 작업
tools = [
    search_web,
    save_to_file,
    read_from_file,
    calculator,
    get_current_time,
]
```

**연습 과제:**
- [ ] "웹에서 정보 검색 → 요약 → 파일 저장" 워크플로우
- [ ] "파일 읽기 → 데이터 분석 → 결과 저장" 파이프라인

---

## Level 3: Memory & Context 관리 (중요 🔥)

### 3.1 대화 기록 유지

**목표:** Agent가 이전 대화를 기억하게 만들기

```python
# examples/03_memory.py
from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()

# 대화 추가
chat_history.add_user_message("내 이름은 김철수야")
chat_history.add_ai_message("안녕하세요 김철수님!")

# Agent에 히스토리 전달
response = agent.invoke({
    "messages": chat_history.messages + [
        {"role": "user", "content": "내 이름이 뭐였지?"}
    ]
})
```

**연습 과제:**
- [ ] 다중 턴 대화 Agent 만들기
- [ ] 대화 히스토리 파일로 저장/로드
- [ ] 세션별로 대화 분리 관리

### 3.2 Context Window 관리

**목표:** 긴 대화에서 중요한 내용만 유지

```python
# 최근 N개 메시지만 유지
def trim_messages(messages, max_messages=10):
    return messages[-max_messages:]
```

---

## Level 4: RAG (Retrieval-Augmented Generation) 🚀

### 4.1 문서 로드 및 벡터화

**목표:** 로컬 문서를 Agent가 참조하게 만들기

```python
# examples/04_rag_basic.py
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 문서 로드
loader = TextLoader("my_document.txt")
documents = loader.load()

# 2. 청크로 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_documents(documents)

# 3. 임베딩 생성
embeddings = OllamaEmbeddings(model="gpt-oss:20b")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 4. Retriever 도구 생성
@tool
def search_documents(query: str) -> str:
    """문서에서 관련 정보 검색"""
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])
```

**연습 과제:**
- [ ] README.md 파일을 RAG로 로드
- [ ] PDF 문서 로드 및 검색
- [ ] 여러 파일을 하나의 vectorstore로 통합

### 4.2 실전 RAG Agent

```python
# Agent가 문서 검색 도구를 사용
tools = [search_documents, calculator]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="문서를 검색하여 정확한 정보를 제공하세요."
)

response = agent.invoke({
    "messages": [{"role": "user", "content": "프로젝트 설치 방법은?"}]
})
```

**연습 과제:**
- [ ] 회사 문서 Q&A 봇
- [ ] 기술 문서 검색 Assistant
- [ ] 코드베이스 설명 Agent

---

## Level 5: LangGraph - 복잡한 워크플로우 (고급 🎓)

### 5.1 Multi-Agent 시스템

**목표:** 여러 Agent가 협력하는 시스템

```python
# examples/05_multi_agent.py
from langgraph.graph import StateGraph

# Agent 1: 연구원
researcher = create_agent(
    model=llm,
    tools=[search_documents],
    system_prompt="당신은 연구원입니다. 정보를 찾아 요약하세요."
)

# Agent 2: 작가
writer = create_agent(
    model=llm,
    tools=[save_to_file],
    system_prompt="당신은 작가입니다. 연구 내용을 바탕으로 글을 작성하세요."
)

# Workflow 정의
workflow = StateGraph()
workflow.add_node("research", researcher)
workflow.add_node("write", writer)
workflow.add_edge("research", "write")
```

**연습 과제:**
- [ ] Researcher + Writer + Reviewer 팀
- [ ] Data Analyst + Visualizer 협업
- [ ] Planner + Executor + Validator 파이프라인

### 5.2 조건부 분기

```python
# 조건에 따라 다른 경로 실행
def route(state):
    if "search" in state["query"]:
        return "researcher"
    else:
        return "calculator"

workflow.add_conditional_edges("start", route)
```

---

## Level 6: 실전 프로젝트 아이디어 💡

### 6.1 업무 자동화 Agent

```
1. Email 처리 Agent
   - 이메일 분류
   - 우선순위 판단
   - 자동 답변 생성

2. 문서 정리 Agent
   - 파일 분류
   - 메타데이터 추출
   - 요약 생성

3. 코드 리뷰 Agent
   - 코드 분석
   - 개선 제안
   - 문서 생성
```

### 6.2 데이터 분석 Assistant

```python
# Pandas + Agent 통합
@tool
def analyze_dataframe(query: str) -> str:
    """데이터프레임 분석"""
    # SQL-like 쿼리 실행
    # 통계 계산
    # 시각화 생성
```

### 6.3 개인 비서 Agent

```
기능:
- 일정 관리
- 메모 저장/검색
- 할 일 추적
- 정보 요약
```

---

## 학습 자료

### 공식 문서
- [LangChain 공식 튜토리얼](https://python.langchain.com/docs/tutorials/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Ollama 모델 라이브러리](https://ollama.ai/library)

### 추천 코스
1. **LangChain 기초** → Level 2-3
2. **RAG 마스터** → Level 4
3. **Multi-Agent 시스템** → Level 5

### 실습 프로젝트 순서
```
Week 1: Custom Tools (Level 2)
Week 2: Memory & Context (Level 3)
Week 3: RAG 구현 (Level 4)
Week 4: Multi-Agent (Level 5)
Week 5: 실전 프로젝트 (Level 6)
```

---

## 다음 단계 추천 (우선순위)

### 🥇 1순위: Custom Tools 마스터
- 파일: `examples/02_custom_tools.py`
- 실용적이고 즉시 활용 가능
- Agent의 능력을 극대화

### 🥈 2순위: RAG 구현
- 파일: `examples/04_rag_basic.py`
- 폐쇄망 환경에서 매우 유용
- 회사 문서 활용 가능

### 🥉 3순위: Memory 관리
- 파일: `examples/03_memory.py`
- 대화형 Agent의 핵심
- 사용자 경험 향상

---

## 폐쇄망 환경 특화 학습

### 필요한 패키지 미리 준비
```bash
# RAG 관련
uv add langchain-community faiss-cpu pypdf

# 데이터 처리
uv add pandas numpy matplotlib

# 문서 로더
uv add unstructured python-docx
```

### 폐쇄망 RAG 워크플로우
```
1. 개발 환경에서 문서 임베딩 생성
2. vectorstore를 파일로 저장 (FAISS)
3. 저장된 vectorstore를 폐쇄망으로 전송
4. 폐쇄망에서 로드 및 사용
```

---

## 시작하기

### 오늘 바로 시작할 수 있는 것

**Option 1: Custom Tools 실습**
```bash
# 파일 생성
touch examples/02_custom_tools.py

# 실습 시작
# - 3개 이상의 도구 만들기
# - Agent에 연결
# - 복잡한 작업 수행
```

**Option 2: RAG 튜토리얼**
```bash
# 문서 준비
echo "LangChain은 LLM 애플리케이션 개발 프레임워크입니다." > sample.txt

# RAG 구현
touch examples/04_rag_basic.py
```

**Option 3: 실전 프로젝트**
```bash
# 간단한 프로젝트부터 시작
touch examples/06_todo_agent.py  # 할 일 관리 Agent
```

---

## 어떤 주제부터 시작하고 싶으세요?

1. **Custom Tools** - 실용적이고 재미있음
2. **RAG** - 회사에서 바로 쓸 수 있음
3. **Multi-Agent** - 복잡하지만 강력함
4. **실전 프로젝트** - 포트폴리오용

알려주시면 해당 주제의 예제 코드를 바로 만들어드릴게요!

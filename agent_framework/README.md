# Agent Framework

LangChain + Ollama 기반 Agent 개발 프레임워크

## 📦 패키지 구조

```
agent_framework/
├── __init__.py              # 패키지 진입점
├── agents/                  # Agent 관련 모듈
│   ├── __init__.py
│   ├── base.py             # BaseAgent 클래스
│   └── factory.py          # Agent 팩토리 함수들
├── tools/                   # Tool 모음
│   ├── __init__.py
│   ├── basic.py            # 기본 도구 (계산기, 시간 등)
│   └── file_tools.py       # 파일 처리 도구
├── utils/                   # 유틸리티
│   ├── __init__.py
│   ├── config.py           # 설정 관리
│   └── helpers.py          # 헬퍼 함수들
├── examples/                # 사용 예제
│   ├── __init__.py
│   ├── 01_basic_agent.py   # 기본 Agent 예제
│   └── 02_file_agent.py    # 파일 처리 Agent 예제
└── tests/                   # 테스트
    └── __init__.py
```

## 🚀 빠른 시작

### 1. 기본 Agent 생성

```python
from agent_framework import create_simple_agent
from agent_framework.tools import calculator, get_word_length

# Agent 생성
agent = create_simple_agent(
    model_name="gpt-oss:20b",
    temperature=0.1,
    tools=[calculator, get_word_length]
)

# 사용
response = agent.chat("25 곱하기 4는?")
print(response)  # "100입니다."
```

### 2. 파일 처리 Agent

```python
from agent_framework import create_simple_agent
from agent_framework.tools import read_file, write_file, list_files

agent = create_simple_agent(
    tools=[read_file, write_file, list_files]
)

# 파일 읽기
agent.chat("README.md를 읽어줘")

# 파일 쓰기
agent.chat("'hello.txt'에 'Hello World'를 저장해줘")
```

### 3. Custom System Prompt

```python
agent = create_simple_agent(
    system_prompt="""당신은 전문 데이터 분석가입니다.
사용자의 데이터 분석 요청을 도와주세요.
항상 한국어로 응답하세요.""",
    tools=[calculator]
)
```

## 🛠️ 사용 가능한 Tool

### 기본 Tools (`agent_framework.tools`)

#### calculator
수식 계산
```python
from agent_framework.tools import calculator

agent = create_simple_agent(tools=[calculator])
agent.chat("123 곱하기 456은?")
```

#### get_word_length
단어 길이 확인
```python
from agent_framework.tools import get_word_length

agent = create_simple_agent(tools=[get_word_length])
agent.chat("'LangChain'은 몇 글자야?")
```

#### get_current_time
현재 시간 조회
```python
from agent_framework.tools import get_current_time

agent = create_simple_agent(tools=[get_current_time])
agent.chat("지금 몇 시야?")
```

### 파일 Tools (`agent_framework.tools`)

#### read_file
파일 읽기
```python
from agent_framework.tools import read_file

agent = create_simple_agent(tools=[read_file])
agent.chat("config.py 파일을 읽어줘")
```

#### write_file
파일 쓰기
```python
from agent_framework.tools import write_file

agent = create_simple_agent(tools=[write_file])
agent.chat("'output.txt'에 'Hello'를 저장해줘")
```

#### list_files
파일 목록 조회
```python
from agent_framework.tools import list_files

agent = create_simple_agent(tools=[list_files])
agent.chat("현재 디렉토리의 파일 목록을 보여줘")
```

## 🎯 고급 사용법

### 1. BaseAgent 상속

```python
from agent_framework.agents.base import BaseAgent
from langchain.agents import create_agent

class MyCustomAgent(BaseAgent):
    def _create_agent(self):
        # 커스텀 Agent 생성 로직
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

# 사용
agent = MyCustomAgent(
    model_name="gpt-oss:20b",
    tools=[calculator]
)
```

### 2. Custom Tool 만들기

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """내 커스텀 도구 설명"""
    # 도구 로직
    return f"처리 결과: {input}"

# Agent에 추가
agent = create_simple_agent(tools=[my_custom_tool])
```

### 3. 여러 Tool 조합

```python
from agent_framework.tools import (
    calculator,
    read_file,
    write_file,
    get_current_time
)

# 모든 도구를 가진 만능 Agent
agent = create_simple_agent(
    tools=[calculator, read_file, write_file, get_current_time]
)

# 복잡한 작업 가능
agent.chat("현재 시간을 계산해서 'time.txt'에 저장해줘")
```

## 📝 예제 실행

### 예제 1: 기본 Agent
```bash
python -m agent_framework.examples.01_basic_agent
```

### 예제 2: 파일 처리
```bash
python -m agent_framework.examples.02_file_agent
```

## 🔧 설정

### 환경변수
`.env` 파일을 만들어 설정할 수 있습니다:

```env
OLLAMA_MODEL=gpt-oss:20b
```

### 코드에서 설정
```python
from agent_framework.utils import get_model_config

# 모델별 권장 설정 가져오기
config = get_model_config("gpt-oss:20b")
print(config)
# {'temperature': 0.1, 'num_predict': 256, ...}
```

## 🎨 패턴 및 Best Practices

### 1. Tool 선택 가이드

**계산 작업:**
```python
tools=[calculator]
```

**파일 작업:**
```python
tools=[read_file, write_file, list_files]
```

**정보 조회:**
```python
tools=[get_current_time, get_word_length]
```

**복합 작업:**
```python
tools=[calculator, read_file, write_file, get_current_time]
```

### 2. Temperature 설정

```python
# 정확한 답변이 필요할 때 (계산, 데이터 처리)
agent = create_simple_agent(temperature=0.0)

# 창의적인 답변이 필요할 때 (글쓰기, 아이디어)
agent = create_simple_agent(temperature=0.7)

# 균형잡힌 답변 (일반적 용도)
agent = create_simple_agent(temperature=0.3)
```

### 3. System Prompt 작성 팁

```python
# ❌ 나쁜 예
system_prompt = "당신은 AI입니다."

# ✅ 좋은 예
system_prompt = """당신은 전문 프로그래머 어시스턴트입니다.
다음 역할을 수행하세요:
1. 코드 작성 및 디버깅
2. 기술 문서 검색
3. 파일 관리

사용 가능한 도구:
- read_file: 파일 읽기
- write_file: 파일 쓰기

항상 한국어로 명확하게 답변하세요."""
```

## 🐛 트러블슈팅

### UTF-8 인코딩 에러
```python
from agent_framework.utils import clean_text

# 응답 텍스트 정리
response = agent.chat("질문")
clean_response = clean_text(response)
```

### Ollama 연결 오류
```bash
# Ollama 서버 실행 확인
ollama list

# 모델 존재 확인
ollama pull gpt-oss:20b
```

### Agent 응답이 이상할 때
```python
# temperature 낮추기
agent = create_simple_agent(temperature=0.0)

# 다른 모델 시도
agent = create_simple_agent(model_name="llama3.2:3b")
```

## 🔄 확장 가이드

### 새로운 Tool 추가
1. `agent_framework/tools/` 에 새 파일 생성
2. `@tool` 데코레이터로 함수 정의
3. `agent_framework/tools/__init__.py`에 추가
4. 예제 작성

```python
# agent_framework/tools/my_tools.py
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """웹 검색 시뮬레이션"""
    return f"'{query}' 검색 결과..."
```

```python
# agent_framework/tools/__init__.py
from agent_framework.tools.my_tools import search_web

__all__ = [..., "search_web"]
```

### 새로운 Agent 타입 추가
1. `agent_framework/agents/factory.py`에 클래스 추가
2. 팩토리 함수 작성
3. `__init__.py`에 export 추가

## 📚 다음 단계

1. **RAG 구현** - 문서 검색 기능 추가
2. **Multi-Agent** - 여러 Agent 협업
3. **Memory** - 대화 기록 관리
4. **Streaming** - 실시간 응답 스트리밍

## 🤝 기여

이슈와 PR을 환영합니다!

## 📄 라이센스

MIT License

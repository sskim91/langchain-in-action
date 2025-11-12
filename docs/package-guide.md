# Python 패키지 구조 완성 가이드

## 📦 완성된 패키지 구조

```
langchain-example/
├── src/              # 메인 패키지
│   ├── __init__.py              # 패키지 진입점
│   ├── README.md                # 패키지 문서
│   │
│   ├── agents/                   # Agent 모듈
│   │   ├── __init__.py
│   │   ├── base.py              # BaseAgent 클래스
│   │   └── factory.py           # 팩토리 함수들
│   │
│   ├── tools/                    # Tool 모음
│   │   ├── __init__.py
│   │   ├── basic.py             # 기본 도구
│   │   └── file_tools.py        # 파일 처리 도구
│   │
│   ├── utils/                    # 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py            # 설정 관리
│   │   └── helpers.py           # 헬퍼 함수
│   │
│   ├── examples/                 # 예제
│   │   ├── __init__.py
│   │   ├── 01_basic_agent.py
│   │   └── 02_file_agent.py
│   │
│   └── tests/                    # 테스트
│       └── __init__.py
│
├── pyproject.toml               # 프로젝트 설정
└── README.md                    # 프로젝트 문서
```

## 🎯 패키지 설계 원칙

### 1. 모듈화 (Modularity)
각 기능을 독립적인 모듈로 분리:
- `agents/` - Agent 생성 및 관리
- `tools/` - 재사용 가능한 도구
- `utils/` - 공통 유틸리티
- `examples/` - 사용 예제
- `tests/` - 테스트 코드

### 2. 계층 구조 (Hierarchy)
```
패키지 진입점 (__init__.py)
    ↓
서브 패키지 (agents, tools, utils)
    ↓
구현 모듈 (base.py, factory.py, ...)
```

### 3. 명확한 인터페이스
```python
# src/__init__.py
from src.agents.base import BaseAgent
from src.agents.factory import create_simple_agent

__all__ = ["BaseAgent", "create_simple_agent"]
```

## 🔧 주요 컴포넌트

### 1. BaseAgent 클래스
**위치:** `src/agents/base.py`

**역할:**
- 모든 Agent의 부모 클래스
- LLM 초기화
- 공통 메서드 제공 (`invoke`, `chat`)

**사용 예:**
```python
from src.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def _create_agent(self):
        # 커스텀 Agent 로직
        pass
```

### 2. Factory 함수
**위치:** `src/agents/factory.py`

**역할:**
- Agent 생성을 단순화
- 다양한 유형의 Agent 제공

**제공하는 함수:**
- `create_simple_agent()` - 기본 Agent
- `create_rag_agent()` - RAG Agent

### 3. Tools 모음
**위치:** `src/tools/`

**제공하는 도구:**

**기본 도구 (`basic.py`):**
- `calculator` - 수식 계산
- `get_word_length` - 문자열 길이
- `get_current_time` - 현재 시간

**파일 도구 (`file_tools.py`):**
- `read_file` - 파일 읽기
- `write_file` - 파일 쓰기
- `list_files` - 파일 목록

### 4. 유틸리티
**위치:** `src/utils/`

**제공하는 기능:**
- `config.py` - 설정 관리, 모델별 권장 설정
- `helpers.py` - 텍스트 정리, 응답 포맷팅

## 💻 사용 방법

### 방법 1: 패키지로 import
```python
# 프로젝트 루트에서
from src import create_simple_agent
from src.tools import calculator

agent = create_simple_agent(tools=[calculator])
response = agent.chat("2 + 2는?")
```

### 방법 2: 예제 실행
```bash
# 예제 1 실행
python -m src.examples.01_basic_agent

# 예제 2 실행
python -m src.examples.02_file_agent
```

### 방법 3: 모듈로 직접 사용
```python
from src.agents.factory import SimpleAgent
from src.tools.basic import calculator

agent = SimpleAgent(
    model_name="gpt-oss:20b",
    tools=[calculator]
)
```

## 🎨 패키지 확장 가이드

### 새로운 Tool 추가

**1단계: Tool 함수 작성**
```python
# src/tools/my_new_tools.py
from langchain_core.tools import tool

@tool
def my_tool(input: str) -> str:
    """도구 설명"""
    return f"결과: {input}"
```

**2단계: __init__.py에 추가**
```python
# src/tools/__init__.py
from src.tools.my_new_tools import my_tool

__all__ = [..., "my_tool"]
```

**3단계: 사용**
```python
from src.tools import my_tool
agent = create_simple_agent(tools=[my_tool])
```

### 새로운 Agent 타입 추가

**1단계: Agent 클래스 작성**
```python
# src/agents/factory.py
class MyCustomAgent(BaseAgent):
    def _create_agent(self):
        # 커스텀 로직
        return create_agent(...)
```

**2단계: 팩토리 함수 작성**
```python
def create_my_agent(...) -> MyCustomAgent:
    return MyCustomAgent(...)
```

**3단계: Export**
```python
# src/__init__.py
from src.agents.factory import create_my_agent

__all__ = [..., "create_my_agent"]
```

### 새로운 예제 추가

```python
# src/examples/03_my_example.py
from src import create_simple_agent

def main():
    agent = create_simple_agent()
    # 예제 코드

if __name__ == "__main__":
    main()
```

## 📚 Python 패키지 베스트 프랙티스

### 1. __init__.py 역할

**패키지 진입점:**
```python
# src/__init__.py
"""패키지 설명"""

__version__ = "0.1.0"

from src.agents import BaseAgent

__all__ = ["BaseAgent"]
```

**서브패키지:**
```python
# src/tools/__init__.py
from src.tools.basic import calculator

__all__ = ["calculator"]
```

### 2. Import 스타일

**❌ 나쁜 예:**
```python
from src.agents.factory import *
```

**✅ 좋은 예:**
```python
from src import create_simple_agent
from src.tools import calculator
```

### 3. 모듈 구조

**하나의 책임:**
- `base.py` - BaseAgent만
- `factory.py` - 팩토리 함수들만
- `basic.py` - 기본 도구들만

**명확한 이름:**
- `file_tools.py` (구체적) ✅
- `utils.py` (모호함) ❌

### 4. 문서화

**모듈 docstring:**
```python
"""
모듈 설명

주요 클래스:
- BaseAgent: Agent 기본 클래스
"""
```

**함수 docstring:**
```python
def create_simple_agent() -> SimpleAgent:
    """
    간단한 Agent 생성

    Args:
        ...

    Returns:
        SimpleAgent 인스턴스

    Example:
        >>> agent = create_simple_agent()
    """
```

## 🔍 패키지 디버깅

### Import 문제 해결

**문제:** `ModuleNotFoundError: No module named 'src'`

**해결:**
```bash
# 프로젝트 루트에서 실행하는지 확인
pwd  # /Users/sskim/dev/langchain-example

# Python path 확인
python -c "import sys; print(sys.path)"
```

### 순환 import 방지

**❌ 나쁜 예:**
```python
# a.py
from b import something

# b.py
from a import something  # 순환!
```

**✅ 좋은 예:**
```python
# a.py와 b.py 둘 다
from common import something
```

## 📝 다음 단계

### Level 1: 기본 사용 (완료 ✅)
- [x] 패키지 구조 이해
- [x] 기본 Agent 사용
- [x] Tool 사용

### Level 2: 커스터마이징
- [ ] Custom Tool 만들기
- [ ] Custom Agent 만들기
- [ ] 설정 파일 활용

### Level 3: 고급 기능
- [ ] RAG 구현
- [ ] Memory 추가
- [ ] Multi-Agent 시스템

### Level 4: 프로덕션
- [ ] 테스트 작성
- [ ] 에러 처리 강화
- [ ] 로깅 추가
- [ ] 배포 준비

## 🎯 실습 과제

### 과제 1: 새로운 Tool 추가
**목표:** 날씨 조회 도구 만들기
```python
@tool
def get_weather(city: str) -> str:
    """도시의 날씨 조회 (가짜 데이터)"""
    return f"{city}의 날씨: 맑음, 20도"
```

### 과제 2: 특화된 Agent 만들기
**목표:** 파일 관리 전용 Agent
```python
file_agent = create_simple_agent(
    tools=[read_file, write_file, list_files],
    system_prompt="파일 관리 전문 어시스턴트"
)
```

### 과제 3: 예제 작성
**목표:** `03_todo_agent.py` 만들기
- 할 일 추가
- 할 일 조회
- 할 일 삭제

## 💡 팁

### 1. 패키지 테스트
```bash
# 패키지 import 확인
python -c "from src import create_simple_agent; print('OK')"

# 예제 실행
python -m src.examples.01_basic_agent
```

### 2. 개발 모드 설치
```bash
# editable install (개발 중)
uv pip install -e .
```

### 3. 패키지 배포 준비
```bash
# 빌드
python -m build

# PyPI 업로드 (준비되면)
# twine upload dist/*
```

## 🎉 완성!

이제 **체계적인 Python 패키지**를 갖추었습니다:
- ✅ 명확한 구조
- ✅ 재사용 가능한 컴포넌트
- ✅ 확장 가능한 설계
- ✅ 풍부한 예제와 문서

**다음 학습:**
1. Custom Tools 만들기
2. RAG 구현
3. Multi-Agent 시스템

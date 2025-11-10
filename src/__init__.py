"""
Agent Framework - LangChain + Ollama 기반 Agent 개발 프레임워크

주요 모듈:
- agents: Agent 클래스 및 팩토리
- tools: Custom Tool 모음
- utils: 유틸리티 함수
- examples: 사용 예제
"""

__version__ = "0.1.0"

from core.agents.base import BaseAgent
from core.agents.factory import create_simple_agent

__all__ = [
    "BaseAgent",
    "create_simple_agent",
]

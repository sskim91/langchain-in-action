"""
Multi-Agent Lab - LangChain + Ollama 기반 Multi-Agent 개발 프레임워크

주요 모듈:
- multi_agent_lab: Multi-Agent Lab 메인 패키지
  - core: 프레임워크 핵심 (Agent base, Middleware)
  - platform: 실행 플랫폼 (LangChain adapter, Skill Card)
  - domains: 비즈니스 도메인 (Personal Assistant, Financial, Research)
  - infra: 인프라 (LLM, Database, Cache)
  - shared: 공유 컴포넌트 (Types, Utils, Tools)
- examples: 사용 예제
"""

__version__ = "0.2.0"

from multi_agent_lab.core.agents.base import BaseAgent
from multi_agent_lab.core.agents.factory import create_simple_agent

__all__ = [
    "BaseAgent",
    "create_simple_agent",
]

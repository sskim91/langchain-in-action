"""
Agent 팩토리 함수들

다양한 유형의 Agent를 쉽게 생성할 수 있는 팩토리 함수 제공
"""

from typing import Optional

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from .base import BaseAgent


class SimpleAgent(BaseAgent):
    """간단한 Tool 기반 Agent"""

    def _create_agent(self):
        """LangChain create_agent로 Agent 생성"""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )


class RAGAgent(BaseAgent):
    """RAG(Retrieval-Augmented Generation) Agent"""

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
        system_prompt: Optional[str] = None,
        tools: Optional[list[BaseTool]] = None,
    ):
        # RAG 전용 시스템 프롬프트
        if system_prompt is None:
            system_prompt = """You are a helpful research assistant.
Use the document search tool to find relevant information.
Always cite your sources when using information from documents.
Respond in Korean."""

        super().__init__(
            model_name=model_name,
            temperature=temperature,
            system_prompt=system_prompt,
            tools=tools,
        )

    def _create_agent(self):
        """RAG용 Agent 생성"""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )


# 팩토리 함수들
def create_simple_agent(
    model_name: str = "gpt-oss:20b",
    temperature: float = 0.1,
    system_prompt: Optional[str] = None,
    tools: Optional[list[BaseTool]] = None,
) -> SimpleAgent:
    """
    간단한 Agent 생성

    Args:
        model_name: Ollama 모델명
        temperature: 생성 온도
        system_prompt: 시스템 프롬프트 (None이면 기본값)
        tools: Tool 리스트

    Returns:
        SimpleAgent 인스턴스

    Example:
        >>> from src.tools import calculator
        >>> agent = create_simple_agent(tools=[calculator])
        >>> response = agent.chat("2 + 2는?")
    """
    kwargs = {
        "model_name": model_name,
        "temperature": temperature,
        "tools": tools or [],
    }

    if system_prompt is not None:
        kwargs["system_prompt"] = system_prompt

    return SimpleAgent(**kwargs)


def create_rag_agent(
    model_name: str = "gpt-oss:20b",
    temperature: float = 0.1,
    system_prompt: Optional[str] = None,
    tools: Optional[list[BaseTool]] = None,
) -> RAGAgent:
    """
    RAG Agent 생성

    Args:
        model_name: Ollama 모델명
        temperature: 생성 온도
        system_prompt: 시스템 프롬프트 (None이면 RAG 기본값)
        tools: Tool 리스트 (문서 검색 도구 포함해야 함)

    Returns:
        RAGAgent 인스턴스

    Example:
        >>> from src.tools import create_document_search_tool
        >>> search_tool = create_document_search_tool("documents/")
        >>> agent = create_rag_agent(tools=[search_tool])
        >>> response = agent.chat("문서에서 설치 방법을 찾아줘")
    """
    return RAGAgent(
        model_name=model_name,
        temperature=temperature,
        system_prompt=system_prompt,
        tools=tools or [],
    )

"""
Base Agent 클래스
"""

from typing import Any, Optional

from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama


class BaseAgent:
    """
    Agent의 기본 클래스

    모든 Agent는 이 클래스를 상속받아 구현합니다.
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
        system_prompt: str = "You are a helpful assistant. Always respond in Korean.",
        tools: Optional[list[BaseTool]] = None,
    ):
        """
        Args:
            model_name: Ollama 모델명
            temperature: 생성 온도 (0.0 ~ 1.0)
            system_prompt: 시스템 프롬프트
            tools: Agent가 사용할 도구 리스트
        """
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.tools = tools or []

        # LLM 초기화
        self.llm = self._create_llm()

        # Agent 초기화 (서브클래스에서 구현)
        self.agent = self._create_agent()

    def _create_llm(self) -> ChatOllama:
        """LLM 인스턴스 생성"""
        return ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            num_predict=256,
            top_k=10,
            top_p=0.9,
        )

    def _create_agent(self) -> Any:
        """
        Agent 생성 (서브클래스에서 오버라이드)

        Returns:
            Agent 인스턴스
        """
        raise NotImplementedError("서브클래스에서 구현해야 합니다")

    def invoke(self, message: str, **kwargs) -> dict[str, Any]:
        """
        Agent 실행

        Args:
            message: 사용자 메시지
            **kwargs: 추가 파라미터

        Returns:
            Agent 응답
        """
        if not self.agent:
            raise RuntimeError("Agent가 초기화되지 않았습니다")

        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]}, **kwargs
        )

        return response

    def get_response_text(self, response: dict[str, Any]) -> str:
        """
        응답에서 텍스트 추출

        Args:
            response: Agent invoke 결과

        Returns:
            응답 텍스트
        """
        if "messages" in response:
            last_message = response["messages"][-1]
            return last_message.content
        return str(response)

    def chat(self, message: str) -> str:
        """
        간단한 채팅 인터페이스

        Args:
            message: 사용자 메시지

        Returns:
            Agent 응답 텍스트
        """
        response = self.invoke(message)
        return self.get_response_text(response)

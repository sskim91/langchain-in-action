"""
일정 관리 Agent
"""

from typing import Any

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from personal_assistant.tools.schedule_tools import (
    create_event,
    find_free_time,
    list_events,
)


class ScheduleManagerAgent:
    """
    일정 관리 전문 Agent

    사용자의 일정을 생성, 조회하고 비어있는 시간대를 찾아주는 Agent입니다.
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
    ):
        """
        Args:
            model_name: Ollama 모델명
            temperature: 생성 온도 (0.0 ~ 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature

        # LLM 초기화
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
        )

        # Tools 설정
        self.tools = [create_event, list_events, find_free_time]

        # System Prompt
        self.system_prompt = """당신은 일정 관리 전문가입니다.

사용자의 일정을 효율적으로 관리하고, 다음 작업을 수행합니다:

1. **일정 생성**: 사용자가 요청한 일정을 생성합니다.
2. **일정 조회**: 특정 날짜 또는 전체 일정을 조회합니다.
3. **빈 시간 찾기**: 회의나 약속을 잡을 수 있는 시간대를 찾아줍니다.

**주의사항:**
- 시작 시간은 반드시 'YYYY-MM-DD HH:MM' 형식으로 파싱하세요.
- 과거 날짜에는 일정을 생성하지 마세요.
- 비어있는 시간대를 제안할 때는 구체적으로 알려주세요.

항상 한국어로 응답하세요."""

        # Prompt Template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        # Agent 생성
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        # Agent Executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    def chat(self, message: str) -> str:
        """
        간단한 채팅 인터페이스

        Args:
            message: 사용자 메시지

        Returns:
            str: Agent 응답

        Example:
            >>> agent = ScheduleManagerAgent()
            >>> response = agent.chat("내일 오후 2시에 팀 회의 일정 잡아줘")
            >>> print(response)
            '일정 "팀 회의"가 2025-11-15 14:00에 생성되었습니다.'
        """
        result = self.executor.invoke({"input": message})
        return result["output"]

    def invoke(self, message: str, **kwargs) -> dict[str, Any]:
        """
        Agent 실행 (상세 결과 포함)

        Args:
            message: 사용자 메시지
            **kwargs: 추가 파라미터

        Returns:
            dict: Agent 실행 결과
        """
        return self.executor.invoke({"input": message}, **kwargs)

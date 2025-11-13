"""
일정 관리 Agent

📌 목적:
- 도구를 사용할 줄 아는 AI (= Agent)
- 사용자 말을 듣고 → 생각하고 → 도구를 골라 → 실행

🤖 동작 흐름:
1. 사용자: "내일 2시에 회의 잡아줘"
2. Middleware: PII 탐지/마스킹 (전처리)
3. Agent 생각: "일정을 만들어야겠군"
4. Agent 실행: create_event 도구 사용
5. Middleware: 감사 로깅 (후처리)
6. 결과 반환: "일정이 등록되었습니다!"

🔧 사용 가능한 도구:
- create_event: 일정 생성
- list_events: 일정 조회
- find_free_time: 빈 시간 찾기

🛡️ Middleware:
- PIIDetectionMiddleware: 개인정보 탐지/마스킹
- AuditLoggingMiddleware: 감사 로깅

💡 핵심 개념:
- LLM (Ollama): AI의 두뇌
- Tools: AI가 사용할 손과 발
- Middleware: 보안/로깅 레이어
- Prompt: AI의 역할 정의 ("당신은 일정 관리 전문가입니다")
"""

from typing import Any

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from multi_agent_lab.core.middleware import BaseMiddleware
from multi_agent_lab.domains.personal_assistant.tools.schedule_tools import (
    create_event,
    find_free_time,
    list_events,
)


class ScheduleManagerAgent:
    """
    일정 관리 전문 Agent

    사용자의 일정을 생성, 조회하고 비어있는 시간대를 찾아주는 Agent입니다.
    Middleware를 통해 보안/로깅 기능을 제공합니다.
    """

    def __init__(
        self,
        model_name: str = "gpt-oss:20b",
        temperature: float = 0.1,
        middleware: list[BaseMiddleware] | None = None,
    ):
        """
        Args:
            model_name: Ollama 모델명
            temperature: 생성 온도 (0.0 ~ 1.0)
            middleware: Middleware 리스트 (순서대로 실행)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.middleware = middleware or []

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

    def chat(self, message: str, **kwargs) -> str:
        """
        간단한 채팅 인터페이스 (Middleware 지원)

        Args:
            message: 사용자 메시지
            **kwargs: 추가 컨텍스트 (user_id 등)

        Returns:
            str: Agent 응답

        Example:
            >>> from core.middleware import (
            ...     PIIDetectionMiddleware,
            ...     AuditLoggingMiddleware,
            ... )
            >>>
            >>> agent = ScheduleManagerAgent(
            ...     middleware=[PIIDetectionMiddleware(), AuditLoggingMiddleware()]
            ... )
            >>> response = agent.chat("홍길동(010-1234-5678) 내일 2시 회의")
            >>> # PII가 자동으로 마스킹되고, 로그에 기록됨
        """
        # 1. Before Request - Middleware 전처리
        processed_input = message
        for mw in self.middleware:
            try:
                processed_input = mw.before_request(processed_input, **kwargs)
            except Exception as e:
                mw.on_error(e, **kwargs)
                raise

        # 2. Agent 실행
        try:
            result = self.executor.invoke({"input": processed_input})
            output = result["output"]
        except Exception as e:
            # 에러 발생 시 모든 middleware에 알림
            for mw in self.middleware:
                mw.on_error(e, **kwargs)
            raise

        # 3. After Response - Middleware 후처리
        processed_output = output
        for mw in self.middleware:
            try:
                processed_output = mw.after_response(processed_output, **kwargs)
            except Exception as e:
                mw.on_error(e, **kwargs)
                raise

        return processed_output

    def invoke(self, message: str, **kwargs) -> dict[str, Any]:
        """
        Agent 실행 (상세 결과 포함)

        Args:
            message: 사용자 메시지
            **kwargs: 추가 파라미터

        Returns:
            dict: Agent 실행 결과
        """
        # Middleware 전처리
        processed_input = message
        for mw in self.middleware:
            processed_input = mw.before_request(processed_input, **kwargs)

        # Agent 실행
        result = self.executor.invoke({"input": processed_input}, **kwargs)

        # Middleware 후처리
        result["output"] = self._apply_after_middleware(result["output"], **kwargs)

        return result

    def _apply_after_middleware(self, output: str, **kwargs) -> str:
        """Middleware 후처리 적용"""
        processed_output = output
        for mw in self.middleware:
            processed_output = mw.after_response(processed_output, **kwargs)
        return processed_output

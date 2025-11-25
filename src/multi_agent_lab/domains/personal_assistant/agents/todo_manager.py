"""
TodoManagerAgent - 할일 관리 전문 Agent

LLM이 Tool을 동적으로 선택하여 할일을 관리합니다.

사용 예시:
    from multi_agent_lab.domains.personal_assistant.agents.todo_manager import (
        TodoManagerAgent,
    )

    agent = TodoManagerAgent()
    response = agent.chat("장보기 할일 추가해줘")
    print(response)

실행:
    uv run python -c "
    from multi_agent_lab.domains.personal_assistant.agents.todo_manager import TodoManagerAgent
    agent = TodoManagerAgent()
    print(agent.chat('장보기 할일 추가해줘'))
    "
"""

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from multi_agent_lab.core.middleware import BaseMiddleware
from multi_agent_lab.domains.personal_assistant.tools.todo_tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
)


class TodoManagerAgent:
    """
    할일 관리 전문 Agent

    LangChain의 Tool Calling Agent를 사용하여
    사용자 요청에 따라 적절한 Tool을 선택하고 실행합니다.

    Attributes:
        model_name: 사용할 Ollama 모델명
        temperature: 생성 온도 (0.0 ~ 1.0)
        middleware: 미들웨어 리스트

    Example:
        >>> agent = TodoManagerAgent()
        >>> response = agent.chat("오늘 할일 목록 보여줘")
        >>> print(response)
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
        self.tools = [add_task, list_tasks, complete_task, delete_task]

        # System Prompt
        self.system_prompt = """당신은 할일 관리 전문가입니다.

사용자의 할일을 효율적으로 관리하고, 다음 작업을 수행합니다:

1. **할일 추가**: 새로운 할일을 등록합니다.
   - 우선순위를 high, medium, low 중 하나로 설정할 수 있습니다.
   - 마감일을 YYYY-MM-DD 형식으로 설정할 수 있습니다.

2. **할일 조회**: 전체 또는 상태별 할일을 조회합니다.
   - status: all(전체), pending(미완료), completed(완료)
   - priority: high, medium, low로 필터링 가능

3. **할일 완료**: 완료된 할일을 처리합니다.

4. **할일 삭제**: 불필요한 할일을 삭제합니다.

**주의사항:**
- 사용자가 우선순위를 명시하지 않으면 'medium'으로 설정하세요.
- 할일 목록을 보여줄 때는 우선순위 순서로 정렬하세요.
- 완료된 할일은 별도로 표시하세요.

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

    def chat(self, query: str) -> str:
        """
        사용자 질문에 응답

        Args:
            query: 사용자 질문

        Returns:
            str: Agent 응답
        """
        # Before Middleware 적용
        processed_input = query
        for mw in self.middleware:
            if hasattr(mw, "before_request"):
                processed_input = mw.before_request(processed_input)
            elif hasattr(mw, "pre_process"):
                processed_input = mw.pre_process(processed_input)

        # Agent 실행
        try:
            result = self.executor.invoke({"input": processed_input})
            output = result.get("output", "")
        except Exception as e:
            # 에러 미들웨어 처리
            error_msg = str(e)
            for mw in self.middleware:
                if hasattr(mw, "on_error"):
                    error_msg = mw.on_error(error_msg)
            return f"오류가 발생했습니다: {error_msg}"

        # After Middleware 적용
        final_output = self._apply_after_middleware(output)

        return final_output

    def invoke(self, query: str) -> dict:
        """
        Agent 직접 실행 (상세 결과 반환)

        Args:
            query: 사용자 질문

        Returns:
            dict: Agent 실행 결과 (input, output, intermediate_steps 등)
        """
        # Before Middleware 적용
        processed_input = query
        for mw in self.middleware:
            if hasattr(mw, "before_request"):
                processed_input = mw.before_request(processed_input)
            elif hasattr(mw, "pre_process"):
                processed_input = mw.pre_process(processed_input)

        # Agent 실행
        result = self.executor.invoke({"input": processed_input})

        # After Middleware 적용
        if "output" in result:
            result["output"] = self._apply_after_middleware(result["output"])

        return result

    def _apply_after_middleware(self, output: str) -> str:
        """After Middleware 적용"""
        for mw in self.middleware:
            if hasattr(mw, "after_response"):
                output = mw.after_response(output)
            elif hasattr(mw, "post_process"):
                output = mw.post_process(output)
        return output

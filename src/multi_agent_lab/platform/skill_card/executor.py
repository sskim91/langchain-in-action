"""
Skill Card Executor

Skill Card의 Execution Plan을 실제로 실행하는 엔진

📌 핵심 기능:
1. Execution Plan의 각 Step을 순서대로 실행
2. 변수 치환: ${variable} → 실제 값
3. Step 간 데이터 전달: output_to → 다음 Step의 input
4. 에러 처리: on_error에 따라 fail/skip

💡 사용 방식:
    executor = SkillCardExecutor(skill_card)
    result = executor.execute(user_query="내일 회의", context={...})
"""

import re
from typing import Any

from .schema import ExecutionStep, SkillCard


class ExecutionContext:
    """
    실행 컨텍스트

    Step 실행 중 생성된 변수들을 저장하고 관리합니다.
    """

    def __init__(self, initial_data: dict[str, Any] | None = None):
        """
        Args:
            initial_data: 초기 데이터 (user_query, user_id 등)
        """
        self.variables: dict[str, Any] = initial_data or {}
        self.step_results: list[dict] = []

    def set(self, key: str, value: Any):
        """변수 저장"""
        self.variables[key] = value

    def get(self, key: str) -> Any:
        """변수 조회"""
        return self.variables.get(key)

    def add_step_result(
        self, step: int, action: str, result: Any, error: str | None = None
    ):
        """Step 실행 결과 기록"""
        self.step_results.append(
            {
                "step": step,
                "action": action,
                "result": result,
                "error": error,
            }
        )


class SkillCardExecutor:
    """Skill Card 실행 엔진"""

    def __init__(self, skill_card: SkillCard, verbose: bool = False):
        """
        Args:
            skill_card: 실행할 Skill Card
            verbose: 상세 로그 출력 여부 (기본값: False)
        """
        self.skill_card = skill_card
        self.verbose = verbose
        # Tools 저장소: {tool_name: tool_function}
        self.tools: dict[str, Any] = {}

    def register_tool(self, name: str, tool: Any):
        """
        Tool 등록

        Args:
            name: Tool 이름 (예: "parse_event_info")
            tool: LangChain @tool 함수

        Example:
            >>> from personal_assistant.tools.schedule_tools import parse_event_info
            >>> executor.register_tool("parse_event_info", parse_event_info)
        """
        self.tools[name] = tool
        if self.verbose:
            print(f"✓ Tool 등록: {name}")

    def execute(
        self,
        user_query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Skill Card 실행

        Args:
            user_query: 사용자 질의
            context: 추가 컨텍스트 (user_id, conversation_history 등)

        Returns:
            실행 결과
        """
        # 실행 컨텍스트 초기화
        initial_data = {
            "user_query": user_query,
            **(context or {}),
        }
        ctx = ExecutionContext(initial_data)

        print(f"\n🚀 Execution Plan 시작: {self.skill_card.agent_name}")
        print(f"📝 질의: {user_query}\n")

        # Execution Plan의 각 Step 실행
        for step in self.skill_card.execution_plan:
            try:
                self._execute_step(step, ctx)
            except Exception as e:
                # on_error에 따라 처리
                if step.on_error == "fail":
                    print(f"❌ Step {step.step} 실패: {e}")
                    ctx.add_step_result(step.step, step.action, None, str(e))
                    raise
                elif step.on_error == "skip":
                    print(f"⚠️  Step {step.step} 스킵: {e}")
                    ctx.add_step_result(step.step, step.action, None, str(e))
                    continue

        print("\n✅ Execution Plan 완료!\n")

        # 최종 결과 반환
        return {
            "success": True,
            "variables": ctx.variables,
            "step_results": ctx.step_results,
        }

    def _execute_step(self, step: ExecutionStep, ctx: ExecutionContext):
        """
        단일 Step 실행

        Args:
            step: 실행할 Step
            ctx: 실행 컨텍스트
        """
        print(f"▶ Step {step.step}: {step.action}")
        if self.verbose:
            print(f"  📄 {step.description}")

        # 1. Input 변수 치환
        resolved_input = self._resolve_variables(step.input, ctx)
        if self.verbose:
            print(f"  📥 Input: {resolved_input}")

        # 2. Action 실행
        result = self._execute_action(step.action, resolved_input)

        if self.verbose:
            print(f"  📤 Output: {result}")
        else:
            # 간단한 요약만 출력
            if isinstance(result, dict):
                print(f"  ✓ 결과: {len(result)}개 필드")
            elif isinstance(result, list):
                print(f"  ✓ 결과: {len(result)}개 항목")
            else:
                print("  ✓ 완료")

        # 3. 결과를 변수에 저장
        if step.output_to:
            ctx.set(step.output_to, result)
            if self.verbose:
                print(f"  💾 저장: {step.output_to} = {result}")

        # 4. 실행 결과 기록
        ctx.add_step_result(step.step, step.action, result)
        print()

    def _resolve_variables(self, data: Any, ctx: ExecutionContext) -> Any:
        """
        변수 치환: ${variable} → 실제 값

        Args:
            data: 치환할 데이터 (str, dict, list 등)
            ctx: 실행 컨텍스트

        Returns:
            치환된 데이터
        """
        if isinstance(data, str):
            # "${variable}" 패턴 찾기
            pattern = r"\$\{([^}]+)\}"

            def replace(match):
                var_path = match.group(1)  # "event_data.title"
                return str(self._get_nested_value(var_path, ctx))

            return re.sub(pattern, replace, data)

        elif isinstance(data, dict):
            # dict의 모든 값에 대해 재귀적으로 치환
            return {k: self._resolve_variables(v, ctx) for k, v in data.items()}

        elif isinstance(data, list):
            # list의 모든 요소에 대해 재귀적으로 치환
            return [self._resolve_variables(item, ctx) for item in data]

        else:
            # 다른 타입은 그대로 반환
            return data

    def _get_nested_value(self, path: str, ctx: ExecutionContext) -> Any:
        """
        중첩된 변수 값 가져오기

        Args:
            path: "event_data.title" 같은 경로
            ctx: 실행 컨텍스트

        Returns:
            해당 경로의 값
        """
        parts = path.split(".")
        value = ctx.get(parts[0])

        # 중첩된 경로 탐색 (event_data.title)
        for part in parts[1:]:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return f"${{{path}}}"  # 못 찾으면 원본 그대로

        return value if value is not None else f"${{{path}}}"

    def _execute_action(self, action: str, input_data: dict) -> Any:
        """
        실제 Action 실행

        등록된 Tool을 호출하거나, 없으면 Mock으로 시뮬레이션합니다.

        Args:
            action: 실행할 액션 이름
            input_data: 입력 데이터

        Returns:
            실행 결과
        """
        # 1. 등록된 Tool이 있으면 실제 실행
        if action in self.tools:
            tool = self.tools[action]

            if self.verbose:
                print(f"\n  🔧 Tool 호출: {action}")
                print(f"  📥 Tool Input: {input_data}")

            try:
                # parse_event_info의 경우 verbose 파라미터 추가
                if action == "parse_event_info" and self.verbose:
                    input_data = {**input_data, "verbose": True}

                # LangChain Tool 호출
                result = tool.invoke(input_data)

                if self.verbose:
                    print(f"  ✅ Tool 성공: {action}")

                return result
            except Exception as e:
                print(f"  ⚠️  Tool 실행 오류: {e}")
                raise

        # 2. Tool이 없으면 Mock 데이터로 시뮬레이션 (하위 호환성)
        if self.verbose:
            print(f"  ⚠️  Tool '{action}'이 등록되지 않았습니다. Mock 데이터 사용")
        mock_results = {
            "parse_event_info": {
                "title": "팀 회의",
                "date": "2025-11-12",
                "time": "14:00",
                "duration": 60,
            },
            "get_calendar_events": [{"title": "기존 회의", "time": "10:00-11:00"}],
            "find_free_time": {"best_slot": {"start": "14:00", "end": "15:00"}},
            "create_event": {
                "id": "evt_12345",
                "title": input_data.get("title", "회의"),
                "created": True,
            },
            "send_notification": {
                "sent": True,
                "message": "알림이 전송되었습니다.",
            },
        }

        return mock_results.get(action, {"executed": True})

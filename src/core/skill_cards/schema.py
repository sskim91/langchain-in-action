"""
Skill Card 데이터 구조 (Pydantic 모델)

📌 목적:
- Skill Card JSON의 형식을 정의하고 검증
- 타입 안정성 보장

💡 핵심 개념:
- Pydantic BaseModel: 자동 검증 + 타입 힌트
- Field: 기본값, 설명, 제약조건 정의
"""

from typing import Any

from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """
    Tool 설정

    각 Tool의 실행 옵션을 정의합니다.
    """

    name: str = Field(..., description="Tool 이름")
    required: bool = Field(False, description="필수 여부")
    timeout_ms: int = Field(3000, description="타임아웃 (밀리초)")
    retry: int = Field(0, description="재시도 횟수")


class ExecutionStep(BaseModel):
    """
    Execution Plan의 단계

    "논리적 사고 전개"의 각 단계를 정의합니다.
    이게 바로 Agent가 문제를 해결하는 순서!
    """

    step: int = Field(..., description="단계 번호 (1부터 시작)")
    action: str = Field(..., description="실행할 액션 (Tool 이름)")
    description: str = Field("", description="단계 설명")
    input: dict[str, Any] = Field(default_factory=dict, description="입력 데이터")
    output_to: str = Field("", description="출력 변수명 (다음 step에서 사용)")
    timeout_ms: int = Field(3000, description="타임아웃")
    on_error: str = Field("fail", description="에러 처리 전략 (fail/skip)")


class Trigger(BaseModel):
    """
    Skill Card 트리거 조건

    "언제 이 Skill Card를 사용할지" 정의합니다.
    """

    keywords: list[str] = Field(default_factory=list, description="트리거 키워드")
    intent: str = Field("", description="의도 (intent)")
    similarity_threshold: float = Field(0.85, description="유사도 임계값")
    examples: list[str] = Field(default_factory=list, description="예시 질의")


class Constraints(BaseModel):
    """
    제약사항

    "무엇을 해서는 안 되는지" 정의합니다.
    """

    validation: list[str] = Field(default_factory=list, description="검증 규칙")
    output_format: str = Field("text", description="출력 형식")
    max_response_length: int = Field(1000, description="최대 응답 길이")
    language: str = Field("ko-KR", description="언어")


class LLMConfig(BaseModel):
    """LLM 설정"""

    model: str = Field("gpt-oss:20b", description="모델명")
    temperature: float = Field(0.1, description="Temperature (0.0 ~ 1.0)")
    max_tokens: int = Field(500, description="최대 토큰")
    system_prompt: str = Field("", description="시스템 프롬프트")


class SkillCard(BaseModel):
    """
    Skill Card 스키마

    AI Agent의 전체 행동을 정의하는 메타데이터입니다.

    📌 핵심 구성요소:
    1. trigger: 언제 사용할지
    2. tools: 어떤 도구를 쓸지
    3. execution_plan: 어떤 순서로 실행할지 (가장 중요!)
    4. constraints: 무엇을 하면 안 되는지
    """

    id: str = Field(..., description="Skill Card 고유 ID")
    version: str = Field("1.0.0", description="버전")
    agent_name: str = Field(..., description="Agent 이름")
    agent_type: str = Field(..., description="Agent 타입")
    description: str = Field("", description="설명")

    trigger: Trigger = Field(default_factory=Trigger, description="트리거")
    tools: list[ToolConfig] = Field(default_factory=list, description="Tool 목록")
    execution_plan: list[ExecutionStep] = Field(
        default_factory=list, description="실행 계획 (논리적 사고 전개)"
    )
    constraints: Constraints = Field(
        default_factory=Constraints, description="제약사항"
    )
    llm_config: LLMConfig = Field(default_factory=LLMConfig, description="LLM 설정")

    metadata: dict[str, Any] = Field(default_factory=dict, description="메타데이터")

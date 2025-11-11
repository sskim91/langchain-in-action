# Step 03: Skill Card 시스템 구현

## 🎯 목표

**Skill Card 개념을 이해하고, ScheduleManagerAgent를 Skill Card 방식으로 업그레이드합니다.**

### 배울 내용
1. Skill Card가 왜 필요한지 (문제와 해결)
2. Skill Card JSON 구조 설계
3. SkillCardManager 구현
4. Skill Card로 Agent 통제하기

---

## 💡 왜 Skill Card가 필요한가?

### 문제 상황: LLM의 불확실성

현재 우리의 ScheduleManagerAgent는 이렇게 작동합니다:

```python
# 사용자 질의
user: "내일 회의 일정 잡아줘"

# LLM이 판단
LLM: "create_event를 호출해야겠군!"
     → create_event(title="회의", start_time="???")
```

**발생하는 문제들:**
- 🔴 **매번 다른 결과**: 같은 질문에 다른 Tool을 호출할 수 있음
- 🔴 **예측 불가능**: 어떤 Tool을 쓸지 보장할 수 없음
- 🔴 **품질 관리 어려움**: 일관성 없는 응답
- 🔴 **비용 증가**: LLM이 매번 "생각"해야 함 (ReAct 패턴)

### 해결책: Skill Card

**"논리적 사고 전개 과정"을 미리 정의해두자!**

```json
{
  "execution_plan": [
    {"step": 1, "action": "parse_event_info"},
    {"step": 2, "action": "check_availability"},
    {"step": 3, "action": "create_event"},
    {"step": 4, "action": "set_reminder"}
  ]
}
```

**장점:**
- ✅ **통제 가능**: 정해진 순서대로만 실행
- ✅ **예측 가능**: 항상 같은 결과
- ✅ **비용 절감**: LLM 호출 최소화
- ✅ **품질 보장**: 제약사항 강제

---

## 📁 1. Skill Card 구조 설계

### 완전한 Skill Card 예시

`src/personal_assistant/skill_cards/schedule_card.json`:

```json
{
  "id": "SC_SCHEDULE_001",
  "version": "1.0.0",
  "agent_name": "일정 관리 전문가",
  "agent_type": "schedule",
  "description": "사용자의 일정을 생성, 조회, 수정하고 시간 관리를 도와주는 Agent",

  "trigger": {
    "keywords": ["일정", "스케줄", "약속", "회의", "미팅", "calendar"],
    "intent": "일정 관리",
    "similarity_threshold": 0.85,
    "examples": [
      "내일 오후 3시에 팀 회의 잡아줘",
      "이번 주 금요일 빈 시간 알려줘",
      "다음주 월요일 일정 보여줘"
    ]
  },

  "tools": [
    {
      "name": "create_event",
      "required": true,
      "timeout_ms": 3000,
      "retry": 2
    },
    {
      "name": "find_free_time",
      "required": false,
      "timeout_ms": 2000,
      "retry": 1
    },
    {
      "name": "list_events",
      "required": false,
      "timeout_ms": 2000,
      "retry": 1
    }
  ],

  "execution_plan": [
    {
      "step": 1,
      "action": "parse_event_info",
      "description": "사용자 입력에서 일정 정보 추출",
      "input": {
        "query": "${user_query}"
      },
      "output_to": "event_data",
      "timeout_ms": 2000,
      "on_error": "fail"
    },
    {
      "step": 2,
      "action": "find_free_time",
      "description": "해당 시간대에 기존 일정과 충돌 확인",
      "input": {
        "date": "${event_data.date}",
        "duration": "${event_data.duration}"
      },
      "output_to": "available_slots",
      "timeout_ms": 2000,
      "on_error": "skip"
    },
    {
      "step": 3,
      "action": "create_event",
      "description": "일정 생성",
      "input": {
        "title": "${event_data.title}",
        "start_time": "${event_data.start_time}",
        "duration": "${event_data.duration}"
      },
      "output_to": "created_event",
      "timeout_ms": 3000,
      "on_error": "fail"
    }
  ],

  "constraints": {
    "validation": [
      "과거 날짜 일정 생성 금지",
      "종료 시간이 시작 시간보다 앞설 수 없음",
      "일정 제목 필수 (최소 1자)"
    ],
    "output_format": "markdown",
    "max_response_length": 500,
    "language": "ko-KR"
  },

  "fallback_strategy": {
    "type": "default_response",
    "message": "죄송합니다. 일정 생성에 실패했습니다. 정보를 다시 확인해 주세요.",
    "actions": ["log_failure", "notify_user"]
  },

  "llm_config": {
    "model": "gpt-oss:20b",
    "temperature": 0.1,
    "max_tokens": 500,
    "system_prompt": "당신은 사용자의 개인 비서입니다. 일정을 효율적으로 관리하고 시간 관리를 도와주세요."
  },

  "metadata": {
    "created_at": "2025-11-10T09:00:00Z",
    "created_by": "admin",
    "last_updated": "2025-11-10T09:00:00Z",
    "tags": ["schedule", "calendar", "time-management"]
  }
}
```

### 각 섹션 설명

#### 1. 기본 정보
```json
{
  "id": "SC_SCHEDULE_001",           // 고유 ID
  "version": "1.0.0",                // 버전 관리
  "agent_name": "일정 관리 전문가",   // Agent 이름
  "agent_type": "schedule",          // Agent 타입
  "description": "..."               // 설명
}
```

#### 2. Trigger (트리거)
**"언제 이 Skill Card를 사용할지" 정의**

```json
{
  "trigger": {
    "keywords": ["일정", "스케줄", ...],      // 키워드 매칭
    "intent": "일정 관리",                    // 의도
    "similarity_threshold": 0.85,            // 유사도 임계값
    "examples": ["내일 회의 잡아줘", ...]     // 예시 질의
  }
}
```

#### 3. Tools (도구)
**"어떤 도구를 사용할 수 있는지" 정의**

```json
{
  "tools": [
    {
      "name": "create_event",
      "required": true,       // 필수 도구
      "timeout_ms": 3000,    // 타임아웃
      "retry": 2             // 재시도 횟수
    }
  ]
}
```

#### 4. Execution Plan (실행 계획) ⭐ 핵심!
**"어떤 순서로 문제를 해결할지" 정의 - 논리적 사고 전개!**

```json
{
  "execution_plan": [
    {
      "step": 1,
      "action": "parse_event_info",           // 실행할 액션
      "description": "일정 정보 추출",         // 설명
      "input": {"query": "${user_query}"},   // 입력 (변수 사용)
      "output_to": "event_data",             // 출력 변수명
      "on_error": "fail"                     // 에러 처리 (fail/skip)
    },
    {
      "step": 2,
      "action": "find_free_time",
      "input": {
        "date": "${event_data.date}",        // 이전 step 결과 사용!
        "duration": "${event_data.duration}"
      },
      "output_to": "available_slots",
      "on_error": "skip"                     // 실패해도 계속 진행
    }
  ]
}
```

**이게 바로 "논리적 사고를 스스로 전개"하는 부분!**

#### 5. Constraints (제약사항)
**"무엇을 해서는 안 되는지" 정의**

```json
{
  "constraints": {
    "validation": [
      "과거 날짜 일정 생성 금지",
      "일정 제목 필수"
    ],
    "output_format": "markdown",
    "max_response_length": 500
  }
}
```

---

## 🔨 2. SkillCardManager 구현

Skill Card JSON을 로드하고 관리하는 클래스를 만듭니다.

### `src/core/skill_cards/__init__.py`

```python
"""
Skill Card 시스템

Skill Card를 로드, 검증, 관리합니다.
"""

from .manager import SkillCardManager
from .schema import SkillCard

__all__ = [
    "SkillCardManager",
    "SkillCard",
]
```

### `src/core/skill_cards/schema.py`

```python
"""
Skill Card 데이터 구조 (Pydantic 모델)
"""

from typing import Any

from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """Tool 설정"""

    name: str = Field(..., description="Tool 이름")
    required: bool = Field(False, description="필수 여부")
    timeout_ms: int = Field(3000, description="타임아웃 (밀리초)")
    retry: int = Field(0, description="재시도 횟수")


class ExecutionStep(BaseModel):
    """Execution Plan의 단계"""

    step: int = Field(..., description="단계 번호")
    action: str = Field(..., description="실행할 액션")
    description: str = Field("", description="단계 설명")
    input: dict[str, Any] = Field(default_factory=dict, description="입력 데이터")
    output_to: str = Field("", description="출력 변수명")
    timeout_ms: int = Field(3000, description="타임아웃")
    on_error: str = Field("fail", description="에러 처리 (fail/skip)")


class Trigger(BaseModel):
    """Skill Card 트리거 조건"""

    keywords: list[str] = Field(default_factory=list, description="키워드 목록")
    intent: str = Field("", description="의도")
    similarity_threshold: float = Field(0.85, description="유사도 임계값")
    examples: list[str] = Field(default_factory=list, description="예시 질의")


class Constraints(BaseModel):
    """제약사항"""

    validation: list[str] = Field(default_factory=list, description="검증 규칙")
    output_format: str = Field("text", description="출력 형식")
    max_response_length: int = Field(1000, description="최대 응답 길이")
    language: str = Field("ko-KR", description="언어")


class LLMConfig(BaseModel):
    """LLM 설정"""

    model: str = Field("gpt-oss:20b", description="모델명")
    temperature: float = Field(0.1, description="Temperature")
    max_tokens: int = Field(500, description="최대 토큰")
    system_prompt: str = Field("", description="시스템 프롬프트")


class SkillCard(BaseModel):
    """Skill Card 스키마"""

    id: str = Field(..., description="Skill Card ID")
    version: str = Field("1.0.0", description="버전")
    agent_name: str = Field(..., description="Agent 이름")
    agent_type: str = Field(..., description="Agent 타입")
    description: str = Field("", description="설명")

    trigger: Trigger = Field(default_factory=Trigger, description="트리거")
    tools: list[ToolConfig] = Field(default_factory=list, description="Tool 목록")
    execution_plan: list[ExecutionStep] = Field(
        default_factory=list, description="실행 계획"
    )
    constraints: Constraints = Field(default_factory=Constraints, description="제약사항")
    llm_config: LLMConfig = Field(default_factory=LLMConfig, description="LLM 설정")

    metadata: dict[str, Any] = Field(default_factory=dict, description="메타데이터")
```

### `src/core/skill_cards/manager.py`

```python
"""
Skill Card Manager

Skill Card를 로드하고 관리하는 클래스
"""

import json
from pathlib import Path

from .schema import SkillCard


class SkillCardManager:
    """Skill Card 로드 및 관리"""

    def __init__(self, cards_dir: str | Path = "src/personal_assistant/skill_cards"):
        """
        Args:
            cards_dir: Skill Card JSON 파일들이 있는 디렉토리
        """
        self.cards_dir = Path(cards_dir)
        self.cards: dict[str, SkillCard] = {}
        self._load_all_cards()

    def _load_all_cards(self):
        """디렉토리에서 모든 Skill Card JSON 파일 로드"""
        if not self.cards_dir.exists():
            print(f"⚠️  Skill Cards 디렉토리가 없습니다: {self.cards_dir}")
            self.cards_dir.mkdir(parents=True, exist_ok=True)
            return

        for card_file in self.cards_dir.glob("*.json"):
            try:
                with open(card_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Pydantic으로 검증
                skill_card = SkillCard(**data)

                self.cards[skill_card.id] = skill_card
                print(f"✓ Loaded: {skill_card.id} - {skill_card.agent_name}")

            except Exception as e:
                print(f"✗ Failed to load {card_file.name}: {e}")

    def get(self, card_id: str) -> SkillCard | None:
        """
        Skill Card 조회

        Args:
            card_id: Skill Card ID

        Returns:
            SkillCard 또는 None
        """
        return self.cards.get(card_id)

    def list_all(self) -> list[dict]:
        """
        모든 Skill Card 목록 조회

        Returns:
            Skill Card 목록 (간략 정보)
        """
        return [
            {
                "id": card.id,
                "name": card.agent_name,
                "type": card.agent_type,
                "description": card.description,
                "version": card.version,
            }
            for card in self.cards.values()
        ]

    def find_by_keywords(self, query: str) -> list[SkillCard]:
        """
        키워드 매칭으로 Skill Card 찾기

        Args:
            query: 사용자 질의

        Returns:
            매칭되는 Skill Card 목록
        """
        query_lower = query.lower()
        matched = []

        for card in self.cards.values():
            # 키워드 매칭
            if any(kw in query_lower for kw in card.trigger.keywords):
                matched.append(card)

        return matched

    def validate(self, card: SkillCard) -> tuple[bool, list[str]]:
        """
        Skill Card 유효성 검증

        Args:
            card: 검증할 Skill Card

        Returns:
            (유효 여부, 에러 메시지 목록)
        """
        errors = []

        # ID 검증
        if not card.id:
            errors.append("ID가 없습니다")

        # Agent 이름 검증
        if not card.agent_name:
            errors.append("Agent 이름이 없습니다")

        # Execution Plan 검증
        if not card.execution_plan:
            errors.append("Execution Plan이 비어있습니다")

        # Step 번호 연속성 검증
        steps = [s.step for s in card.execution_plan]
        if steps != list(range(1, len(steps) + 1)):
            errors.append("Execution Plan의 step 번호가 연속적이지 않습니다")

        return len(errors) == 0, errors

    def reload(self):
        """Skill Card 재로드"""
        self.cards.clear()
        self._load_all_cards()
```

---

## 📝 3. Skill Card JSON 파일 작성

실제로 사용할 Skill Card를 작성합니다.

### `src/personal_assistant/skill_cards/schedule_card.json`

위에서 본 완전한 Skill Card 예시를 이 파일로 저장합니다.

---

## ✅ 4. 테스트 작성

### `tests/core/test_skill_card_manager.py`

```python
"""
SkillCardManager 테스트
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.core.skill_cards import SkillCard, SkillCardManager


def test_load_skill_card():
    """Skill Card JSON 로드 테스트"""
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as tmpdir:
        # 테스트용 Skill Card JSON 생성
        card_data = {
            "id": "SC_TEST_001",
            "version": "1.0.0",
            "agent_name": "테스트 Agent",
            "agent_type": "test",
            "description": "테스트용 Skill Card",
            "trigger": {
                "keywords": ["테스트"],
                "intent": "테스트",
                "similarity_threshold": 0.85,
            },
            "tools": [{"name": "test_tool", "required": True}],
            "execution_plan": [
                {
                    "step": 1,
                    "action": "test_action",
                    "description": "테스트",
                    "output_to": "result",
                }
            ],
        }

        card_file = Path(tmpdir) / "test_card.json"
        with open(card_file, "w", encoding="utf-8") as f:
            json.dump(card_data, f, ensure_ascii=False)

        # SkillCardManager로 로드
        manager = SkillCardManager(cards_dir=tmpdir)

        # 검증
        assert "SC_TEST_001" in manager.cards
        card = manager.get("SC_TEST_001")
        assert card is not None
        assert card.agent_name == "테스트 Agent"
        assert len(card.execution_plan) == 1


def test_find_by_keywords():
    """키워드로 Skill Card 찾기 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Schedule Card
        schedule_card = {
            "id": "SC_SCHEDULE_001",
            "version": "1.0.0",
            "agent_name": "일정 관리",
            "agent_type": "schedule",
            "trigger": {"keywords": ["일정", "스케줄", "회의"]},
            "execution_plan": [{"step": 1, "action": "test"}],
        }

        card_file = Path(tmpdir) / "schedule_card.json"
        with open(card_file, "w", encoding="utf-8") as f:
            json.dump(schedule_card, f, ensure_ascii=False)

        manager = SkillCardManager(cards_dir=tmpdir)

        # 키워드 매칭
        results = manager.find_by_keywords("내일 회의 일정 잡아줘")
        assert len(results) == 1
        assert results[0].id == "SC_SCHEDULE_001"


def test_validate_skill_card():
    """Skill Card 유효성 검증 테스트"""
    manager = SkillCardManager(cards_dir=tempfile.mkdtemp())

    # 올바른 Skill Card
    valid_card = SkillCard(
        id="SC_VALID",
        agent_name="Valid Agent",
        agent_type="test",
        execution_plan=[
            {"step": 1, "action": "step1", "output_to": "result1"},
            {"step": 2, "action": "step2", "output_to": "result2"},
        ],
    )

    is_valid, errors = manager.validate(valid_card)
    assert is_valid
    assert len(errors) == 0

    # 잘못된 Skill Card (step 번호 불연속)
    invalid_card = SkillCard(
        id="SC_INVALID",
        agent_name="Invalid Agent",
        agent_type="test",
        execution_plan=[
            {"step": 1, "action": "step1", "output_to": "result1"},
            {"step": 3, "action": "step3", "output_to": "result3"},  # step 2 누락!
        ],
    )

    is_valid, errors = manager.validate(invalid_card)
    assert not is_valid
    assert len(errors) > 0
```

---

## 🚀 5. 실행 예제

### `src/examples/05_skill_card_demo.py`

```python
"""
Skill Card 시스템 데모
"""

from src.core.skill_cards import SkillCardManager


def main():
    """Skill Card Manager 데모"""
    print("=" * 60)
    print("Skill Card 시스템 데모")
    print("=" * 60)
    print()

    # Skill Card Manager 생성
    manager = SkillCardManager()

    # 1. 모든 Skill Card 목록
    print("📋 등록된 Skill Cards:")
    cards = manager.list_all()
    for card in cards:
        print(f"  - {card['id']}: {card['name']} (v{card['version']})")
    print()

    # 2. 특정 Skill Card 조회
    print("🔍 SC_SCHEDULE_001 조회:")
    schedule_card = manager.get("SC_SCHEDULE_001")
    if schedule_card:
        print(f"  이름: {schedule_card.agent_name}")
        print(f"  설명: {schedule_card.description}")
        print(f"  트리거 키워드: {', '.join(schedule_card.trigger.keywords)}")
        print(f"  실행 단계 수: {len(schedule_card.execution_plan)}")
        print()

        # Execution Plan 출력
        print("  📝 Execution Plan:")
        for step in schedule_card.execution_plan:
            print(f"    Step {step.step}: {step.action}")
            print(f"      - {step.description}")
            print(f"      - Output to: {step.output_to}")
            print(f"      - On error: {step.on_error}")
            print()

    # 3. 키워드로 Skill Card 찾기
    print("🔎 키워드 매칭 테스트:")
    queries = [
        "내일 회의 일정 잡아줘",
        "이번 주 금요일 빈 시간 알려줘",
        "프로젝트 문서 작성 할 일 추가",
    ]

    for query in queries:
        results = manager.find_by_keywords(query)
        if results:
            print(f"  '{query}' → {results[0].agent_name}")
        else:
            print(f"  '{query}' → (매칭 안 됨)")

    print()
    print("=" * 60)
    print("데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

## 📊 6. 개념 정리

### Skill Card가 해결하는 문제

```
기존 방식 (ReAct):
  사용자 질의 → LLM 생각 → Tool 선택 → LLM 생각 → Tool 선택 → ...
  💰 비용: 높음 | 🎯 일관성: 낮음 | ⏱️ 속도: 느림

Skill Card 방식:
  사용자 질의 → Execution Plan 실행 → Tool1 → Tool2 → Tool3 → 결과
  💰 비용: 낮음 | 🎯 일관성: 높음 | ⏱️ 속도: 빠름
```

### Execution Plan = 논리적 사고 전개

```
문제: "내일 회의 일정 잡아줘"

논리적 사고 전개 (Execution Plan):
  1. 먼저 일정 정보를 파싱해야 한다 → parse_event_info()
  2. 그 시간에 다른 일정이 있는지 확인해야 한다 → find_free_time()
  3. 문제없으면 일정을 생성한다 → create_event()
  4. 알림을 설정한다 → set_reminder()
```

이게 바로 **"Agent가 문제해결을 위해 논리적 사고를 스스로 전개"**하는 것입니다!

---

## ✅ 체크리스트

- [ ] Skill Card 구조 이해
- [ ] `schedule_card.json` 작성
- [ ] `SkillCardManager` 구현
- [ ] Pydantic 스키마 정의
- [ ] 테스트 작성 및 통과
- [ ] 예제 실행 성공

## 다음 단계

👉 **[Step 04: Execution Plan & SkillCardExecutor](./04-skill-card-executor.md)**

Execution Plan을 실제로 실행하는 Executor를 구현합니다!

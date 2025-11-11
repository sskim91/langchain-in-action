"""
Skill Card 시스템 데모

이 예제는 Skill Card 시스템의 핵심 개념을 보여줍니다:
1. Skill Card 로드 및 검증
2. 키워드 매칭으로 적절한 Agent 선택
3. Execution Plan (논리적 사고 전개) 확인
4. 변수 체이닝 (Step 간 데이터 흐름)

실행:
    uv run python -m src.examples.05_skill_card_demo
"""

import json

from core.skill_cards import SkillCardManager


def print_section(title: str):
    """섹션 구분선 출력"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print("=" * 80)


def demo_load_skill_card():
    """1. Skill Card 로드 데모"""
    print_section("1️⃣  Skill Card 로드")

    manager = SkillCardManager()

    # 로드된 Skill Card 목록 출력
    cards = manager.list_all()
    print(f"\n✅ 총 {len(cards)}개의 Skill Card가 로드되었습니다:\n")

    for card in cards:
        print(f"  • {card['id']}")
        print(f"    - 이름: {card['name']}")
        print(f"    - 타입: {card['type']}")
        print(f"    - 설명: {card['description'][:50]}...")
        print()

    return manager


def demo_keyword_matching(manager: SkillCardManager):
    """2. 키워드 매칭 데모"""
    print_section("2️⃣  키워드 매칭 (자동 Agent 선택)")

    # 다양한 사용자 질의
    test_queries = [
        "내일 오후 2시에 팀 회의 일정 잡아줘",
        "다음주 월요일에 1시간짜리 미팅 추가해줘",
        "오늘 날씨 어때?",  # 매칭 안 됨
        "회의 시간 좀 잡아줄래?",
    ]

    for query in test_queries:
        print(f'\n📝 질의: "{query}"')

        matched = manager.find_by_keywords(query)

        if matched:
            print(f"   ✅ 매칭된 Skill Card: {matched[0].agent_name}")
            print(f"   📌 Skill Card ID: {matched[0].id}")
        else:
            print("   ❌ 매칭되는 Skill Card가 없습니다")


def demo_execution_plan(manager: SkillCardManager):
    """3. Execution Plan (논리적 사고 전개) 데모"""
    print_section("3️⃣  Execution Plan - Agent의 논리적 사고 과정")

    card = manager.get("SC_SCHEDULE_001")

    print(f"\n🎯 Agent: {card.agent_name}")
    print(f"📋 Execution Plan ({len(card.execution_plan)}단계):\n")

    for step in card.execution_plan:
        print(f"  Step {step.step}: {step.action}")
        print(f"    📝 설명: {step.description}")
        print(f"    📥 입력: {json.dumps(step.input, ensure_ascii=False, indent=6)}")
        print(f"    📤 출력 변수: {step.output_to or '(없음)'}")
        print(f"    ⚠️  에러 처리: {step.on_error}")
        print()


def demo_variable_chaining(manager: SkillCardManager):
    """4. 변수 체이닝 (Step 간 데이터 흐름) 데모"""
    print_section("4️⃣  변수 체이닝 - Step 간 데이터 흐름")

    card = manager.get("SC_SCHEDULE_001")

    print("\n🔗 Execution Plan의 데이터 흐름:\n")

    # Step별 입출력 추적
    variables = {}

    for step in card.execution_plan:
        print(f"Step {step.step}: {step.action}")

        # 출력 변수 등록
        if step.output_to:
            variables[step.output_to] = f"<{step.output_to}의 결과>"
            print(f"  ➡️  출력: ${{{step.output_to}}}")

        # 입력에서 사용하는 변수 찾기
        input_str = json.dumps(step.input)
        used_vars = [var for var in variables if f"${{{var}" in input_str]

        if used_vars:
            print(f"  ⬅️  사용 변수: {', '.join(f'${{{v}}}' for v in used_vars)}")

        print()

    # 실제 시나리오 시뮬레이션
    print("\n💡 예시 시나리오: '내일 오후 2시에 팀 회의 일정 잡아줘'\n")

    scenario_data = {
        "Step 1": {
            "action": "parse_event_info",
            "input": {"query": "내일 오후 2시에 팀 회의 일정 잡아줘"},
            "output": {
                "event_data": {
                    "title": "팀 회의",
                    "date": "2025-11-12",
                    "preferred_time": "14:00",
                    "duration": 60,
                }
            },
        },
        "Step 2": {
            "action": "get_calendar_events",
            "input": {"date": "${event_data.date}"},
            "output": {
                "existing_events": [{"title": "기존 회의", "time": "10:00-11:00"}]
            },
        },
        "Step 3": {
            "action": "find_free_time",
            "input": {
                "duration": "${event_data.duration}",
                "existing_events": "${existing_events}",
            },
            "output": {
                "available_slots": {"best_slot": {"start": "14:00", "end": "15:00"}}
            },
        },
        "Step 4": {
            "action": "create_event",
            "input": {
                "title": "${event_data.title}",
                "start_time": "${available_slots.best_slot.start}",
            },
            "output": {"created_event": {"id": "evt_123", "title": "팀 회의"}},
        },
    }

    for step_name, step_info in scenario_data.items():
        print(f"  {step_name}: {step_info['action']}")
        print(f"    입력: {json.dumps(step_info['input'], ensure_ascii=False)}")
        print(f"    출력: {json.dumps(step_info['output'], ensure_ascii=False)}")
        print()


def demo_validation(manager: SkillCardManager):
    """5. Skill Card 유효성 검증 데모"""
    print_section("5️⃣  Skill Card 유효성 검증")

    card = manager.get("SC_SCHEDULE_001")

    print(f"\n🔍 검증 대상: {card.id}\n")

    is_valid, errors = manager.validate(card)

    if is_valid:
        print("✅ 검증 통과! 이 Skill Card는 유효합니다.")
    else:
        print("❌ 검증 실패:")
        for error in errors:
            print(f"  - {error}")

    # Constraints 출력
    print(f"\n📋 제약사항 ({len(card.constraints.validation)}개):")
    for i, rule in enumerate(card.constraints.validation, 1):
        print(f"  {i}. {rule}")


def demo_llm_config(manager: SkillCardManager):
    """6. LLM 설정 데모"""
    print_section("6️⃣  LLM 설정")

    card = manager.get("SC_SCHEDULE_001")

    print("\n⚙️  LLM Configuration:\n")
    print(f"  모델: {card.llm_config.model}")
    print(f"  Temperature: {card.llm_config.temperature}")
    print(f"  Max Tokens: {card.llm_config.max_tokens}")
    print("\n  System Prompt:")
    print(f"  '{card.llm_config.system_prompt}'")


def main():
    """메인 데모 실행"""
    print("\n" + "🎯" * 40)
    print("    Skill Card 시스템 데모")
    print("    - AI Agent의 행동을 JSON으로 정의하고 제어하기")
    print("🎯" * 40)

    # 1. Skill Card 로드
    manager = demo_load_skill_card()

    # 2. 키워드 매칭
    demo_keyword_matching(manager)

    # 3. Execution Plan 확인
    demo_execution_plan(manager)

    # 4. 변수 체이닝
    demo_variable_chaining(manager)

    # 5. 유효성 검증
    demo_validation(manager)

    # 6. LLM 설정
    demo_llm_config(manager)

    print_section("✨ 데모 완료!")
    print("\n💡 핵심 포인트:")
    print("  1. Skill Card = Agent의 '설계도'")
    print("  2. Execution Plan = '논리적 사고 전개 과정'")
    print("  3. 변수 체이닝 = Step 간 데이터 흐름")
    print("  4. LLM이 아닌 '미리 정의된 로직'으로 동작 → 예측 가능!")
    print()


if __name__ == "__main__":
    main()

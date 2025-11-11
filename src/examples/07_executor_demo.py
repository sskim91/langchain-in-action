"""
Skill Card Executor 데모

Skill Card의 Execution Plan을 실제로 실행해봅니다.

🎯 목표:
- Skill Card 로드
- Executor로 실행
- 변수 치환과 Step 간 데이터 흐름 확인

실행:
    uv run python -m src.examples.07_executor_demo
"""

from core.skill_cards import SkillCardExecutor, SkillCardManager


def main():
    print("=" * 80)
    print("  🚀 Skill Card Executor 데모")
    print("=" * 80)

    # 1. Skill Card 로드
    print("\n1️⃣  Skill Card 로드 중...")
    manager = SkillCardManager()
    card = manager.get("SC_SCHEDULE_001")

    if not card:
        print("   ❌ Skill Card를 찾을 수 없습니다!")
        return

    print(f"   ✅ 로드 완료: {card.agent_name}")
    print(f"   📋 Execution Plan: {len(card.execution_plan)} 단계")

    # 2. Executor 생성
    print("\n2️⃣  Executor 초기화...")
    executor = SkillCardExecutor(card)
    print("   ✅ 초기화 완료!")

    # 3. 실행!
    print("\n3️⃣  Execution Plan 실행!")
    print("-" * 80)

    result = executor.execute(
        user_query="내일 오후 2시에 팀 회의 일정 잡아줘",
        context={
            "user_id": "user_12345",
            "conversation_history": [],
        },
    )

    # 4. 결과 출력
    print("-" * 80)
    print("\n4️⃣  실행 결과:")
    print(f"   ✅ 성공: {result['success']}")
    print("\n   📦 저장된 변수:")
    for key, value in result["variables"].items():
        if key not in ["user_query", "user_id", "conversation_history"]:
            print(f"      • {key}: {value}")

    print("\n   📊 Step 실행 내역:")
    for step_result in result["step_results"]:
        status = "✅" if step_result["error"] is None else "❌"
        print(f"      {status} Step {step_result['step']}: {step_result['action']}")

    # 5. 핵심 설명
    print("\n" + "=" * 80)
    print("  💡 여기서 일어난 일")
    print("=" * 80)
    print("""
  1️⃣  Step 1: parse_event_info
     - 입력: "내일 오후 2시에 팀 회의 일정 잡아줘"
     - 출력: event_data = {title: "팀 회의", date: "2025-11-12", ...}
     - 💾 변수 저장!

  2️⃣  Step 2: get_calendar_events
     - 입력: date = "${event_data.date}" → "2025-11-12"로 치환!
     - 출력: existing_events = [...]

  3️⃣  Step 3: find_free_time
     - 입력: duration = "${event_data.duration}" → 60으로 치환!
     - 출력: available_slots = {best_slot: {...}}

  4️⃣  Step 4: create_event
     - 입력: title = "${event_data.title}" → "팀 회의"로 치환!
     - 출력: created_event = {id: "evt_12345", created: True}
     - 🎉 실제로 일정이 생성됨!

  5️⃣  Step 5: send_notification
     - 입력: event = "${created_event}"
     - 출력: {sent: True}

  🔑 핵심:
     - 각 Step의 출력(output_to)이 다음 Step의 입력(input)으로 전달!
     - ${변수명} 문법으로 자동 치환!
     - LLM이 매번 "생각"하지 않고, 정해진 순서대로 실행!
    """)

    print("=" * 80)
    print("  ✨ 데모 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

"""
Dynamic Agent Demo - LLM이 Tool을 스스로 선택

🎯 목표:
- Static Execution Plan과 달리 LLM이 상황을 보고 Tool 선택
- 같은 질문이어도 필요한 Tool만 선택적으로 사용

실행:
    uv run python -m src.examples.09_dynamic_agent
"""

from personal_assistant.agents.schedule_manager import ScheduleManagerAgent
from personal_assistant.database import db


def main():
    print("=" * 80)
    print("  🤖 Dynamic Agent - LLM이 Tool을 선택합니다")
    print("=" * 80)

    # DB 초기화
    print("\n0️⃣  DB 초기화...")
    db.clear()
    db.add_event(
        {
            "title": "기존 회의",
            "start_time": "2025-11-13 10:00",
            "end_time": "2025-11-13 11:00",
            "duration": 60,
        }
    )
    print(f"   ✅ 기존 일정 {len(db.get_events())}개 추가됨")

    # Dynamic Agent 생성
    print("\n1️⃣  Dynamic Agent 생성...")
    agent = ScheduleManagerAgent()
    print("   ✅ Agent 준비 완료")

    # 테스트
    print("\n" + "=" * 80)
    print("  📝 시나리오 1: 일정 생성")
    print("=" * 80)
    response = agent.chat("내일 오후 2시에 팀 회의 일정 잡아줘")
    print(f"\n응답: {response}")

    print("\n" + "=" * 80)
    print("  📝 시나리오 2: 조회만")
    print("=" * 80)
    response = agent.chat("내 일정 보여줘")
    print(f"\n응답: {response}")

    print("\n✨ 완료!")


if __name__ == "__main__":
    main()

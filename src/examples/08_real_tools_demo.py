"""
Real Tools Demo - 실제 Tool로 동작하는 Executor

이제 Mock이 아니라 진짜로 작동합니다!

🎯 목표:
- parse_event_info: LLM으로 자연어 파싱
- get_calendar_events: DB에서 실제 일정 조회
- find_free_time: 실제 빈 시간 계산
- create_event: DB에 실제 저장
- send_notification: 알림 전송

실행:
    uv run python -m src.examples.08_real_tools_demo
"""

from multi_agent_lab.domains.personal_assistant.tools.schedule_tools import (
    create_event,
    find_free_time,
    get_calendar_events,
    parse_event_info,
    send_notification,
)

from multi_agent_lab.domains.personal_assistant.storage import db
from multi_agent_lab.platform.skill_card import SkillCardExecutor, SkillCardManager


def main():
    print("=" * 80)
    print("  🚀 Real Tools Demo - LLM이 실제로 작동합니다!")
    print("=" * 80)

    # 0. DB 초기화 (깨끗한 상태에서 시작)
    print("\n0️⃣  DB 초기화...")
    db.clear()

    # 기존 일정 몇 개 추가 (충돌 테스트용)
    db.add_event(
        {
            "title": "기존 회의",
            "start_time": "2025-11-13 10:00",
            "end_time": "2025-11-13 11:00",
            "duration": 60,
        }
    )
    db.add_event(
        {
            "title": "점심 약속",
            "start_time": "2025-11-13 12:00",
            "end_time": "2025-11-13 13:00",
            "duration": 60,
        }
    )
    print(f"   ✅ 기존 일정 {len(db.get_events())}개 추가됨")

    # 1. Skill Card 로드
    print("\n1️⃣  Skill Card 로드...")
    manager = SkillCardManager()
    card = manager.get("SC_SCHEDULE_001")
    print(f"   ✅ {card.agent_name}")

    # 2. Executor 생성 (verbose=True로 디버깅 활성화)
    print("\n2️⃣  Executor 생성 및 Tool 등록...")
    executor = SkillCardExecutor(card, verbose=True)

    # 3. ⭐ Real Tools 등록! (이게 핵심!)
    executor.register_tool("parse_event_info", parse_event_info)
    executor.register_tool("get_calendar_events", get_calendar_events)
    executor.register_tool("find_free_time", find_free_time)
    executor.register_tool("create_event", create_event)
    executor.register_tool("send_notification", send_notification)

    # 4. 실행!
    print("\n3️⃣  사용자 질의 실행!")
    print("-" * 80)

    user_query = "내일 오후 2시에 팀 회의 일정 잡아줘"
    print(f"\n사용자: {user_query}")

    try:
        result = executor.execute(
            user_query=user_query,
            context={
                "user_id": "user_12345",
                "conversation_history": [],
            },
        )

        # 5. 결과 출력
        print("\n" + "=" * 80)
        print("  ✅ 실행 완료!")
        print("=" * 80)

        print(f"\n성공: {result['success']}")

        print("\n📦 저장된 변수:")
        for key, value in result["variables"].items():
            if key not in ["user_query", "user_id", "conversation_history"]:
                print(f"  • {key}:")
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"      - {k}: {v}")
                elif isinstance(value, list):
                    print(f"      {len(value)}개 항목")
                else:
                    print(f"      {value}")

        print("\n📊 Step 실행 결과:")
        for step_result in result["step_results"]:
            status = "✅" if step_result["error"] is None else "❌"
            print(f"  {status} Step {step_result['step']}: {step_result['action']}")

        # 6. 실제 DB 확인
        print("\n" + "=" * 80)
        print("  📅 실제 DB 확인")
        print("=" * 80)

        all_events = db.get_events()
        print(f"\n총 일정: {len(all_events)}개")
        for event in all_events:
            print(
                f"  • {event['id']}: {event['title']} ({event['start_time']} ~ {event['end_time']})"
            )

    except Exception as e:
        print(f"\n❌ 실행 실패: {e}")
        import traceback

        traceback.print_exc()

    # 7. 핵심 설명
    print("\n" + "=" * 80)
    print("  💡 여기서 일어난 일")
    print("=" * 80)
    print(
        """
  1️⃣  Step 1: parse_event_info (⭐ LLM 사용!)
     - 입력: "내일 오후 2시에 팀 회의 일정 잡아줘"
     - LLM이 분석: "내일" = 2025-11-13, "오후 2시" = 14:00
     - 출력: {title: "팀 회의", date: "2025-11-13", time: "14:00", ...}
     - 💾 변수 저장!

  2️⃣  Step 2: get_calendar_events (⭐ DB 조회!)
     - 입력: date = "2025-11-13" (Step 1의 결과)
     - DB에서 실제 조회
     - 출력: 기존 일정 2개 발견

  3️⃣  Step 3: find_free_time (⭐ 실제 로직!)
     - 입력: 기존 일정 목록 + 필요 시간
     - 빈 시간 계산: 10:00-11:00 제외, 12:00-13:00 제외
     - 출력: 14:00-15:00 가능!

  4️⃣  Step 4: create_event (⭐ DB 저장!)
     - 입력: title="팀 회의", start_time="2025-11-13 14:00"
     - DB에 실제 저장!
     - 출력: {id: "EVT003", success: True}

  5️⃣  Step 5: send_notification (⭐ 알림!)
     - 입력: 생성된 일정 정보
     - 콘솔에 알림 출력
     - 나중에 실제 푸시 알림으로 확장 가능

  🎉 결과: 진짜로 캘린더에 일정이 생성됨!
    """
    )

    print("=" * 80)
    print("  ✨ 데모 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

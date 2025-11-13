"""
일정 관리 Agent 사용 예제
"""

from multi_agent_lab.domains.personal_assistant.agents.schedule_manager import (
    ScheduleManagerAgent,
)


def main():
    """ScheduleManagerAgent 예제"""
    print("=" * 60)
    print("일정 관리 Agent 데모")
    print("=" * 60)
    print()

    # Agent 생성
    agent = ScheduleManagerAgent()

    # 테스트 질의들
    queries = [
        "2025년 11월 15일 오후 2시에 팀 회의 일정 잡아줘. 회의실 A에서 1시간 동안 해.",
        "2025년 11월 15일 일정 보여줘",
        "2025년 11월 15일에 1시간 회의 잡을 수 있는 시간대 알려줘",
        "2025년 11월 16일 오전 10시에 고객 미팅 일정 추가해줘",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"[질문 {i}] {query}")
        print(f"{'=' * 60}")

        try:
            response = agent.chat(query)
            print(f"\n[답변]\n{response}")
        except Exception as e:
            print(f"\n[오류] {e}")

        print()

    print("=" * 60)
    print("데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

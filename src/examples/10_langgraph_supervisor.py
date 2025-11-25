"""
LangGraph Supervisor Demo - Multi-Agent 라우팅

🎯 목표:
- LangGraph StateGraph를 사용한 Supervisor 패턴 학습
- Supervisor가 질문을 분석하여 적절한 Agent 선택
- Schedule 관련 → ScheduleAgent
- Todo 관련 → TodoAgent

📚 LangGraph 핵심 개념:
- StateGraph: 상태 기반 그래프
- Node: 작업 단위 (함수)
- Edge: Node 간 연결
- Conditional Edge: 조건부 분기
- Compile: 실행 가능한 앱으로 변환

아키텍처:
    User Query → Supervisor (Router) → [ScheduleAgent | TodoAgent | Fallback]

실행:
    uv run python -m src.examples.10_langgraph_supervisor
"""

from multi_agent_lab.domains.personal_assistant.agents import (
    PersonalAssistantSupervisor,
)
from multi_agent_lab.domains.personal_assistant.storage import db


def main():
    print("=" * 80)
    print("  🤖 LangGraph Supervisor - Multi-Agent 라우팅 데모")
    print("=" * 80)

    # ==========================================================================
    # 0️⃣ DB 초기화
    # ==========================================================================
    print("\n0️⃣  DB 초기화...")
    db.clear()

    # 기존 일정 추가
    db.add_event(
        {
            "title": "기존 회의",
            "start_time": "2025-11-15 10:00",
            "end_time": "2025-11-15 11:00",
            "duration": 60,
        }
    )
    print(f"   ✅ 기존 일정 {len(db.get_events())}개 추가됨")

    # 기존 할일 추가
    db.add_task(
        {
            "title": "보고서 작성",
            "priority": "high",
            "completed": False,
        }
    )
    print(f"   ✅ 기존 할일 {len(db.get_tasks())}개 추가됨")

    # ==========================================================================
    # 1️⃣ Supervisor 생성
    # ==========================================================================
    print("\n1️⃣  Supervisor 생성...")
    supervisor = PersonalAssistantSupervisor(verbose=True)

    print("\n" + "=" * 60)
    print(supervisor.get_mermaid())
    print(supervisor.save_graph_image())
    print("\n" + "=" * 60)

    print("   ✅ PersonalAssistantSupervisor 준비 완료")

    # ==========================================================================
    # 2️⃣ 테스트 시나리오
    # ==========================================================================
    test_scenarios = [
        # (카테고리, 예상 Agent, 질문)
        ("📅 일정 생성", "schedule", "내일 오후 2시에 팀 회의 잡아줘"),
        ("✅ 할일 추가", "todo", "장보기 할일 추가해줘"),
        ("📅 일정 조회", "schedule", "내 일정 보여줘"),
        ("✅ 할일 조회", "todo", "오늘 할일 목록 알려줘"),
        ("❓ 알 수 없음", "unknown", "오늘 날씨 어때?"),
    ]

    print("\n" + "=" * 80)
    print("  📝 테스트 시나리오 실행")
    print("=" * 80)

    for i, (category, expected, query) in enumerate(test_scenarios, 1):
        print(f"\n{'─' * 80}")
        print(f"  시나리오 {i}: {category}")
        print(f"  예상 Agent: {expected}")
        print(f"  질문: {query}")
        print(f"{'─' * 80}")

        response = supervisor.chat(query)

        print("\n📤 응답:")
        print(f"   {response}")

    # ==========================================================================
    # 3️⃣ 최종 상태 확인
    # ==========================================================================
    print("\n" + "=" * 80)
    print("  📊 최종 DB 상태")
    print("=" * 80)

    events = db.get_events()
    tasks = db.get_tasks()

    print(f"\n📅 일정 ({len(events)}개):")
    for event in events:
        print(f"   - {event.get('title')} @ {event.get('start_time')}")

    print(f"\n✅ 할일 ({len(tasks)}개):")
    for task in tasks:
        status = "✓" if task.get("completed") else "○"
        print(f"   {status} [{task.get('priority', 'medium')}] {task.get('title')}")

    print("\n" + "=" * 80)
    print("  ✨ 데모 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

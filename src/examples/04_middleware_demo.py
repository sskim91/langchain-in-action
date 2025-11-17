"""
Middleware 데모

📌 목적:
- PII 탐지/마스킹 + 감사 로깅 Middleware 테스트
- 금융권 필수 기능 미리 체험

🧪 테스트 시나리오:
1. Middleware 단독 테스트
2. Agent + Middleware 통합 테스트
"""

from multi_agent_lab.core.middleware import (
    AuditLoggingMiddleware,
    PIIDetectionMiddleware,
)


def test_middleware_standalone():
    """Middleware 단독 테스트"""
    print("\n" + "=" * 70)
    print("🧪 Test 1: Middleware 단독 테스트")
    print("=" * 70)

    # PII Detection Middleware
    pii_middleware = PIIDetectionMiddleware(patterns=["phone", "email", "ssn", "card"])

    # 테스트 케이스
    test_cases = [
        "홍길동(010-1234-5678) 연락처",
        "이메일: user@example.com",
        "주민번호: 123456-1234567",
        "카드번호: 1234-5678-9012-3456",
        "홍길동(010-1234-5678, user@example.com) 정보",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n[Case {i}]")
        print(f"입력:  {text}")

        masked = pii_middleware.before_request(text)
        print(f"마스킹: {masked}")

        # 탐지 요약
        if pii_middleware.detections:
            print(f"탐지: {pii_middleware.get_detection_summary()}")

    # Audit Logging Middleware
    print("\n" + "-" * 70)
    print("📝 Audit Logging 테스트")
    print("-" * 70)

    audit_middleware = AuditLoggingMiddleware(log_dir="logs", log_file="demo_audit.log")

    # 요청/응답 로깅
    audit_middleware.before_request("테스트 입력", user_id="demo_user", action="test")
    audit_middleware.after_response("테스트 응답")

    # 세션 요약
    summary = audit_middleware.get_session_summary()
    print("\n세션 요약:")
    print(f"  - Session ID: {summary['session_id']}")
    print(f"  - Total Requests: {summary['total_requests']}")
    print(f"  - Log File: {summary['log_file']}")


def test_agent_with_middleware():
    """Agent + Middleware 통합 테스트"""
    print("\n" + "=" * 70)
    print("🤖 Test 2: Agent + Middleware 통합 테스트")
    print("=" * 70)

    from multi_agent_lab.domains.personal_assistant.agents.schedule_manager import (
        ScheduleManagerAgent,
    )
    from multi_agent_lab.domains.personal_assistant.storage.memory_db import db

    # DB 초기화
    db.clear()

    # Middleware 설정
    middleware = [
        PIIDetectionMiddleware(patterns=["phone", "email"]),
        AuditLoggingMiddleware(log_dir="logs", log_file="agent_audit.log"),
    ]

    # Agent 생성 (Middleware 포함)
    agent = ScheduleManagerAgent(middleware=middleware)

    # 테스트 질의 (PII 포함)
    test_queries = [
        "홍길동(010-1234-5678) 님의 일정을 2025년 11월 15일 오후 2시에 추가해줘",
        "user@example.com으로 일정 알림 보내줘",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[질문 {i}]")
        print(f"입력: {query}")
        print("\n처리 중...")

        try:
            # Agent 실행 (Middleware가 자동으로 적용됨)
            response = agent.chat(query, user_id=f"user_{i}", action="create_event")
            print(f"\n응답: {response}")
        except Exception as e:
            print(f"\n오류: {e}")

    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("=" * 70)


if __name__ == "__main__":
    # 1. Middleware 단독 테스트
    test_middleware_standalone()

    # 2. Agent + Middleware 통합 테스트 (Ollama 필요)
    print("\n" + "=" * 70)
    print("⚠️  Agent 테스트는 Ollama가 실행 중이어야 합니다.")
    print("    계속하시겠습니까? (y/n): ", end="")

    answer = input().strip().lower()
    if answer == "y":
        test_agent_with_middleware()
    else:
        print("Agent 테스트를 건너뜁니다.")

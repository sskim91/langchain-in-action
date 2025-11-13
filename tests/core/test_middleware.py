"""
Middleware 테스트
"""

# conftest.py가 자동으로 sys.path를 설정하므로 제거
from multi_agent_lab.core.middleware import (
    AuditLoggingMiddleware,
    PIIDetectionMiddleware,
)


def test_pii_phone_masking():
    """전화번호 마스킹 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["phone"])

    input_text = "홍길동(010-1234-5678) 연락처입니다"
    result = middleware.before_request(input_text)

    assert "010-****-5678" in result
    assert "010-1234-5678" not in result


def test_pii_email_masking():
    """이메일 마스킹 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["email"])

    input_text = "이메일은 user@example.com 입니다"
    result = middleware.before_request(input_text)

    assert "u***@example.com" in result
    assert "user@example.com" not in result


def test_pii_ssn_masking():
    """주민번호 마스킹 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["ssn"])

    input_text = "주민번호: 123456-1234567"
    result = middleware.before_request(input_text)

    assert "******-*******" in result
    assert "123456-1234567" not in result


def test_pii_card_masking():
    """카드번호 마스킹 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["card"])

    input_text = "카드번호: 1234-5678-9012-3456"
    result = middleware.before_request(input_text)

    assert "****-****-****-3456" in result
    assert "1234-5678-9012-3456" not in result


def test_pii_multiple_detection():
    """여러 PII 동시 탐지 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["phone", "email"])

    input_text = "홍길동(010-1234-5678) user@example.com"
    result = middleware.before_request(input_text)

    assert "010-****-5678" in result
    assert "u***@example.com" in result
    assert len(middleware.detections) == 2


def test_pii_redact_action():
    """Redact 액션 테스트"""
    middleware = PIIDetectionMiddleware(patterns=["phone"], action="redact")

    input_text = "전화번호: 010-1234-5678"
    result = middleware.before_request(input_text)

    assert "[REDACTED_PHONE]" in result


def test_audit_logging_creates_log():
    """감사 로깅 파일 생성 테스트"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        middleware = AuditLoggingMiddleware(log_dir=tmpdir, log_file="test_audit.log")

        # Before request
        middleware.before_request("테스트 입력", user_id="test_user")

        # After response
        middleware.after_response("테스트 응답")

        # 로그 파일 생성 확인
        log_files = list(Path(tmpdir).glob("*.log"))
        assert len(log_files) > 0


def test_audit_logging_session_summary():
    """감사 로깅 세션 요약 테스트"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        middleware = AuditLoggingMiddleware(log_dir=tmpdir)

        # 여러 요청 처리
        for i in range(3):
            middleware.before_request(f"요청 {i}")
            middleware.after_response(f"응답 {i}")

        # 세션 요약
        summary = middleware.get_session_summary()
        assert summary["total_requests"] == 3
        assert "session_id" in summary

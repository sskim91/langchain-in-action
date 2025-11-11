"""
Audit Logging Middleware (감사 로깅)

📌 목적:
- 모든 Agent 요청/응답 기록
- 금융권 규정 준수 (감사 증적)
- 문제 발생 시 추적 가능

📝 기록 내용:
- 타임스탬프
- 사용자 입력
- Agent 응답
- 실행 시간
- 에러 발생 여부

💾 저장 방식:
- JSON Lines 형식 (각 줄이 하나의 로그)
- 파일 로테이션 (날짜별 분리)

💡 금융권 활용:
- 모든 거래 내역 추적
- 부정 거래 분석
- 컴플라이언스 보고서 생성
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from core.middleware.base import BaseMiddleware


class AuditLoggingMiddleware(BaseMiddleware):
    """감사 로깅 Middleware"""

    def __init__(
        self,
        log_dir: str = "logs",
        log_file: str = "audit.log",
        include_pii: bool = False,
    ):
        """
        Args:
            log_dir: 로그 파일 디렉토리
            log_file: 로그 파일명
            include_pii: PII 포함 여부 (False 권장)
        """
        super().__init__(name="Audit Logging")
        self.log_dir = Path(log_dir)
        self.log_file = log_file
        self.include_pii = include_pii

        # 로그 디렉토리 생성
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 현재 세션 정보
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.request_count = 0

        # 로깅 설정
        self._setup_logger()

    def _setup_logger(self):
        """로거 설정"""
        self.logger = logging.getLogger(f"audit.{self.session_id}")
        self.logger.setLevel(logging.INFO)

        # 파일 핸들러
        log_path = (
            self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{self.log_file}"
        )
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setLevel(logging.INFO)

        # JSON 형식 포맷터
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # 콘솔에도 출력 (옵션)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        self.logger.addHandler(console_handler)

    def before_request(self, input_text: str, **kwargs) -> str:
        """요청 전 로그 기록 시작"""
        self.request_count += 1

        # 요청 메타데이터 저장 (임시)
        self._current_request = {
            "request_id": f"{self.session_id}_{self.request_count:04d}",
            "timestamp": datetime.now().isoformat(),
            "input": input_text if self.include_pii else self._sanitize(input_text),
            "user_id": kwargs.get("user_id", "unknown"),
            "action": kwargs.get("action", "unknown"),
        }

        print(f"📝 [Audit] Request #{self.request_count} logged")

        return input_text

    def after_response(self, output_text: str, **kwargs) -> str:
        """응답 후 로그 기록 완료"""
        if not hasattr(self, "_current_request"):
            return output_text

        # 로그 엔트리 완성
        log_entry = {
            **self._current_request,
            "output": output_text if self.include_pii else self._sanitize(output_text),
            "completed_at": datetime.now().isoformat(),
            "duration_ms": self._calculate_duration(),
            "status": "success",
            "tool_calls": kwargs.get("tool_calls", []),
        }

        # JSON Lines 형식으로 기록
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

        return output_text

    def on_error(self, error: Exception, **kwargs) -> None:
        """에러 발생 시 로그 기록"""
        if not hasattr(self, "_current_request"):
            return

        log_entry = {
            **self._current_request,
            "error": str(error),
            "error_type": type(error).__name__,
            "completed_at": datetime.now().isoformat(),
            "duration_ms": self._calculate_duration(),
            "status": "error",
        }

        self.logger.error(json.dumps(log_entry, ensure_ascii=False))
        print(f"❌ [Audit] Request #{self.request_count} failed: {error}")

    def _calculate_duration(self) -> int:
        """실행 시간 계산 (밀리초)"""
        if not hasattr(self, "_current_request"):
            return 0

        start_time = datetime.fromisoformat(self._current_request["timestamp"])
        end_time = datetime.now()
        return int((end_time - start_time).total_seconds() * 1000)

    def _sanitize(self, text: str) -> str:
        """민감정보 제거 (간단한 버전)"""
        # PII Middleware가 이미 처리했다면 그대로 사용
        # 추가적인 sanitization이 필요하면 여기서 처리
        return text[:200] + "..." if len(text) > 200 else text

    def get_session_summary(self) -> dict[str, Any]:
        """현재 세션 요약"""
        return {
            "session_id": self.session_id,
            "total_requests": self.request_count,
            "log_file": str(
                self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{self.log_file}"
            ),
        }

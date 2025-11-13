"""
PII Detection Middleware (개인정보 탐지 및 마스킹)

📌 목적:
- 개인정보(PII) 자동 탐지 및 마스킹
- 금융권 규정 준수 (개인정보보호법)

🔍 탐지 대상:
- 전화번호: 010-1234-5678 → 010-****-5678
- 이메일: user@example.com → u***@example.com
- 주민번호: 123456-1234567 → ******-*******
- 카드번호: 1234-5678-9012-3456 → ****-****-****-3456
- 계좌번호: 110-123-456789 → ***-***-****89

💡 마스킹 전략:
- phone: 중간 4자리 마스킹
- email: 앞 2자 제외 마스킹
- ssn: 전체 마스킹
- card: 마지막 4자리만 노출
- account: 마지막 2자리만 노출
"""

import re
from typing import ClassVar

from multi_agent_lab.core.middleware.base import BaseMiddleware


class PIIDetectionMiddleware(BaseMiddleware):
    """개인정보 탐지 및 마스킹 Middleware"""

    # PII 패턴 정의
    PII_PATTERNS: ClassVar[dict[str, str]] = {
        "phone": r"(01[0-9])-?([0-9]{3,4})-?([0-9]{4})",
        "email": r"([a-zA-Z0-9._%+-]{2,})@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        "ssn": r"(\d{6})-?(\d{7})",
        "card": r"(\d{4})-?(\d{4})-?(\d{4})-?(\d{4})",
        "account": r"(\d{2,3})-?(\d{2,3})-?(\d{4,6})",
    }

    def __init__(
        self,
        patterns: list[str] | None = None,
        action: str = "mask",
    ):
        """
        Args:
            patterns: 탐지할 PII 유형 리스트 (기본: 모두)
            action: 처리 방식 ("mask", "redact", "block")
        """
        super().__init__(name="PII Detection")
        self.patterns = patterns or list(self.PII_PATTERNS.keys())
        self.action = action
        self.detections: list[dict] = []  # 탐지 기록

    def before_request(self, input_text: str, **kwargs) -> str:
        """요청 전 PII 마스킹"""
        self.detections = []
        masked_text = input_text

        for pii_type in self.patterns:
            if pii_type in self.PII_PATTERNS:
                masked_text = self._mask_pii(masked_text, pii_type)

        if self.detections:
            print(
                f"⚠️  [PII Detected] {len(self.detections)}건의 개인정보가 감지되었습니다."
            )
            for detection in self.detections:
                print(
                    f"   - {detection['type']}: {detection['original']} → {detection['masked']}"
                )

        return masked_text

    def after_response(self, output_text: str, **kwargs) -> str:
        """응답 후 PII 마스킹 (응답에도 민감정보가 있을 수 있음)"""
        masked_text = output_text

        for pii_type in self.patterns:
            if pii_type in self.PII_PATTERNS:
                masked_text = self._mask_pii(masked_text, pii_type, log=False)

        return masked_text

    def _mask_pii(self, text: str, pii_type: str, log: bool = True) -> str:
        """PII 타입별 마스킹"""
        pattern = self.PII_PATTERNS[pii_type]

        def replace_match(match):
            original = match.group(0)
            masked = self._get_masked_value(match, pii_type)

            if log and original != masked:
                self.detections.append(
                    {"type": pii_type, "original": original, "masked": masked}
                )

            return masked

        return re.sub(pattern, replace_match, text)

    def _get_masked_value(self, match, pii_type: str) -> str:
        """PII 타입별 마스킹 규칙"""
        if self.action == "redact":
            return f"[REDACTED_{pii_type.upper()}]"

        if self.action == "block":
            raise ValueError(f"개인정보({pii_type})가 포함되어 있습니다.")

        # action == "mask"
        if pii_type == "phone":
            # 010-1234-5678 → 010-****-5678
            return f"{match.group(1)}-****-{match.group(3)}"

        elif pii_type == "email":
            # user@example.com → u***@example.com
            username = match.group(1)
            domain = match.group(2)
            masked_user = username[0] + "*" * (len(username) - 1)
            return f"{masked_user}@{domain}"

        elif pii_type == "ssn":
            # 123456-1234567 → ******-*******
            return "******-*******"

        elif pii_type == "card":
            # 1234-5678-9012-3456 → ****-****-****-3456
            return f"****-****-****-{match.group(4)}"

        elif pii_type == "account":
            # 110-123-456789 → ***-***-****89
            account_num = match.group(3)
            return f"***-***-{'*' * (len(account_num) - 2)}{account_num[-2:]}"

        return match.group(0)

    def get_detection_summary(self) -> dict:
        """탐지 요약 정보"""
        summary = {}
        for detection in self.detections:
            pii_type = detection["type"]
            summary[pii_type] = summary.get(pii_type, 0) + 1
        return summary

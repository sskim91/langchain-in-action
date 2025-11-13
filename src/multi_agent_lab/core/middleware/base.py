"""
Base Middleware (미들웨어 기본 클래스)

📌 목적:
- 모든 Middleware의 기본 틀 제공
- Agent 실행 전후에 공통 작업 수행

🔄 실행 흐름:
- before_request: Agent 실행 전 (입력 전처리)
- after_response: Agent 실행 후 (출력 후처리)
- on_error: 에러 발생 시

💡 사용 방식:
- 이 클래스를 상속받아 custom middleware 구현
- 예: PIIDetectionMiddleware, AuditLoggingMiddleware
"""

from abc import ABC, abstractmethod


class BaseMiddleware(ABC):
    """Middleware 기본 인터페이스"""

    def __init__(self, name: str):
        """
        Args:
            name: Middleware 이름 (로깅용)
        """
        self.name = name

    @abstractmethod
    def before_request(self, input_text: str, **kwargs) -> str:
        """
        Agent 실행 전 호출

        Args:
            input_text: 사용자 입력
            **kwargs: 추가 컨텍스트

        Returns:
            str: 전처리된 입력
        """
        pass

    @abstractmethod
    def after_response(self, output_text: str, **kwargs) -> str:
        """
        Agent 실행 후 호출

        Args:
            output_text: Agent 응답
            **kwargs: 추가 컨텍스트

        Returns:
            str: 후처리된 응답
        """
        pass

    def on_error(self, error: Exception, **kwargs) -> None:
        """
        에러 발생 시 호출 (기본 구현: 에러 로깅)

        Args:
            error: 발생한 예외
            **kwargs: 추가 컨텍스트
        """
        # 기본 구현: 에러 정보 출력 (서브클래스에서 오버라이드 가능)
        print(f"[{self.name}] Error: {error}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"

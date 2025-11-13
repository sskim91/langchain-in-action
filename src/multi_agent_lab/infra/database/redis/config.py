"""Redis Configuration

환경 변수 또는 직접 설정으로 Redis 연결 정보 관리
"""

import os
from dataclasses import dataclass


@dataclass
class RedisConfig:
    """Redis 연결 설정"""

    host: str
    port: int = 6379
    db: int = 0
    password: str | None = None
    username: str | None = None
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    decode_responses: bool = True
    ssl: bool = False
    ssl_cert_reqs: str = "required"

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """
        환경 변수에서 설정 로드

        환경 변수:
            REDIS_HOST: Redis 호스트 (필수)
            REDIS_PORT: 포트 (기본값: 6379)
            REDIS_DB: 데이터베이스 번호 (기본값: 0)
            REDIS_PASSWORD: 비밀번호
            REDIS_USERNAME: 사용자명 (Redis 6.0+)
            REDIS_SOCKET_TIMEOUT: 소켓 타임아웃 (기본값: 5.0초)
            REDIS_SSL: SSL 사용 여부 (기본값: false)

        Returns:
            RedisConfig 인스턴스
        """
        host = os.getenv("REDIS_HOST")
        if not host:
            raise ValueError("REDIS_HOST environment variable is required")

        return cls(
            host=host,
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            username=os.getenv("REDIS_USERNAME"),
            socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
            socket_connect_timeout=float(
                os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5.0")
            ),
            decode_responses=os.getenv("REDIS_DECODE_RESPONSES", "true").lower()
            == "true",
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
        )

    def to_dict(self) -> dict:
        """
        Redis 클라이언트에 전달할 딕셔너리 형태로 변환

        Returns:
            redis.Redis() 생성자에 전달할 설정 딕셔너리
        """
        config = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "decode_responses": self.decode_responses,
        }

        # 인증 설정
        if self.password:
            config["password"] = self.password
        if self.username:
            config["username"] = self.username

        # SSL 설정
        if self.ssl:
            config["ssl"] = True
            config["ssl_cert_reqs"] = self.ssl_cert_reqs

        return config

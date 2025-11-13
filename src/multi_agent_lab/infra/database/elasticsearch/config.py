"""Elasticsearch Configuration

환경 변수 또는 직접 설정으로 Elasticsearch 연결 정보 관리
"""

import os
from dataclasses import dataclass


@dataclass
class ElasticsearchConfig:
    """Elasticsearch 연결 설정"""

    host: str
    port: int = 9200
    scheme: str = "https"
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    verify_certs: bool = True
    ca_certs: str | None = None

    @classmethod
    def from_env(cls) -> "ElasticsearchConfig":
        """
        환경 변수에서 설정 로드

        환경 변수:
            ES_HOST: Elasticsearch 호스트 (필수)
            ES_PORT: 포트 (기본값: 9200)
            ES_SCHEME: http 또는 https (기본값: https)
            ES_USERNAME: 사용자명
            ES_PASSWORD: 비밀번호
            ES_API_KEY: API 키 (username/password 대신 사용 가능)
            ES_VERIFY_CERTS: 인증서 검증 여부 (기본값: true)
            ES_CA_CERTS: CA 인증서 파일 경로

        Returns:
            ElasticsearchConfig 인스턴스
        """
        host = os.getenv("ES_HOST")
        if not host:
            raise ValueError("ES_HOST environment variable is required")

        return cls(
            host=host,
            port=int(os.getenv("ES_PORT", "9200")),
            scheme=os.getenv("ES_SCHEME", "https"),
            username=os.getenv("ES_USERNAME"),
            password=os.getenv("ES_PASSWORD"),
            api_key=os.getenv("ES_API_KEY"),
            verify_certs=os.getenv("ES_VERIFY_CERTS", "true").lower() == "true",
            ca_certs=os.getenv("ES_CA_CERTS"),
        )

    def to_dict(self) -> dict:
        """
        Elasticsearch 클라이언트에 전달할 딕셔너리 형태로 변환

        Returns:
            Elasticsearch() 생성자에 전달할 설정 딕셔너리
        """
        config = {
            "hosts": [f"{self.scheme}://{self.host}:{self.port}"],
            "verify_certs": self.verify_certs,
        }

        # CA 인증서 사용 시 호스트 이름 검증 비활성화 (개발 환경)
        if self.ca_certs:
            config["ca_certs"] = self.ca_certs
            config["ssl_assert_hostname"] = False  # IP 주소 사용 시 필요
            config["ssl_show_warn"] = False  # 경고 메시지 억제

        # 인증 설정
        if self.api_key:
            config["api_key"] = self.api_key
        elif self.username and self.password:
            config["basic_auth"] = (self.username, self.password)

        return config

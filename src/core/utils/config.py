"""
설정 관리 유틸리티
"""

import os


def load_config(config_file: str = ".env") -> dict[str, str]:
    """
    설정 파일 로드

    Args:
        config_file: 설정 파일 경로

    Returns:
        설정 딕셔너리
    """
    config = {}

    if os.path.exists(config_file):
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

    return config


def get_default_model() -> str:
    """
    기본 모델명 반환

    환경변수 또는 기본값 사용

    Returns:
        모델명
    """
    return os.getenv("OLLAMA_MODEL", "gpt-oss:20b")


def get_model_config(model_name: str | None = None) -> dict:
    """
    모델별 권장 설정 반환

    Args:
        model_name: 모델명 (None이면 기본 모델)

    Returns:
        모델 설정 딕셔너리
    """
    model_name = model_name or get_default_model()

    # 모델별 권장 설정
    configs = {
        "gpt-oss:20b": {
            "temperature": 0.1,
            "num_predict": 256,
            "top_k": 10,
            "top_p": 0.9,
        },
        "llama3.2:3b": {
            "temperature": 0.3,
            "num_predict": 512,
            "top_k": 20,
            "top_p": 0.95,
        },
        "mistral:7b": {
            "temperature": 0.2,
            "num_predict": 512,
            "top_k": 15,
            "top_p": 0.92,
        },
    }

    return configs.get(model_name, configs["gpt-oss:20b"])

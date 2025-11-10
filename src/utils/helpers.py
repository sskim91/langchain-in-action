"""
헬퍼 함수들

텍스트 처리, 응답 포맷팅 등 유틸리티 함수를 제공합니다.
"""

from typing import Any


def clean_text(text: str) -> str:
    """
    텍스트에서 잘못된 유니코드 문자 제거

    Args:
        text: 정리할 텍스트

    Returns:
        정리된 텍스트
    """
    try:
        # UTF-8 surrogate 문자 제거
        return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        return text


def format_response(response: dict[str, Any]) -> str:
    """
    Agent 응답을 포맷팅

    Args:
        response: Agent invoke 결과

    Returns:
        포맷팅된 응답 텍스트
    """
    if "messages" in response:
        last_message = response["messages"][-1]
        return clean_text(last_message.content)
    return str(response)


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    텍스트를 지정된 길이로 자르기

    Args:
        text: 자를 텍스트
        max_length: 최대 길이

    Returns:
        잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."

"""
기본 도구들

수학 계산, 문자열 처리 등 기본적인 도구를 제공합니다.
"""

from datetime import datetime

from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    수식을 계산합니다.

    Args:
        expression: 계산할 수식 (예: "2 + 2", "10 * 5")

    Returns:
        계산 결과

    Example:
        >>> calculator("2 + 2")
        "계산 결과: 4"
    """
    try:
        result = eval(expression)
        return f"계산 결과: {result}"
    except Exception as e:
        return f"계산 오류: {e!s}"


@tool
def get_word_length(word: str) -> str:
    """
    단어의 길이를 반환합니다.

    Args:
        word: 길이를 확인할 단어

    Returns:
        단어 길이

    Example:
        >>> get_word_length("Hello")
        "'Hello'의 길이는 5글자입니다."
    """
    return f"'{word}'의 길이는 {len(word)}글자입니다."


@tool
def get_current_time() -> str:
    """
    현재 시간을 반환합니다.

    Returns:
        현재 시간 문자열

    Example:
        >>> get_current_time()
        "현재 시간: 2025-11-07 16:30:00"
    """
    now = datetime.now()
    return f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}"

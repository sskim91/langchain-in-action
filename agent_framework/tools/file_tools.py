"""
파일 관련 도구들

파일 읽기, 쓰기, 목록 조회 등의 기능을 제공합니다.
"""

import os
from pathlib import Path

from langchain_core.tools import tool


@tool
def read_file(filepath: str) -> str:
    """
    파일의 내용을 읽습니다.

    Args:
        filepath: 읽을 파일 경로

    Returns:
        파일 내용

    Example:
        >>> read_file("README.md")
        "# Project Title\\n\\nDescription..."
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"파일 '{filepath}' 내용:\n\n{content}"
    except FileNotFoundError:
        return f"오류: 파일 '{filepath}'을(를) 찾을 수 없습니다."
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"


@tool
def write_file(filepath: str, content: str) -> str:
    """
    파일에 내용을 씁니다.

    Args:
        filepath: 저장할 파일 경로
        content: 저장할 내용

    Returns:
        작업 결과 메시지

    Example:
        >>> write_file("output.txt", "Hello World")
        "파일 'output.txt'에 저장되었습니다."
    """
    try:
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"파일 '{filepath}'에 저장되었습니다."
    except Exception as e:
        return f"파일 쓰기 오류: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """
    디렉토리의 파일 목록을 조회합니다.

    Args:
        directory: 조회할 디렉토리 경로 (기본값: 현재 디렉토리)

    Returns:
        파일 목록

    Example:
        >>> list_files(".")
        "디렉토리 '.' 파일 목록:\n- file1.txt\n- file2.py\n- folder/"
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"오류: 디렉토리 '{directory}'을(를) 찾을 수 없습니다."

        if not path.is_dir():
            return f"오류: '{directory}'은(는) 디렉토리가 아닙니다."

        files = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                files.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                files.append(f"📄 {item.name} ({size} bytes)")

        file_list = "\n".join(files)
        return f"디렉토리 '{directory}' 파일 목록:\n\n{file_list}"
    except Exception as e:
        return f"디렉토리 조회 오류: {str(e)}"

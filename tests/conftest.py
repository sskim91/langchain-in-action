"""
pytest 설정 파일

PyCharm에서 tests/ 디렉토리에서 실행할 때도
프로젝트 루트를 기준으로 경로를 찾을 수 있게 설정합니다.
"""

import os
import sys
from pathlib import Path


def pytest_configure(config):
    """
    pytest 실행 전 환경 설정

    PyCharm이 tests/ 디렉토리에서 실행하더라도
    working directory를 프로젝트 루트로 변경합니다.
    """
    # 프로젝트 루트 찾기 (pyproject.toml 기준)
    current = Path(__file__).parent  # tests/
    project_root = current.parent  # 프로젝트 루트

    # Working directory를 프로젝트 루트로 변경
    os.chdir(project_root)

    # src/ 경로가 sys.path에 없으면 추가 (이미 editable install로 추가되어 있지만 확실하게)
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    print(f"✓ Working directory: {os.getcwd()}")
    print(f"✓ Project root: {project_root}")

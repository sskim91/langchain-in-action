"""
Core tests configuration
"""

import sys
from pathlib import Path

# Add src to Python path (더 가까운 conftest가 먼저 실행됨)
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

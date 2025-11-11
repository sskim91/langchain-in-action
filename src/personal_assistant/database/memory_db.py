"""
In-memory Database (메모리 데이터베이스)

📌 목적:
- 개발/테스트용 간단한 데이터 저장소
- 실제 DB(SQLite, PostgreSQL) 없이도 동작 가능

💾 저장 방식:
- 메모리(RAM)에 저장 → 프로그램 종료 시 데이터 사라짐
- 개발 초기에는 이걸로 충분, 나중에 실제 DB로 교체

📦 저장 데이터:
- events: 일정 목록
- tasks: 할일 목록
- notes: 메모 목록

💡 싱글톤 패턴:
- db = MemoryDB() → 전체 앱에서 하나의 DB만 사용
"""

from typing import Any


class MemoryDB:
    """간단한 인메모리 데이터베이스"""

    def __init__(self):
        self._events: list[dict[str, Any]] = []
        self._tasks: list[dict[str, Any]] = []
        self._notes: list[dict[str, Any]] = []

    def add_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """일정 추가"""
        event["id"] = f"EVT{len(self._events) + 1:03d}"
        self._events.append(event)
        return event

    def get_events(self) -> list[dict[str, Any]]:
        """모든 일정 조회"""
        return self._events.copy()

    def add_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """할 일 추가"""
        task["id"] = f"TASK{len(self._tasks) + 1:03d}"
        self._tasks.append(task)
        return task

    def get_tasks(self, completed: bool | None = None) -> list[dict[str, Any]]:
        """할 일 조회"""
        if completed is None:
            return self._tasks.copy()
        return [t for t in self._tasks if t.get("completed") == completed]

    def add_note(self, note: dict[str, Any]) -> dict[str, Any]:
        """메모 추가"""
        note["id"] = f"NOTE{len(self._notes) + 1:03d}"
        self._notes.append(note)
        return note

    def search_notes(self, query: str) -> list[dict[str, Any]]:
        """메모 검색 (단순 텍스트 매칭)"""
        query_lower = query.lower()
        return [
            n
            for n in self._notes
            if query_lower in n.get("title", "").lower()
            or query_lower in n.get("content", "").lower()
        ]

    def clear(self):
        """모든 데이터 삭제 (테스트용)"""
        self._events.clear()
        self._tasks.clear()
        self._notes.clear()


# 전역 DB 인스턴스 (싱글톤)
db = MemoryDB()

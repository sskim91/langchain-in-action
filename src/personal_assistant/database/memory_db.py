"""
In-memory database for development and testing
나중에 SQLite나 PostgreSQL로 교체 가능
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

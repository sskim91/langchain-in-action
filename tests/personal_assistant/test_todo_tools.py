"""
Todo Tools 단위 테스트

Ollama 없이 실행 가능한 Tool 레벨 테스트입니다.
"""

import pytest

from multi_agent_lab.domains.personal_assistant.storage.memory_db import db
from multi_agent_lab.domains.personal_assistant.tools.todo_tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
)


@pytest.fixture(autouse=True)
def clear_db():
    """각 테스트 전에 DB 초기화"""
    db.clear()
    yield
    db.clear()


class TestAddTask:
    """add_task Tool 테스트"""

    def test_add_task_basic(self):
        """기본 할일 추가"""
        result = add_task.invoke({"title": "장보기"})

        assert result["success"] is True
        assert result["task"]["title"] == "장보기"
        assert result["task"]["priority"] == "medium"
        assert result["task"]["completed"] is False
        assert "id" in result["task"]

    def test_add_task_with_priority(self):
        """우선순위 지정 할일 추가"""
        result = add_task.invoke({"title": "긴급 작업", "priority": "high"})

        assert result["success"] is True
        assert result["task"]["priority"] == "high"

    def test_add_task_with_due_date(self):
        """마감일 지정 할일 추가"""
        result = add_task.invoke({"title": "보고서 작성", "due_date": "2025-11-20"})

        assert result["success"] is True
        assert result["task"]["due_date"] == "2025-11-20"

    def test_add_task_invalid_priority(self):
        """잘못된 우선순위"""
        result = add_task.invoke({"title": "테스트", "priority": "urgent"})

        assert result["success"] is False
        assert "우선순위" in result["error"]

    def test_add_task_invalid_date_format(self):
        """잘못된 마감일 형식"""
        result = add_task.invoke({"title": "테스트", "due_date": "내일"})

        assert result["success"] is False
        assert "형식" in result["error"]


class TestListTasks:
    """list_tasks Tool 테스트"""

    def test_list_tasks_empty(self):
        """빈 목록 조회"""
        result = list_tasks.invoke({})

        assert result["total"] == 0
        assert result["count"] == 0
        assert result["tasks"] == []

    def test_list_tasks_all(self):
        """전체 할일 조회"""
        add_task.invoke({"title": "할일 1"})
        add_task.invoke({"title": "할일 2"})

        result = list_tasks.invoke({})

        assert result["total"] == 2
        assert result["count"] == 2

    def test_list_tasks_by_status_pending(self):
        """미완료 할일만 조회"""
        add_task.invoke({"title": "미완료"})
        add_task.invoke({"title": "완료됨"})
        complete_task.invoke({"task_id": "TASK002"})

        result = list_tasks.invoke({"status": "pending"})

        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "미완료"

    def test_list_tasks_by_priority(self):
        """우선순위별 조회"""
        add_task.invoke({"title": "낮음", "priority": "low"})
        add_task.invoke({"title": "높음", "priority": "high"})

        result = list_tasks.invoke({"priority": "high"})

        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "높음"

    def test_list_tasks_sorted_by_priority(self):
        """우선순위 순 정렬"""
        add_task.invoke({"title": "낮음", "priority": "low"})
        add_task.invoke({"title": "높음", "priority": "high"})
        add_task.invoke({"title": "중간", "priority": "medium"})

        result = list_tasks.invoke({})

        # high > medium > low 순으로 정렬
        assert result["tasks"][0]["priority"] == "high"
        assert result["tasks"][1]["priority"] == "medium"
        assert result["tasks"][2]["priority"] == "low"


class TestCompleteTask:
    """complete_task Tool 테스트"""

    def test_complete_task_success(self):
        """할일 완료 처리"""
        add_task.invoke({"title": "테스트"})

        result = complete_task.invoke({"task_id": "TASK001"})

        assert result["success"] is True
        assert result["task"]["completed"] is True
        assert "completed_at" in result["task"]

    def test_complete_task_not_found(self):
        """존재하지 않는 할일"""
        result = complete_task.invoke({"task_id": "TASK999"})

        assert result["success"] is False
        assert "찾을 수 없습니다" in result["error"]

    def test_complete_task_already_completed(self):
        """이미 완료된 할일"""
        add_task.invoke({"title": "테스트"})
        complete_task.invoke({"task_id": "TASK001"})

        result = complete_task.invoke({"task_id": "TASK001"})

        assert result["success"] is False
        assert "이미 완료" in result["error"]


class TestDeleteTask:
    """delete_task Tool 테스트"""

    def test_delete_task_success(self):
        """할일 삭제"""
        add_task.invoke({"title": "삭제할 할일"})
        assert len(db.get_tasks()) == 1

        result = delete_task.invoke({"task_id": "TASK001"})

        assert result["success"] is True
        assert len(db.get_tasks()) == 0

    def test_delete_task_not_found(self):
        """존재하지 않는 할일 삭제"""
        result = delete_task.invoke({"task_id": "TASK999"})

        assert result["success"] is False
        assert "찾을 수 없습니다" in result["error"]

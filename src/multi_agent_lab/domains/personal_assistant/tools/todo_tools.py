"""
Todo Tools - 할일 관리 도구

할일 추가, 조회, 완료, 삭제 기능을 제공합니다.

사용 예시:
    from multi_agent_lab.domains.personal_assistant.tools.todo_tools import (
        add_task,
        list_tasks,
        complete_task,
    )

    # 할일 추가
    result = add_task.invoke({"title": "장보기", "priority": "high"})

    # 할일 조회
    tasks = list_tasks.invoke({})

    # 할일 완료
    complete_task.invoke({"task_id": "TASK001"})
"""

from datetime import datetime

from langchain_core.tools import tool

from multi_agent_lab.domains.personal_assistant.storage import db


@tool
def add_task(
    title: str,
    priority: str = "medium",
    due_date: str | None = None,
    description: str | None = None,
) -> dict:
    """
    새로운 할일 추가

    Args:
        title: 할일 제목
        priority: 우선순위 (high, medium, low). 기본값: medium
        due_date: 마감일 (YYYY-MM-DD 형식, 선택)
        description: 상세 설명 (선택)

    Returns:
        dict: 생성된 할일 정보

    Example:
        >>> task = add_task(title="장보기", priority="high", due_date="2025-11-15")
        >>> print(task["id"])
        'TASK001'
    """
    # 우선순위 검증
    valid_priorities = ["high", "medium", "low"]
    if priority not in valid_priorities:
        return {
            "success": False,
            "error": f"우선순위는 {valid_priorities} 중 하나여야 합니다.",
        }

    # 마감일 검증
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "마감일 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식으로 입력해주세요.",
            }

    # 할일 데이터 생성
    task = {
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }

    # DB에 저장
    saved_task = db.add_task(task)

    return {
        "success": True,
        "task": saved_task,
        "message": f"할일 '{title}'이(가) 추가되었습니다.",
    }


@tool
def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    limit: int = 10,
) -> dict:
    """
    할일 목록 조회

    Args:
        status: 상태 필터 (all, pending, completed). 기본값: all
        priority: 우선순위 필터 (high, medium, low). 기본값: None (전체)
        limit: 최대 조회 개수. 기본값: 10

    Returns:
        dict: 할일 목록

    Example:
        >>> tasks = list_tasks(status="pending")
        >>> print(len(tasks["tasks"]))
        5
    """
    # 상태에 따른 조회
    if status == "completed":
        all_tasks = db.get_tasks(completed=True)
    elif status == "pending":
        all_tasks = db.get_tasks(completed=False)
    else:
        all_tasks = db.get_tasks()

    # 우선순위 필터링
    if priority:
        all_tasks = [t for t in all_tasks if t.get("priority") == priority]

    # 우선순위 순으로 정렬 (high > medium > low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

    # 제한
    tasks = all_tasks[:limit]

    return {
        "total": len(all_tasks),
        "count": len(tasks),
        "tasks": tasks,
    }


@tool
def complete_task(task_id: str) -> dict:
    """
    할일 완료 처리

    Args:
        task_id: 완료할 할일 ID (예: TASK001)

    Returns:
        dict: 완료 처리 결과

    Example:
        >>> result = complete_task(task_id="TASK001")
        >>> print(result["success"])
        True
    """
    all_tasks = db.get_tasks()

    for task in all_tasks:
        if task.get("id") == task_id:
            if task.get("completed"):
                return {
                    "success": False,
                    "error": f"할일 '{task_id}'은(는) 이미 완료되었습니다.",
                }
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            return {
                "success": True,
                "task": task,
                "message": f"할일 '{task.get('title')}'이(가) 완료되었습니다.",
            }

    return {
        "success": False,
        "error": f"할일 '{task_id}'을(를) 찾을 수 없습니다.",
    }


@tool
def delete_task(task_id: str) -> dict:
    """
    할일 삭제

    Args:
        task_id: 삭제할 할일 ID (예: TASK001)

    Returns:
        dict: 삭제 결과

    Example:
        >>> result = delete_task(task_id="TASK001")
        >>> print(result["success"])
        True
    """
    all_tasks = db.get_tasks()

    for i, task in enumerate(all_tasks):
        if task.get("id") == task_id:
            # 내부 리스트에서 직접 삭제
            db._tasks.pop(i)
            return {
                "success": True,
                "message": f"할일 '{task.get('title')}'이(가) 삭제되었습니다.",
            }

    return {
        "success": False,
        "error": f"할일 '{task_id}'을(를) 찾을 수 없습니다.",
    }

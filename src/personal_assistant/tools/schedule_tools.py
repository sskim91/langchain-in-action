"""
일정 관리 Tools
"""

from datetime import datetime, timedelta
from typing import Optional

from langchain_core.tools import tool

from personal_assistant.database.memory_db import db


@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60,
    location: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    새로운 일정 생성

    Args:
        title: 일정 제목
        start_time: 시작 시간 (YYYY-MM-DD HH:MM 형식)
        duration: 소요 시간 (분, 기본값: 60)
        location: 장소 (선택)
        description: 상세 설명 (선택)

    Returns:
        dict: 생성된 일정 정보

    Example:
        >>> event = create_event(
        ...     title="팀 회의",
        ...     start_time="2025-11-15 14:00",
        ...     duration=60
        ... )
        >>> print(event["id"])
        'EVT001'
    """
    # 시작 시간 파싱
    try:
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except ValueError as e:
        return {
            "success": False,
            "error": f"시작 시간 형식이 올바르지 않습니다. 'YYYY-MM-DD HH:MM' 형식으로 입력해주세요. (예: 2025-11-15 14:00)",
            "details": str(e),
        }

    end = start + timedelta(minutes=duration)

    # 일정 데이터 생성
    event = {
        "title": title,
        "start_time": start_time,
        "end_time": end.strftime("%Y-%m-%d %H:%M"),
        "duration": duration,
        "location": location,
        "description": description,
        "created_at": datetime.now().isoformat(),
    }

    # DB에 저장
    saved_event = db.add_event(event)

    return {
        "success": True,
        "event": saved_event,
        "message": f"일정 '{title}'이(가) {start_time}에 생성되었습니다.",
    }


@tool
def list_events(
    date: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    일정 목록 조회

    Args:
        date: 특정 날짜 (YYYY-MM-DD 형식, None이면 전체)
        limit: 최대 조회 개수 (기본값: 10)

    Returns:
        dict: 일정 목록

    Example:
        >>> events = list_events(date="2025-11-15")
        >>> print(len(events["events"]))
        3
    """
    all_events = db.get_events()

    # 날짜 필터링
    if date:
        all_events = [e for e in all_events if e["start_time"].startswith(date)]

    # 시작 시간 순으로 정렬
    all_events.sort(key=lambda x: x["start_time"])

    # 제한
    events = all_events[:limit]

    return {
        "total": len(all_events),
        "count": len(events),
        "events": events,
    }


@tool
def find_free_time(date: str, duration: int = 60) -> dict:
    """
    특정 날짜의 비어있는 시간대 찾기

    Args:
        date: 날짜 (YYYY-MM-DD 형식)
        duration: 필요한 시간 (분)

    Returns:
        dict: 사용 가능한 시간대 목록

    Example:
        >>> slots = find_free_time(date="2025-11-15", duration=60)
        >>> print(slots["available_slots"][0])
        '09:00-10:00'
    """
    # 해당 날짜의 일정 조회
    events = db.get_events()
    date_events = [e for e in events if e["start_time"].startswith(date)]

    # 업무 시간 (09:00 ~ 18:00)
    try:
        work_start = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
        work_end = datetime.strptime(f"{date} 18:00", "%Y-%m-%d %H:%M")
    except ValueError as e:
        return {
            "date": date,
            "error": f"날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식으로 입력해주세요. (예: 2025-11-15)",
            "details": str(e),
            "available_slots": [],
            "count": 0,
        }

    # 사용 중인 시간대 수집
    busy_slots = []
    for event in date_events:
        start = datetime.strptime(event["start_time"], "%Y-%m-%d %H:%M")
        end = datetime.strptime(event["end_time"], "%Y-%m-%d %H:%M")
        busy_slots.append((start, end))

    # 비어있는 시간대 찾기
    available_slots = []
    current = work_start

    busy_slots.sort()  # 시작 시간 순 정렬

    for busy_start, busy_end in busy_slots:
        if (busy_start - current).total_seconds() >= duration * 60:
            slot_end = current + timedelta(minutes=duration)
            available_slots.append(
                f"{current.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
            )
        current = max(current, busy_end)

    # 마지막 여유 시간
    if (work_end - current).total_seconds() >= duration * 60:
        slot_end = current + timedelta(minutes=duration)
        available_slots.append(
            f"{current.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
        )

    return {
        "date": date,
        "duration": duration,
        "available_slots": available_slots,
        "count": len(available_slots),
    }

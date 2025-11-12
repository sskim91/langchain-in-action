"""
일정 관리 Tools

📌 목적:
- Agent가 사용할 수 있는 "도구(Tool)" 정의
- 망치, 드라이버처럼 Agent가 필요할 때 골라 쓰는 기능들

🔧 제공 도구:
1. parse_event_info: LLM으로 자연어에서 일정 정보 추출 ⭐ NEW!
2. get_calendar_events: 특정 날짜의 일정 조회 ⭐ NEW!
3. create_event: 새로운 일정 생성
4. list_events: 일정 목록 조회
5. find_free_time: 비어있는 시간대 찾기
6. send_notification: 일정 생성 알림 전송 ⭐ NEW!

💡 동작 방식:
- Agent가 사용자 말을 듣고 → 적절한 도구 선택 → 실행
- 예: "회의 잡아줘" → Agent가 create_event 도구 사용
"""

from datetime import datetime, timedelta

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from personal_assistant.database.memory_db import db

# ============================================================================
# Pydantic 모델: LLM Structured Output용
# ============================================================================


class EventInfo(BaseModel):
    """일정 정보 구조화 모델"""

    title: str = Field(description="일정 제목")
    date: str = Field(description="날짜 (YYYY-MM-DD 형식)")
    time: str = Field(description="시간 (HH:MM 형식, 24시간제)")
    duration: int = Field(default=60, description="소요 시간 (분 단위)")
    location: str | None = Field(default=None, description="장소 (선택 사항)")
    description: str | None = Field(default=None, description="상세 설명 (선택 사항)")


# ============================================================================
# Tools
# ============================================================================


@tool
def parse_event_info(query: str, verbose: bool = False) -> dict:
    """
    자연어 질의에서 일정 정보 추출 (LLM 사용)

    Args:
        query: 사용자 질의 (예: "내일 오후 2시에 팀 회의")
        verbose: 디버깅 정보 출력 여부 (기본값: False)

    Returns:
        dict: 추출된 일정 정보
        {
            "title": "팀 회의",
            "date": "2025-11-13",
            "time": "14:00",
            "duration": 60,
            "location": None,
            "description": None
        }

    Example:
        >>> result = parse_event_info("내일 오후 2시에 팀 회의 일정 잡아줘")
        >>> print(result["title"])
        '팀 회의'
    """
    # 오늘 날짜 (상대적 날짜 파싱용)
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]

    # verbose 모드일 때 LangChain 디버그 활성화
    if verbose:
        from langchain_core.globals import set_debug

        set_debug(True)

    # LLM 초기화
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0.0,
    )

    # Structured Output 설정
    structured_llm = llm.with_structured_output(EventInfo)

    # Prompt 구성
    prompt = f"""당신은 일정 정보를 추출하는 전문가입니다.

오늘 날짜: {today_str} ({weekday_kr}요일)
현재 시간: {today.strftime("%H:%M")}

사용자 요청:
{query}

위 요청에서 일정 정보를 추출하세요.

규칙:
1. "내일" = 오늘 +1일, "모레" = 오늘 +2일
2. "다음주 월요일" = 다음주 월요일 날짜
3. "오후 2시" = 14:00, "오전 10시" = 10:00
4. 시간이 명시되지 않으면 기본값 09:00 사용
5. 소요시간이 명시되지 않으면 60분 사용
6. 날짜 형식: YYYY-MM-DD
7. 시간 형식: HH:MM (24시간제)

예시:
- "내일 오후 2시에 팀 회의" → date: "2025-11-13", time: "14:00", title: "팀 회의"
- "다음주 월요일 10시 미팅" → date: "2025-11-18", time: "10:00", title: "미팅"
"""

    if verbose:
        print("\n" + "=" * 80)
        print("🤖 LLM 호출 (LangChain verbose=True)")
        print("=" * 80)

    try:
        # LLM 호출 - LangChain이 자동으로 로깅함
        result: EventInfo = structured_llm.invoke(prompt)

        if verbose:
            print("\n✅ LLM 응답 (Structured Output):")
            print(f"  • title: {result.title}")
            print(f"  • date: {result.date}")
            print(f"  • time: {result.time}")
            print(f"  • duration: {result.duration}분")
            print(f"  • location: {result.location}")
            print(f"  • description: {result.description}")
            print("=" * 80 + "\n")

        # Pydantic 모델 → dict 변환
        return result.model_dump()

    except Exception as e:
        if verbose:
            print(f"\n❌ LLM 호출 실패: {e}")
            print("=" * 80 + "\n")

        # 에러 발생 시 기본값 반환
        return {
            "error": f"일정 정보 추출 실패: {e!s}",
            "title": "일정",
            "date": today_str,
            "time": "09:00",
            "duration": 60,
            "location": None,
            "description": None,
        }


@tool
def get_calendar_events(date: str) -> list[dict]:
    """
    특정 날짜의 캘린더 이벤트 조회

    Args:
        date: 날짜 (YYYY-MM-DD 형식)

    Returns:
        list[dict]: 해당 날짜의 이벤트 목록

    Example:
        >>> events = get_calendar_events(date="2025-11-15")
        >>> print(len(events))
        2
    """
    all_events = db.get_events()

    # 날짜 필터링
    date_events = [e for e in all_events if e["start_time"].startswith(date)]

    # 시작 시간 순 정렬
    date_events.sort(key=lambda x: x["start_time"])

    return date_events


@tool
def send_notification(event: dict) -> dict:
    """
    일정 생성 알림 전송

    Args:
        event: 생성된 일정 정보

    Returns:
        dict: 알림 전송 결과

    Example:
        >>> result = send_notification(event={"id": "EVT001", "title": "회의"})
        >>> print(result["sent"])
        True
    """
    # 현재는 콘솔 출력으로 구현 (나중에 실제 알림 시스템 연동)
    event_id = event.get("id", "N/A")
    title = event.get("title", "일정")
    start_time = event.get("start_time", "N/A")

    message = f"📅 새 일정이 생성되었습니다!\n- ID: {event_id}\n- 제목: {title}\n- 시간: {start_time}"

    print("\n" + "=" * 60)
    print(message)
    print("=" * 60 + "\n")

    return {"sent": True, "message": message, "event_id": event_id}


@tool
def create_event(
    title: str,
    start_time: str,
    duration: int = 60,
    location: str | None = None,
    description: str | None = None,
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
        ...     title="팀 회의", start_time="2025-11-15 14:00", duration=60
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
            "error": "시작 시간 형식이 올바르지 않습니다. 'YYYY-MM-DD HH:MM' 형식으로 입력해주세요. (예: 2025-11-15 14:00)",
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
    date: str | None = None,
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
            "error": "날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식으로 입력해주세요. (예: 2025-11-15)",
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

    # 첫 번째 슬롯을 best_slot으로 선택
    best_slot = None
    if available_slots:
        # "09:00-10:00" → {"start": "2025-11-13 09:00", "end": "2025-11-13 10:00"}
        first_slot = available_slots[0]
        start_time, end_time = first_slot.split("-")
        best_slot = {
            "start": f"{date} {start_time}",
            "end": f"{date} {end_time}",
        }

    return {
        "date": date,
        "duration": duration,
        "available_slots": available_slots,
        "count": len(available_slots),
        "best_slot": best_slot,  # 추가!
    }

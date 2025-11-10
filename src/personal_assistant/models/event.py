"""
Event 데이터 모델
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EventBase(BaseModel):
    """Event 기본 모델"""

    title: str = Field(..., min_length=1, max_length=200, description="일정 제목")
    start_time: str = Field(..., description="시작 시간 (YYYY-MM-DD HH:MM)")
    duration: int = Field(60, gt=0, le=1440, description="소요 시간 (분)")
    location: Optional[str] = Field(None, max_length=200, description="장소")
    description: Optional[str] = Field(None, max_length=1000, description="상세 설명")

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        """시작 시간 형식 검증"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
            return v
        except ValueError:
            raise ValueError("시작 시간은 'YYYY-MM-DD HH:MM' 형식이어야 합니다")


class EventCreate(EventBase):
    """Event 생성 요청"""

    pass


class Event(EventBase):
    """Event (DB에 저장된)"""

    id: str = Field(..., description="일정 ID")
    end_time: str = Field(..., description="종료 시간 (YYYY-MM-DD HH:MM)")
    created_at: str = Field(..., description="생성 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "EVT001",
                "title": "팀 회의",
                "start_time": "2025-11-15 14:00",
                "end_time": "2025-11-15 15:00",
                "duration": 60,
                "location": "회의실 A",
                "description": "프로젝트 진행 상황 공유",
                "created_at": "2025-11-10 10:30:00",
            }
        }

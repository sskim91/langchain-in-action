"""Redis Client Wrapper

Redis 5.x와 호환되는 Python 클라이언트 래퍼
"""

from typing import Any

import redis

from .config import RedisConfig


class RedisClient:
    """
    Redis 클라이언트 래퍼

    기본 Key-Value 작업 및 캐싱 기능을 제공합니다.

    Example:
        >>> from multi_agent_lab.infra.database.redis import (
        ...     RedisClient,
        ...     RedisConfig,
        ... )
        >>> config = RedisConfig(host="localhost", password="yourpassword")
        >>> client = RedisClient(config)
        >>> client.ping()
        True
    """

    def __init__(self, config: RedisConfig):
        """
        Redis 클라이언트 초기화

        Args:
            config: RedisConfig 인스턴스
        """
        self.config = config
        self.client = redis.Redis(**config.to_dict())

    def ping(self) -> bool:
        """
        Redis 서버 연결 확인

        Returns:
            연결 성공 여부
        """
        return self.client.ping()

    def info(self, section: str | None = None) -> dict:
        """
        Redis 서버 정보 조회

        Args:
            section: 정보 섹션 (server, clients, memory, stats 등)

        Returns:
            서버 정보 딕셔너리
        """
        return self.client.info(section=section)

    # === String Operations ===

    def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        키-값 설정

        Args:
            key: 키
            value: 값
            ex: 만료 시간 (초)
            px: 만료 시간 (밀리초)
            nx: 키가 존재하지 않을 때만 설정
            xx: 키가 존재할 때만 설정

        Returns:
            설정 성공 여부

        Example:
            >>> client.set("user:123", "John Doe")
            >>> client.set("session:456", "active", ex=3600)  # 1시간 후 만료
        """
        return self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key: str) -> str | None:
        """
        키로 값 조회

        Args:
            key: 키

        Returns:
            값 (존재하지 않으면 None)
        """
        return self.client.get(key)

    def delete(self, *keys: str) -> int:
        """
        키 삭제

        Args:
            *keys: 삭제할 키들

        Returns:
            삭제된 키 개수
        """
        return self.client.delete(*keys)

    def exists(self, *keys: str) -> int:
        """
        키 존재 여부 확인

        Args:
            *keys: 확인할 키들

        Returns:
            존재하는 키 개수
        """
        return self.client.exists(*keys)

    def expire(self, key: str, seconds: int) -> bool:
        """
        키에 만료 시간 설정

        Args:
            key: 키
            seconds: 만료 시간 (초)

        Returns:
            설정 성공 여부
        """
        return self.client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        """
        키의 남은 만료 시간 조회

        Args:
            key: 키

        Returns:
            남은 시간 (초), -1: 만료 시간 없음, -2: 키 없음
        """
        return self.client.ttl(key)

    # === Hash Operations ===

    def hset(self, name: str, key: str, value: Any) -> int:
        """
        해시에 필드-값 설정

        Args:
            name: 해시 이름
            key: 필드
            value: 값

        Returns:
            새로 추가된 필드 개수
        """
        return self.client.hset(name, key, value)

    def hget(self, name: str, key: str) -> str | None:
        """
        해시에서 필드 값 조회

        Args:
            name: 해시 이름
            key: 필드

        Returns:
            값 (존재하지 않으면 None)
        """
        return self.client.hget(name, key)

    def hgetall(self, name: str) -> dict:
        """
        해시의 모든 필드-값 조회

        Args:
            name: 해시 이름

        Returns:
            필드-값 딕셔너리
        """
        return self.client.hgetall(name)

    def hdel(self, name: str, *keys: str) -> int:
        """
        해시에서 필드 삭제

        Args:
            name: 해시 이름
            *keys: 삭제할 필드들

        Returns:
            삭제된 필드 개수
        """
        return self.client.hdel(name, *keys)

    # === List Operations ===

    def lpush(self, name: str, *values: Any) -> int:
        """
        리스트 왼쪽에 값 추가

        Args:
            name: 리스트 이름
            *values: 추가할 값들

        Returns:
            리스트 길이
        """
        return self.client.lpush(name, *values)

    def rpush(self, name: str, *values: Any) -> int:
        """
        리스트 오른쪽에 값 추가

        Args:
            name: 리스트 이름
            *values: 추가할 값들

        Returns:
            리스트 길이
        """
        return self.client.rpush(name, *values)

    def lpop(self, name: str) -> str | None:
        """
        리스트 왼쪽에서 값 제거 및 반환

        Args:
            name: 리스트 이름

        Returns:
            제거된 값 (리스트가 비어있으면 None)
        """
        return self.client.lpop(name)

    def rpop(self, name: str) -> str | None:
        """
        리스트 오른쪽에서 값 제거 및 반환

        Args:
            name: 리스트 이름

        Returns:
            제거된 값 (리스트가 비어있으면 None)
        """
        return self.client.rpop(name)

    def lrange(self, name: str, start: int, end: int) -> list:
        """
        리스트에서 범위 조회

        Args:
            name: 리스트 이름
            start: 시작 인덱스
            end: 종료 인덱스 (-1: 끝까지)

        Returns:
            값 리스트
        """
        return self.client.lrange(name, start, end)

    # === Set Operations ===

    def sadd(self, name: str, *values: Any) -> int:
        """
        집합에 값 추가

        Args:
            name: 집합 이름
            *values: 추가할 값들

        Returns:
            새로 추가된 값 개수
        """
        return self.client.sadd(name, *values)

    def smembers(self, name: str) -> set:
        """
        집합의 모든 멤버 조회

        Args:
            name: 집합 이름

        Returns:
            멤버 집합
        """
        return self.client.smembers(name)

    def sismember(self, name: str, value: Any) -> bool:
        """
        집합에 값이 존재하는지 확인

        Args:
            name: 집합 이름
            value: 확인할 값

        Returns:
            존재 여부
        """
        return self.client.sismember(name, value)

    def srem(self, name: str, *values: Any) -> int:
        """
        집합에서 값 제거

        Args:
            name: 집합 이름
            *values: 제거할 값들

        Returns:
            제거된 값 개수
        """
        return self.client.srem(name, *values)

    # === Sorted Set Operations ===

    def zadd(self, name: str, mapping: dict) -> int:
        """
        정렬된 집합에 값 추가

        Args:
            name: 정렬된 집합 이름
            mapping: {값: 점수} 딕셔너리

        Returns:
            새로 추가된 값 개수

        Example:
            >>> client.zadd("leaderboard", {"player1": 100, "player2": 200})
        """
        return self.client.zadd(name, mapping)

    def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        """
        정렬된 집합에서 범위 조회 (낮은 점수부터)

        Args:
            name: 정렬된 집합 이름
            start: 시작 인덱스
            end: 종료 인덱스 (-1: 끝까지)
            withscores: 점수 포함 여부

        Returns:
            값 리스트 (withscores=True면 (값, 점수) 튜플 리스트)
        """
        return self.client.zrange(name, start, end, withscores=withscores)

    def zrevrange(
        self, name: str, start: int, end: int, withscores: bool = False
    ) -> list:
        """
        정렬된 집합에서 범위 조회 (높은 점수부터)

        Args:
            name: 정렬된 집합 이름
            start: 시작 인덱스
            end: 종료 인덱스 (-1: 끝까지)
            withscores: 점수 포함 여부

        Returns:
            값 리스트 (withscores=True면 (값, 점수) 튜플 리스트)
        """
        return self.client.zrevrange(name, start, end, withscores=withscores)

    def zrem(self, name: str, *values: Any) -> int:
        """
        정렬된 집합에서 값 제거

        Args:
            name: 정렬된 집합 이름
            *values: 제거할 값들

        Returns:
            제거된 값 개수
        """
        return self.client.zrem(name, *values)

    # === Key Operations ===

    def keys(self, pattern: str = "*") -> list:
        """
        패턴과 일치하는 키 조회

        Args:
            pattern: 키 패턴 (예: "user:*", "*session*")

        Returns:
            키 리스트

        Warning:
            프로덕션에서는 SCAN 사용 권장 (대량의 키가 있을 때 성능 문제)
        """
        return self.client.keys(pattern)

    def flushdb(self, asynchronous: bool = False) -> bool:
        """
        현재 데이터베이스의 모든 키 삭제

        Args:
            asynchronous: 비동기 삭제 여부

        Returns:
            성공 여부

        Warning:
            위험한 작업! 테스트 환경에서만 사용
        """
        return self.client.flushdb(asynchronous=asynchronous)

    def close(self):
        """클라이언트 연결 종료"""
        self.client.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

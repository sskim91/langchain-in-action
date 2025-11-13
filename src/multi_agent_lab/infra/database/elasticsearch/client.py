"""Elasticsearch Client Wrapper

Elasticsearch 8.19와 호환되는 Python 클라이언트 래퍼
"""

from typing import Any

from elasticsearch import Elasticsearch

from .config import ElasticsearchConfig


class ElasticsearchClient:
    """
    Elasticsearch 클라이언트 래퍼

    기본 CRUD 작업 및 검색 기능을 제공합니다.

    Example:
        >>> from infra.clients.elasticsearch import (
        ...     ElasticsearchClient,
        ...     ElasticsearchConfig,
        ... )
        >>> config = ElasticsearchConfig(
        ...     host="localhost", username="elastic", password="changeme"
        ... )
        >>> client = ElasticsearchClient(config)
        >>> client.ping()
        True
    """

    def __init__(self, config: ElasticsearchConfig):
        """
        Elasticsearch 클라이언트 초기화

        Args:
            config: ElasticsearchConfig 인스턴스
        """
        self.config = config
        self.client = Elasticsearch(**config.to_dict())

    def ping(self) -> bool:
        """
        Elasticsearch 서버 연결 확인

        Returns:
            연결 성공 여부
        """
        return self.client.ping()

    def info(self) -> dict:
        """
        Elasticsearch 클러스터 정보 조회

        Returns:
            클러스터 정보 딕셔너리
        """
        return self.client.info()

    def create_index(
        self, index: str, mappings: dict | None = None, settings: dict | None = None
    ) -> dict:
        """
        인덱스 생성

        Args:
            index: 인덱스 이름
            mappings: 필드 매핑 정의
            settings: 인덱스 설정

        Returns:
            생성 결과

        Example:
            >>> mappings = {
            ...     "properties": {
            ...         "title": {"type": "text"},
            ...         "timestamp": {"type": "date"},
            ...     }
            ... }
            >>> client.create_index("my_index", mappings=mappings)
        """
        body = {}
        if mappings:
            body["mappings"] = mappings
        if settings:
            body["settings"] = settings

        return self.client.indices.create(index=index, body=body if body else None)

    def delete_index(self, index: str) -> dict:
        """
        인덱스 삭제

        Args:
            index: 인덱스 이름

        Returns:
            삭제 결과
        """
        return self.client.indices.delete(index=index)

    def index_exists(self, index: str) -> bool:
        """
        인덱스 존재 여부 확인

        Args:
            index: 인덱스 이름

        Returns:
            존재 여부
        """
        return self.client.indices.exists(index=index)

    def index_document(
        self, index: str, document: dict, doc_id: str | None = None
    ) -> dict:
        """
        문서 인덱싱

        Args:
            index: 인덱스 이름
            document: 인덱싱할 문서
            doc_id: 문서 ID (None이면 자동 생성)

        Returns:
            인덱싱 결과

        Example:
            >>> doc = {"title": "Hello", "content": "World"}
            >>> client.index_document("my_index", doc)
        """
        return self.client.index(index=index, id=doc_id, document=document)

    def get_document(self, index: str, doc_id: str) -> dict:
        """
        문서 조회

        Args:
            index: 인덱스 이름
            doc_id: 문서 ID

        Returns:
            문서 데이터
        """
        return self.client.get(index=index, id=doc_id)

    def update_document(self, index: str, doc_id: str, document: dict) -> dict:
        """
        문서 업데이트

        Args:
            index: 인덱스 이름
            doc_id: 문서 ID
            document: 업데이트할 필드

        Returns:
            업데이트 결과
        """
        return self.client.update(index=index, id=doc_id, doc=document)

    def delete_document(self, index: str, doc_id: str) -> dict:
        """
        문서 삭제

        Args:
            index: 인덱스 이름
            doc_id: 문서 ID

        Returns:
            삭제 결과
        """
        return self.client.delete(index=index, id=doc_id)

    def search(
        self,
        index: str,
        query: dict | None = None,
        size: int = 10,
        from_: int = 0,
        sort: list | None = None,
    ) -> dict:
        """
        문서 검색

        Args:
            index: 인덱스 이름
            query: 검색 쿼리 (None이면 match_all)
            size: 반환할 문서 수
            from_: 시작 위치 (페이지네이션)
            sort: 정렬 조건

        Returns:
            검색 결과

        Example:
            >>> # 전체 검색
            >>> client.search("my_index")
            >>> # Match 쿼리
            >>> query = {"match": {"title": "hello"}}
            >>> client.search("my_index", query=query)
        """
        body: dict[str, Any] = {
            "query": query or {"match_all": {}},
            "size": size,
            "from": from_,
        }

        if sort:
            body["sort"] = sort

        return self.client.search(index=index, body=body)

    def bulk_index(self, index: str, documents: list[dict]) -> dict:
        """
        대량 문서 인덱싱

        Args:
            index: 인덱스 이름
            documents: 인덱싱할 문서 리스트

        Returns:
            대량 작업 결과

        Example:
            >>> docs = [
            ...     {"title": "Doc 1", "content": "Content 1"},
            ...     {"title": "Doc 2", "content": "Content 2"},
            ... ]
            >>> client.bulk_index("my_index", docs)
        """
        operations = []
        for doc in documents:
            operations.append({"index": {"_index": index}})
            operations.append(doc)

        return self.client.bulk(operations=operations)

    def close(self):
        """클라이언트 연결 종료"""
        self.client.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

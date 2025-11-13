"""
Elasticsearch 클라이언트 연결 테스트

클라우드 서버의 Elasticsearch 8.19에 연결하여 클러스터 정보 확인
"""

import warnings

import urllib3
from dotenv import load_dotenv

from multi_agent_lab.infra.database.elasticsearch import (
    ElasticsearchClient,
    ElasticsearchConfig,
)

# HTTPS 인증서 검증 비활성화 시 나오는 경고 억제 (개발 환경용)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message=".*verify_certs=False.*")


def main():
    """Elasticsearch 연결 테스트 실행"""
    print("🔍 Elasticsearch 연결 테스트")
    print("=" * 60)

    # .env 파일 로드
    load_dotenv()

    # 1. 설정 로드
    print("\n1️⃣  설정 로드")
    try:
        # 환경 변수에서 로드
        config = ElasticsearchConfig.from_env()
        print("   ✅ 환경 변수에서 설정 로드")
        print(f"      - 호스트: {config.host}")
        print(f"      - 포트: {config.port}")
        print(f"      - 스킴: {config.scheme}")
        print(f"      - 인증서 검증: {config.verify_certs}")
    except ValueError:
        # 환경 변수가 없으면 직접 입력
        print("   ⚠️  환경 변수가 설정되지 않았습니다.")
        print("   💡 직접 설정을 입력해주세요:")
        host = input("   ES_HOST (예: your-server.com): ").strip()
        port = input("   ES_PORT (기본값: 9200): ").strip() or "9200"
        username = input("   ES_USERNAME: ").strip()
        password = input("   ES_PASSWORD: ").strip()

        config = ElasticsearchConfig(
            host=host,
            port=int(port),
            username=username or None,
            password=password or None,
            verify_certs=False,  # 개발용: 인증서 검증 비활성화
        )
        print("   ✅ 수동 설정 완료")

    # 2. Elasticsearch 연결 테스트
    print("\n2️⃣  Elasticsearch 연결 테스트")
    try:
        with ElasticsearchClient(config) as client:
            # 연결 테스트
            print("   연결 시도 중...")
            info = client.info()
            print("   ✅ 연결 성공!")

            # 클러스터 정보 출력
            print("\n   📊 클러스터 정보:")
            print(f"      - 클러스터 이름: {info['cluster_name']}")
            print(f"      - Elasticsearch 버전: {info['version']['number']}")
            print(f"      - Lucene 버전: {info['version']['lucene_version']}")
            print(f"      - 빌드 타입: {info['version']['build_type']}")

            # 클러스터 상태 확인
            print("\n3️⃣  클러스터 상태 확인")
            health = client.client.cluster.health()
            print(f"   상태: {health['status']}")
            print(f"   노드 수: {health['number_of_nodes']}")
            print(f"   데이터 노드 수: {health['number_of_data_nodes']}")
            print(f"   활성 샤드: {health['active_shards']}")

    except Exception as e:
        print(f"\n❌ 연결 실패: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ Elasticsearch 연결 테스트 완료!")


if __name__ == "__main__":
    main()

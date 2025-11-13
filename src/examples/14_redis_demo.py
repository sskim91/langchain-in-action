"""
Redis 클라이언트 연결 테스트

Oracle Cloud의 Redis 7.x에 연결하여 서버 정보 확인 및 기본 작업 테스트
"""

from dotenv import load_dotenv

from multi_agent_lab.infra.database.redis import RedisClient, RedisConfig


def main():
    """Redis 연결 테스트 실행"""
    print("🔴 Redis 연결 테스트")
    print("=" * 60)

    # .env 파일 로드
    load_dotenv()

    # 1. 설정 로드
    print("\n1️⃣  설정 로드")
    try:
        # 환경 변수에서 로드
        config = RedisConfig.from_env()
        print("   ✅ 환경 변수에서 설정 로드")
        print(f"      - 호스트: {config.host}")
        print(f"      - 포트: {config.port}")
        print(f"      - DB: {config.db}")
        print(f"      - SSL: {config.ssl}")
    except ValueError:
        # 환경 변수가 없으면 직접 입력
        print("   ⚠️  환경 변수가 설정되지 않았습니다.")
        print("   💡 직접 설정을 입력해주세요:")
        host = input("   REDIS_HOST (예: your-server.com): ").strip()
        port = input("   REDIS_PORT (기본값: 6379): ").strip() or "6379"
        password = input("   REDIS_PASSWORD: ").strip()
        db = input("   REDIS_DB (기본값: 0): ").strip() or "0"

        config = RedisConfig(
            host=host,
            port=int(port),
            db=int(db),
            password=password or None,
        )
        print("   ✅ 수동 설정 완료")

    # 2. Redis 연결 테스트
    print("\n2️⃣  Redis 연결 테스트")
    try:
        with RedisClient(config) as client:
            # 연결 테스트
            print("   연결 시도 중...")
            if client.ping():
                print("   ✅ PING 성공!")
            else:
                print("   ❌ PING 실패!")
                return

            # 서버 정보 출력
            print("\n   📊 서버 정보:")
            info = client.info("server")
            print(f"      - Redis 버전: {info.get('redis_version', 'N/A')}")
            print(f"      - OS: {info.get('os', 'N/A')}")
            print(f"      - 아키텍처: {info.get('arch_bits', 'N/A')}bit")
            print(f"      - 업타임(초): {info.get('uptime_in_seconds', 'N/A')}")

            # 메모리 정보
            print("\n   💾 메모리 정보:")
            memory_info = client.info("memory")
            used_memory = memory_info.get("used_memory_human", "N/A")
            max_memory = memory_info.get("maxmemory_human", "N/A")
            print(f"      - 사용 중: {used_memory}")
            print(f"      - 최대: {max_memory}")

            # 클라이언트 정보
            print("\n   👥 클라이언트 정보:")
            clients_info = client.info("clients")
            print(
                f"      - 연결된 클라이언트: {clients_info.get('connected_clients', 'N/A')}"
            )

            # 3. 기본 작업 테스트
            print("\n3️⃣  기본 작업 테스트")

            # String 작업
            print("   📝 String 작업:")
            test_key = "test:connection:demo"
            client.set(test_key, "Hello Redis!", ex=60)
            value = client.get(test_key)
            print(f"      - SET/GET: {value}")
            ttl = client.ttl(test_key)
            print(f"      - TTL: {ttl}초")

            # Hash 작업
            print("\n   🗂️  Hash 작업:")
            hash_key = "test:user:1001"
            client.hset(hash_key, "name", "홍길동")
            client.hset(hash_key, "age", "30")
            client.hset(hash_key, "city", "서울")
            user_data = client.hgetall(hash_key)
            print(f"      - User Data: {user_data}")

            # List 작업
            print("\n   📋 List 작업:")
            list_key = "test:tasks"
            client.rpush(list_key, "Task 1", "Task 2", "Task 3")
            tasks = client.lrange(list_key, 0, -1)
            print(f"      - Tasks: {tasks}")

            # Set 작업
            print("\n   🎯 Set 작업:")
            set_key = "test:tags"
            client.sadd(set_key, "python", "redis", "database", "cache")
            tags = client.smembers(set_key)
            print(f"      - Tags: {tags}")

            # Sorted Set 작업
            print("\n   📊 Sorted Set 작업:")
            zset_key = "test:leaderboard"
            client.zadd(
                zset_key,
                {"player1": 100, "player2": 250, "player3": 180, "player4": 320},
            )
            top_players = client.zrevrange(zset_key, 0, 2, withscores=True)
            print(f"      - Top 3 Players: {top_players}")

            # 4. 정리
            print("\n4️⃣  테스트 데이터 정리")
            deleted_count = client.delete(
                test_key, hash_key, list_key, set_key, zset_key
            )
            print(f"   🗑️  {deleted_count}개 키 삭제 완료")

    except Exception as e:
        print(f"\n❌ 연결 실패: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ Redis 연결 테스트 완료!")


if __name__ == "__main__":
    main()

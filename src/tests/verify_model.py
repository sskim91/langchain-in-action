"""
실제로 로컬 Ollama 모델을 사용하는지 확인하는 스크립트
"""

import time

from langchain_ollama import ChatOllama


def verify_ollama_model():
    """Ollama 모델 사용 확인"""

    print("=" * 60)
    print("Ollama 모델 연결 확인")
    print("=" * 60)
    print()

    # 1. 모델 초기화
    print("[1] ChatOllama 초기화...")
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0,
    )
    print(f"   모델: {llm.model}")
    print(f"   Temperature: {llm.temperature}")
    print()

    # 2. 간단한 프롬프트로 테스트
    print("[2] 로컬 모델 응답 테스트...")
    print("   질문: 'Hello'를 한국어로 번역해줘")
    print()

    start_time = time.time()

    try:
        response = llm.invoke("'Hello'를 한국어로 번역해줘")
        elapsed_time = time.time() - start_time

        print(f"   응답: {response.content}")
        print(f"   응답 시간: {elapsed_time:.2f}초")
        print()

        # 3. Response metadata 확인
        print("[3] Response Metadata 확인...")
        if hasattr(response, "response_metadata"):
            metadata = response.response_metadata
            print(f"   모델: {metadata.get('model', 'N/A')}")
            print(f"   Total Duration: {metadata.get('total_duration', 'N/A')}")
            print(f"   Load Duration: {metadata.get('load_duration', 'N/A')}")
            print(f"   Prompt Eval Count: {metadata.get('prompt_eval_count', 'N/A')}")
            print(f"   Eval Count: {metadata.get('eval_count', 'N/A')}")
            print()

        print("=" * 60)
        print("✅ 로컬 Ollama 모델 (gpt-oss:20b) 정상 작동!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback

        traceback.print_exc()


def check_ollama_api():
    """Ollama API 직접 호출해서 확인"""
    import httpx

    print("\n" + "=" * 60)
    print("Ollama API 직접 호출 테스트")
    print("=" * 60)
    print()

    try:
        # Ollama API 엔드포인트
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": "gpt-oss:20b",
            "prompt": "Say 'OK' if you can hear me.",
            "stream": False,
        }

        print("[요청 정보]")
        print(f"   URL: {url}")
        print(f"   Model: {payload['model']}")
        print(f"   Prompt: {payload['prompt']}")
        print()

        start_time = time.time()
        response = httpx.post(url, json=payload, timeout=30.0)
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"[응답]")
            print(f"   모델: {result.get('model', 'N/A')}")
            print(f"   응답: {result.get('response', 'N/A')}")
            print(f"   응답 시간: {elapsed_time:.2f}초")
            print()
            print("✅ Ollama API 직접 호출 성공!")
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"   응답: {response.text}")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 1. LangChain을 통한 확인
    verify_ollama_model()

    # 2. Ollama API 직접 호출
    check_ollama_api()

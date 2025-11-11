"""
간단한 LLM 연결 예제

Ollama와 LangChain을 연결해서 실제로 LLM 응답을 받아봅니다.

실행:
    uv run python -m src.examples.06_simple_llm
"""

from langchain_ollama import ChatOllama


def main():
    print("=" * 80)
    print("  🤖 LLM 연결 테스트")
    print("=" * 80)

    # 1. Ollama LLM 초기화
    print("\n1️⃣  Ollama 초기화 중...")
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0.7,
    )
    print("   ✅ 연결 완료!")

    # 2. 간단한 질의
    print("\n2️⃣  질의: '안녕하세요!'")
    response = llm.invoke("안녕하세요!")
    print(f"   응답: {response.content}\n")

    # 3. 일정 관련 질의 (우리가 만들 기능)
    print("\n3️⃣  질의: '내일 오후 2시에 팀 회의 일정 잡아줘'")
    response = llm.invoke("내일 오후 2시에 팀 회의 일정 잡아줘")
    print(f"   응답: {response.content}\n")

    print("=" * 80)
    print("  ✨ 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

"""
간단한 LLM 연결 예제

Ollama와 LangChain을 연결해서 실제로 LLM 응답을 받아봅니다.

🎯 목표:
- Ollama.app GUI vs LangChain 동작 차이 이해
- 시스템 프롬프트가 응답에 미치는 영향 확인

실행:
    uv run python -m src.examples.06_simple_llm
"""

from langchain_ollama import ChatOllama


def main():
    print("=" * 80)
    print("  🤖 LLM 시스템 프롬프트 비교 테스트")
    print("=" * 80)

    # Ollama LLM 초기화 (verbose=True로 LangChain 로깅 활성화)
    llm = ChatOllama(
        model="gpt-oss:20b",
        temperature=0.0,  # 일관된 응답을 위해 0으로 설정
        verbose=True,  # ⭐ LangChain이 자동으로 프롬프트/응답 로깅
    )

    user_query = "내일 오후 2시에 팀 회의 일정 잡아줘"

    # ========================================================================
    # Case 1: 시스템 프롬프트 없음 (LangChain 기본)
    # ========================================================================
    print("\n" + "=" * 80)
    print("1️⃣  시스템 프롬프트 없음 (LangChain 기본)")
    print("=" * 80)
    print(f"\n질의: {user_query}")

    response = llm.invoke(user_query)
    print(f"\n응답 길이: {len(response.content)} 글자")
    print(f"응답 시작 100자:\n{response.content}")

    # ========================================================================
    # Case 2: 거부하도록 시스템 프롬프트 추가
    # ========================================================================
    print("\n" + "=" * 80)
    print("2️⃣  시스템 프롬프트: 캘린더 접근 불가 (강제 거부)")
    print("=" * 80)

    messages = [
        (
            "system",
            "You cannot schedule events. You have no access to calendars. Always refuse politely.",
        ),
        ("human", user_query),
    ]

    response = llm.invoke(messages)
    print(f"\n질의: {user_query}")
    print(f"\n응답:\n{response.content}")

    # ========================================================================
    # Case 3: Ollama.app과 동일한 시스템 프롬프트
    # ========================================================================
    print("\n" + "=" * 80)
    print("3️⃣  시스템 프롬프트: Ollama.app GUI와 동일 (ChatGPT 역할)")
    print("=" * 80)

    messages = [
        (
            "system",
            """You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-11-12

Reasoning: medium

When asked to perform actions (like scheduling), think about whether you actually have the capability to do so.""",
        ),
        ("human", user_query),
    ]

    response = llm.invoke(messages)
    print(f"\n질의: {user_query}")
    print(f"\n응답:\n{response.content}")

    # ========================================================================
    # 결론
    # ========================================================================
    print("\n" + "=" * 80)
    print("  💡 핵심 발견")
    print("=" * 80)
    print(
        """
1️⃣  시스템 프롬프트 없음:
   → LLM이 단순히 "도와주는" 텍스트 생성
   → 실제 캘린더 접근 없이도 친절하게 응답

2️⃣  시스템 프롬프트로 제약 추가:
   → "캘린더 접근 불가"라고 명시하면 거부
   → Ollama.app GUI가 이런 방식으로 동작

3️⃣  Ollama.app과 동일한 프롬프트:
   → "ChatGPT처럼 행동" + "Reasoning: medium"
   → 모델이 자기 능력을 판단하고 거부

🎯 결론:
   - Ollama.app GUI ≠ LangChain (시스템 프롬프트 차이)
   - 우리 시스템은 LangChain 사용 = 문제없음!
   - parse_event_info는 명확한 지시로 정보만 추출 = 작동 완벽!
    """
    )

    print("=" * 80)
    print("  ✨ 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

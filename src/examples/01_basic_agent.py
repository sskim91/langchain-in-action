"""
예제 1: 기본 Agent 사용법

간단한 Tool을 가진 Agent를 생성하고 사용하는 예제입니다.
"""

from src import create_simple_agent
from src.tools import calculator, get_current_time, get_word_length


def main():
    """기본 Agent 예제"""
    print("=" * 60)
    print("예제 1: 기본 Agent 사용")
    print("=" * 60)
    print()

    # 1. Agent 생성
    print("[1] Agent 생성 중...")
    agent = create_simple_agent(
        model_name="gpt-oss:20b",
        temperature=0.1,
        tools=[calculator, get_word_length, get_current_time],
    )
    print("✅ Agent 생성 완료")
    print()

    # 2. 질문들
    questions = [
        "현재 시간이 몇 시야?",
        "25 곱하기 4는?",
        "'Python'이라는 단어는 몇 글자야?",
        "100 더하기 200을 계산한 다음, 그 결과가 몇 글자인지 알려줘",
    ]

    # 3. 각 질문에 답변
    for i, question in enumerate(questions, 1):
        print(f"[질문 {i}] {question}")
        print("-" * 60)

        try:
            # Agent 실행
            answer = agent.chat(question)
            print(f"답변: {answer}")
        except Exception as e:
            print(f"오류: {e}")

        print()

    print("=" * 60)
    print("예제 완료!")


if __name__ == "__main__":
    main()

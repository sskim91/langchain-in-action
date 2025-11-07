"""
간단한 LangChain 1.0 + Ollama Agent 예제

LangChain 1.0의 새로운 create_agent API 사용
"""

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# 1. Tool 정의 - Agent가 사용할 수 있는 도구들
@tool
def calculator(expression: str) -> str:
    """간단한 수식을 계산합니다. 예: '2 + 2', '10 * 5'"""
    try:
        result = eval(expression)
        return f"계산 결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


@tool
def get_word_length(word: str) -> str:
    """단어의 길이를 반환합니다."""
    return f"'{word}'의 길이는 {len(word)}글자입니다."


# 2. Ollama LLM 초기화
llm = ChatOllama(
    model="gpt-oss:20b",  # ollama list로 확인한 모델명
    temperature=0,  # 일관된 응답을 위해 0으로 설정
    num_predict=512,  # 생성 토큰 수 제한 (긴 응답에서 에러 방지)
)

# 3. Tools 리스트
tools = [calculator, get_word_length]

# 4. Agent 생성 (LangChain 1.0 새로운 방식)
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""당신은 도움이 되는 AI 어시스턴트입니다.
사용 가능한 도구를 활용하여 사용자의 질문에 답변하세요.

사용 가능한 도구:
- calculator: 수식 계산
- get_word_length: 단어 길이 확인

도구를 사용해야 할 때는 반드시 사용하고, 결과를 자연스럽게 설명해주세요.""",
)


def main():
    """Agent 실행 예제"""
    print("=" * 60)
    print("LangChain 1.0 + Ollama Agent 예제")
    print("=" * 60)
    print()

    # 예제 질문들
    test_queries = [
        "25 곱하기 4는 얼마야?",
        "'LangChain'이라는 단어는 몇 글자야?",
        "안녕하세요! 당신은 누구인가요?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[질문 {i}] {query}")
        print("-" * 60)

        try:
            # LangChain 1.0 invoke 형식
            response = agent.invoke({"messages": [{"role": "user", "content": query}]})

            # 응답에서 마지막 메시지 추출
            if "messages" in response:
                last_message = response["messages"][-1]
                print(f"\n[답변] {last_message.content}")
            else:
                print(f"\n[답변] {response}")

        except Exception as e:
            print(f"\n[오류] {str(e)}")
            import traceback

            traceback.print_exc()

        print("=" * 60)


def interactive_mode():
    """대화형 모드"""
    print("=" * 60)
    print("대화형 모드 (종료하려면 'quit' 또는 'exit' 입력)")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("\n질문: ").strip()

            if user_input.lower() in ["quit", "exit", "종료"]:
                print("프로그램을 종료합니다.")
                break

            if not user_input:
                continue

            print("-" * 60)

            # LangChain 1.0 invoke 형식
            try:
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )

                # 응답에서 마지막 메시지 추출
                if "messages" in response:
                    last_message = response["messages"][-1]
                    # UTF-8 에러 방지: surrogate 문자 제거
                    content = last_message.content
                    # surrogate 문자 필터링
                    clean_content = content.encode("utf-8", errors="ignore").decode(
                        "utf-8", errors="ignore"
                    )
                    print(f"\n답변: {clean_content}")
                else:
                    print(f"\n답변: {response}")

                print("=" * 60)

            except UnicodeEncodeError as e:
                print(
                    f"\n⚠️ 인코딩 오류가 발생했습니다. 모델이 잘못된 문자를 생성했습니다."
                )
                print(f"   다른 질문을 시도해보세요.")
                print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류 발생: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    import sys

    # 명령행 인자로 모드 선택
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        main()

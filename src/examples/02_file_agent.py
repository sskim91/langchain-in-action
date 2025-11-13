"""
예제 2: 파일 처리 Agent

파일 읽기/쓰기 도구를 사용하는 Agent 예제입니다.
"""

from multi_agent_lab.core.agents import create_simple_agent
from multi_agent_lab.shared.tools import list_files, read_file, write_file


def main():
    """파일 처리 Agent 예제"""
    print("=" * 60)
    print("예제 2: 파일 처리 Agent")
    print("=" * 60)
    print()

    # 1. Agent 생성
    print("[1] Agent 생성 중...")
    agent = create_simple_agent(
        model_name="gpt-oss:20b",
        temperature=0.1,
        tools=[read_file, write_file, list_files],
        system_prompt="""당신은 파일 관리 어시스턴트입니다.
파일 읽기, 쓰기, 목록 조회 도구를 사용하여 사용자를 도와주세요.
항상 한국어로 응답하세요.""",
    )
    print("✅ Agent 생성 완료")
    print()

    # 2. 작업들
    tasks = [
        "현재 디렉토리의 파일 목록을 보여줘",
        "README.md 파일을 읽어줘",
        "'test.txt' 파일에 'Hello from Agent!'라고 저장해줘",
    ]

    # 3. 각 작업 실행
    for i, task in enumerate(tasks, 1):
        print(f"[작업 {i}] {task}")
        print("-" * 60)

        try:
            answer = agent.chat(task)
            print(f"결과: {answer}")
        except Exception as e:
            print(f"오류: {e}")

        print()

    print("=" * 60)
    print("예제 완료!")


if __name__ == "__main__":
    main()

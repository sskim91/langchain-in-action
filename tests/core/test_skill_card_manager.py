"""
SkillCardManager 테스트

테스트 항목:
1. Skill Card JSON 파일 로드
2. Pydantic 검증
3. Execution Plan 연속성 검증
4. 키워드 매칭
5. 유효성 검사
"""

import json

from core.skill_cards import SkillCard, SkillCardManager
from core.skill_cards.schema import Constraints, ExecutionStep, LLMConfig, Trigger


class TestSkillCardManager:
    """SkillCardManager 기능 테스트"""

    def test_load_schedule_card(self):
        """schedule_card.json 로드 테스트"""
        # Given: SkillCardManager 초기화
        manager = SkillCardManager()

        # When: schedule_card 조회
        card = manager.get("SC_SCHEDULE_001")

        # Then: 카드가 정상 로드됨
        assert card is not None
        assert card.id == "SC_SCHEDULE_001"
        assert card.agent_name == "일정 관리 전문가"
        assert card.agent_type == "ScheduleManagerAgent"

    def test_schedule_card_structure(self):
        """schedule_card의 구조 검증"""
        # Given
        manager = SkillCardManager()
        card = manager.get("SC_SCHEDULE_001")

        # Then: Trigger 검증
        assert card.trigger.keywords
        assert "일정" in card.trigger.keywords
        assert "회의" in card.trigger.keywords
        assert card.trigger.similarity_threshold == 0.85

        # Then: Tools 검증
        assert len(card.tools) > 0
        tool_names = [tool.name for tool in card.tools]
        assert "parse_event_info" in tool_names
        assert "find_free_time" in tool_names
        assert "create_event" in tool_names

        # Then: Execution Plan 검증
        assert len(card.execution_plan) == 5
        assert card.execution_plan[0].step == 1
        assert card.execution_plan[0].action == "parse_event_info"
        assert card.execution_plan[4].step == 5
        assert card.execution_plan[4].action == "send_notification"

    def test_execution_plan_continuity(self):
        """Execution Plan의 step 번호 연속성 검증"""
        # Given
        manager = SkillCardManager()
        card = manager.get("SC_SCHEDULE_001")

        # When: Step 번호 추출
        steps = [s.step for s in card.execution_plan]

        # Then: 1부터 순차적으로 증가
        assert steps == [1, 2, 3, 4, 5]

    def test_execution_plan_variables(self):
        """Execution Plan의 입출력 변수 검증"""
        # Given
        manager = SkillCardManager()
        card = manager.get("SC_SCHEDULE_001")

        # When: Step 1의 출력
        step1 = card.execution_plan[0]
        assert step1.output_to == "event_data"

        # Then: Step 2는 Step 1의 출력을 사용
        step2 = card.execution_plan[1]
        assert "${event_data.date}" in str(step2.input)

        # Then: Step 3는 Step 2의 출력을 사용
        step3 = card.execution_plan[2]
        assert "${existing_events}" in str(step3.input)

    def test_keyword_matching(self):
        """키워드 매칭으로 Skill Card 찾기"""
        # Given
        manager = SkillCardManager()

        # When: 일정 관련 질의
        queries = [
            "내일 오후 2시에 팀 회의 일정 잡아줘",
            "다음주 월요일 미팅 추가해줘",
            "오늘 오후 약속 만들어줘",
        ]

        for query in queries:
            # Then: schedule_card가 매칭됨
            matched = manager.find_by_keywords(query)
            assert len(matched) > 0
            assert matched[0].id == "SC_SCHEDULE_001"

    def test_no_match_for_irrelevant_query(self):
        """관련 없는 질의는 매칭 안 됨"""
        # Given
        manager = SkillCardManager()

        # When: 일정과 무관한 질의
        query = "오늘 날씨 어때?"

        # Then: 매칭 안 됨
        matched = manager.find_by_keywords(query)
        assert len(matched) == 0

    def test_validate_valid_card(self):
        """유효한 Skill Card 검증"""
        # Given
        manager = SkillCardManager()
        card = manager.get("SC_SCHEDULE_001")

        # When: 검증 수행
        is_valid, errors = manager.validate(card)

        # Then: 검증 통과
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_card(self):
        """잘못된 Skill Card 검증"""
        # Given: ID가 없는 카드
        invalid_card = SkillCard(
            id="",  # 빈 ID
            agent_name="테스트 Agent",
            agent_type="TestAgent",
        )

        # When: 검증 수행
        manager = SkillCardManager()
        is_valid, errors = manager.validate(invalid_card)

        # Then: 검증 실패
        assert is_valid is False
        assert "ID가 없습니다" in errors

    def test_validate_discontinuous_steps(self):
        """Step 번호가 연속적이지 않은 경우"""
        # Given: Step이 1, 3, 5로 불연속
        invalid_card = SkillCard(
            id="SC_TEST_001",
            agent_name="테스트 Agent",
            agent_type="TestAgent",
            execution_plan=[
                ExecutionStep(step=1, action="action1"),
                ExecutionStep(step=3, action="action2"),  # 2를 건너뜀
                ExecutionStep(step=5, action="action3"),  # 4를 건너뜀
            ],
        )

        # When: 검증 수행
        manager = SkillCardManager()
        is_valid, errors = manager.validate(invalid_card)

        # Then: 검증 실패
        assert is_valid is False
        assert any("연속적이지 않습니다" in err for err in errors)

    def test_list_all_cards(self):
        """모든 Skill Card 목록 조회"""
        # Given
        manager = SkillCardManager()

        # When: 목록 조회
        cards = manager.list_all()

        # Then: schedule_card 포함
        assert len(cards) >= 1
        card_ids = [c["id"] for c in cards]
        assert "SC_SCHEDULE_001" in card_ids

    def test_reload_cards(self):
        """Skill Card 재로드"""
        # Given
        manager = SkillCardManager()
        initial_count = len(manager.cards)

        # When: 재로드
        manager.reload()

        # Then: 동일한 개수의 카드 로드됨
        assert len(manager.cards) == initial_count
        assert manager.get("SC_SCHEDULE_001") is not None


class TestSkillCardSchema:
    """SkillCard Pydantic 모델 테스트"""

    def test_minimal_skill_card(self):
        """최소 필수 필드만으로 SkillCard 생성"""
        # Given: 필수 필드만 제공
        card = SkillCard(
            id="SC_TEST_001",
            agent_name="테스트 Agent",
            agent_type="TestAgent",
        )

        # Then: 기본값으로 초기화됨
        assert card.id == "SC_TEST_001"
        assert card.version == "1.0.0"
        assert card.trigger.keywords == []
        assert card.tools == []
        assert card.execution_plan == []

    def test_full_skill_card(self):
        """모든 필드를 포함한 SkillCard 생성"""
        # Given: 모든 필드 제공
        card = SkillCard(
            id="SC_TEST_002",
            version="2.0.0",
            agent_name="완전한 Agent",
            agent_type="FullAgent",
            description="설명",
            trigger=Trigger(
                keywords=["키워드1", "키워드2"],
                intent="test_intent",
                similarity_threshold=0.9,
            ),
            execution_plan=[
                ExecutionStep(
                    step=1,
                    action="test_action",
                    description="테스트 액션",
                    input={"key": "value"},
                    output_to="result",
                ),
            ],
            constraints=Constraints(
                validation=["규칙1", "규칙2"],
                output_format="json",
            ),
            llm_config=LLMConfig(
                model="test-model",
                temperature=0.5,
                max_tokens=100,
            ),
        )

        # Then: 모든 필드가 올바르게 설정됨
        assert card.id == "SC_TEST_002"
        assert card.trigger.keywords == ["키워드1", "키워드2"]
        assert len(card.execution_plan) == 1
        assert card.execution_plan[0].input == {"key": "value"}
        assert card.llm_config.temperature == 0.5

    def test_execution_step_defaults(self):
        """ExecutionStep 기본값 테스트"""
        # Given: 최소 필드만 제공
        step = ExecutionStep(step=1, action="test_action")

        # Then: 기본값 적용됨
        assert step.description == ""
        assert step.input == {}
        assert step.output_to == ""
        assert step.timeout_ms == 3000
        assert step.on_error == "fail"

    def test_json_serialization(self):
        """Skill Card의 JSON 직렬화"""
        # Given
        manager = SkillCardManager()
        card = manager.get("SC_SCHEDULE_001")

        # When: dict로 변환
        card_dict = card.model_dump()

        # Then: JSON으로 변환 가능
        json_str = json.dumps(card_dict, ensure_ascii=False, indent=2)
        assert "SC_SCHEDULE_001" in json_str
        assert "일정 관리 전문가" in json_str

        # Then: 다시 로드 가능
        loaded_dict = json.loads(json_str)
        reloaded_card = SkillCard(**loaded_dict)
        assert reloaded_card.id == card.id
        assert reloaded_card.agent_name == card.agent_name

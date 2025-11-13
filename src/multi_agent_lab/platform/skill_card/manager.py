"""
Skill Card Manager

Skill Card를 로드하고 관리하는 클래스

📌 목적:
- Skill Card JSON 파일들을 로드
- 키워드 매칭으로 적절한 Skill Card 선택
- 유효성 검증

💡 사용 방식:
    manager = SkillCardManager()
    card = manager.get("SC_SCHEDULE_001")
    matched = manager.find_by_keywords("회의 일정 잡아줘")
"""

import json
from pathlib import Path

from .schema import SkillCard


class SkillCardManager:
    """Skill Card 로드 및 관리"""

    def __init__(
        self,
        cards_dir: str
        | Path = "src/multi_agent_lab/domains/personal_assistant/skill_cards",
    ):
        """
        Args:
            cards_dir: Skill Card JSON 파일들이 있는 디렉토리
        """
        self.cards_dir = Path(cards_dir)
        self.cards: dict[str, SkillCard] = {}
        self._load_all_cards()

    def _load_all_cards(self):
        """디렉토리에서 모든 Skill Card JSON 파일 로드"""
        if not self.cards_dir.exists():
            print(f"⚠️  Skill Cards 디렉토리가 없습니다: {self.cards_dir}")
            self.cards_dir.mkdir(parents=True, exist_ok=True)
            return

        for card_file in self.cards_dir.glob("*.json"):
            try:
                with open(card_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Pydantic으로 검증
                skill_card = SkillCard(**data)

                self.cards[skill_card.id] = skill_card
                print(f"✓ Loaded: {skill_card.id} - {skill_card.agent_name}")

            except Exception as e:
                print(f"✗ Failed to load {card_file.name}: {e}")

    def get(self, card_id: str) -> SkillCard | None:
        """
        Skill Card 조회

        Args:
            card_id: Skill Card ID

        Returns:
            SkillCard 또는 None
        """
        return self.cards.get(card_id)

    def list_all(self) -> list[dict]:
        """
        모든 Skill Card 목록 조회

        Returns:
            Skill Card 목록 (간략 정보)
        """
        return [
            {
                "id": card.id,
                "name": card.agent_name,
                "type": card.agent_type,
                "description": card.description,
                "version": card.version,
            }
            for card in self.cards.values()
        ]

    def find_by_keywords(self, query: str) -> list[SkillCard]:
        """
        키워드 매칭으로 Skill Card 찾기

        Args:
            query: 사용자 질의

        Returns:
            매칭되는 Skill Card 목록

        Example:
            >>> manager = SkillCardManager()
            >>> cards = manager.find_by_keywords("내일 회의 일정 잡아줘")
            >>> print(cards[0].agent_name)
            '일정 관리 전문가'
        """
        query_lower = query.lower()
        matched = []

        for card in self.cards.values():
            # 키워드 매칭
            if any(kw in query_lower for kw in card.trigger.keywords):
                matched.append(card)

        return matched

    def validate(self, card: SkillCard) -> tuple[bool, list[str]]:
        """
        Skill Card 유효성 검증

        Args:
            card: 검증할 Skill Card

        Returns:
            (유효 여부, 에러 메시지 목록)
        """
        errors = []

        # ID 검증
        if not card.id:
            errors.append("ID가 없습니다")

        # Agent 이름 검증
        if not card.agent_name:
            errors.append("Agent 이름이 없습니다")

        # Execution Plan 검증
        if not card.execution_plan:
            errors.append("Execution Plan이 비어있습니다")

        # Step 번호 연속성 검증
        steps = [s.step for s in card.execution_plan]
        if steps and steps != list(range(1, len(steps) + 1)):
            errors.append("Execution Plan의 step 번호가 연속적이지 않습니다")

        return len(errors) == 0, errors

    def reload(self):
        """Skill Card 재로드"""
        self.cards.clear()
        self._load_all_cards()

import logging
from app.classification.embeddings import EmbeddingSearcher
from app.classification.llm import LLMClient
from app.classification.censor import CensorFilter
from typing import List, Dict

logger = logging.getLogger(__name__)

class AppealClassifier:
    def __init__(self):
        self.embedder = EmbeddingSearcher()
        self.llm = LLMClient()
        self.profanity = CensorFilter()

    async def classify(self, text: str) -> tuple[List[Dict[str, str]], bool, str | None]:
        """
        Возвращает (categories, contains_explicit, unclassified_reason).
        categories = [{"category": "...", "reason": "..."}]
        """
        # 1. Проверка на недопустимую лексику
        is_bad, reason = self.profanity.check_text(text)
        if is_bad:
            return [], True, reason

        # 2. Эмбеддинги: top-k (5)
        top_cats = self.embedder.top_k_categories(text, k=5)

        # 3. LLM выбирает категории и обосновывает
        raw_results = await self.llm.classify_with_reasons(text, top_cats)

        # 4. Валидация результатов: оставляем только категории из общего справочника
        all_categories = set(self.embedder.categories)
        valid_results = []
        for item in raw_results:
            cat = item.get("category")
            reason = item.get("reason", "")
            if cat in all_categories:
                valid_results.append({"category": cat, "reason": reason})
                break  # берём только одну, выходим из цикла

        if not valid_results:
            return [], False, "Не удалось определить категорию (низкая уверенность LLM)"

        return valid_results, False, None  # valid_results содержит ровно один элемент
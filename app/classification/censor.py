import re
from transformers import pipeline

class CensorFilter:
    def __init__(self):
        self.toxicity_classifier = pipeline(
            "text-classification",
            model="SkolkovoInstitute/russian_toxicity_classifier",
            tokenizer="SkolkovoInstitute/russian_toxicity_classifier",
            top_k=None,
        )
        self.bad_words = [
            "дурак", "идиот", "ублюдок", "сволочь", "мразь", "тварь", "нахер",
            "убью", "уничтожу", "ненавижу", "чёрт", "сука", "блядь",
        ]
        self.pattern = re.compile(
            r'\b(' + '|'.join(re.escape(w) for w in self.bad_words) + r')\b',
            re.IGNORECASE
        )

    def check_text(self, text: str) -> tuple[bool, str | None]:
        """
        Проверяет текст на наличие запрещённой лексики.
        Возвращает (True, причина) если найдено, иначе (False, None).
        """
        # 1. Прямой поиск по словарю мата/оскорблений
        if self.pattern.search(text):
            return True, "Обнаружена нецензурная/оскорбительная лексика"

        # 2. Модель токсичности (угрозы, враждебность)
        results = self.toxicity_classifier(text, truncation=True, max_length=512)
        for item in results[0]:
            if item["label"].lower() in ("toxic") and item["score"] > 0.3:
                return True, "Обнаружена враждебная или угрожающая лексика"

        return False, None
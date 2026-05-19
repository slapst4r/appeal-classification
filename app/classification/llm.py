import json
import logging
from app.config import settings
from typing import List, Dict
import httpx 

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.backend = settings.llm_backend

    async def classify_with_reasons(self, text: str, candidate_categories: List[str]) -> List[Dict[str, str]]:
        """Отправляет запрос к LLM и возвращает список {'category': ..., 'reason': ...}."""
        if self.backend == "ollama":
            return await self._ollama_classify(text, candidate_categories)
        else:
            raise ValueError(f"Unsupported LLM backend: {self.backend}")

    async def _ollama_classify(self, text: str, categories: List[str]) -> List[Dict[str, str]]:
        prompt = self._build_prompt(text, categories)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ollama_host}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            raw_output = data["response"]
            try:
                result = json.loads(raw_output)
                data = result
                if isinstance(data, dict) and "category" in data and "reason" in data:
                    return [data]
                else:
                    return []
            except json.JSONDecodeError:
                logger.error(f"Ollama returned invalid JSON: {raw_output}")
                return []

    def _build_prompt(self, text: str, categories: List[str]) -> str:
        cat_list = ", ".join(categories)
        prompt = f"""Ты — система классификации обращений граждан. Из предложенного списка категорий выбери **только одну**, наиболее точно соответствующую сути обращения. Объясни, почему выбрана именно она.

Список категорий: {cat_list}

Обращение: "{text}"

Ответ верни строго в формате JSON с объектом, содержащим поля "category" и "reason". Не добавляй ничего лишнего.
Пример ответа: {{"category": "Водоснабжение", "reason": "В тексте упоминается отключение воды."}}
"""
        return prompt
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingSearcher:
    def __init__(self, categories_path: str = "app/data/categories.json"):
        with open(categories_path, 'r') as f:
            self.categories = json.load(f)
        self.model = SentenceTransformer(settings.embeddings_model)
        self.category_embeddings = self.model.encode(
            self.categories, normalize_embeddings=True
        )

    def top_k_categories(self, query: str, k: int = 3) -> list[str]:
        text_emb = self.model.encode([query], normalize_embeddings=True)[0]
        similarities = np.dot(self.category_embeddings, text_emb.T)
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        print(self.categories[i] for i in top_k_indices)
        return [self.categories[i] for i in top_k_indices]
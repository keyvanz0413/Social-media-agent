"""
Deterministic local embeddings for FAISS indexing without external APIs.
"""

from __future__ import annotations

import hashlib
import re
from typing import List

from langchain_core.embeddings import Embeddings


class HashEmbeddings(Embeddings):
    """Simple hashing-based embedding model."""

    def __init__(self, dim: int = 256):
        self.dim = max(32, int(dim))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dim

        vec = [0.0] * self.dim
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % self.dim
            sign = 1.0 if int(digest[8:9], 16) % 2 == 0 else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = (text or "").lower()
        parts = re.findall(r"[\u4e00-\u9fff]+|[a-z0-9_]+", text)
        tokens: List[str] = []
        for part in parts:
            if re.fullmatch(r"[\u4e00-\u9fff]+", part):
                tokens.extend(list(part))
            else:
                tokens.append(part)
        return [t for t in tokens if t]

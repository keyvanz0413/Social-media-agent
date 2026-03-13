"""
Memory vector store with FAISS backend and graceful fallback.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from social_media_agent.config import Config
from social_media_agent.memory.embeddings import HashEmbeddings

logger = logging.getLogger(__name__)


class MemoryVectorStore:
    """Store and retrieve memory items using FAISS when available."""

    def __init__(self):
        self.records_path = Path(Config.MEMORY_RECORDS_PATH)
        self.index_dir = Path(Config.MEMORY_INDEX_DIR)
        self.records_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.embeddings = HashEmbeddings(dim=Config.MEMORY_EMBEDDING_DIM)
        self._records: List[Dict[str, Any]] = self._load_records()
        self._faiss_store = None
        self._backend = "fallback"
        self._init_faiss()

    @property
    def backend(self) -> str:
        return self._backend

    def add_memory(
        self,
        item_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "manual",
    ) -> Dict[str, Any]:
        if not content or not content.strip():
            raise ValueError("content 不能为空")
        if not item_type or not item_type.strip():
            raise ValueError("item_type 不能为空")

        now = datetime.now().isoformat(timespec="seconds")
        record = {
            "memory_id": f"mem_{uuid4().hex[:12]}",
            "item_type": item_type.strip(),
            "content": content.strip(),
            "source": source,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }

        self._records.append(record)
        self._append_record(record)
        self._faiss_add(record)
        return record

    def search(
        self,
        query: str,
        top_k: int = 5,
        item_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        k = max(1, min(top_k, 50))
        if self._faiss_store is not None:
            items = self._search_faiss(query=query, top_k=k, item_type=item_type)
            if items:
                return items
        return self._search_fallback(query=query, top_k=k, item_type=item_type)

    def list_recent(
        self,
        limit: int = 20,
        item_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = self._records
        if item_type:
            rows = [r for r in rows if r.get("item_type") == item_type]
        rows = sorted(rows, key=lambda x: x.get("created_at", ""), reverse=True)
        return rows[: max(1, min(limit, 200))]

    def _load_records(self) -> List[Dict[str, Any]]:
        if not self.records_path.exists():
            return []
        records: List[Dict[str, Any]] = []
        with self.records_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("跳过损坏记忆记录行")
        return records

    def _append_record(self, record: Dict[str, Any]) -> None:
        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _init_faiss(self) -> None:
        try:
            from langchain_community.vectorstores import FAISS

            index_file = self.index_dir / "index.faiss"
            if index_file.exists():
                self._faiss_store = FAISS.load_local(
                    str(self.index_dir),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            self._backend = "faiss"
            logger.info("记忆向量库已启用 FAISS 后端")
        except Exception as e:
            self._faiss_store = None
            self._backend = "fallback"
            logger.warning("FAISS 不可用，使用 fallback 记忆检索: %s", str(e))

    def _faiss_add(self, record: Dict[str, Any]) -> None:
        try:
            if self._faiss_store is None:
                # Try lazy initialize for environments that install FAISS later.
                self._init_faiss()
            if self._faiss_store is None:
                return

            metadata = {
                "memory_id": record["memory_id"],
                "item_type": record["item_type"],
                "source": record["source"],
                "created_at": record["created_at"],
                "payload": json.dumps(record.get("metadata", {}), ensure_ascii=False),
            }

            from langchain_community.vectorstores import FAISS

            if self._faiss_store is None:
                self._faiss_store = FAISS.from_texts(
                    texts=[record["content"]],
                    embedding=self.embeddings,
                    metadatas=[metadata],
                )
            else:
                self._faiss_store.add_texts(
                    texts=[record["content"]],
                    metadatas=[metadata],
                )

            self._faiss_store.save_local(str(self.index_dir))
        except Exception as e:
            self._backend = "fallback"
            logger.warning("FAISS 写入失败，继续使用 fallback: %s", str(e))

    def _search_faiss(
        self,
        query: str,
        top_k: int,
        item_type: Optional[str],
    ) -> List[Dict[str, Any]]:
        try:
            docs_with_score = self._faiss_store.similarity_search_with_score(
                query, k=max(top_k * 3, top_k)
            )
        except Exception:
            docs = self._faiss_store.similarity_search(query, k=max(top_k * 3, top_k))
            docs_with_score = [(doc, None) for doc in docs]

        rows: List[Dict[str, Any]] = []
        for doc, score in docs_with_score:
            meta = getattr(doc, "metadata", {}) or {}
            if item_type and meta.get("item_type") != item_type:
                continue

            payload_raw = meta.get("payload", "{}")
            try:
                payload = json.loads(payload_raw)
            except Exception:
                payload = {}

            row = {
                "memory_id": meta.get("memory_id"),
                "item_type": meta.get("item_type"),
                "content": getattr(doc, "page_content", ""),
                "source": meta.get("source", ""),
                "metadata": payload,
                "created_at": meta.get("created_at", ""),
                "score": float(score) if score is not None else None,
            }
            rows.append(row)
            if len(rows) >= top_k:
                break

        return rows

    def _search_fallback(
        self,
        query: str,
        top_k: int,
        item_type: Optional[str],
    ) -> List[Dict[str, Any]]:
        q_tokens = set(HashEmbeddings._tokenize(query))
        if not q_tokens:
            return []

        scored: List[Dict[str, Any]] = []
        for record in self._records:
            if item_type and record.get("item_type") != item_type:
                continue
            c_tokens = set(HashEmbeddings._tokenize(record.get("content", "")))
            if not c_tokens:
                continue

            overlap = len(q_tokens & c_tokens)
            union = len(q_tokens | c_tokens)
            score = overlap / union if union else 0.0
            if score <= 0:
                continue

            row = dict(record)
            row["score"] = round(score, 6)
            scored.append(row)

        scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return scored[:top_k]

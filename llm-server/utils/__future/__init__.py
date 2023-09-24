import warnings
from typing import List, Optional, Tuple

from qdrant_client import QdrantClient
from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore


def fetch_qdrant_docs(
    vector_db: VectorStore, namespace: str, input: str
) -> List[Tuple[Document, float]]:
    docs = vector_db.similarity_search_with_relevance_scores(input, 4)

    if docs[0][1] - docs[1][1] > 0.2:
        return [docs[0]]

    similar_docs = [(doc, score) for doc, score in docs if score > 0.8]

    if len(similar_docs) > 1:
        print("Warning: multiple highly similar documents returned")

    return similar_docs

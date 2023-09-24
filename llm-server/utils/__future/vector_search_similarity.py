from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document
from typing import List, Tuple

from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document
from typing import List, Tuple, Union


def vector_similarity_search_with_warning(
    vector_db: VectorStore, collection_name: str, input: str
) -> Tuple[List[Tuple[Document, float]], str]:
    """
    Performs similarity search on vector database and returns results with a warning if duplicate documents are found.

    Args:
        vector_db: VectorStore instance to search on
        collection_name: Name of the collection to search
        input: Input vector to search for similar documents

    Returns:
        docs: List of tuples containing (Document, score) for top 4 most similar docs
        warning: String warning message if duplicate documents are found, empty string otherwise

    Example:
        docs, warning = vector_similarity_search_with_warning(vectorstore, "collection", input_vec)
    """

    docs: List[
        Tuple[Document, float]
    ] = vector_db.similarity_search_with_relevance_scores(
        input, 4, collection_name=collection_name
    )

    if docs[0][1] - docs[1][1] > 0.2:
        return ([docs[0]], "Warning: Only one highly similar document found")

    similar_docs = [(doc, score) for doc, score in docs if score > 0.8]

    warning_message = ""
    if len(similar_docs) > 1:
        warning_message = "Warning: Multiple highly similar documents found"

    return (similar_docs, warning_message)

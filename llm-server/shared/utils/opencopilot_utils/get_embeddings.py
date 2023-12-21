import os
import warnings
from functools import lru_cache
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.ollama import OllamaEmbeddings
from .embedding_type import EmbeddingProvider
from langchain.embeddings.base import Embeddings
from utils.get_logger import CustomLogger
from langchain.embeddings.fastembed import FastEmbedEmbeddings


logger = CustomLogger(module_name=__name__)

LOCAL_IP = os.getenv("LOCAL_IP", "host.docker.internal")


@lru_cache(maxsize=1)
def get_embeddings():
    embedding_provider = os.environ.get(
        "EMBEDDING_PROVIDER", EmbeddingProvider.OPENAI.value
    )

    if embedding_provider == EmbeddingProvider.azure.value:
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL_NAME")
        client = os.environ.get("AZURE_OPENAI_API_TYPE")

        # These keys should be set
        # os.environ["OPENAI_API_TYPE"] = "azure"
        # os.environ["OPENAI_API_BASE"] = "https://<your-endpoint.openai.azure.com/"
        # os.environ["OPENAI_API_KEY"] = "your AzureOpenAI key"
        # os.environ["OPENAI_API_VERSION"] = "2023-05-15"
        # os.environ["OPENAI_PROXY"] = "http://your-corporate-proxy:8080"

        return OpenAIEmbeddings(
            deployment=deployment,
            client=client,
            chunk_size=8,
        )

    elif embedding_provider == EmbeddingProvider.openchat.value:
        logger.info("Got ollama embedding provider", provider=embedding_provider)
        return OllamaEmbeddings(base_url=f"{LOCAL_IP}:11434", model="openchat")

    elif (
        embedding_provider == EmbeddingProvider.OPENAI.value
        or embedding_provider is None
    ):
        if embedding_provider is None:
            warnings.warn("No embedding provider specified. Defaulting to OpenAI.")
        return OpenAIEmbeddings()
    elif embedding_provider == EmbeddingProvider.fastembed.value:
        return FastEmbedEmbeddings()

    else:
        available_providers = ", ".join(
            [service.value for service in EmbeddingProvider]
        )
        raise ValueError(
            f"Embedding service '{embedding_provider}' is not currently available. "
            f"Available services: {available_providers}"
        )

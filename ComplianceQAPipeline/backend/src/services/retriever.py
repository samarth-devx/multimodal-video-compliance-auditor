from typing import Protocol

from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

from backend.src.config import Settings
from backend.src.schemas import Rule


class RuleRetriever(Protocol):
    """Anything that can return policy rules for a query (Azure AI Search, an in-memory fake for tests, etc.)."""

    def search(self, query: str, k: int = 3) -> list[Rule]: ...


def build_vector_store(settings: Settings) -> AzureSearch:
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=settings.embedding_deployment,
        azure_endpoint=settings.openai_endpoint,
        api_key=settings.openai_api_key,
        openai_api_version=settings.openai_api_version,
    )
    return AzureSearch(
        azure_search_endpoint=settings.search_endpoint,
        azure_search_key=settings.search_api_key,
        index_name=settings.search_index,
        embedding_function=embeddings.embed_query,
    )


class AzureSearchRetriever:
    def __init__(self, store: AzureSearch):
        self._store = store

    def search(self, query: str, k: int = 3) -> list[Rule]:
        docs = self._store.similarity_search(query, k=k)
        return [Rule(text=d.page_content, source=d.metadata.get("source", "unknown")) for d in docs]
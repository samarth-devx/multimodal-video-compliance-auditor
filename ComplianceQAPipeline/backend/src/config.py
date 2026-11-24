import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

_REQUIRED = (
    "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_INDEX_NAME",
    "AZURE_VI_ACCOUNT_ID", "AZURE_VI_LOCATION",
    "AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP",
)


@dataclass(frozen=True)
class Settings:
    openai_endpoint: str
    openai_api_key: str
    openai_api_version: str
    chat_deployment: str
    embedding_deployment: str
    search_endpoint: str
    search_api_key: str
    search_index: str
    vi_account_id: str
    vi_location: str
    vi_name: str
    subscription_id: str
    resource_group: str
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    load_dotenv(override=True)
    missing = [name for name in _REQUIRED if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    env = os.environ
    return Settings(
        openai_endpoint=env["AZURE_OPENAI_ENDPOINT"],
        openai_api_key=env["AZURE_OPENAI_API_KEY"],
        openai_api_version=env.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        chat_deployment=env["AZURE_OPENAI_CHAT_DEPLOYMENT"],
        embedding_deployment=env.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
        search_endpoint=env["AZURE_SEARCH_ENDPOINT"],
        search_api_key=env["AZURE_SEARCH_API_KEY"],
        search_index=env["AZURE_SEARCH_INDEX_NAME"],
        vi_account_id=env["AZURE_VI_ACCOUNT_ID"],
        vi_location=env["AZURE_VI_LOCATION"],
        vi_name=env.get("AZURE_VI_NAME", "mvca-vi"),
        subscription_id=env["AZURE_SUBSCRIPTION_ID"],
        resource_group=env["AZURE_RESOURCE_GROUP"],
        cors_origins=tuple(env.get("CORS_ORIGINS", "http://localhost:3000").split(",")),
    )
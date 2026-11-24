from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, StateGraph

from backend.src.config import Settings, get_settings
from backend.src.graph.nodes import AuditNodes
from backend.src.graph.state import AuditState
from backend.src.services.judge import ComplianceJudge
from backend.src.services.retriever import AzureSearchRetriever, build_vector_store
from backend.src.services.video_indexer import VideoIndexerClient


def _stop_on_error(next_node: str):
    def route(state: AuditState) -> str:
        return END if state.get("errors") else next_node
    return route


def build_graph(settings: Settings | None = None):
    s = settings or get_settings()
    llm = AzureChatOpenAI(
        azure_deployment=s.chat_deployment,
        azure_endpoint=s.openai_endpoint,
        api_key=s.openai_api_key,
        openai_api_version=s.openai_api_version,
        temperature=0.0,
    )
    nodes = AuditNodes(
        indexer=VideoIndexerClient(s),
        retriever=AzureSearchRetriever(build_vector_store(s)),
        judge=ComplianceJudge(llm),
    )

    g = StateGraph(AuditState)
    g.add_node("extract_evidence", nodes.extract_evidence)
    g.add_node("retrieve_rules", nodes.retrieve_rules)
    g.add_node("judge", nodes.judge_content)

    g.set_entry_point("extract_evidence")
    g.add_conditional_edges("extract_evidence", _stop_on_error("retrieve_rules"))
    g.add_conditional_edges("retrieve_rules", _stop_on_error("judge"))
    g.add_edge("judge", END)
    return g.compile()
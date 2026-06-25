import json
import os
import logging
import re
from typing import Dict, Any

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.messages import SystemMessage, HumanMessage

from backend.src.graph.state import VideoAuditState
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("mvca")
logging.basicConfig(level=logging.INFO)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.0
)

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

vector_store = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    embedding_function=embeddings.embed_query
)


def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")
    local_filename = f"{video_id_input}.mp4"

    logger.info(f"--- [Node: Indexer] Processing: {video_url} ---")

    try:
        vi_service = VideoIndexerService()

        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            raise Exception("Please provide a valid YouTube URL.")

        azure_video_id = vi_service.upload_video(local_path, video_name=video_id_input)
        logger.info(f"Upload Success. Azure ID: {azure_video_id}")

        if os.path.exists(local_path):
            os.remove(local_path)

        raw_insights = vi_service.wait_for_processing(azure_video_id)
        clean_data = vi_service.extract_data(raw_insights)

        logger.info("--- [Node: Indexer] Extraction Complete ---")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer Failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": []
        }


def audit_content_node(state: VideoAuditState) -> Dict[str, Any]:
    logger.info("--- [Node: Auditor] Querying Knowledge Base & LLM ---")

    transcript = state.get("transcript", "")

    if not transcript:
        logger.warning("No transcript available. Skipping Audit.")
        return {
            "final_status": "FAIL",
            "final_report": "Audit skipped because video processing failed (No Transcript)."
        }

    ocr_text = state.get("ocr_text", [])
    query_text = f"{transcript} {' '.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text, k=3)
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])

    system_prompt = f"""
You are a Senior Brand Compliance Auditor specializing in FTC regulations, YouTube ad policies, and influencer marketing guidelines.

OFFICIAL REGULATORY RULES FROM KNOWLEDGE BASE:
{retrieved_rules}

YOUR JOB - Check for ALL of the following:
1. FTC DISCLOSURE — Is there a clear paid partnership/sponsorship disclosure?
2. CLAIM VALIDATION — Are product claims substantiated? Any absolute guarantees?
3. CELEBRITY/INFLUENCER ENDORSEMENT — Is the endorser's relationship to the brand disclosed?
4. AD SPECS COMPLIANCE — Does the ad meet YouTube advertising standards?
5. MISLEADING CONTENT — Any deceptive pricing, fake urgency, or exaggerated results?
6. PROFESSIONAL MISREPRESENTATION — Are any doctors/experts shown without verified credentials?
7. TRADEMARK ISSUES — Any unauthorized use of trademarks or copyrighted material?

INSTRUCTIONS:
- Be specific — mention exact phrases or moments from the transcript/OCR that are violations
- Assign severity: CRITICAL (legal risk), MAJOR (serious issue), MODERATE (should fix), WARNING (minor)
- Only flag real violations, not assumptions

Return strictly JSON:
{{
    "compliance_results": [
        {{
            "category": "FTC Disclosure",
            "severity": "CRITICAL",
            "description": "Exact detail of the violation..."
        }}
    ],
    "status": "FAIL",
    "final_report": "Concise professional summary with recommended actions..."
}}

If no violations found, set status to "PASS" and compliance_results to [].
"""

    user_message = f"""
VIDEO METADATA: {state.get('video_metadata', {})}
TRANSCRIPT: {transcript}
ON-SCREEN TEXT (OCR): {ocr_text}
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        content = response.content
        if "```" in content:
            content = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL).group(1)

        audit_data = json.loads(content.strip())

        return {
            "compliance_results": audit_data.get("compliance_results", []),
            "final_status": audit_data.get("status", "FAIL"),
            "final_report": audit_data.get("final_report", "No report generated.")
        }

    except Exception as e:
        logger.error(f"Auditor Node Error: {str(e)}")
        logger.error(f"Raw LLM Response: {response.content if 'response' in locals() else 'None'}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL"
        }
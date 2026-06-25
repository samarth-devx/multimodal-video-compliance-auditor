import os
import glob
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("indexer")


def index_docs():
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

    required_vars = [
        "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_INDEX_NAME"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return

    try:
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        return

    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    try:
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search: {e}")
        return

    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder}")
        return

    logger.info(f"Found {len(pdf_files)} PDFs: {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            splits = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            ).split_documents(loader.load())
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            all_splits.extend(splits)
            logger.info(f"{os.path.basename(pdf_path)} → {len(splits)} chunks")
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")

    if all_splits:
        try:
            vector_store.add_documents(documents=all_splits)
            logger.info(f"✅ Indexing Complete! Total chunks: {len(all_splits)}")
        except Exception as e:
            logger.error(f"Failed to upload to Azure Search: {e}")
    else:
        logger.warning("No documents processed.")


if __name__ == "__main__":
    index_docs()
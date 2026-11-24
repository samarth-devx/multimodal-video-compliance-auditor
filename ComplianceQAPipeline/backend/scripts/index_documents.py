import glob
import logging
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.src.config import get_settings
from backend.src.services.retriever import build_vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("indexer")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")


def index_docs():
    store = build_vector_store(get_settings())
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    pdfs = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdfs:
        logger.warning("No PDFs found in %s", DATA_DIR)
        return

    chunks = []
    for pdf in pdfs:
        splits = splitter.split_documents(PyPDFLoader(pdf).load())
        for s in splits:
            s.metadata["source"] = os.path.basename(pdf)
        chunks.extend(splits)
        logger.info("%s -> %d chunks", os.path.basename(pdf), len(splits))

    store.add_documents(chunks)
    logger.info("Indexing complete. Total chunks: %d", len(chunks))


if __name__ == "__main__":
    index_docs()
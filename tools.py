# ---------------------------------------
# Financial Document Q&A - Tools
# ---------------------------------------

import os
from langchain_community.document_loaders import PyPDFLoader


def read_financial_document(file_path: str) -> str:
    """
    Reads a PDF file and returns cleaned full text content.
    """

    if not file_path:
        raise ValueError("File path is required.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    full_text = ""

    for doc in documents:
        content = doc.page_content.strip()

        while "\n\n" in content:
            content = content.replace("\n\n", "\n")

        full_text += content + "\n"

    if not full_text.strip():
        raise ValueError("The PDF appears to be empty or unreadable.")

    return full_text
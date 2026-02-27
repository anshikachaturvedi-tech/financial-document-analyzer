# ---------------------------------------
# Financial Document Q&A - Task
# ---------------------------------------

from crewai import Task
from agents import financial_analyst


analyze_financial_document = Task(
    description=(
        "You are given the full content of a financial document below:\n\n"
        "{document_content}\n\n"

        "Your task is to answer the user's query:\n"
        "{query}\n\n"

        "Important Instructions:\n"
        "- Use ONLY the information present in the document.\n"
        "- If the answer is not available in the document, clearly state that.\n"
        "- Do NOT fabricate data.\n"
        "- Be clear and concise.\n"
    ),

    expected_output=(
        "A clear and accurate answer to the user's query based strictly "
        "on the provided document content."
    ),

    agent=financial_analyst,
    async_execution=False,
)
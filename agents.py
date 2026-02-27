# ---------------------------------------
# Financial Document Q&A - Agents
# ---------------------------------------

import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from crewai import LLM


# -------------------------------
# GROQ LLM SETUP
# -------------------------------
llm = LLM(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2,
)


# -------------------------------
# FINANCIAL DOCUMENT ANALYST
# -------------------------------
financial_analyst = Agent(
    role="Financial Document Analyst",

    goal=(
        "Answer user queries accurately using ONLY the provided financial document content. "
        "Do not fabricate information. If the answer is not found in the document, clearly state it."
    ),

    backstory=(
        "You are an expert financial analyst who carefully reads financial documents "
        "and provides precise, factual responses. You prioritize accuracy and clarity "
        "over assumptions or speculation."
    ),

    verbose=True,
    memory=False,
    llm=llm,
    max_iter=3,
    allow_delegation=False,
)
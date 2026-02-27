import os
from dotenv import load_dotenv
from crewai import LLM

# Disable verbose logging
os.environ["LITELLM_LOG"] = "ERROR"

load_dotenv()

llm = LLM(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = llm.call("Explain revenue growth in simple terms.")
print(response)
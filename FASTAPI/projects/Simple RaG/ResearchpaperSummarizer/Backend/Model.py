from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
def model():
    llm = ChatOpenAI(
    model = "arcee-ai/trinity-large-preview:free",
    temperature = 0.9,
    base_url = "https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "RAG with Langchain"
    }
)
    return llm
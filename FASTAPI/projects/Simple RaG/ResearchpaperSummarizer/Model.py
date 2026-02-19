import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import JSONResponse
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun 
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()

load_dotenv()

class Query(BaseModel):
    query: Annotated[str, Field(description="The query to be processed by the LLM")]
    

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


########################### TOOLS #######################################
try:
    api_wrapper = WikipediaAPIWrapper(top_k=1, doc_content_chars_max=500)
    arxiv_api_wrapper = ArxivAPIWrapper(top_k=2, doc_content_chars_max=1000)
    wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)   
    tools = [wiki_tool, arxiv_tool]
except Exception as e:
    print(f"Error initializing tools: {e}")
    tools = []

############################ CHAINS And Retrivers #####################################
@app.post("/llm")
def main(Query: Query):
    
    llm = model()
    agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        """You are a research assistant that explains academic papers in depth.
1. Always use the registered tools (Wikipedia, Arxiv) to gather evidence; never hallucinate.
2. As soon as the tools return relevant passages, synthesize them into a detailed explanation covering motivation, methodology, math, experiments, results, and implications. Structure the answer clearly (Introduction → Architecture/Method → Training/Experiments → Findings → Practical impact).
3. If every tool call fails or finds nothing, respond exactly with “I don’t know.”
4. Never ask the user for confirmation; they already gave the paper title.
5. Mention tool sources inline (e.g., “(Arxiv tool)”) and note any gaps if evidence is incomplete.
6. If user query is not about research papers, respond with I can only answer questions about academic research papers. And if it's about research paper just explain the paper according to the above instructions."""
    ),
)
    inputs = {"messages": [{"role": "user", "content": Query.query}]}
    result = agent.invoke(inputs)

    answer = result["messages"][-1].content
    return JSONResponse(status_code=200, content = {"response": answer})
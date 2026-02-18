import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, Path, HTTPException
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun 
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain.agents import create_agent

app = FastAPI()

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


########################### TOOLS #######################################
api_wrapper = WikipediaAPIWrapper(top_k=2, doc_content_chars_max=1000)
arxiv_api_wrapper = ArxivAPIWrapper(top_k=2, doc_content_chars_max=1000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)   
tools = [wiki_tool, arxiv_tool]

############################ CHAINS And Retrivers #####################################
app.post("llm/{query}")
def main(Query):
    
    llm = model()
    agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a helpful assistant who answers questions with the help of tools. "
        "You have access to the following tools:\n{tools}\n"
        "If you still don't know the answer after using the tools, say \"I don't know\"."
    ),
)
    inputs = {"messages": [{"role": "user", "content": Query}]}
    result = agent.invoke(inputs)


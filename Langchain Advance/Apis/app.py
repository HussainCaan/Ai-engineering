from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn 
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title = "Langchain APi",
    version="1.0.0",
    description="An simple API for langchain using FASTAPI and Langserve"
)

add_routes(
    app,
    ChatOpenAI(),
    path="/chat"
)

model = ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",
    temperature = 0.4,
    base_url = "https://openrouter.ai/api/v1",
    default_headers = {
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)
model2 = ChatOpenAI(
    model="liquid/lfm-2.5-1.2b-thinking:free",
    temperature = 0.4,
    base_url = "https://openrouter.ai/api/v1",
    default_headers = {
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

prompt1 = ChatPromptTemplate.from_template("Write me a poem about {topic} in 4 lines.")
prompt2 = ChatPromptTemplate.from_template("Write me a eassy about {topic} in 4 lines.")


add_routes(
    app,
    prompt1 | model | StrOutputParser(),
)
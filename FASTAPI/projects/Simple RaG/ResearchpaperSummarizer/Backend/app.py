import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain.agents import create_agent
from Query import Query
from Model import model
from Tools import tools
from Prompt import prompt
app = FastAPI()

MODEL_VERSION = os.getenv("MODEL_VERSION", "arcee-ai/trinity-large-preview:free")

######################## API Endpoints #####################################
@app.get("/")
def read_root():
    return {"message": "Welcome to the Research Paper Assistant API. Use the /llm endpoint to analyze research papers."}

@app.get("/health")
def health_check():
    
    return {"status": "ok", "message": "API is healthy and running.", "model_version": MODEL_VERSION}

@app.post("/llm")
def main(Query: Query):
    
    llm = model()
    agent = create_agent(
    model=llm,
    tools=tools(),
    system_prompt= prompt(),
)
    try:
        inputs = {"messages": [{"role": "user", "content": Query.query}]}
        result = agent.invoke(inputs)

        answer = result["messages"][-1].content
        return JSONResponse(status_code=200, content = {"response": answer})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
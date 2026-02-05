from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that help with user queries."),
    ("user", "Question: {question}"),
])


st.title("Chatbot using Open Source LLM")
input_question = st.text_input("Enter your question:")

llm = ChatOpenAI(
    model = "arcee-ai/trinity-large-preview:free",
    temperature = 0.4,
    base_url = "https://openrouter.ai/api/v1",
    default_headers = {
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
    
)
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

if input_question:
    st.write("Generating response...")
    response = chain.invoke({"question": input_question})
    st.write("Response: ", response)



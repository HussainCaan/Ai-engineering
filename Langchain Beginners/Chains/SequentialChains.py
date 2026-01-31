from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

prompt = PromptTemplate(
    template = "You are a professional financial advisor who manage user risk and rewards and Provide  key insights about stocks. Now help user to make a decision with this {stock_name} stock\n\n",
    input_variables = ["stock_name"]
)
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

result = chain.invoke({"Meezan Bank Limited"})
print(result)
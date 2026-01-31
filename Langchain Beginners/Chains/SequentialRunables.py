from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
load_dotenv()

llm = ChatOpenAI(
    model="arcee-ai/trinity-mini:free",  
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

prompt1 = PromptTemplate(
    template="Generate a Joke related to the stock market for the stock {stock_name}.\n\n",
    input_variables=["stock_name"]
)

prompt2 = PromptTemplate(
    template="Explain the following joke in simple terms: {joke}\n\n",
    input_variables=["joke"]
)
output_parser = StrOutputParser()

chain = RunnableSequence(prompt1, llm, output_parser, prompt2, llm, output_parser)

result = chain.invoke({"Apple Inc."})
print(result)

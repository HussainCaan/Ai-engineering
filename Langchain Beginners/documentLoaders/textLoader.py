from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
# Initialize the loader with the path to your text file
loader = TextLoader("cricket.txt", encoding= "utf-8")


model = ChatOpenAI(
    model="arcee-ai/trinity-mini:free",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

docs = loader.load()

prompt = PromptTemplate(
    template = "Give me a detailed summary of the following document: {document}\n\n",
    input_variables = ["document"]
)

parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"document": docs[0].page_content})
print(result)
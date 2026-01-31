# PyPDF loader is good for simple PDF loading needs. They re good for extracting text from PDFs without complex formatting or structure.
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

document_path = "tasks_01.pdf"  
document = PyPDFLoader(document_path)
docs = document.load()

model = ChatOpenAI(
    model="arcee-ai/trinity-mini:free",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)
# print(docs[0].metadata)

prompt = PromptTemplate(
    template = "Give me a detailed summary of the following document: {document}\n\n",
    input_variables = ["document"]
)

parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"document": docs[0].page_content})
print(result)

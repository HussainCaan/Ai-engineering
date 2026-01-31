# from langchain_community.document_loaders import PDFPlumberLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import UnstructuredPDFLoader
load_dotenv()

loader = UnstructuredPDFLoader(
    "financial_report.pdf",
    strategy="ocr_only"   # 👈 THIS is the key
)

docs = loader.load()

# print(len(docs), "pages loaded")

model = ChatOpenAI(
    model = "xiaomi/mimo-v2-flash:free",
    temperature = 0.4,
    base_url = "https://openrouter.ai/api/v1",
    default_headers = {
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

prompt = PromptTemplate(
    template = "Analyze the whole document extract these list of important information about financial of the company. Extract in a proper json format with proper key and value: -> {document}\n\n"
    "If not explicitly mentioned, check if they are there with some other names or similar meanings if yes provide the values, else return 'Not Available' for that field.\n\n",
    input_variables = ["document"]
)

parser = StrOutputParser()
chain = prompt | model | parser

chain_result = chain.invoke({
    "document": docs,
})

print(chain_result)
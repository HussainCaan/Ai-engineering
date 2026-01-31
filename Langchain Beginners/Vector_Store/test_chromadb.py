from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
load_dotenv()

loader = PyPDFLoader("tasks_01.pdf")

docs = loader.load()
# doc

vector_store = Chroma(
    embedding_function = OpenAIEmbeddings(),
    persist_directory= "My_chroma_db",
    collection_name= "tasks_01_collection"
)

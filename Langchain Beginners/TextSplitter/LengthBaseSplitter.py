# Length based text splitting can be done by Character, Word or token count.
# It's simple and fast 
# But may split in the middle of sentences or important context. No Semantic understanding.
# If no sementic understanding is required and speed is important, this is a good choice.
# But if sementic is required, and we use this so embedding won't capture full context.

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("tasks_01.pdf")

pages = loader.load()

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=10, # Advantage of overlap is some context is carried forward to next chunk. i-e may be the context pass on to next chunk.
    separator=''
)
result = splitter.split_documents(pages)
print(result[0].page_content)


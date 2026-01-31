from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader(
    "financial_report.pdf",
    strategy="ocr_only"   # 👈 THIS is the key
)

docs = loader.load()

print(len(docs))
print(docs[0].page_content[:500])

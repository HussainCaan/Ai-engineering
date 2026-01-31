from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever(
    top_k=5,
    language="en",
    summary_length=3,
)
docs = retriever.invoke("Artificial Intelligence")
print(len(docs))
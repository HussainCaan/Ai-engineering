# Other retrievers usually search based on similarity or relevance.
# MMR (Maximal Marginal Relevance) retrievers aim to balance relevance and diversity in the results.
# MMR try to select documents that are not only relevant to the query but also diverse from each other, so that the user gets a broader perspective on the topic.

from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever(
    top_k=5,
    language="en",
    search_type="mmr",  # Specify MMR search type
    summary_length=3,
    lambda_mult=0.5  # Balance between relevance and diversity
)

docs = retriever.invoke("What is Artificial Intelligence and its applications?")

for i, doc in enumerate(docs):
    print(f"Document {i+1}:\n{doc.page_content}\n")
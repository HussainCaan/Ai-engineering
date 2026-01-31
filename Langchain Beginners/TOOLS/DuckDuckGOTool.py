from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

# Perform a search
query = "latest AI news"
result = search.invoke(query)

# Print the result
print(result)
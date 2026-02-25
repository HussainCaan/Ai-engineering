from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun 
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun


########################### TOOLS #######################################
def tools():
    try:
        api_wrapper = WikipediaAPIWrapper(top_k=1, doc_content_chars_max=500)
        arxiv_api_wrapper = ArxivAPIWrapper(top_k=2, doc_content_chars_max=1000)
        wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)   
        tools = [wiki_tool, arxiv_tool]
        return tools
    except Exception as e:
        print(f"Error initializing tools: {e}")
        tools = []
    
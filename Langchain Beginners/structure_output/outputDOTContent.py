from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts  import PromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model="xiaomi/mimo-v2-flash:free",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

# First prompt -> detailed report
template1 = PromptTemplate(
    template="Write a detailed report on the following topic:\n\n{topic}\n\nReport:",
    input_variables=["topic"]
)

# Second prompt -> concise summary
    
template2 = PromptTemplate(
    template="Write a 5 line summary of following text: {text}\n\nSummary:",
    input_variables=["text"]
)
prompt1 = template1.invoke("Black Hole Physics")

result = llm.invoke(prompt1)

prompt2 = template2.invoke(input=result.content)
summary = llm.invoke(prompt2)
print("Detailed Report:\n", result.content)
print("\nConcise Summary:\n", summary.content)
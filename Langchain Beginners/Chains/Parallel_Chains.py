from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

model1 = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

model2 = ChatOpenAI(
    model="arcee-ai/trinity-mini:free",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

prompt1 = PromptTemplate(
    template="You are a profesional financial advisor who get key insights for stocks. Provide key insights about the stock {stock_name} and it's financial records like EPS, Dept, Market cap and few more important factors.\n\n",
    input_variables=["stock_name"]
)

prompt2 = PromptTemplate(
    template="You are a professional financial advisor for analyzing risk and reward. Based on the following insights: {insights}, analyze the risk and reward for this {stock_name} stock.\n\n",
    input_variables=["insights", "stock_name"]
)

prompt3 = PromptTemplate(
    template="You are a professional financial advisor who help user to make decisions. Based on the following insights: {insights}, and {risk_reward_analysis}, help user to buy or not this {stock_name} stock\n\n",
    input_variables=["insights", "stock_name"]
)

parser = StrOutputParser()

# Chains -----------------------------------------------------------------------------------------------------------------------------------------
insights_chain = prompt1 | model1 | parser

risk_reward_chain = (
    {'insights': insights_chain, 'stock_name': RunnablePassthrough()}
    | prompt2
    | model2
    | parser
)

decision_chain = (
    {
        'insights': insights_chain,
        'risk_reward_analysis': risk_reward_chain,
        'stock_name': RunnablePassthrough()
    }
    | prompt3
    | model1
    | parser
)

# End Chains -------------------------------------------------------------------------------------------------------------------------------------
result = decision_chain.invoke({
    "stock_name": "Meezan Bank Limited"
})
print(result)
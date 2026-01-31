from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnablePassthrough

load_dotenv()

model = ChatOpenAI(
    model="arcee-ai/trinity-mini:free",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project" 
    }
)

prompt1 = PromptTemplate(
    template = "Analyze the following stock for the data {data} and get key insights about the stock {stock_name}.\n\n",
    input_variables = ["data", "stock_name"]
)

prompt2 = PromptTemplate(
    template = "Extact the important financial records like EPS, Market cap etc from the given Data: {data} for the stock {stock_name}.\n\n",
    input_variables = ["data", "stock_name"]
)
prompt3 = PromptTemplate(
    template = "Based on the following insights: {insights}, and financial records: {financials}, help user to buy or not this {stock_name} stock\n\n",
    input_variables = ["insights", "financials", "stock_name"]
)

parser = StrOutputParser()

# Chains -----------------------------------------------------------------------------------------------------------------------------------------
parallel_chain = RunnableParallel({
    'insight': RunnableSequence(prompt1, model, parser),
    'financials': RunnableSequence(prompt2, model, parser)
}
)

decision_chain = (
    parallel_chain
    | {
        "insights": lambda x: x["insight"],
        "financials": lambda x: x["financials"],
        "stock_name": RunnablePassthrough(),
    }
    | prompt3
    | model
    | parser
)

result = decision_chain.invoke({"data":"""Company Financial Snapshot – ABC Industries Ltd.

Earning-to-Price Ratio: 6.25%
Indicates the company generates stable earnings relative to its share price.

Price-to-Earning Ratio: 16
Shows the stock is fairly valued in the market.

Market Capitalization: PKR 150 Billion
Reflects a strong and stable large-cap company.

Dividend Yield: 3.8%
Provides a reasonable return to shareholders through dividends.

Summary: ABC Industries Ltd. appears financially stable with balanced valuation and steady returns.""", "stock_name": "ABC Industries Ltd."})

print(result)
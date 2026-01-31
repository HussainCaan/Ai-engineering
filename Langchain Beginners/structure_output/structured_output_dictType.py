from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

import os

load_dotenv()

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

class StructureOutputDictType(BaseModel):
    EarntoPriceRatio: Optional[str]
    PriceToEarningsRatio: Optional[str]
    Market_Capitalization: Optional[str]
    Dividend_Yield: Optional[str]
    sentiment_analysis: Optional[str]
    

structuredModel = llm.with_structured_output(StructureOutputDictType)

result = structuredModel.invoke("""Company Financial Snapshot – ABC Industries Ltd.

Earning-to-Price Ratio: 6.25%
Indicates the company generates stable earnings relative to its share price.

Price-to-Earning Ratio: 16
Shows the stock is fairly valued in the market.

Market Capitalization: PKR 150 Billion
Reflects a strong and stable large-cap company.

Dividend Yield: 3.8%
Provides a reasonable return to shareholders through dividends.

Summary: ABC Industries Ltd. appears financially stable with balanced valuation and steady returns.""")
print(result)


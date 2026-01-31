from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Student(BaseModel):
    name: str
    email: Optional[EmailStr] = None

    
newstudent = Student(name="Alice")

print(newstudent)
# we can also convert to dictionary

Student_dict = dict(newstudent)
# print(Student_dict)

# ALso we can convert to JSON
Student_json = newstudent.model_dump_json()
print(Student_json)

# Now let's see how we can use this with langchain structured output--------------------------------

load_dotenv()

class StructureOutputDictType(BaseModel):
    key_themes: list[str] = Field(description="List of key themes discussed in the text")
    summary: str = Field(description="A concise summary of the text")
    phone_Name: Optional[str] = Field(description="Name of the phone mentioned in the text, if any")
    sentiment_analysis: Optional[str] = Field(description="Sentiment analysis of the text, if applicable, e.g., positive, negative, neutral")
    pros: Optional[list[str]] = Field(description="List of pros mentioned in the text, if any")
    cons: Optional[list[str]] = Field(description="List of cons mentioned in the text, if any")    


llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.4,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "LangChain Learning Project"
    }
)

structured_model = llm.with_structured_output(StructureOutputDictType)

result = structured_model.invoke("""The Nova X10 comes with a sleek design and a bright, smooth display that makes everyday use comfortable. Day-to-day tasks like browsing, social media, and video streaming run smoothly, and the battery easily lasts a full day under normal usage. In good lighting, the camera captures sharp and vibrant photos.

However, performance can slow down slightly when running heavy apps or games, and low-light camera results are average. Fast charging is supported, but the charger included in the box is not the fastest available in this price range.

Overall, the Nova X10 is a well-balanced mid-range smartphone that offers good value for everyday users, especially those who prioritize design, display, and battery life.""")

print(result)

to_json = result.model_dump_json()

with open("structured_output.json", "w") as f:
    f.write(to_json)

print("Structured output saved to structured_output.json")
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id= "meta-llama/Llama-3.1-8B-Instruct",
    task= "text-generation"
)
chat_history = []
model = ChatHuggingFace(llm=llm)
while True:
    user_input = input('You: ')
    chat_history.append(user_input)
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting the chatbot. Goodbye!")
        break
    response = model.invoke(chat_history)
    chat_history.append(response.content)
    print('Bot:', response.content)
    
print("Chat session ended and this is the chat history: ", chat_history)

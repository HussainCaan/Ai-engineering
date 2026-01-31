from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


chat_template = ChatPromptTemplate([
    ("system", "You are a helpful {domain} expert"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])
chat_history = []

# load chat history placeholder
with open("chat_history.txt", "r") as f:
    chat_history.extend(f.readlines())


prompts = chat_template.invoke({'chat_history': chat_history, 'question': 'What is Newton Third Law?','domain':'physics and science'})

print(prompts)
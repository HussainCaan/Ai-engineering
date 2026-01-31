from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

llm = HuggingFacePipeline(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    model_kwargs={"temperature": 0.7, "max_new_tokens": 512}
)

model = ChatHuggingFace(llm=llm)
result = model.invoke("What is capital of Pakistan?")
print(result.content)
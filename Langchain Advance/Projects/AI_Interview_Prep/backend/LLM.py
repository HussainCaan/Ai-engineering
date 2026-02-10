from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from pydantic import BaseModel

import os
import json
import tempfile


load_dotenv()

app = FastAPI(title="AI Interview Prep Backend")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


def load_text(file_path: str, content_type: str) -> str:
	if content_type == "application/pdf":
		loader = PyPDFLoader(file_path)
		docs = loader.load()
		return "\n".join([d.page_content for d in docs])

	if content_type in {
		"application/msword",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	}:
		try:
			import docx2txt
		except ImportError as exc:  # keep this simple: prompt to install
			raise HTTPException(status_code=500, detail="Install docx2txt to parse DOC/DOCX") from exc
		return docx2txt.process(file_path) or ""

	raise HTTPException(status_code=400, detail="Unsupported file type")


def split_and_embed(text: str):
	splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
	chunks = splitter.split_text(text)
	if not chunks:
		raise HTTPException(status_code=400, detail="No text extracted from document")

	embeddings = CohereEmbeddings(
		model="embed-english-light-v3.0",
		cohere_api_key=os.getenv("COHERE_API_KEY"),
	)
	vectors = embeddings.embed_documents(chunks)
	return chunks, vectors


def build_store(chunks, vectors, source: str):
	embeddings = CohereEmbeddings(
		model="embed-english-light-v3.0",
		cohere_api_key=os.getenv("COHERE_API_KEY"),
	)
	text_embeddings = [(chunk, vector) for chunk, vector in zip(chunks, vectors)]
	metadatas = [{"source": source, "index": i} for i in range(len(chunks))]
	
	return FAISS.from_embeddings(text_embeddings, embeddings, metadatas=metadatas)


prompt = ChatPromptTemplate.from_messages([
	(
		"system",
		"""
		You are an interview coach. Use the provided context (candidate CV + job description) to ask targeted interview questions.
		Prioritize projects, responsibilities, and skills that align with the job description. Keep each turn concise: one question at a time.
		If the user's last answer is provided, briefly critique correctness and clarity, then ask the next question.
		""".strip(),
	),
	(
		"system",
		"Context you can use:\n{context}\n\nShort chat history (Q/A):\n{chat_history}\n\nUser's last answer (if any): {user_answer}",
	),
	(
		"user",
		"Generate the next interview question. If user_answer is non-empty, first give a brief critique (2-3 sentences), then the next question.",
	),
])

score_prompt = ChatPromptTemplate.from_messages([
	(
		"system",
		"""
		You are an interview evaluator. Read the following short transcript of interview
		questions and answers. Provide a JSON object with keys:
		- score: integer 1-10 reflecting how strong the candidate is
		- feedback: concise (<=60 words) guidance on improvement.
		Return ONLY valid JSON.
		""".strip(),
	),
	(
		"user",
		"Conversation transcript:\n{chat_history}\n\nRespond with JSON now.",
	),
])


# Step 2: model + document chain
def get_model():
	return ChatOpenAI(
		model="arcee-ai/trinity-large-preview:free",
		temperature=0.9,
		base_url="https://openrouter.ai/api/v1",
		default_headers={
			"HTTP-Referer": "http://localhost:8000",
			"X-Title": "RAG with Langchain",
		},
	)

def get_chain():
	model = get_model()
	return create_stuff_documents_chain(model, prompt)


def format_chat_history(limit: int = 20, only_complete: bool = False) -> str:
	if not chat_history_list:
		return ""
	# Filter to only completed Q/A pairs if requested (for scoring)
	items = chat_history_list if not only_complete else [
		item for item in chat_history_list if item.get('answer')
	]
	window = items[-limit:]
	return "\n\n".join(
		f"Question: {item.get('question', '').strip()}\nAnswer: {item.get('answer', '').strip() or '(no answer)'}"
		for item in window
	)



cv_store = None
jd_store = None
chat_history_list = []  


@app.post("/reset")
async def reset_session():
	"""Clear all session state - CV, JD, and chat history."""
	global cv_store, jd_store, chat_history_list
	cv_store = None
	jd_store = None
	chat_history_list = []
	return {"message": "Session reset"}


@app.post("/analyze")
async def analyze_profile(
	resume: UploadFile = File(...),
	job_description: str = Form(...),
):
	global cv_store, jd_store, chat_history_list

	# Basic validation of file type
	allowed_types = {
		"application/pdf",
		"application/msword",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	}
	if resume.content_type not in allowed_types:
		raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or DOCX.")


	upload_dir = os.path.join(tempfile.gettempdir(), "ai_interview_uploads")
	os.makedirs(upload_dir, exist_ok=True)
	file_path = os.path.join(upload_dir, resume.filename)

	with open(file_path, "wb") as f:
		content = await resume.read()
		f.write(content)

	text = load_text(file_path, resume.content_type)
	chunks, vectors = split_and_embed(text)

	jd_chunks, jd_vectors = split_and_embed(job_description)

	cv_store = build_store(chunks, vectors, source="CV")
	jd_store = build_store(jd_chunks, jd_vectors, source="JD")
	chat_history_list = []  

	return {
		"message": "Processed",
		"filename": resume.filename,
		"chunks": len(chunks),
		"embedding_dimension": len(vectors[0]) if vectors else 0,
		"sample_chunk": chunks[0][:300],
		"job_description_chunks": len(jd_chunks),
		"job_description_sample": jd_chunks[0][:200] if jd_chunks else "",
		"job_description_preview": job_description[:200],
	}


class ChatRequest(BaseModel):
	user_answer: str = ""


@app.post("/chat/next")
async def chat_next(req: ChatRequest):
	global cv_store, jd_store, chat_history_list

	if cv_store is None or jd_store is None:
		raise HTTPException(status_code=400, detail="Run /analyze first to upload CV and JD")

	if chat_history_list and req.user_answer:
		chat_history_list[-1]["answer"] = req.user_answer

	query = req.user_answer or "generate interview question"
	cv_docs = cv_store.similarity_search(query, k=3)
	jd_docs = jd_store.similarity_search(query, k=2)
	context_docs = cv_docs + jd_docs

	history_str = ""
	if chat_history_list:
		history_str = "\n".join(
			f"Q: {item['question']}\nA: {item['answer']}" for item in chat_history_list[-3:]
		)

	chain = get_chain()
	result = chain.invoke({
		"context": context_docs,
		"chat_history": history_str,
		"user_answer": req.user_answer,
	})

	# Parse result: assume it contains critique (if any) + next question
	# For simplicity, store the entire result as the next question
	chat_history_list.append({"question": result, "answer": ""})

	return {
		"question": result,
		"history_length": len(chat_history_list),
	}


@app.post("/chat/score")
async def chat_score():
	# Check if we have at least one completed Q/A pair (some entries may have empty answers)
	completed_pairs = [item for item in chat_history_list if item.get("answer")]
	if not completed_pairs:
		raise HTTPException(status_code=400, detail="Complete at least one Q/A before scoring")

	model = get_model()
	history_str = format_chat_history(only_complete=True)  # Only score completed Q/A pairs
	messages = score_prompt.format_messages(chat_history=history_str)
	response = model.invoke(messages)
	content = getattr(response, "content", response)

	try:
		payload = json.loads(content)
	except json.JSONDecodeError as exc:
		raise HTTPException(status_code=500, detail=f"Scoring model returned invalid JSON: {content}") from exc

	score = payload.get("score")
	feedback = payload.get("feedback", "")
	if score is None:
		raise HTTPException(status_code=500, detail="Score missing from model response")

	try:
		score_value = max(1, min(10, round(float(score))))
	except (TypeError, ValueError) as exc:
		raise HTTPException(status_code=500, detail="Score must be numeric") from exc

	return {
		"score": score_value,
		"feedback": feedback,
		"entries": len(chat_history_list),
	}

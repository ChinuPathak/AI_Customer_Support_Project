from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
from chatPrompt import build_prompt
from faq import faq
import redis
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

chroma_client = chromadb.HttpClient(host='localhost', port=8001)
collection = chroma_client.get_or_create_collection(name="my_collection1")
# chat_collection = chroma_client.get_or_create_collection(name="chat_memory")

app = FastAPI()
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development (later restrict this)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_name: str
    message: str             

secret_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key = secret_key)
model = genai.GenerativeModel("gemini-2.5-flash")


if collection.count() == 0:
    print("Loading FAQ into ChromaDB...")
    for data in faq:
        document = f"""
        Question: {data['question']}
        Answer: {data['answer']}
        """

        collection.add(
            documents=[document],
            ids=[data['id']],
            metadatas=[{"category": data["category"]}]
        )

def extract_answer(doc):
    if "Answer:" in doc:
        return doc.split("Answer:")[1].strip()
    return None


@app.post("/chat")
def chat(request: ChatRequest):
    print("request>>>>>>>>>>>>>>" , request)
    name = request.user_name
    print(name)
    query = request.message
    print(query)
    chatName = f"chat:{name}"
    print(chatName)

    chat_collection = chroma_client.get_or_create_collection(
        name=f"chat_memory_{name}"
    )

    chat_results = chat_collection.query(
        query_texts=[query],
        n_results=1
    )
    print("chat result>>>>>>>>>>>>>>>>>>" , chat_results)

    if (
        chat_results["documents"]
        and len(chat_results["documents"][0]) > 0
        and chat_results["distances"][0][0] < 0.2 
    ):
        print("🔥 Semantic Cache Hit")
        return {
            "response": chat_results["metadatas"][0][0]["answer"]
        }

    print("❌ Cache Miss")

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    print(results)
    doc = results['documents'][0][0]
    response = extract_answer(doc)
    print("response>>>>>>>>>>>>>" , response)
    # prompt = build_prompt(results, query)
    # response = model.generate_content(prompt)

    chat_collection.add(
        documents=[query],
        ids=[str(uuid4())],
        metadatas=[{
            "user": name,
            "answer": response
        }]
    )
    
    if not redis_client.exists(chatName):
        redis_client.json().set(chatName, "$", [])

    chat_data = {
        "question": query,
        "answer": response
    }

    redis_client.json().arrappend(chatName, "$", chat_data)

    return {
        "response": response
    }

@app.get("/history/{username}")
def get_history(username: str): 
    chatName = f"chat:{username}"

    if not redis_client.exists(chatName):
        return {"history": []}

    data = redis_client.json().get(chatName)
    return {"history": data}

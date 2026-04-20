from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
import chromadb
from chatPrompt import build_prompt
from faq import faq
import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

chroma_client = chromadb.HttpClient(host='localhost', port=8001)
collection = chroma_client.get_or_create_collection(name="my_collection1")

app = FastAPI()
load_dotenv()

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

@app.post("/chat")
def chat(request: ChatRequest):
    name = request.user_name
    print(name)
    query = request.message
    print(query)
    chatName = f"chat:{name}"
    print(chatName)

    cached_data = redis_client.json().get(chatName)

    if cached_data:
        for item in cached_data:
            if item["question"] == query:
                print("Cache Hit")
                return {
                    "response": item["answer"]
                }
    
    # Query data
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    print(results)
    prompt = build_prompt(results, query)
    response = model.generate_content(prompt)
    
    if not redis_client.exists(chatName):
        redis_client.json().set(chatName, "$", [])

    chat_data = {
        "question": query,
        "answer": response.text
    }

    redis_client.json().arrappend(chatName, "$", chat_data)

    return {
        "response": response.text
    }
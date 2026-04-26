# 🤖 AI Customer Support System (Semantic Search-Based)

A lightweight AI customer support backend built with **FastAPI**, using **semantic search (vector database)** instead of LLMs to provide fast and accurate responses from a predefined FAQ dataset.

This system is optimized for **speed, scalability, and cost-efficiency** by avoiding real-time LLM calls and leveraging **ChromaDB semantic caching** and **Redis for chat history**.

---

## 🚀 Key Features

* 🔍 **Semantic Search (ChromaDB)**

  * Finds the most relevant answer using vector similarity.
  * No keyword matching — understands intent.

* ⚡ **Semantic Caching (Per User)**

  * Stores previous queries in vector DB.
  * If a similar query is asked again → instant response (no recomputation).

* 🧠 **LLM-Free Architecture**

  * Currently **not using any LLM**
  * Responses are directly retrieved from FAQ embeddings.

* 💾 **Chat History (Redis)**

  * Stores conversation history per user.
  * Used for frontend display (not for caching responses).

* 👤 **User-Based Memory**

  * Each user has their own semantic memory collection.

* 🌐 **FastAPI Backend**

  * Clean and high-performance API.

---

## 🏗️ Tech Stack

* **Backend:** FastAPI
* **Vector Database:** ChromaDB
* **Cache/Storage:** Redis (JSON)
* **AI/Embeddings:** ChromaDB default embeddings
* **Language:** Python

---

## 📂 Project Structure

```id="struct01"
ai-customer-support/
│
├── main.py              # Main FastAPI application
├── faq.py               # FAQ dataset
├── chatPrompt.py        # (Optional - currently unused)
├── .env                 # API keys (not required currently)
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

### 1. FAQ Initialization

* On server start, FAQs are embedded and stored in **ChromaDB**.
* Each entry is stored as:

```text id="faqfmt"
Question: ...
Answer: ...
```

---

### 2. User Query Flow

1. User sends:

   ```json
   {
     "user_name": "chinmay",
     "message": "Do you provide invoices?"
   }
   ```

2. System checks **user-specific semantic cache**:

   * Collection: `chat_memory_<username>`
   * If similar query found (`distance < 0.2`) → return cached answer

3. If cache miss:

   * Query main FAQ collection
   * Extract answer from best match

4. Store result:

   * Save in **user semantic cache (ChromaDB)**
   * Save in **Redis (chat history)**

5. Return response

---

## 🧠 Semantic Cache Logic

```python id="semcache"
if distance < 0.2:
    return cached_answer
```

* Lower distance = higher similarity
* Threshold can be tuned based on accuracy needs

---

## 📡 API Endpoints

### 🔹 POST `/chat`

#### Request

```json id="chatreq"
{
  "user_name": "john",
  "message": "How can I get invoice?"
}
```

#### Response

```json id="chatres"
{
  "response": "Yes, invoices are available in the 'My Orders' section."
}
```

---

### 🔹 GET `/history/{username}`

#### Example

```
GET /history/john
```

#### Response

```json id="histres"
{
  "history": [
    {
      "question": "How can I get invoice?",
      "answer": "Yes, invoices are available in the 'My Orders' section."
    }
  ]
}
```

---

## 🗄️ Data Storage Design

### 📌 ChromaDB

| Collection Name      | Purpose                    |
| -------------------- | -------------------------- |
| `my_collection1`     | Stores FAQ embeddings      |
| `chat_memory_<user>` | Stores user semantic cache |

---

### 📌 Redis

| Key Format    | Purpose                          |
| ------------- | -------------------------------- |
| `chat:<user>` | Stores chat history (JSON array) |

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash id="clone01"
git clone https://github.com/your-username/ai-customer-support.git
cd ai-customer-support
```

---

### 2. Create Virtual Environment

```bash id="venv01"
python -m venv venv
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash id="install01"
pip install -r requirements.txt
```

---

### 4. Start Services

#### 🔹 Start Redis

```bash id="redis01"
redis-server
```

#### 🔹 Start ChromaDB

```bash id="chroma01"
chroma run --host localhost --port 8001
```

---

### 5. Run Backend

```bash id="run01"
uvicorn main:app --reload
```

---

## ⚠️ Important Notes

* ❌ **LLM is currently NOT used**
* ⚠️ `chatPrompt.py` and Gemini setup are unused (can be removed or used later)
* ⚡ System is optimized for **low latency and zero AI cost**

---

## 🔮 Future Improvements

* 🤖 Add LLM fallback for unknown queries
* 📊 Admin dashboard for FAQ management
* 🌍 Multi-language support
* 📈 Analytics for user queries
* 🧠 Hybrid (Semantic + LLM) system

---

## 🤝 Contributing

Feel free to contribute:

1. Fork the repo
2. Create a new branch
3. Make changes
4. Submit PR

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Chinmay Pathak**

---

⭐ If you found this helpful, consider giving it a star!

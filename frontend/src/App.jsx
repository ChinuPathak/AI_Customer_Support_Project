import { useState, useEffect, useRef } from "react";
import "./App.css";

export default function ChatUI() {
  const [userName, setUserName] = useState("");     // input value
  const [activeUser, setActiveUser] = useState(""); // actual session user

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  // 🔥 Auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // 🔥 Detect user change (debounced)
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (userName && userName !== activeUser) {
        setActiveUser(userName);

        // ✅ Reset everything instantly
        setMessages([]);
        setHistory([]);
        setExpandedIndex(null);
      }
    }, 500); // wait 500ms after typing stops

    return () => clearTimeout(timeout);
  }, [userName]);

  // 🔥 Load history (sidebar only)
  const loadHistory = async () => {
    if (!activeUser) return;

    const res = await fetch(`http://localhost:8000/history/${activeUser}`);
    const data = await res.json();

    setHistory(data.history || []);
  };

  // 🔥 Toggle history answer
  const toggleHistory = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeUser) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_name: activeUser, // ✅ important change
          message: input,
        }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.response },
      ]);

      loadHistory(); // refresh sidebar
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="layout">

      {/* SIDEBAR */}
      <div className="sidebar">
        <h2>💬 Chats</h2>

        <button onClick={loadHistory}>Load History</button>

        <div className="history-list">
          {history.map((item, i) => (
            <div key={i} className="history-item">

              {/* QUESTION */}
              <div onClick={() => toggleHistory(i)}>
                {item.question}
              </div>

              {/* ANSWER (toggle) */}
              {expandedIndex === i && (
                <div className="history-answer">
                  {item.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* MAIN CHAT */}
      <div className="main">

        {/* HEADER */}
        <div className="header">
          <h1>🤖 AI Support</h1>
          <input
            placeholder="Enter your name..."
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
          />
        </div>

        {/* CHAT AREA */}
        <div className="chat-container">

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`message ${
                msg.role === "user" ? "user" : "bot"
              }`}
            >
              {msg.text}
            </div>
          ))}

          {/* 🔥 Typing animation */}
          {loading && (
            <div className="typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* INPUT */}
        <div className="input-area">
          <input
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Send 🚀</button>
        </div>
      </div>
    </div>
  );
}

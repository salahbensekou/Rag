import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const question = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Error calling backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h1>Quorium RAG Chatbot</h1>
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 16,
          minHeight: 300,
          marginBottom: 16,
          overflowY: "auto",
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              marginBottom: 12,
              textAlign: m.role === "user" ? "right" : "left",
            }}
          >
            <div
              style={{
                display: "inline-block",
                padding: 8,
                borderRadius: 8,
                background:
                  m.role === "user" ? "#d0ebff" : "#e9ecef",
              }}
            >
              <strong>{m.role === "user" ? "You" : "Assistant"}</strong>
              <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
              {m.sources && m.sources.length > 0 && (
                <div style={{ marginTop: 4, fontSize: 12 }}>
                  Sources: {m.sources.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div>Thinking...</div>}
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={3}
        style={{ width: "100%", marginBottom: 8 }}
        placeholder="Ask something about the documents..."
      />
      <button onClick={handleSend} disabled={loading}>
        Send
      </button>
    </div>
  );
}

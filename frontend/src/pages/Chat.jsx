import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  const isProf = msg.role === 'professor';

  const bubbleStyle = {
    ...styles.bubble,
    alignSelf: isUser ? 'flex-end' : 'flex-start',
    background: isUser ? '#1a73e8' : isProf ? '#2e7d32' : '#f1f3f4',
    color: isUser || isProf ? '#fff' : '#1a1a2e',
    borderBottomRightRadius: isUser ? 4 : 18,
    borderBottomLeftRadius: isUser ? 18 : 4,
  };

  return (
    <div style={{ alignSelf: isUser ? 'flex-end' : 'flex-start', maxWidth: '75%' }}>
      {isProf && <div style={styles.profLabel}>👨‍⚕️ Dr. Professor</div>}
      <div style={bubbleStyle}>
        {msg.content.split('\n').map((line, i) => (
          <span key={i}>{line}{i < msg.content.split('\n').length - 1 && <br />}</span>
        ))}
      </div>
      <div style={{ ...styles.timestamp, textAlign: isUser ? 'right' : 'left' }}>
        {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
      </div>
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [convId, setConvId] = useState(null);
  const bottomRef = useRef(null);
  const navigate = useNavigate();
  const name = localStorage.getItem('name') || 'Patient';
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetch('/api/conversation', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        setConvId(data.conversation_id);
        setMessages(data.messages.length > 0 ? data.messages : [{
          role: 'assistant',
          content: `Hello ${name}! 👋 I'm your orthodontic assistant. I'm here to answer questions about your treatment, braces, or oral hygiene. How can I help you today?`,
          created_at: new Date().toISOString(),
        }]);
      })
      .catch(() => navigate('/login'));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', content: input.trim(), created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('/api/conversation/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content: userMsg.content }),
      });
      const data = await res.json();
      if (res.ok) setMessages(prev => [...prev, data]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I had trouble responding. Please try again.', created_at: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.clear();
    navigate('/login');
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.headerIcon}>🦷</span>
          <div>
            <div style={styles.headerTitle}>Orthodontic Assistant</div>
            <div style={styles.headerSub}>Always here to help</div>
          </div>
        </div>
        <div style={styles.headerRight}>
          <span style={styles.userName}>👤 {name}</span>
          <button onClick={logout} style={styles.logoutBtn}>Sign out</button>
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => <MessageBubble key={i} msg={msg} />)}
        {loading && (
          <div style={{ ...styles.bubble, background: '#f1f3f4', alignSelf: 'flex-start', color: '#666' }}>
            <span style={styles.typing}>● ● ●</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} style={styles.inputRow}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question about your treatment..."
          style={styles.textInput}
          disabled={loading}
        />
        <button type="submit" style={styles.sendBtn} disabled={loading || !input.trim()}>
          ➤
        </button>
      </form>
    </div>
  );
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', height: '100vh', background: '#fafafa', fontFamily: 'Inter,sans-serif' },
  header: { background: '#1a73e8', color: '#fff', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 2px 8px rgba(0,0,0,0.15)' },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 12 },
  headerIcon: { fontSize: 28 },
  headerTitle: { fontWeight: 700, fontSize: 16 },
  headerSub: { fontSize: 12, opacity: 0.8 },
  headerRight: { display: 'flex', alignItems: 'center', gap: 12 },
  userName: { fontSize: 14 },
  logoutBtn: { background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff', padding: '6px 14px', borderRadius: 20, cursor: 'pointer', fontSize: 13 },
  messages: { flex: 1, overflowY: 'auto', padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 8 },
  bubble: { padding: '12px 16px', borderRadius: 18, fontSize: 14, lineHeight: 1.5, maxWidth: '100%', wordBreak: 'break-word' },
  profLabel: { fontSize: 11, fontWeight: 600, color: '#2e7d32', marginBottom: 4, paddingLeft: 4 },
  timestamp: { fontSize: 10, color: '#aaa', marginTop: 3, paddingHorizontal: 4 },
  typing: { fontSize: 18, letterSpacing: 4, animation: 'pulse 1s infinite' },
  inputRow: { padding: '12px 16px', background: '#fff', borderTop: '1px solid #eee', display: 'flex', gap: 10, alignItems: 'center' },
  textInput: { flex: 1, padding: '12px 16px', borderRadius: 24, border: '1.5px solid #ddd', fontSize: 14, outline: 'none', fontFamily: 'Inter,sans-serif' },
  sendBtn: { width: 44, height: 44, borderRadius: '50%', background: '#1a73e8', color: '#fff', border: 'none', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' },
};

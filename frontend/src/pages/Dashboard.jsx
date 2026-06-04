import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [selected, setSelected] = useState(null);
  const [thread, setThread] = useState(null);
  const [reply, setReply] = useState('');
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  function authHeaders() {
    return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  }

  useEffect(() => {
    fetch('/api/professor/patients', { headers: authHeaders() })
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(setPatients)
      .catch(() => navigate('/login'));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [thread]);

  async function loadThread(patient) {
    setSelected(patient);
    const res = await fetch(`/api/professor/patients/${patient.id}/messages`, { headers: authHeaders() });
    const data = await res.json();
    setThread(data);
  }

  async function sendReply(e) {
    e.preventDefault();
    if (!reply.trim() || !selected) return;
    setSending(true);
    await fetch(`/api/professor/patients/${selected.id}/reply`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ content: reply }),
    });
    setReply('');
    await loadThread(selected);
    setSending(false);
  }

  function logout() {
    localStorage.clear();
    navigate('/login');
  }

  function roleColor(role) {
    if (role === 'user') return '#1a73e8';
    if (role === 'professor') return '#2e7d32';
    return '#555';
  }

  function roleLabel(role) {
    if (role === 'user') return thread?.patient_name || 'Patient';
    if (role === 'professor') return '👨‍⚕️ You';
    return '🤖 AI Assistant';
  }

  return (
    <div style={styles.page}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.sideHeader}>
          <span style={{ fontSize: 24 }}>🦷</span>
          <div>
            <div style={styles.sideTitle}>Professor Dashboard</div>
            <div style={styles.sideSub}>{patients.length} patient{patients.length !== 1 ? 's' : ''}</div>
          </div>
        </div>

        <div style={styles.patientList}>
          {patients.length === 0 && <div style={styles.empty}>No patients yet</div>}
          {patients.map(p => (
            <div
              key={p.id}
              style={{ ...styles.patientCard, background: selected?.id === p.id ? '#e8f0fe' : '#fff' }}
              onClick={() => loadThread(p)}
            >
              <div style={styles.avatar}>{p.name[0].toUpperCase()}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={styles.patientName}>{p.name}</div>
                <div style={styles.lastMsg}>{p.last_message || 'No messages yet'}</div>
                {p.last_active && (
                  <div style={styles.lastTime}>{new Date(p.last_active).toLocaleDateString()}</div>
                )}
              </div>
            </div>
          ))}
        </div>

        <button onClick={logout} style={styles.logoutBtn}>Sign out</button>
      </div>

      {/* Main panel */}
      <div style={styles.main}>
        {!selected ? (
          <div style={styles.placeholder}>
            <div style={{ fontSize: 64 }}>💬</div>
            <div style={{ fontSize: 18, fontWeight: 600, marginTop: 16, color: '#555' }}>Select a patient to view their conversation</div>
          </div>
        ) : (
          <>
            <div style={styles.threadHeader}>
              <div style={styles.avatar}>{selected.name[0].toUpperCase()}</div>
              <div>
                <div style={styles.threadName}>{selected.name}</div>
                <div style={styles.threadEmail}>{selected.email}</div>
              </div>
            </div>

            <div style={styles.messages}>
              {thread?.messages?.length === 0 && (
                <div style={styles.empty}>No messages yet</div>
              )}
              {thread?.messages?.map((msg, i) => (
                <div key={i} style={{ ...styles.msgRow, justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 11, color: roleColor(msg.role), marginBottom: 3, fontWeight: 600, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                      {roleLabel(msg.role)}
                    </div>
                    <div style={{
                      ...styles.bubble,
                      background: msg.role === 'user' ? '#e8f0fe' : msg.role === 'professor' ? '#e8f5e9' : '#f1f3f4',
                      borderBottomRightRadius: msg.role === 'user' ? 4 : 18,
                      borderBottomLeftRadius: msg.role === 'user' ? 18 : 4,
                    }}>
                      {msg.content}
                    </div>
                    <div style={{ fontSize: 10, color: '#aaa', marginTop: 3, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                      {new Date(msg.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <form onSubmit={sendReply} style={styles.replyRow}>
              <input
                value={reply}
                onChange={e => setReply(e.target.value)}
                placeholder={`Reply to ${selected.name} as Dr. Professor...`}
                style={styles.replyInput}
                disabled={sending}
              />
              <button type="submit" style={styles.sendBtn} disabled={sending || !reply.trim()}>
                Send
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: { display: 'flex', height: '100vh', fontFamily: 'Inter,sans-serif', background: '#f5f6fa' },
  sidebar: { width: 300, background: '#fff', borderRight: '1px solid #e8eaed', display: 'flex', flexDirection: 'column' },
  sideHeader: { padding: '20px 16px', background: '#1a73e8', color: '#fff', display: 'flex', alignItems: 'center', gap: 12 },
  sideTitle: { fontWeight: 700, fontSize: 15 },
  sideSub: { fontSize: 12, opacity: 0.8 },
  patientList: { flex: 1, overflowY: 'auto', padding: 8 },
  patientCard: { display: 'flex', alignItems: 'center', gap: 12, padding: '12px', borderRadius: 10, cursor: 'pointer', marginBottom: 4, transition: 'background 0.15s' },
  avatar: { width: 40, height: 40, borderRadius: '50%', background: '#1a73e8', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 16, flexShrink: 0 },
  patientName: { fontWeight: 600, fontSize: 14, color: '#1a1a2e' },
  lastMsg: { fontSize: 12, color: '#888', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 180 },
  lastTime: { fontSize: 11, color: '#bbb', marginTop: 2 },
  logoutBtn: { margin: 12, padding: '10px', borderRadius: 8, background: '#f1f3f4', border: 'none', color: '#555', cursor: 'pointer', fontWeight: 600 },
  main: { flex: 1, display: 'flex', flexDirection: 'column' },
  placeholder: { flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' },
  threadHeader: { padding: '16px 20px', background: '#fff', borderBottom: '1px solid #e8eaed', display: 'flex', alignItems: 'center', gap: 14 },
  threadName: { fontWeight: 700, fontSize: 16, color: '#1a1a2e' },
  threadEmail: { fontSize: 13, color: '#888' },
  messages: { flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 12 },
  msgRow: { display: 'flex' },
  bubble: { padding: '10px 14px', borderRadius: 16, fontSize: 14, lineHeight: 1.5, maxWidth: 480, wordBreak: 'break-word' },
  replyRow: { padding: '12px 20px', background: '#fff', borderTop: '1px solid #e8eaed', display: 'flex', gap: 10 },
  replyInput: { flex: 1, padding: '11px 16px', borderRadius: 24, border: '1.5px solid #ddd', fontSize: 14, outline: 'none', fontFamily: 'Inter,sans-serif' },
  sendBtn: { padding: '10px 22px', borderRadius: 24, background: '#1a73e8', color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: 14 },
  empty: { textAlign: 'center', color: '#aaa', padding: 32, fontSize: 14 },
};

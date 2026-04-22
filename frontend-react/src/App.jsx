import { useState, useRef, useEffect } from "react";
import "./index.css";
import { login, register, chatQuery, getStaffProfile, toggleAvailability, addSchedule, updateStaffProfile, addTextData, uploadFile, getUsers, getDocuments } from "./api";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [role, setRole] = useState(localStorage.getItem("role"));
  const [view, setView] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const chatEnd = useRef(null);

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  const handleLogout = () => {
    localStorage.removeItem("token"); localStorage.removeItem("role");
    setToken(null); setRole(null); setMessages([]); setView("chat");
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const data = await chatQuery(q, token);
      setMessages((m) => [...m, { role: "assistant", text: data.answer || data.error, intent: data.intent }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Connection error. Is the backend running?" }]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } };

  if (!token) return <AuthScreen onLogin={(t, r) => { setToken(t); setRole(r); localStorage.setItem("token", t); localStorage.setItem("role", r); }} />;

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header"><span style={{ fontSize: 20 }}>🎓</span><h2>Campus OS</h2></div>
        <button className="new-chat-btn" onClick={() => { setMessages([]); setView("chat"); }}>+ New Chat</button>
        <nav className="sidebar-nav">
          <div className={`nav-item ${view === "chat" ? "active" : ""}`} onClick={() => setView("chat")}>💬 Assistant</div>
          {role === "staff" && <div className={`nav-item ${view === "faculty" ? "active" : ""}`} onClick={() => setView("faculty")}>👩‍🏫 Faculty Hub</div>}
          {role === "admin" && <div className={`nav-item ${view === "admin" ? "active" : ""}`} onClick={() => setView("admin")}>🛠️ Admin Center</div>}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{role?.[0]?.toUpperCase()}</div>
            <div className="user-details"><div className="user-name">{role}</div><div className="user-role">{role}</div></div>
            <button className="logout-btn" onClick={handleLogout} title="Logout">⏻</button>
          </div>
        </div>
      </aside>

      <div className="main-area">
        {view === "chat" ? (
          <>
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <h2>Campus AI</h2>
                  <p>Ask anything about DSCE — placements, admissions, departments, faculty availability, or campus life.</p>
                  <div className="suggestion-chips">
                    {[
                      { t: "Placements", s: "Tell me about DSCE placement statistics" },
                      { t: "Faculty", s: "When can I meet Shreya mam?" },
                      { t: "Departments", s: "What departments does DSCE offer?" },
                      { t: "Events", s: "What is Catalysis v4?" },
                    ].map((c) => (
                      <div key={c.t} className="chip" onClick={() => { setInput(c.s); }}>
                        <div className="chip-title">{c.t}</div>{c.s}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((m, i) => (
                  <div key={i} className={`message-row ${m.role}`}>
                    <div className="message-content">
                      <div className={`message-avatar ${m.role === "user" ? "user-msg" : "ai-msg"}`}>
                        {m.role === "user" ? "U" : "AI"}
                      </div>
                      <div className="message-text">
                        {m.text.split("\n").map((line, j) => <p key={j}>{line}</p>)}
                        {m.intent && <div className="message-meta">Source: {m.intent}</div>}
                      </div>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="message-row assistant">
                  <div className="message-content">
                    <div className="message-avatar ai-msg">AI</div>
                    <div className="thinking"><span /><span /><span /></div>
                  </div>
                </div>
              )}
              <div ref={chatEnd} />
            </div>
            <div className="input-area">
              <div className="input-wrapper">
                <textarea className="input-box" rows={1} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} placeholder="Ask anything about DSCE..." />
                <button className="send-btn" onClick={handleSend} disabled={loading || !input.trim()}>↑</button>
              </div>
              <div className="input-footer">Campus AI OS — Powered by DSCE Knowledge Base</div>
            </div>
          </>
        ) : view === "faculty" ? (
          <FacultyPanel token={token} showToast={showToast} />
        ) : (
          <AdminPanel token={token} showToast={showToast} />
        )}
      </div>
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function AuthScreen({ onLogin }) {
  const [tab, setTab] = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authRole, setAuthRole] = useState("student");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleLogin = async () => {
    setError("");
    try {
      const data = await login(username, password);
      onLogin(data.access_token, data.role);
    } catch (e) { setError(e.message); }
  };

  const handleRegister = async () => {
    setError(""); setSuccess("");
    try {
      await register(username, email, password, authRole);
      setSuccess("Account created! Switch to Login.");
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-logo"><h1>Campus AI OS</h1><p>Dayananda Sagar College of Engineering</p></div>
        <div className="auth-tabs">
          <button className={`auth-tab ${tab === "login" ? "active" : ""}`} onClick={() => setTab("login")}>Login</button>
          <button className={`auth-tab ${tab === "register" ? "active" : ""}`} onClick={() => setTab("register")}>Register</button>
        </div>
        <div className="form-group"><label>Username</label><input value={username} onChange={(e) => setUsername(e.target.value)} /></div>
        {tab === "register" && <div className="form-group"><label>Email</label><input value={email} onChange={(e) => setEmail(e.target.value)} /></div>}
        <div className="form-group"><label>Password</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        {tab === "register" && (
          <div className="form-group"><label>Role</label>
            <select value={authRole} onChange={(e) => setAuthRole(e.target.value)}>
              <option value="student">Student</option><option value="staff">Faculty</option><option value="admin">Admin</option>
            </select>
          </div>
        )}
        <button className="auth-btn" onClick={tab === "login" ? handleLogin : handleRegister}>{tab === "login" ? "Access Hub" : "Create Account"}</button>
        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}
      </div>
    </div>
  );
}

function FacultyPanel({ token, showToast }) {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDept, setEditDept] = useState("");
  const [editDesig, setEditDesig] = useState("");
  const [day, setDay] = useState("Monday");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  const reload = () => getStaffProfile(token).then(setProfile);
  useEffect(() => { reload(); }, [token]);

  const startEdit = () => {
    setEditName(profile.name); setEditDept(profile.dept); setEditDesig(profile.designation);
    setEditing(true);
  };

  const saveProfile = async () => {
    await updateStaffProfile(editName, editDept, editDesig, token);
    setEditing(false);
    await reload();
    showToast("Profile updated!");
  };

  if (!profile) return <div className="panel-view"><div className="panel-content">Loading...</div></div>;

  return (
    <div className="panel-view">
      <div className="panel-header"><h1>Faculty Hub</h1><p>Manage your profile, availability, and consultation hours</p></div>
      <div className="panel-content">
        <div className="grid-2">
          <div className="card">
            <h3>Availability Status</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: 13, marginBottom: 12 }}>
              Toggle this ON when you are available for student meetings.
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div className={`toggle-switch ${profile.availability ? "on" : ""}`}
                onClick={async () => {
                  await toggleAvailability(!profile.availability, token);
                  setProfile({ ...profile, availability: !profile.availability });
                  showToast(profile.availability ? "Marked as unavailable" : "Marked as available");
                }} />
              <span style={{ fontWeight: 600, color: profile.availability ? "var(--accent)" : "var(--danger)" }}>
                {profile.availability ? "✅ Available for meetings" : "❌ Not available"}
              </span>
            </div>
          </div>
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3>My Profile</h3>
              {!editing && <button className="card-btn" style={{ marginTop: 0, padding: "6px 14px", fontSize: 13 }} onClick={startEdit}>Edit</button>}
            </div>
            {editing ? (
              <>
                <div className="form-group"><label>Full Name</label><input value={editName} onChange={(e) => setEditName(e.target.value)} /></div>
                <div className="form-group"><label>Department</label>
                  <select value={editDept} onChange={(e) => setEditDept(e.target.value)} style={{ padding: "12px 14px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)", width: "100%" }}>
                    {["ISE", "CSE", "AIML", "ECE", "EEE", "ME", "CV", "BT", "CH", "AE", "MCA", "MBA", "Physics", "Chemistry", "Mathematics"].map(d => <option key={d}>{d}</option>)}
                  </select>
                </div>
                <div className="form-group"><label>Designation</label>
                  <select value={editDesig} onChange={(e) => setEditDesig(e.target.value)} style={{ padding: "12px 14px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)", width: "100%" }}>
                    {["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "HOD", "Dean"].map(d => <option key={d}>{d}</option>)}
                  </select>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button className="card-btn" onClick={saveProfile}>Save</button>
                  <button className="card-btn" style={{ background: "var(--bg-hover)" }} onClick={() => setEditing(false)}>Cancel</button>
                </div>
              </>
            ) : (
              <>
                <p><strong>Name:</strong> {profile.name}</p>
                <p><strong>Department:</strong> {profile.dept}</p>
                <p><strong>Designation:</strong> {profile.designation}</p>
              </>
            )}
          </div>
        </div>
        <div className="card">
          <h3>Consultation Hours (When students can meet you)</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: 13, marginBottom: 12 }}>
            Add the time slots when you are <strong>free and available</strong> for student consultations. Students will see these hours when they ask the AI assistant about your availability.
          </p>
          {profile.schedule?.length > 0 ? (
            <table className="data-table">
              <thead><tr><th>Day</th><th>Available From</th><th>Available Until</th></tr></thead>
              <tbody>{profile.schedule.map((s, i) => <tr key={i}><td>{s.day}</td><td>{s.start}</td><td>{s.end}</td></tr>)}</tbody>
            </table>
          ) : <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>No consultation hours set. Students won't know when to meet you.</p>}
          <div style={{ display: "flex", gap: 10, marginTop: 16, alignItems: "end", flexWrap: "wrap" }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label>Day</label>
              <select value={day} onChange={(e) => setDay(e.target.value)} style={{ padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)" }}>
                {["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"].map(d => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}><label>Free From</label><input value={start} onChange={(e) => setStart(e.target.value)} placeholder="e.g. 10:00 AM" /></div>
            <div className="form-group" style={{ margin: 0 }}><label>Free Until</label><input value={end} onChange={(e) => setEnd(e.target.value)} placeholder="e.g. 11:30 AM" /></div>
            <button className="card-btn" onClick={async () => {
              if (!start || !end) { showToast("Please fill both time fields"); return; }
              await addSchedule(day, start, end, token);
              await reload();
              setStart(""); setEnd("");
              showToast("Consultation hours added!");
            }}>Add Available Hours</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function AdminPanel({ token, showToast }) {
  const [subTab, setSubTab] = useState("snap");
  const [snippet, setSnippet] = useState("");
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("Rules");
  const [content, setContent] = useState("");
  const [users, setUsers] = useState([]);
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    if (subTab === "system") {
      getUsers(token).then(setUsers);
      getDocuments(token).then(setDocs);
    }
  }, [subTab, token]);

  return (
    <div className="panel-view">
      <div className="panel-header"><h1>Admin Command Center</h1><p>Manage campus knowledge and system users</p></div>
      <div className="panel-content">
        <div className="panel-tabs">
          <button className={`panel-tab ${subTab === "snap" ? "active" : ""}`} onClick={() => setSubTab("snap")}>⚡ Snap Knowledge</button>
          <button className={`panel-tab ${subTab === "formal" ? "active" : ""}`} onClick={() => setSubTab("formal")}>📄 Formal Entry</button>
          <button className={`panel-tab ${subTab === "upload" ? "active" : ""}`} onClick={() => setSubTab("upload")}>📁 Upload</button>
          <button className={`panel-tab ${subTab === "system" ? "active" : ""}`} onClick={() => setSubTab("system")}>📊 System</button>
        </div>

        {subTab === "snap" && (
          <div className="card">
            <h3>Quick Brain Update</h3>
            <p style={{ color: "var(--text-secondary)", marginBottom: 12, fontSize: 14 }}>Add random campus facts instantly. No formal category needed.</p>
            <textarea value={snippet} onChange={(e) => setSnippet(e.target.value)} placeholder="e.g., The highest placement at DSCE this year was 50 LPA for a CSE student." />
            <button className="card-btn" onClick={async () => {
              if (!snippet.trim()) return;
              const title = `Snap_${Date.now()}`;
              await addTextData(title, snippet, "Snap Update", token);
              setSnippet("");
              showToast("Knowledge injected into brain!");
            }}>⚡ Inject into Vector DB</button>
          </div>
        )}

        {subTab === "formal" && (
          <div className="card">
            <h3>Add Formal Knowledge</h3>
            <div className="form-group"><label>Title</label><input value={title} onChange={(e) => setTitle(e.target.value)} /></div>
            <div className="form-group">
              <label>Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ padding: "12px 14px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", borderRadius: 8, color: "var(--text-primary)", width: "100%" }}>
                {["Rules","Events","Notices","Letters","Faculty","Courses"].map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group"><label>Content</label><textarea value={content} onChange={(e) => setContent(e.target.value)} /></div>
            <button className="card-btn" onClick={async () => {
              if (!title || !content) return;
              await addTextData(title, content, category, token);
              setTitle(""); setContent("");
              showToast("Knowledge updated!");
            }}>Update Knowledge Base</button>
          </div>
        )}

        {subTab === "upload" && (
          <div className="card">
            <h3>Bulk Document Upload</h3>
            <p style={{ color: "var(--text-secondary)", marginBottom: 12, fontSize: 14 }}>Upload PDFs or TXT files to expand the knowledge base.</p>
            <input type="file" accept=".pdf,.txt" onChange={async (e) => {
              const file = e.target.files?.[0];
              if (file) {
                const res = await uploadFile(file, token);
                showToast(res.message);
              }
            }} style={{ color: "var(--text-secondary)" }} />
          </div>
        )}

        {subTab === "system" && (
          <div className="grid-2">
            <div className="card">
              <h3>Identity Registry ({users.length} users)</h3>
              <table className="data-table">
                <thead><tr><th>ID</th><th>Username</th><th>Role</th></tr></thead>
                <tbody>{users.map((u) => <tr key={u.id}><td>{u.id}</td><td>{u.username}</td><td><span className="status-badge online">{u.role}</span></td></tr>)}</tbody>
              </table>
            </div>
            <div className="card">
              <h3>Neural Index ({docs.length} docs)</h3>
              <table className="data-table">
                <thead><tr><th>Title</th><th>Category</th><th>Date</th></tr></thead>
                <tbody>{docs.map((d) => <tr key={d.id}><td>{d.title}</td><td>{d.category}</td><td>{d.uploaded_at}</td></tr>)}</tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

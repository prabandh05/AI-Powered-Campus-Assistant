import streamlit as st
import requests
import os
from datetime import datetime

# --- SETTINGS & AESTHETICS ---
st.set_page_config(page_title="Campus AI OS", layout="wide", page_icon="🎓")

API_URL = "http://127.0.0.1:8000"

# Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Premium Cards */
    .premium-card {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Chat Bubbles */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.3) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }

    /* Heartbeat Animation */
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.5; }
        50% { transform: scale(1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.5; }
    }
    .heartbeat {
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: AUTH & STATUS ---
with st.sidebar:
    st.image("https://dsce.edu.in/images/DSCE_Logo_New.png", width=180)
    st.title("Campus OS")
    
    # Backend Heartbeat
    try:
        requests.get(f"{API_URL}/")
        st.markdown('<div><span class="heartbeat"></span> <span style="font-size: 0.8rem; color: #10b981;">Brain Engine Online</span></div>', unsafe_allow_html=True)
    except:
        st.markdown('<div><span class="heartbeat" style="background-color: #ef4444;"></span> <span style="font-size: 0.8rem; color: #ef4444;">Brain Engine Offline</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    if not st.session_state.token:
        auth_mode = st.radio("Access Control", ["Login", "Register"], horizontal=True)
        
        if auth_mode == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Access Hub"):
                try:
                    resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.role = data["role"]
                        st.rerun()
                    else:
                        st.error("Access Denied: Invalid Credentials")
                except: st.error("Link Failure")
        
        else:
            reg_user = st.text_input("Choose Username")
            reg_email = st.text_input("College Email")
            reg_pass = st.text_input("Choose Password", type="password")
            reg_role = st.selectbox("Assign Role", ["student", "staff", "admin"])
            if st.button("Create Profile"):
                if reg_user and reg_pass and reg_email:
                    try:
                        resp = requests.post(f"{API_URL}/auth/register", params={
                            "username": reg_user, "email": reg_email, "password": reg_pass, "role": reg_role
                        })
                        if resp.status_code == 200:
                            st.success("Account Created! You can now login.")
                        else:
                            st.error(resp.json().get("detail", "Registration Error"))
                    except: st.error("Link Failure")
                else:
                    st.warning("All fields are mandatory")
    else:
        st.subheader(f"Session: {st.session_state.role.upper()}")
        if st.button("System Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.caption("AI Grounding: DSCE Knowledge Base v2.1")

# --- MAIN DASHBOARD ---
if not st.session_state.token:
    st.title("Next-Gen Campus Intelligence")
    st.markdown("""
    Welcome to the **DSCE AI Operating System**. 
    A unified platform for academic records, faculty availability, and campus knowledge.
    
    <div class="premium-card">
        <h3>🚀 Ready to Start?</h3>
        <p>Please use the sidebar to login or create a new account.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Navigation Hub
    nav_tabs = ["💬 Brain Chat"]
    if st.session_state.role == "staff": nav_tabs.append("👩‍🏫 Faculty Hub")
    elif st.session_state.role == "admin": nav_tabs.append("🛠️ Admin Center")
    
    active_tab = st.tabs(nav_tabs)
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # --- CHAT HUB ---
    with active_tab[0]:
        st.header("Intelligent Assistant")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "intent" in msg: st.caption(f"Decision: {msg['intent']}")

        if prompt := st.chat_input("Ask anything about DSCE..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Retrieving from Brain Cache..."):
                    try:
                        resp = requests.post(f"{API_URL}/chat/query", params={"query": prompt}, headers=headers)
                        if resp.status_code == 200:
                            data = resp.json()
                            st.markdown(data["answer"])
                            st.session_state.messages.append({"role": "assistant", "content": data["answer"], "intent": data.get("intent")})
                    except Exception as e: st.error(f"Brain Sync Error: {e}")

    # --- FACULTY HUB ---
    if st.session_state.role == "staff":
        with active_tab[1]:
            st.header("Faculty Operations")
            try:
                prof = requests.get(f"{API_URL}/staff/me", headers=headers).json()
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                    st.subheader("Availability")
                    st.write("Toggle your real-time status:")
                    stat = st.toggle("I am Currently Available", value=prof.get("availability", True))
                    if st.button("Update Presence"):
                        requests.post(f"{API_URL}/staff/availability", params={"status": stat}, headers=headers)
                        st.toast("Presence updated!")
                    st.markdown('</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                    st.subheader("Weekly Schedule")
                    for s in prof.get("schedule", []):
                        st.write(f"🔹 **{s['day']}**: {s['start']} - {s['end']}")
                    with st.expander("Add New Slot"):
                        day = st.selectbox("Select Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
                        s_t = st.text_input("Start")
                        e_t = st.text_input("End")
                        if st.button("Lock Slot"):
                            requests.post(f"{API_URL}/staff/schedule", params={"day": day, "start": s_t, "end": e_t}, headers=headers)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            except: st.error("Hub Connection Error")

    # --- ADMIN CENTER ---
    elif st.session_state.role == "admin":
        with active_tab[1]:
            st.header("Admin Command Center")
            st_1, st_2, st_3 = st.tabs(["🧠 Snap Knowledge", "📄 Docs", "👥 System"])
            
            with st_1:
                st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                st.subheader("Rapid Brain Update")
                txt = st.text_area("Neural Injection Content", height=150, placeholder="Paste random campus facts here...")
                if st.button("⚡ Inject Into Vector DB"):
                    if txt:
                        title = f"Snap_{int(datetime.now().timestamp())}"
                        resp = requests.post(f"{API_URL}/admin/add_text_data", 
                                          params={"title": title, "content": txt, "category": "Snap Update"}, headers=headers)
                        st.success(resp.json()["message"])
                st.markdown('</div>', unsafe_allow_html=True)

            with st_2:
                up_file = st.file_uploader("Upload Knowledge PDF/TXT", type=["pdf", "txt"])
                if up_file and st.button("Process Knowledge"):
                    files = {"file": (up_file.name, up_file.getvalue())}
                    resp = requests.post(f"{API_URL}/admin/upload", files=files, headers=headers)
                    st.success(resp.json()["message"])

            with st_3:
                c_u, c_d = st.columns(2)
                with c_u:
                    st.subheader("Identity Registry")
                    st.dataframe(requests.get(f"{API_URL}/admin/users", headers=headers).json(), use_container_width=True)
                with c_d:
                    st.subheader("Neural Index")
                    st.dataframe(requests.get(f"{API_URL}/admin/documents", headers=headers).json(), use_container_width=True)

const API_URL = "http://127.0.0.1:8000";

export async function login(username, password) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Invalid credentials");
  return res.json();
}

export async function register(username, email, password, role) {
  const res = await fetch(
    `${API_URL}/auth/register?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&role=${role}`,
    { method: "POST" }
  );
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Registration failed");
  return data;
}

export async function chatQuery(query, token) {
  const res = await fetch(`${API_URL}/chat/query?query=${encodeURIComponent(query)}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getStaffProfile(token) {
  const res = await fetch(`${API_URL}/staff/me`, { headers: { Authorization: `Bearer ${token}` } });
  return res.json();
}

export async function toggleAvailability(status, token) {
  await fetch(`${API_URL}/staff/availability?status=${status}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function addSchedule(day, start, end, token) {
  await fetch(`${API_URL}/staff/schedule?day=${day}&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function updateStaffProfile(name, dept, designation, token) {
  const params = new URLSearchParams();
  if (name) params.append("name", name);
  if (dept) params.append("dept", dept);
  if (designation) params.append("designation", designation);
  await fetch(`${API_URL}/staff/update_profile?${params.toString()}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function addTextData(title, content, category, token) {
  const res = await fetch(
    `${API_URL}/admin/add_text_data?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}&category=${encodeURIComponent(category)}`,
    { method: "POST", headers: { Authorization: `Bearer ${token}` } }
  );
  return res.json();
}

export async function uploadFile(file, token) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/admin/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return res.json();
}

export async function getUsers(token) {
  const res = await fetch(`${API_URL}/admin/users`, { headers: { Authorization: `Bearer ${token}` } });
  return res.json();
}

export async function getDocuments(token) {
  const res = await fetch(`${API_URL}/admin/documents`, { headers: { Authorization: `Bearer ${token}` } });
  return res.json();
}

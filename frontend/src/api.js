const TOKEN_KEY = 'cb_token'
const USER_KEY = 'cb_user'

export const auth = {
  get token() { return localStorage.getItem(TOKEN_KEY) },
  get user() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null }
  },
  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}

async function request(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
      ...(options.headers || {}),
    },
  })
  if (res.status === 401) {
    auth.clear()
    window.dispatchEvent(new Event('cb-logout'))
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res
}

export async function login(username, password) {
  const res = await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  const data = await res.json()
  auth.save(data.access_token, data.user)
  return data.user
}

export async function listDocuments() {
  return (await request('/api/rag/documents')).json()
}

export function documentUrl(name) {
  return `/api/rag/documents/${encodeURIComponent(name)}?token=${encodeURIComponent(auth.token)}`
}

/** POST a chat message and invoke onEvent for every Server-Sent Event from the agent run. */
export async function streamChat(message, sessionId, onEvent) {
  const res = await request('/api/chat/stream', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split('\n\n')
    buffer = frames.pop()
    for (const frame of frames) {
      const line = frame.split('\n').find((l) => l.startsWith('data: '))
      if (line) onEvent(JSON.parse(line.slice(6)))
    }
  }
}

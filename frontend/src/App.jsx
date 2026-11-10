import { useEffect, useState } from 'react'
import { auth } from './api'
import Login from './components/Login.jsx'
import Chat from './components/Chat.jsx'

export default function App() {
  const [user, setUser] = useState(auth.user)

  useEffect(() => {
    const onLogout = () => setUser(null)
    window.addEventListener('cb-logout', onLogout)
    return () => window.removeEventListener('cb-logout', onLogout)
  }, [])

  if (!user || !auth.token) return <Login onLogin={setUser} />
  return <Chat user={user} onLogout={() => { auth.clear(); setUser(null) }} />
}

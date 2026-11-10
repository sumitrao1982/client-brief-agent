import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { documentUrl, streamChat } from '../api'
import AgentPanel, { AGENTS } from './AgentPanel.jsx'

const SUGGESTIONS = [
  'Prepare me for my meeting with Northwind Logistics tomorrow about refinancing their 2027 notes',
  'Brief me on HLXB — I am meeting their CFO next week',
  'I have a pitch to Aurora Renewable Power on a green hybrid bond. Get me ready.',
]

const LABELS = Object.fromEntries(AGENTS.map((a) => [a.id, a.label]))

function sourceKind(source = '') {
  if (source.includes('RAG')) return 'rag'
  if (source.includes('FactSet')) return 'factset'
  if (source.includes('Web')) return 'web'
  return 'orch'
}

const newSessionId = () => (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()))

export default function Chat({ user, onLogout }) {
  const [sessionId, setSessionId] = useState(newSessionId)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [statuses, setStatuses] = useState({})
  const [toolCounts, setToolCounts] = useState({})
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  function updateLast(fn) {
    setMessages((prev) => {
      const copy = [...prev]
      copy[copy.length - 1] = fn({ ...copy[copy.length - 1] })
      return copy
    })
  }

  async function send(text) {
    const message = (text ?? input).trim()
    if (!message || busy) return
    setInput('')
    setBusy(true)
    setStatuses({})
    setToolCounts({})
    setMessages((prev) => [...prev,
      { role: 'user', text: message },
      { role: 'assistant', events: [], answers: [], drafts: [], status: 'running' }])

    try {
      await streamChat(message, sessionId, (evt) => {
        switch (evt.type) {
          case 'agent_start':
            setStatuses((s) => ({ ...s, [evt.agent]: 'running' }))
            break
          case 'agent_done':
            setStatuses((s) => ({ ...s, [evt.agent]: 'done' }))
            break
          case 'tool_call':
            setToolCounts((c) => ({ ...c, [evt.agent]: (c[evt.agent] || 0) + 1 }))
            updateLast((m) => ({ ...m, events: [...m.events, evt] }))
            break
          case 'tool_result':
            updateLast((m) => ({ ...m, events: [...m.events, evt] }))
            break
          case 'message':
            updateLast((m) => (evt.final
              ? { ...m, answers: [...m.answers, evt] }
              : { ...m, drafts: [...m.drafts, evt] }))
            if (evt.final) setStatuses((s) => ({ ...s, [evt.agent]: 'done' }))
            break
          case 'error':
            updateLast((m) => ({ ...m, status: 'error', error: evt.message }))
            break
          case 'done':
            setStatuses((s) => Object.fromEntries(Object.entries(s).map(([k, v]) => [k, v === 'running' ? 'done' : v])))
            updateLast((m) => ({ ...m, status: m.status === 'error' ? 'error' : 'done' }))
            break
          default:
        }
      })
    } catch (err) {
      updateLast((m) => ({ ...m, status: 'error', error: err.message }))
    } finally {
      setBusy(false)
      updateLast((m) => ({ ...m, status: m.status === 'running' ? 'done' : m.status }))
    }
  }

  function newChat() {
    setSessionId(newSessionId())
    setMessages([])
    setStatuses({})
    setToolCounts({})
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand small">
          <span className="brand-mark">CB</span>
          <div><strong>Client Brief</strong> <span className="muted">· Agentic Copilot</span></div>
        </div>
        <div className="topbar-right">
          <button className="ghost" onClick={newChat} disabled={busy}>+ New chat</button>
          <div className="user-chip">
            <div className="avatar">{user.full_name?.[0] || 'U'}</div>
            <div><div>{user.full_name}</div><div className="muted small">{user.role}</div></div>
          </div>
          <button className="ghost" onClick={onLogout}>Sign out</button>
        </div>
      </header>

      <div className="layout">
        <AgentPanel statuses={statuses} toolCounts={toolCounts} />

        <main className="chat">
          <div className="messages">
            {!messages.length && (
              <div className="empty">
                <h2>Good to see you, {user.full_name?.split(' ')[0]}.</h2>
                <p className="muted">Name a client or ticker and I&apos;ll get specialist agents to research internal documents (RAG),
                  the latest news (Web Search MCP) and market data (FactSet MCP), then write you a meeting brief.</p>
                <div className="suggestions">
                  {SUGGESTIONS.map((s) => <button key={s} onClick={() => send(s)}>{s}</button>)}
                </div>
              </div>
            )}
            {messages.map((m, i) => (m.role === 'user'
              ? <div key={i} className="msg user"><div className="bubble">{m.text}</div></div>
              : <AssistantTurn key={i} m={m} />))}
            <div ref={bottomRef} />
          </div>

          <form className="composer" onSubmit={(e) => { e.preventDefault(); send() }}>
            <textarea
              value={input}
              placeholder="e.g. Prepare me for my meeting with Northwind Logistics (NWLG)…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
              rows={2}
            />
            <button type="submit" disabled={busy || !input.trim()}>{busy ? 'Working…' : 'Send'}</button>
          </form>
        </main>
      </div>
    </div>
  )
}

function AssistantTurn({ m }) {
  const calls = m.events.filter((e) => e.type === 'tool_call')
  const results = m.events.filter((e) => e.type === 'tool_result')
  const citations = results.flatMap((r) => r.citations || [])
  const articles = results.flatMap((r) => r.articles || [])
  const uniqueDocs = [...new Map(citations.map((c) => [`${c.document}-${c.page}`, c])).values()]
  const uniqueArticles = [...new Map(articles.map((a) => [a.url, a])).values()]
  const factsetTools = [...new Set(results.filter((r) => sourceKind(r.source) === 'factset').map((r) => r.tool))]

  return (
    <div className="msg assistant">
      <div className="bubble wide">
        {m.events.length > 0 && (
          <details className="trace" open={m.status === 'running'}>
            <summary>
              {m.status === 'running' ? <span className="spinner" /> : '✓'} Agent activity · {calls.length} tool calls
            </summary>
            <ul>
              {m.events.map((e, i) => (
                <li key={i} className={e.type}>
                  <span className="who">{LABELS[e.agent] || e.agent}</span>
                  <span className={`badge ${sourceKind(e.source)}`}>{e.source}</span>
                  {e.type === 'tool_call'
                    ? <span>→ <code>{e.tool}</code>({Object.entries(e.args || {}).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join(', ')})</span>
                    : <span className="muted">← {e.summary}</span>}
                </li>
              ))}
            </ul>
          </details>
        )}

        {m.drafts.length > 0 && (
          <details className="trace">
            <summary>Specialist agent findings ({m.drafts.length})</summary>
            {m.drafts.map((d, i) => (
              <div key={i} className="draft">
                <div className="who">{d.label}</div>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{d.text}</ReactMarkdown>
              </div>
            ))}
          </details>
        )}

        {m.status === 'running' && !m.answers.length && (
          <div className="thinking"><span className="spinner" /> Agents are working on it…</div>
        )}

        {m.answers.map((a, i) => (
          <div key={i} className="answer markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{a.text}</ReactMarkdown>
          </div>
        ))}

        {m.status === 'error' && <div className="error">⚠ {m.error}</div>}

        {(uniqueDocs.length > 0 || uniqueArticles.length > 0 || factsetTools.length > 0) && (
          <div className="sources">
            <div className="sources-title">Sources used</div>
            {uniqueDocs.length > 0 && (
              <div className="source-group">
                <span className="badge rag">Internal Research RAG</span>
                {uniqueDocs.map((c) => (
                  <a key={`${c.document}-${c.page}`} className="chip" href={documentUrl(c.document)}
                     target="_blank" rel="noreferrer" title={c.excerpt}>
                    📄 {c.document} · p.{c.page} <span className="muted">({c.relevance})</span>
                  </a>
                ))}
              </div>
            )}
            {uniqueArticles.length > 0 && (
              <div className="source-group">
                <span className="badge web">Web Search MCP</span>
                {uniqueArticles.map((a) => (
                  <span key={a.url} className="chip" title={a.url}>📰 {a.title} <span className="muted">· {a.publisher}, {a.date}</span></span>
                ))}
              </div>
            )}
            {factsetTools.length > 0 && (
              <div className="source-group">
                <span className="badge factset">FactSet MCP</span>
                {factsetTools.map((t) => <span key={t} className="chip">📊 {t}</span>)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

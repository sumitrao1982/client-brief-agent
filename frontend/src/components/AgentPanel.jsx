import { useEffect, useState } from 'react'
import { documentUrl, listDocuments } from '../api'

export const AGENTS = [
  { id: 'client_brief_coordinator', label: 'Coordinator', source: 'Google ADK · LlmAgent', kind: 'orch' },
  { id: 'internal_research_agent', label: 'Internal Research', source: 'RAG · ChromaDB', kind: 'rag' },
  { id: 'market_news_agent', label: 'Market News', source: 'Web Search MCP', kind: 'web' },
  { id: 'financial_data_agent', label: 'Financial Data', source: 'FactSet MCP', kind: 'factset' },
  { id: 'brief_writer_agent', label: 'Brief Writer', source: 'Synthesis', kind: 'orch' },
]

export default function AgentPanel({ statuses, toolCounts }) {
  const [docs, setDocs] = useState([])
  useEffect(() => { listDocuments().then(setDocs).catch(() => setDocs([])) }, [])

  return (
    <aside className="sidebar">
      <section>
        <h3>Agent team</h3>
        <div className="agent-flow-note">Coordinator → <b>parallel</b> research → Brief Writer</div>
        {AGENTS.map((a, i) => (
          <div key={a.id} className={`agent-card ${statuses[a.id] || 'idle'} ${i >= 1 && i <= 3 ? 'indent' : ''}`}>
            <span className="dot" />
            <div className="agent-info">
              <div className="agent-name">{a.label}</div>
              <div className={`badge ${a.kind}`}>{a.source}</div>
            </div>
            <div className="agent-meta">
              {toolCounts[a.id] ? `${toolCounts[a.id]} calls` : ''}
              <div className="agent-status">{statuses[a.id] || 'idle'}</div>
            </div>
          </div>
        ))}
      </section>
      <section>
        <h3>Knowledge base (RAG)</h3>
        <p className="muted small">Internal PDFs indexed in ChromaDB</p>
        <ul className="doc-list">
          {docs.map((d) => (
            <li key={d.document}>
              <a href={documentUrl(d.document)} target="_blank" rel="noreferrer">📄 {d.document.replace(/_/g, ' ').replace('.pdf', '')}</a>
              <span className="muted small">{d.doc_type} · {d.chunks} chunks</span>
            </li>
          ))}
          {!docs.length && <li className="muted small">No documents indexed</li>}
        </ul>
      </section>
    </aside>
  )
}

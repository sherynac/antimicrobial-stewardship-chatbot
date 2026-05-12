import React, { useState, useRef, useEffect } from 'react'
import ophiuchus_logo from './assets/ophiuchus_logo.svg'
import ophiuchus_logo_dark from './assets/ophiuchus_logo_dark.svg'
import clear_chat from './assets/clear-chat.svg'
import menu from './assets/menu.svg'
import about_icon from './assets/about.svg'
import chat_icon from './assets/chat.svg'
import faqs_icon from './assets/FAQs.svg'
import send_button from './assets/send-button.svg'
import clear_chat_dark from './assets/clear-chat-dark.svg'
import menu_dark from './assets/menu-dark.svg'
import about_icon_dark from './assets/about-dark.svg'
import chat_icon_dark from './assets/chat-dark.svg'
import faqs_icon_dark from './assets/FAQs-dark.svg'
import send_button_dark from './assets/send-button-dark.svg'

import light_mode from './assets/light-mode.svg'
import dark_mode from './assets/dark-mode.svg'

import './App.css'

import FAQ from './components/faq.jsx'
import About from './components/about.jsx'

const API_BASE_URL = '/api'

const generateSessionId = () => crypto.randomUUID()

// ---------------------------------------------------------------------------
// Utility — strip duplicate "Php Php" currency prefix
// build_antibiotic_single() prepends "Php " to unit_price, but some VRB
// responseTexts already include the word "Php" before {unit_price}.
// ---------------------------------------------------------------------------
function stripDoubleCurrency(text) {
  return text.replace(/\bPrice:\s*Php\s+Php\s+/gi, 'Price: Php ')
}

// ---------------------------------------------------------------------------
// formatDrugText
// Splits a single long drug-info sentence into stacked lines at field labels.
// Applied to every `text` block so it also catches postText lines.
// ---------------------------------------------------------------------------
function formatDrugText(text, entities = []) {
  const cleaned = stripDoubleCurrency(text)
  const FIELD_LABELS = ['Manufacturer:', 'Distributor:', 'Price:']
  const regex = new RegExp(`(?=${FIELD_LABELS.join('|')})`, 'g')
  const parts = cleaned.split(regex).map(s => s.trim()).filter(Boolean)

  const isDisclaimer = cleaned.trim().startsWith('Disclaimer:')

  if (parts.length <= 1) return (
    <p className={`bot-text${isDisclaimer ? ' bot-disclaimer' : ''}`}>
      {highlightEntities(cleaned, entities)}
    </p>
  )

  return (
    <p className={`bot-text${isDisclaimer ? ' bot-disclaimer' : ''}`}>
      {parts.map((part, i) => (
        <span key={i} className="bot-text-line">{highlightEntities(part, entities)}</span>
      ))}
    </p>
  )
}

// ---------------------------------------------------------------------------
// Block renderers
// These map 1-to-1 to what response_service.py actually builds and sends.
//
// response_service.py emits exactly FIVE block types inside composite.responses:
//
//  1. { type: "text", content: "..." }
//     → build_text_response()
//     Used for: intro sentences, postText disclaimers, plain replies
//
//  2. { type: "table", columns: [...], rows: [[...], ...] }
//     → build_table_response()
//     Used for: antibiotic generic_only, brand_multiple, indications generic_only,
//               substance interactions (generic + multiple)
//
//  3. { type: "bullet_list", items: [ { type:"bullet", main_text, description }, ... ] }
//     → build_bullet_list()  wrapping  build_bullet()
//     Used for: side effects (brand_only, generic_brand_only),
//               indications (single + multiple), administration (multiple)
//     • main_text  — bold label, e.g. "Nausea (Common)" or disease headline
//     • description — plain detail text beneath the label (may be empty string)
//
//  4. { type: "section", title: "...", items: [ { type:"bullet", ... }, ... ] }
//     → build_section()  wrapping  build_bullet()
//     Used for: side effects generic_only (one section per brand),
//               warnings (brand_only, generic_verify_match),
//               interactions (single + match + generic_match),
//               food_and_timing generic, administration generic
//     • title  — section header, e.g. brand name or warning type
//     • items  — same bullet shape as bullet_list above
//
//  5. { type: "reference_list", sources: [ { type:"reference", name, title, url }, ... ] }
//     → build_reference_list()
//     Used for: every response as the last block
// ---------------------------------------------------------------------------

// ── 1. TEXT ─────────────────────────────────────────────────────────────────
// Handled inline inside BotMessage via formatDrugText — no separate component needed.


// ---------------------------------------------------------------------------
// highlightEntities
// Splits a user message string and wraps any resolved entity names in
// a <strong> with Cabin-Bold so they stand out in the chat bubble.
// Matching is case-insensitive; original casing is preserved in output.
// ---------------------------------------------------------------------------
function highlightEntities(text, entities) {
  if (!entities || entities.length === 0) return text
  const escaped = entities.map(e => e.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const pattern = new RegExp(`(${escaped.join('|')})`, 'gi')
  const parts = text.split(pattern)
  return parts.map((part, i) =>
    pattern.test(part)
      ? <strong key={i} className="font-[Cabin-Bold]">{part}</strong>
      : part
  )
}

// ── 2. TABLE ─────────────────────────────────────────────────────────────────
function TableBlock({ block }) {
  const darkMode = React.useContext(DarkModeContext)
  const activeEntities = React.useContext(ActiveEntitiesContext)
  const shouldHighlight = React.useContext(ShouldHighlightContext)
  const entities = shouldHighlight ? activeEntities : []

  const wrapperRef = useRef(null)
  const [isOverflowing, setIsOverflowing] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)

  useEffect(() => {
    const el = wrapperRef.current
    if (!el) return
    const check = () => setIsOverflowing(el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight)
    check()
    const ro = new ResizeObserver(check)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  useEffect(() => {
    if (!isExpanded) return
    const onKey = (e) => { if (e.key === 'Escape') setIsExpanded(false) }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [isExpanded])

  const handleOpen = () => { setZoomLevel(1); setIsExpanded(true) }
  const zoomIn = () => setZoomLevel(z => Math.min(z + 0.25, 3))
  const zoomOut = () => setZoomLevel(z => Math.max(z - 0.25, 0.5))

  if (!Array.isArray(block.columns) || !Array.isArray(block.rows) || block.rows.length === 0) {
    return <p className="bot-text bot-text-muted">No data available.</p>
  }

  const tableMarkup = (
    <table className="bot-table">
      <thead>
        <tr>{block.columns.map((col, i) => <th key={i}>{highlightEntities(col, entities)}</th>)}</tr>
      </thead>
      <tbody>
        {block.rows.map((row, i) => (
          <tr key={i}>{row.map((cell, j) => <td key={j}>{highlightEntities(String(cell ?? ''), entities)}</td>)}</tr>
        ))}
      </tbody>
    </table>
  )

  return (
    <>
      <div className="bot-table-outer">
        <div className="bot-table-wrapper" ref={wrapperRef}>
          {tableMarkup}
        </div>
        {isOverflowing && (
          <button className="bot-table-expand-btn" onClick={handleOpen} title="Expand table">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 3 21 3 21 9" /><polyline points="9 21 3 21 3 15" />
              <line x1="21" y1="3" x2="14" y2="10" /><line x1="3" y1="21" x2="10" y2="14" />
            </svg>
            Expand
          </button>
        )}
      </div>

      {isExpanded && (
        <div className="table-modal-overlay" onClick={() => setIsExpanded(false)}>
          <div className={`table-modal${darkMode ? ' dark-modal' : ''}`} onClick={e => e.stopPropagation()}>
            <button className="table-modal-close" onClick={() => setIsExpanded(false)} title="Close (Esc)">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <div className="table-modal-scroll">
              <div className="table-modal-inner">
                <div className="bot-table-wrapper" style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center' }}>
                  {tableMarkup}
                </div>
              </div>
            </div>
            <div className="table-modal-controls">
              <button className="table-zoom-btn" onClick={zoomOut} disabled={zoomLevel <= 0.5} title="Zoom out">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /><line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </button>
              <span className="table-zoom-label">{Math.round(zoomLevel * 100)}%</span>
              <button className="table-zoom-btn" onClick={zoomIn} disabled={zoomLevel >= 3} title="Zoom in">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /><line x1="11" y1="8" x2="11" y2="14" /><line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

// ── 3. BULLET_LIST ───────────────────────────────────────────────────────────
const COLLAPSE_THRESHOLD = 3

function BulletListBlock({ block }) {
  const activeEntities = React.useContext(ActiveEntitiesContext)
  const shouldHighlight = React.useContext(ShouldHighlightContext)
  const entities = shouldHighlight ? activeEntities : []
  const items = block.items || []
  const [expanded, setExpanded] = useState(false)

  if (items.length === 0) return <p className="bot-text bot-text-muted">No items to display.</p>

  const shouldCollapse = items.length > COLLAPSE_THRESHOLD
  const visibleItems = shouldCollapse && !expanded ? items.slice(0, COLLAPSE_THRESHOLD) : items

  return (
    <div>
      <ul className="bot-bullet-list">
        {visibleItems.map((item, i) => (
          <li key={i} className="bot-bullet-item">
            <div className="bot-bullet-item-inner">
              {item.main_text && (
                <span className="bot-bullet-main">{highlightEntities(item.main_text, entities)}</span>
              )}
              {item.description && (
                <span className={`bot-bullet-description${item.main_text ? ' bot-bullet-description-indented' : ''}`}>
                  {highlightEntities(item.description.trim(), entities)}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
      {shouldCollapse && (
        <button className="bot-bullet-toggle" onClick={() => setExpanded(!expanded)}>
          {expanded ? '▲ See less' : `▼ See ${items.length - COLLAPSE_THRESHOLD} more`}
        </button>
      )}
    </div>
  )
}

// ── 4. SECTION ────────────────────────────────────────────────────────────────
// { type: "section", title: "BrandName", items: [{ type:"bullet", main_text, description }] }
// Renders a titled group with the same bullet shape and collapse logic as BulletListBlock.
function SectionBlock({ block }) {
  const activeEntities = React.useContext(ActiveEntitiesContext)
  const shouldHighlight = React.useContext(ShouldHighlightContext)
  const entities = shouldHighlight ? activeEntities : []
  const items = block.items || []
  const [expanded, setExpanded] = useState(false)

  const shouldCollapse = items.length > COLLAPSE_THRESHOLD
  const visibleItems = shouldCollapse && !expanded ? items.slice(0, COLLAPSE_THRESHOLD) : items

  return (
    <div className="bot-section">
      {block.title && (
        <p className="bot-section-title"><strong>{highlightEntities(block.title, entities)}</strong></p>
      )}
      {items.length > 0 ? (
        <>
          <ul className="bot-bullet-list">
            {visibleItems.map((item, i) => (
              <li key={i} className="bot-bullet-item">
                <div className="bot-bullet-item-inner">
                  {item.main_text && (
                    <span className="bot-bullet-main">{highlightEntities(item.main_text, entities)}</span>
                  )}
                  {item.description && (
                    <span className={`bot-bullet-description${item.main_text ? ' bot-bullet-description-indented' : ''}`}>
                      {highlightEntities(item.description.trim(), entities)}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
          {shouldCollapse && (
            <button className="bot-bullet-toggle" onClick={() => setExpanded(!expanded)}>
              {expanded ? '▲ See less' : `▼ See ${items.length - COLLAPSE_THRESHOLD} more`}
            </button>
          )}
        </>
      ) : (
        <p className="bot-text bot-text-muted">No details available.</p>
      )}
    </div>
  )
}

// ── 5. REFERENCE_LIST ────────────────────────────────────────────────────────
// { type: "reference_list", sources: [{ name, title, url }] }
function ReferenceListBlock({ block }) {
  const sources = block.sources || []
  if (sources.length === 0) return null
  return (
    <div className="bot-references">
      <p className="bot-references-label">References</p>
      <ul>
        {sources.map((src, j) => (
          <li key={j}>
            <a href={src.url} target="_blank" rel="noopener noreferrer">
              {src.title || src.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

// ---------------------------------------------------------------------------
// BotMessage — top-level renderer
//
// Dispatches each block in payload.responses to the correct renderer above.
// Every block type that response_service.py can emit is handled here.
// ---------------------------------------------------------------------------
const DarkModeContext = React.createContext(false)
const ActiveEntitiesContext = React.createContext([])
const ShouldHighlightContext = React.createContext(false)

function BotMessage({ payload }) {
  const activeEntities = React.useContext(ActiveEntitiesContext)


  if (typeof payload === 'string') {
    return <p>{payload}</p>
  }

  if (payload?.type === 'text' && payload?.content) {
    return <p className="bot-text">{payload.content}</p>
  }

  if (payload?.type === 'composite' && Array.isArray(payload.responses)) {

    let entityHighlightUsed = false

    return (
      <div className="bot-composite">
        {payload.responses.map((block, i) => {
          switch (block.type) {
            case 'text': {
              const hasEntity = activeEntities.length > 0 &&
                activeEntities.some(e =>
                  new RegExp(e.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(block.content)
                )
              const shouldHighlight = hasEntity && !entityHighlightUsed
              if (shouldHighlight) entityHighlightUsed = true
              return <div key={i}>{formatDrugText(block.content, shouldHighlight ? activeEntities : [])}</div>
            }

            case 'table':
              return (
                <ShouldHighlightContext.Provider key={i} value={!entityHighlightUsed}>
                  <TableBlock block={block} />
                </ShouldHighlightContext.Provider>
              )

            case 'bullet_list':
              return (
                <ShouldHighlightContext.Provider key={i} value={!entityHighlightUsed}>
                  <BulletListBlock block={block} />
                </ShouldHighlightContext.Provider>
              )

            case 'section':
              return (
                <ShouldHighlightContext.Provider key={i} value={!entityHighlightUsed}>
                  <SectionBlock block={block} />
                </ShouldHighlightContext.Provider>
              )

            case 'reference_list':
              return <ReferenceListBlock key={i} block={block} />

            default:

              return block.content
                ? <p key={i} className="bot-text">{block.content}</p>
                : null
          }
        })}
      </div>
    )
  }


  return <p>{JSON.stringify(payload)}</p>
}

function App() {
  const [activePage, setActivePage] = useState('chat')
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [sessionId, setSessionId] = useState(() => {
    const newId = generateSessionId()
    sessionStorage.setItem('ophiuchus_session_id', newId)
    return newId
  })
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeEntities, setActiveEntities] = useState([])
  const chatBottomRef = useRef(null)

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed || isLoading) return

    setMessages(prev => [...prev, { role: 'user', text: trimmed, entities: [] }])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(
          errorData?.error || `Server error: ${response.status} ${response.statusText}`
        )
      }

      const data = await response.json()
      const botReply = data.reply ?? 'Sorry, I did not receive a valid response.'

      let parsedReply
      if (typeof botReply === 'string') {
        try {
          parsedReply = JSON.parse(botReply)
        } catch {
          try {
            const asJson = botReply
              .replace(/'/g, '"')
              .replace(/\bNone\b/g, 'null')
              .replace(/\bTrue\b/g, 'true')
              .replace(/\bFalse\b/g, 'false')
            parsedReply = JSON.parse(asJson)
          } catch {
            parsedReply = botReply
          }
        }
      } else {
        parsedReply = botReply
      }


      const resolvedEntities = data.resolved_entities
        ? Object.values(data.resolved_entities).flat()
        : []


      if (resolvedEntities.length > 0) {
        setActiveEntities(resolvedEntities)
      }


      setMessages(prev => {
        const updated = [...prev]
        for (let i = updated.length - 1; i >= 0; i--) {
          if (updated[i].role === 'user') {
            updated[i] = { ...updated[i], entities: resolvedEntities }
            break
          }
        }
        return updated
      })

      setMessages(prev => [...prev, { role: 'bot', payload: parsedReply, entities: resolvedEntities }])

    } catch (err) {
      const errorText = err.message || 'Something went wrong. Please try again.'
      setMessages(prev => [...prev, { role: 'bot', payload: `⚠️ ${errorText}`, isError: true }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = async (e) => {
    e.preventDefault()


    try {
      await fetch(`${API_BASE_URL}/session/clear`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch {
    }


    const newSessionId = generateSessionId()
    sessionStorage.setItem('ophiuchus_session_id', newSessionId)
    setSessionId(newSessionId)
    setMessages([])
    setInputValue('')
    setActiveEntities([])
    setActivePage('chat')
  }

  return (
    <>
      <div className={`navbar ${navCollapsed ? 'navbar-collapsed' : ''} ${darkMode ? 'dark-mode' : ''}`}>
        <div className="first-row">
          {!navCollapsed && (
            <div id="clear-chat-button"
              onClick={(e) => { handleClearChat(e); setActivePage('chat') }}
            >
              {!darkMode
                ? <img src={clear_chat} alt="clear-icon" id="clear-icon" className="icons" />
                : <img src={clear_chat_dark} alt="clear-icon" id="clear-icon-dark" className="icons" />}
              <a href="" id="clear-chat">Clear Chat</a>
            </div>
          )}
          <div className="menu-button-container" id="menu-button" onClick={() => setNavCollapsed(!navCollapsed)}>
            {!darkMode
              ? <img src={menu} alt="menu-icon" id='menu-icon' className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
              : <img src={menu_dark} alt="menu-icon" id='menu-icon-dark' className={`icons ${navCollapsed ? 'collapsed' : ''}`} />}
          </div>
        </div>

        <div
          className={`${activePage === 'chat' ? 'button-container-active' : 'button-container'} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('chat')}
        >
          {!darkMode
            ? <img src={chat_icon} alt="chat-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
            : <img src={chat_icon_dark} alt="chat-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />}
          {!navCollapsed && <div className={`nav-title ${activePage === 'chat' ? 'font-[Cabin-Bold]' : ''}`}>Chat</div>}
        </div>

        <div
          className={`${activePage === 'about' ? 'button-container-active' : 'button-container'} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('about')}
        >
          {!darkMode
            ? <img src={about_icon} alt="about-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
            : <img src={about_icon_dark} alt="about-icon-dark" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />}
          {!navCollapsed && <div className={`nav-title ${activePage === 'about' ? 'font-[Cabin-Bold]' : ''}`}>About</div>}
        </div>

        <div
          className={`${activePage === 'faqs' ? 'button-container-active' : 'button-container'} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('faqs')}
        >
          {!darkMode
            ? <img src={faqs_icon} alt="FAQs-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
            : <img src={faqs_icon_dark} alt="FAQs-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />}
          {!navCollapsed && <div className={`nav-title ${activePage === 'faqs' ? 'font-[Cabin-Bold]' : ''}`}>FAQs</div>}
        </div>

        {!navCollapsed && (
          <div className={`theme-switch ${darkMode ? 'theme-switch-dark' : ''}`} onClick={() => setDarkMode(!darkMode)}>
            {!darkMode ? <img src={light_mode} alt="" /> : <img src={dark_mode} alt="" />}
          </div>
        )}
      </div>

      <div className={`main-container ${darkMode ? 'dark-mode' : ''}`}>
        <div className="main-content">
          {activePage === 'chat' && (
            <>
              <div className="header">
                {!darkMode
                  ? <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
                  : <img src={ophiuchus_logo_dark} className="" alt="Ophiuchus logo" />}
                <div className="title-container">
                  <p className="title">Ophiuchus</p>
                  <p className="sub-title">Ask me anything</p>
                </div>
              </div>

              <div className={`main-chat ${navCollapsed ? 'collapsed' : ''} ${messages.length === 0 ? 'empty' : ''}`}>
                {messages.length === 0 && (
                  <div className="welcome-message">
                    <p id='greeting'>Hello, I am <span>Ophiuchus</span>!</p>
                    <p id='intro'>I am a conversational guide for antimicrobial stewardship. I'm here to help promote responsible antibiotic use</p>
                    <p id='disclaimer'>Disclaimer: Ophiuchus is for educational and informational purposes only. I do <span>not</span> provide medical diagnoses, treatment plans, or prescriptions. Always consult a qualified healthcare professional for medical advice.</p>
                  </div>
                )}

                {(() => {
                  const lastBotIndex = messages.reduce((last, msg, i) => msg.role === 'bot' ? i : last, -1)
                  const lastUserIndex = messages.reduce((last, msg, i) => msg.role === 'user' ? i : last, -1)
                  return messages.map((msg, index) =>
                    msg.role === 'user' ? (
                      <div className="message-container" key={index}>
                        <div className="message-prompt">
                          <p>{highlightEntities(msg.text, index === lastUserIndex ? msg.entities : [])}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="reply-container" key={index}>
                        <div className={`chatbot-reply ${msg.isError ? 'error' : ''}`}>
                          <DarkModeContext.Provider value={darkMode}>
                            <ActiveEntitiesContext.Provider value={index === lastBotIndex ? (msg.entities ?? []) : []}>
                              <BotMessage payload={msg.payload} />
                            </ActiveEntitiesContext.Provider>
                          </DarkModeContext.Provider>
                        </div>
                      </div>
                    )
                  )
                })()}

                {isLoading && (
                  <div className="reply-container">
                    <div className="chatbot-reply loading">
                      <span className="dot" /><span className="dot" /><span className="dot" />
                    </div>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              <div className={`message-box ${navCollapsed ? 'collapsed' : ''}`}>
                <form onSubmit={handleSubmit}>
                  <input
                    type="text"
                    id="message"
                    placeholder='Type your message here..'
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    autoComplete='off'
                    disabled={isLoading}
                  />
                  {!darkMode
                    ? <input type="image" src={send_button} alt="Submit" disabled={isLoading} />
                    : <input type="image" src={send_button_dark} alt="Submit" disabled={isLoading} />}
                </form>
              </div>
            </>
          )}

          {activePage === 'about' && <About navCollapsed={navCollapsed} darkMode={darkMode} />}
          {activePage === 'faqs' && <FAQ navCollapsed={navCollapsed} darkMode={darkMode} />}
        </div>
      </div>
    </>
  )
}

export default App
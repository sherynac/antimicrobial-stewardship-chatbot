import { useState, useRef, useEffect } from 'react'
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

// Base URL for your Flask backend.
// In development, Vite's proxy (vite.config.js) can forward '/api' to 'http://127.0.0.1:5000'.
// In production, replace with your deployed backend URL.
const API_BASE_URL = '/api'

// Generates a UUID v4 to uniquely identify a chat session.
const generateSessionId = () => crypto.randomUUID()

// Retrieves the existing session ID from sessionStorage, or creates and stores a new one.
// sessionStorage is automatically cleared when the tab is closed, which naturally
// triggers a fresh session on the next visit.
const getOrCreateSessionId = () => {
  let sessionId = sessionStorage.getItem('ophiuchus_session_id')
  if (!sessionId) {
    sessionId = generateSessionId()
    sessionStorage.setItem('ophiuchus_session_id', sessionId)
  }
  return sessionId
}

// ---------------------------------------------------------------------------
// BotMessage — renders a structured bot reply from the backend.
//
// The backend returns either:
//   • A plain string  →  rendered as a simple paragraph
//   • A composite object:
//     {
//       type: 'composite',
//       responses: [
//         { type: 'text',           content: '...' },
//         { type: 'reference_list', sources: [{ name, title, url }] }
//       ]
//     }
// ---------------------------------------------------------------------------
// Splits a drug info sentence into multiple lines at known field labels.
// e.g. "...Doxycycline Hyclate. Manufacturer: BIOFEMME. Distributor: UNILAB. Price: Php 103."
// becomes three separate <span> lines inside the same <p>.
function formatDrugText(text) {
  const FIELD_LABELS = ['Manufacturer:', 'Distributor:', 'Price:']
  const regex = new RegExp(`(?=${FIELD_LABELS.join('|')})`, 'g')
  const parts = text.split(regex).map(s => s.trim()).filter(Boolean)

  if (parts.length <= 1) return <p className="bot-text">{text}</p>

  return (
    <p className="bot-text">
      {parts.map((part, i) => (
        <span key={i} className="bot-text-line">{part}</span>
      ))}
    </p>
  )
}

function BotMessage({ payload }) {
  // If the payload is a plain string, just render it as-is
  if (typeof payload === 'string') {
    return <p>{payload}</p>
  }

  // Composite response — iterate over each block
  if (payload?.type === 'composite' && Array.isArray(payload.responses)) {
    return (
      <div className="bot-composite">
        {payload.responses.map((block, i) => {
          if (block.type === 'text') {
            return <div key={i}>{formatDrugText(block.content)}</div>
          }

          if (block.type === 'reference_list' && Array.isArray(block.sources)) {
            return (
              <div key={i} className="bot-references">
                <p className="bot-references-label">References</p>
                <ul>
                  {block.sources.map((src, j) => (
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

          // Fallback for unknown block types — render raw content if available
          return block.content
            ? <p key={i} className="bot-text">{block.content}</p>
            : null
        })}
      </div>
    )
  }

  // Absolute fallback — stringify whatever came through
  return <p>{JSON.stringify(payload)}</p>
}

function App() {
  const [activePage, setActivePage] = useState('chat') // 'chat', 'about', 'faqs'
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

  // Session ID — loaded from sessionStorage on mount, or freshly generated.
  // Stored in state so React re-renders reflect the current session.
  const [sessionId, setSessionId] = useState(() => getOrCreateSessionId())

  // Each entry: { role: 'user' | 'bot', text: string }
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)  // tracks whether we're awaiting a bot reply
  const chatBottomRef = useRef(null)

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed || isLoading) return

    // Optimistically add the user message and clear the input immediately
    setMessages(prev => [...prev, { role: 'user', text: trimmed }])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
      })

      if (!response.ok) {
        // Surface HTTP-level errors (4xx, 5xx) as a readable message
        const errorData = await response.json().catch(() => null)
        throw new Error(
          errorData?.error || `Server error: ${response.status} ${response.statusText}`
        )
      }

      const data = await response.json()

      // The backend may return a plain string or a structured composite object.
      // Store the raw value — BotMessage handles rendering both shapes.
      const botReply = data.reply ?? 'Sorry, I did not receive a valid response.'

      // Parse the reply into an object if needed.
      // The backend may send a Python dict stringified with single quotes instead of
      // valid JSON double quotes (e.g. "{'type': 'composite', ...}"). We handle both.
      let parsedReply
      if (typeof botReply === 'string') {
        // First, try standard JSON.parse (handles properly serialized responses)
        try {
          parsedReply = JSON.parse(botReply)
        } catch {
          // Fallback: convert Python dict syntax → valid JSON, then parse again.
          // Swaps single-quoted strings to double-quoted, and converts
          // Python's None/True/False to JSON null/true/false.
          try {
            const asJson = botReply
              .replace(/'/g, '"')
              .replace(/\bNone\b/g, 'null')
              .replace(/\bTrue\b/g, 'true')
              .replace(/\bFalse\b/g, 'false')
            parsedReply = JSON.parse(asJson)
          } catch {
            parsedReply = botReply  // genuinely plain text — keep as-is
          }
        }
      } else {
        parsedReply = botReply  // already an object
      }

      setMessages(prev => [...prev, { role: 'bot', payload: parsedReply }])

    } catch (err) {
      // Push the error as a bot message so it persists in chat history
      const errorText = err.message || 'Something went wrong. Please try again.'
      setMessages(prev => [...prev, { role: 'bot', payload: `⚠️ ${errorText}`, isError: true }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = (e) => {
    e.preventDefault()
    setMessages([])
    setInputValue('')
    setActivePage('chat')

    // Invalidate the current session and start a fresh one.
    // The new ID is stored in sessionStorage so a page refresh stays on the same session.
    const newSessionId = generateSessionId()
    sessionStorage.setItem('ophiuchus_session_id', newSessionId)
    setSessionId(newSessionId)
  }

  return (
    <>
      <div className={`navbar ${navCollapsed ? 'navbar-collapsed' : ''} ${darkMode ? 'dark-mode' : ''}`}>
        <div className="first-row">

          {/* Hide clear-chat-button when collapsed */}
          {!navCollapsed && (
            <div id="clear-chat-button"
              onClick={(e) => { handleClearChat(e); setActivePage('chat'); }}
            >
              {!darkMode && (
                <img src={clear_chat} alt="clear-icon" id="clear-icon" className="icons" />
              )}
              {darkMode && (
                <img src={clear_chat_dark} alt="clear-icon" id="clear-icon-dark" className="icons" />
              )}
              <a href="" id="clear-chat">Clear Chat</a>
            </div>
          )}

          {/* Menu button — always visible, toggles collapse */}
          <div
            className="menu-button-container"
            id="menu-button"
            onClick={() => setNavCollapsed(!navCollapsed)}
          >
            {!darkMode && (
              <img src={menu} alt="menu-icon" id='menu-icon' className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
            )}
            {darkMode && (
              <img src={menu_dark} alt="menu-icon" id='menu-icon-dark' className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
            )}

          </div>
        </div>

        {/* Chat */}
        <div
          className={`${activePage === 'chat' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('chat')}
        >
          {!darkMode && (
            <img src={chat_icon} alt="chat-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}
          {darkMode && (
            <img src={chat_icon_dark} alt="chat-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}

          {!navCollapsed && <div className="nav-title">Chat</div>}
        </div>

        {/* About */}
        <div
          className={`${activePage === 'about' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('about')}
        >
          {!darkMode && (
            <img src={about_icon} alt="about-icon-dark" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}
          {darkMode && (
            <img src={about_icon_dark} alt="about-icon-dark" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}

          {!navCollapsed && <div className="nav-title">About</div>}
        </div>

        {/* FAQs */}
        <div
          className={`${activePage === 'faqs' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('faqs')}
        >
          {!darkMode && (
            <img src={faqs_icon} alt="FAQs-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}
          {darkMode && (
            <img src={faqs_icon_dark} alt="FAQs-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          )}

          {!navCollapsed && <div className="nav-title">FAQs</div>}
        </div>

        {!navCollapsed && (
          <div
            className={`theme-switch ${darkMode ? 'theme-switch-dark' : ''}`}
            onClick={() => setDarkMode(!darkMode)}
          >
            {!darkMode && (
              <img src={light_mode} alt="" />
            )}
            {darkMode && (
              <img src={dark_mode} alt="" />
            )}
          </div>
        )}

      </div>

      <div className={`main-container ${darkMode ? 'dark-mode' : ''}`}>
        <div className="main-content">

          {activePage === 'chat' && (
            <>
              <div className="header">
                {!darkMode && (
                  <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
                )}
                {darkMode && (
                  <img src={ophiuchus_logo_dark} className="" alt="Ophiuchus logo" />
                )}

                <div className="title-container">
                  <p className="title">Ophiuchus</p>
                  <p className="sub-title">Ask me anything</p>
                </div>
              </div>

              <div className={`main-chat ${navCollapsed ? 'collapsed' : ''} ${messages.length === 0 ? 'empty' : ''}`}>

                {/* Welcome message — only shown before any messages */}
                {messages.length === 0 && (
                  <div className="welcome-message">
                    <p id='greeting'>Hello, I am <span>Ophiuchus</span>!</p>
                    <p id='intro'>I am a conversational guide for antimicrobial stewardship. I'm here to help promote responsible antibiotic use</p>
                    <p id='disclaimer'>Disclaimer: Ophiuchus is for educational and informational purposes only. I do <span>not</span> provide medical diagnoses, treatment plans, or prescriptions. Always consult a qualified healthcare professional for medical advice.</p>
                  </div>
                )}

                {/* Dynamic message history */}
                {messages.map((msg, index) =>
                  msg.role === 'user' ? (
                    <div className="message-container" key={index}>
                      <div className="message-prompt">
                        <p>{msg.text}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="reply-container" key={index}>
                      <div className={`chatbot-reply ${msg.isError ? 'error' : ''}`}>
                        <BotMessage payload={msg.payload} />
                      </div>
                    </div>
                  )
                )}

                {/* Loading indicator — shown while awaiting bot response */}
                {isLoading && (
                  <div className="reply-container">
                    <div className="chatbot-reply loading">
                      <span className="dot" />
                      <span className="dot" />
                      <span className="dot" />
                    </div>
                  </div>
                )}

                {/* Scroll anchor */}
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
                  {!darkMode && (
                    <input type="image" src={send_button} alt="Submit" disabled={isLoading} />
                  )}
                  {darkMode && (
                    <input type="image" src={send_button_dark} alt="Submit" disabled={isLoading} />
                  )}

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
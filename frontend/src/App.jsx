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

function App() {
  const [activePage, setActivePage] = useState('chat') // 'chat', 'about', 'faqs'
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

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
        body: JSON.stringify({ message: trimmed }),
      })

      if (!response.ok) {
        // Surface HTTP-level errors (4xx, 5xx) as a readable message
        const errorData = await response.json().catch(() => null)
        throw new Error(
          errorData?.error || `Server error: ${response.status} ${response.statusText}`
        )
      }

      const data = await response.json()

      // Expects the Flask backend to return: { "reply": "..." }
      const botReply = data.reply ?? 'Sorry, I did not receive a valid response.'

      setMessages(prev => [...prev, { role: 'bot', text: botReply }])

    } catch (err) {
      // Push the error as a bot message so it persists in chat history
      const errorText = err.message || 'Something went wrong. Please try again.'
      setMessages(prev => [...prev, { role: 'bot', text: `⚠️ ${errorText}`, isError: true }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = (e) => {
    e.preventDefault()
    setMessages([])
    setInputValue('')
    setActivePage('chat')
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
                        <p>{msg.text}</p>
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
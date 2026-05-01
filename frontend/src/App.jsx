import { useState } from 'react'
import ophiuchus_logo from './assets/ophiuchus_logo.svg'
import clear_chat from './assets/clear-chat.svg'
import menu from './assets/menu.svg'
import about_icon from './assets/about.svg'
import chat_icon from './assets/chat.svg'
import faqs_icon from './assets/FAQs.svg'
import send_button from './assets/send-button.svg'

import './App.css'

import FAQ from './components/faq.jsx'
import About from './components/about.jsx'

function App() {
  const [activePage, setActivePage] = useState('chat') // 'chat', 'about', 'faqs'
  const [navCollapsed, setNavCollapsed] = useState(false)

  // Each entry: { role: 'user' | 'bot', text: string }
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed) return

    // Add user message
    // TODO: replace the bot stub below with your actual API/backend call
    setMessages(prev => [
      ...prev,
      { role: 'user', text: trimmed },
      { role: 'bot', text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.' } // placeholder — swap with real response
    ])

    setInputValue('')
  }

  const handleClearChat = (e) => {
    e.preventDefault()
    setMessages([])
    setInputValue([])
  }

  return (
    <>
      <div className={`navbar ${navCollapsed ? 'navbar-collapsed' : ''}`}>
        <div className="first-row">

          {/* Hide clear-chat-button when collapsed */}
          {!navCollapsed && (
            <div className="" id="clear-chat-button">
              <img src={clear_chat} alt="clear-icon" id="clear-icon" className="icons" />
              <a href="" id="clear-chat" onClick={handleClearChat}>Clear Chat</a>
            </div>
          )}

          {/* Menu button — always visible, toggles collapse */}
          <div
            className="menu-button-container"
            id="menu-button"
            onClick={() => setNavCollapsed(!navCollapsed)}
          >
            <img src={menu} alt="menu-icon" id='menu-icon' className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          </div>
        </div>

        {/* Chat */}
        <div
          className={`${activePage === 'chat' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('chat')}
        >
          <img src={chat_icon} alt="chat-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          {!navCollapsed && <div className="nav-title">Chat</div>}
        </div>

        {/* About */}
        <div
          className={`${activePage === 'about' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('about')}
        >
          <img src={about_icon} alt="about-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          {!navCollapsed && <div className="nav-title">About</div>}
        </div>

        {/* FAQs */}
        <div
          className={`${activePage === 'faqs' ? "button-container-active" : "button-container"} ${navCollapsed ? 'collapsed' : ''}`}
          onClick={() => setActivePage('faqs')}
        >
          <img src={faqs_icon} alt="FAQs-icon" id="FAQs-icon" className={`icons ${navCollapsed ? 'collapsed' : ''}`} />
          {!navCollapsed && <div className="nav-title">FAQs</div>}
        </div>
      </div>

      <div className="main-container">
        <div className="main-content">

          {activePage === 'chat' && (
            <>
              <div className="header">
                <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
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
                    <p id='intro'>I am a conversational guide for antimicrobial stewardship. I’m here to help promote responsible antibiotic use</p>
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
                      <div className="chatbot-reply">
                        <p>{msg.text}</p>
                      </div>
                    </div>
                  )
                )}

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
                  />
                  <input type="image" src={send_button} alt="Submit" />
                </form>
              </div>
            </>
          )}

          {activePage === 'about' && <About navCollapsed={navCollapsed} />}

          {activePage === 'faqs' && <FAQ navCollapsed={navCollapsed} />}

        </div>
      </div>
    </>
  )
}

export default App
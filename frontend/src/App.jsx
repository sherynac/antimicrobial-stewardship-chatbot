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
// const navigation=[
//   {}
// ]

// useState('chat') - chat UI ang landing
  const [activePage, setActivePage] = useState('chat') // 'chat', 'about', 'faqs'
  const [navCollapsed, setNavCollapsed] = useState(false)

  return (
    <>

      <div className={`navbar ${navCollapsed ? 'navbar-collapsed' : ''}`}>
        <div className="first-row">

          {/* Hide clear-chat-button when collapsed */}
          {!navCollapsed && (
            <div className="" id="clear-chat-button">
              <img src={clear_chat} alt="clear-icon" id="clear-icon" className="icons" />
              <a href="" id="clear-chat">Clear Chat</a>
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

              <div className={`main-chat ${navCollapsed ? 'collapsed' : ''}`}>
                <div className="message-container">
                  <div className="message-prompt">
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
                  </div>
                </div>
                <div className="reply-container">
                  <div className="chatbot-reply">
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
                  </div>
                </div>
              </div>
              <div className={`message-box ${navCollapsed ? 'collapsed' : ''}`}>
                <form action="">
                  <input type="text" id="message" placeholder='Type your message here..'/>
                  <input type="image" src={send_button} alt="Submit"/>
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

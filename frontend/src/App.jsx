import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import ophiuchus_logo from './assets/ophiuchus_logo.svg'
import './App.css'

function App() {
// const navigation=[
//   {}
// ]
  return (
    <>

      <div className="navbar">
        <div className="first-row">
          <div className="button-container" id="clear-chat-button">
            <img src="src\assets\clear-chat.svg" alt="clear-icon" className="icons" />
            <a href="" id="clear-chat">Clear Chat</a>
          </div>
          <div className="menu-button-container" id="menu-button">
            <img src="src\assets\menu.svg" alt="menu-icon" className="icons" />
          </div>
        </div>
        <div className="button-container-active">
          <img src="src\assets\chat.svg" alt="chat-icon" className="icons" />
          <a href="" id="chat">Chat</a>
        </div>
        <div className="button-container">
          <img src="src\assets\about.svg" alt="about-icon" className="icons" />
          <a href="" id="about">About</a>
        </div>
        <div className="button-container">
          <img src="src\assets\FAQs.svg" alt="FAQs-icon" className="icons" />
          <a href="" id="faqs">FAQs</a>
          </div>
      </div>

      <div className="main-container">
        <div className="header">
          <img src={ophiuchus_logo} className="" alt="Ophiuchus logo" />
            <div className="title-container">
              <p className="title">Ophiuchus</p>
              <p className="sub-title">Ask me anything</p>
            </div>
        </div>

        <div className="main-content">
          <div className="main-chat">
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
          <div className="message-box">
            <form action="">
              <input type="text" id="message" placeholder='Type your message here..'/>
              <input type="image" src="src\assets\send-button.svg" alt="Submit"/>
            </form>
          </div>
        </div>
      </div>
      
    </>
  )
}

export default App

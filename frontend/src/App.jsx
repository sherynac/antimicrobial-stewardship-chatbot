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
          <div className="button-container" id="new-chat-button">
            <a href="" id="new-chat">New Chat</a>
          </div>
          <div className="button-container-active">
            <a href="" id="chat">Chat</a>
          </div>
          <div className="button-container">
            <a href="" id="about">About</a>
          </div>
          <div className="button-container">
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

          </div>
          <div className="message-box">
            <form action="">
              <input type="text" id="message" placeholder='Type your message here..' />
            </form>
          </div>
        </div>
      </div>
      
    </>
  )
}

export default App

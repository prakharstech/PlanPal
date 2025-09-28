// src/App.jsx

import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // Make sure you've updated App.css!
import GoogleCalendar from './Calendar';

function App() {
  const [messages, setMessages] = useState([
    // Start with a welcome message
    {
      role: 'assistant',
      content: "Hello! I'm PlanPal. How can I help you with your calendar today?",
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: inputValue }),
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

      const data = await res.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.response || "Sorry, something went wrong.",
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      console.error("Failed to fetch from agent:", error);
      const errorMessage = {
        role: 'assistant',
        content: "I'm having trouble connecting. Please check your connection and try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        
        <header className="header">
          <div className="avatar">🤖</div>
          <div className="bot-info">
            <div className="bot-name">PlanPal</div>
            <div className="status">Online</div>
          </div>
        </header>

        <div className="messages-list">
          {messages.map((msg, index) => (
            <div key={index} className={`message-container ${msg.role}`}>
              <div className={`message ${msg.role}`}>{msg.content}</div>
            </div>
          ))}

          {isLoading && (
            <div className="message-container assistant">
              <div className="message assistant loading-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Book a meeting for tomorrow..."
            disabled={isLoading}
          />
          <button type="submit" className="send-button" disabled={isLoading || !inputValue.trim()}>
            <svg viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
            </svg>
          </button>
        </form>
        
      </div>
      <div className="calendar-view-container">
        <GoogleCalendar />
      </div>
    </div>
    
  );
}

export default App;
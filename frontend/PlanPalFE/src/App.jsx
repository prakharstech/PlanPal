// src/App.jsx
import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import GoogleCalendar from './Calendar';
import Login from './Login'; 

function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const messagesEndRef = useRef(null);
  const [calendarKey, setCalendarKey] = useState(0);


  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    if (user && user.name && messages.length === 0) {
      const firstName = user.name.split(' ')[0];
      setMessages([
        {
          role: 'assistant',
          content: `Hello ${firstName}! I'm PlanPal. How can I help you with your calendar today?`,
        },
      ]);
    }
  }, [user, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleLoginSuccess = (data) => {
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('authToken', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch("https://planpal-lrka.onrender.com/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
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
      setCalendarKey(prevKey => prevKey + 1);
    }
  };

  const toggleCalendar = () => {
    setShowCalendar(!showCalendar);
  };

  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="chat-container">
      <div className="chat-window">
         <header className="header">
          <div className="header-left">
            <div className="avatar">🤖</div>
            <div className="bot-info">
              <div className="bot-name">PlanPal</div>
              <div className="status">Online</div>
            </div>
          </div>
          <button onClick={handleLogout} className="logout-button">Logout</button>
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
      
      <div className={`calendar-view-container ${showCalendar ? 'show' : ''}`}>
        <GoogleCalendar key={calendarKey} userEmail={user?.email} />
      </div>

      <button className="view-toggle" onClick={toggleCalendar}>
        {showCalendar ? '💬' : '📅'}
      </button>
    </div>
  );
}

export default App;
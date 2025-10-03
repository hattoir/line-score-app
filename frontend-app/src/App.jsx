import React, { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import ChatRoom from './components/ChatRoom';
import DiagnosisPage from './components/DiagnosisPage';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, text: '🎉 山根恵太最強', user: { name: '山根恵太', icon: '山' }, timestamp: '18:00'},
    { id: 2, text: ' 天才', user: { name: 'LINE Bot', icon: 'L' }, timestamp: '17:30'},
    { id: 3, text: '💰 あ', user: { name: '山根', icon: '山' }, timestamp: '15:00' },
  ]);

  const [searchTerm, setSearchTerm] = useState('');

  const filteredMessages = messages.filter((msg) => {
    const term = searchTerm.toLowerCase();
    const userName = msg.user.name.toLowerCase();
    return userName.includes(term) || msg.timestamp.includes(term);
  });

  return (
    <div className="app-container">
      <header className='app-header'>
        <h1>性格診断</h1>
        <input
          type="text"
          placeholder="ユーザー名で検索"
          className="search-box"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </header>
      <main className='chat-room-container'>
        <Routes>
          <Route path="/" element={
            <div className="chatroom-wrapper">
              <Link to="/diagnosis" className="diagnosis-button">
                診断
              </Link>
              <ChatRoom messages={filteredMessages} />
            </div>
          } />
          <Route path="/diagnosis" element={<DiagnosisPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
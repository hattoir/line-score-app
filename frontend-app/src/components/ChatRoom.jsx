import React, { useEffect, useRef } from 'react';

const ChatRoom = ({ messages = [] }) => { 
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-room">
        <p className="no-messages">通知はまだありません。</p>
      </div>
    );
  }

  return (
    <div className="chat-room">
      {messages.map((msg) => (
        <div
          key={msg.id}
          // 'me' という名前のユーザーだったら自分のメッセージとする (今回は未使用)
          className={`message-container ${msg.user.name === 'me' ? 'my-message' : 'other-message'}`}
        >
          {/* ▼ ここから追加 ▼ */}
          <div className="message-icon">
            {msg.user.icon}
          </div>
          {/* ▲ ここまで追加 ▲ */}

          {/* ▼ メッセージ本体をdivで囲む ▼ */}
          <div className="message-content">
            {/* ▼ ユーザー名表示を追加 ▼ */}
            <div className="user-name">{msg.user.name}</div>

            <div className="message-bubble">
              <p className="message-text">{msg.text}</p>
            </div>
            <span className="message-timestamp">{msg.timestamp}</span>
          </div>
        </div>
      ))}
      <div ref={endOfMessagesRef} />
    </div>
  );
};

export default ChatRoom;
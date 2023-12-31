CREATE TABLE chat_history (
      id CHAR(36) PRIMARY KEY,
      chatbot_id VARCHAR(36),
      session_id VARCHAR(255),
      from_user BOOLEAN,
      message VARCHAR(8192),
      created_at DATETIME,
      updated_at DATETIME
    )

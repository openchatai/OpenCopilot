CREATE TABLE chatbots (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'My first chatbot',
    token VARCHAR(255) NOT NULL,
    website VARCHAR(255) DEFAULT 'https://openchat.so',
    status VARCHAR(255),
    prompt_message TEXT,  -- Assuming TEXT data type for a large text field
    enhanced_privacy BOOLEAN DEFAULT false,
    smart_sync BOOLEAN DEFAULT false,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    swagger_url VARCHAR(255),
    is_premade_demo_template BOOLEAN DEFAULT false
);
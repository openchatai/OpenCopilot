use chrono::NaiveDateTime;
use serde::{Serialize, Deserialize}; // You'll need the chrono crate for working with timestamps

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatbotSetting {
    pub id: String,
    pub chatbot_id: String,
    pub name: String,
    pub value: String,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

impl ChatbotSetting {
    pub fn new(id: String, chatbot_id: String, name: String, value: String, created_at: NaiveDateTime, updated_at: NaiveDateTime) -> Self {
        ChatbotSetting {
            id,
            chatbot_id,
            name,
            value,
            created_at,
            updated_at,
        }
    }
}
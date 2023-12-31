use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ChatHistory {
    pub id: String,
    pub chatbot_id: String,
    pub session_id: String,
    pub from_user: bool,
    pub message: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}
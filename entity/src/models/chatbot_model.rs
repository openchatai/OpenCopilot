use serde::{Deserialize, Serialize};
use chrono::NaiveDateTime;
#[derive(Deserialize, Serialize)]
pub struct Chatbot {
    pub id: String,
    pub name: String,
    pub token: String,
    pub website: Option<String>,
    pub status: Option<String>,
    pub prompt_message: Option<String>,
    pub enhanced_privacy: Option<i8>,
    pub smart_sync: Option<i8>,
    pub created_at: Option<NaiveDateTime>,
    pub updated_at: Option<NaiveDateTime>,
    pub deleted_at: Option<NaiveDateTime>,
    pub swagger_url: Option<String>,
    pub is_premade_demo_template: Option<i8>,
}

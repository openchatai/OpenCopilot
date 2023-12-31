use chrono::NaiveDateTime;
use serde::{Serialize, Deserialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct CreateChatbotSetting {
    pub id: String,
    pub chatbot_id: String,
    pub name: String,
    pub value: String,
    #[schema(value_type = String)]
    pub created_at: NaiveDateTime,
    #[schema(value_type = String)]
    pub updated_at: NaiveDateTime,
}

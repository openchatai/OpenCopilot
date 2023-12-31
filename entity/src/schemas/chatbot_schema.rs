use serde::{Serialize, Deserialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ChatbotCreateRequest {
    pub name: String,
    pub token: String,
    pub website: Option<String>,
    pub status: Option<String>,
    pub prompt_message: Option<String>,
    pub enhanced_privacy: Option<bool>,
    pub smart_sync: Option<bool>,
}


#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ChatbotUpdateRequest {
    pub id: String,
    pub name: Option<String>,
    pub token: Option<String>,
    pub website: Option<String>,
    pub status: Option<String>,
    pub prompt_message: Option<String>,
    pub enhanced_privacy: Option<bool>,
    pub smart_sync: Option<bool>,
}


// ChatbotDeleteRequest schema
#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct ChatbotDeleteRequest {
    pub id: String,
}



#[derive(Deserialize, Debug)]
pub struct FilterOptions {
    pub page: Option<usize>,
    pub limit: Option<usize>,
}

// ChatbotSortOptions schema
#[derive(Debug, Serialize, Deserialize)]
pub struct ChatbotSortOptions {
    pub field: String,
    pub order: SortOrder,
}

// SortOrder enum
#[derive(Debug, Serialize, Deserialize)]
pub enum SortOrder {
    Ascending,
    Descending,
}
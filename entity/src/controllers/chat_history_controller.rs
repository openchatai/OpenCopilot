use crate::AppState;
use crate::models::chat_history_model::ChatHistory;
use crate::schemas::chat_history_schema::CreateChatHistoryDto;

use chrono::Utc;
use uuid::Uuid;

use actix_web::{delete, get, post, web, HttpResponse, Responder};
use serde_json::json;

#[utoipa::path(
    get,
    path = "/api/healthchecker",
    tag = "Health Checker Endpoint",
    responses(
        (status = 200, description= "Authenticated User"),       
    )
)]
#[get("/healthchecker")]
async fn health_checker_handler() -> impl Responder {
    const MESSAGE: &str = "Build Simple CRUD API with Rust, SQLX, MySQL, and Actix Web";

    HttpResponse::Ok().json(json!({"status": "success","message": MESSAGE}))
}


#[utoipa::path(
    operation_id = "create_chat_history",
    post,
    path = "/api/chat_history",
    request_body(content = CreateChatHistoryDto, content_type = "application/json"),
    responses(
        (status = 204, description = "Chat History Created Successfully", body = ()),
    )
)]
#[post("/chat_history")]
async fn create_chat_history(
    chat_history: web::Json<CreateChatHistoryDto>, 
    data: web::Data<AppState>,
) -> HttpResponse {
    let chat_history = ChatHistory {
        id: Uuid::new_v4().to_string(),
        chatbot_id: chat_history.chatbot_id.clone(),
        session_id: chat_history.session_id.clone(),
        from_user: chat_history.from_user,
        message: chat_history.message.clone(),
        created_at: Utc::now(),
        updated_at: Utc::now()  
    };

    let _ = sqlx::query!(
        r#"
        INSERT INTO chat_history (
            id, chatbot_id, session_id, from_user, 
            message, created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?
        )
        "#,
        chat_history.id,
        chat_history.chatbot_id,
        chat_history.session_id,
        chat_history.from_user,
        chat_history.message,
        chat_history.created_at,
        chat_history.updated_at
    )
    .execute(&data.db)
    .await
    .map_err(|err: sqlx::Error| err.to_string());

    HttpResponse::Created().finish()
}


#[utoipa::path(
    operation_id = "get_chat_history",
    post,
    path = "/api/chat_history/{id}",
    params(
        ("id" = String, Path, description = "id of chat history")
    ),
    responses(
        (status = 204, description = "Chat History Created Successfully", body = ChatHistoryDto),
    )
)]
#[get("/chat_history/{id}")]
async fn get_chat_history(
    data: web::Data<AppState>,  
    id: web::Path<String>, 
) -> HttpResponse {
    let id = id.into_inner();
    let _ = sqlx::query!("SELECT *
                    FROM chat_history
                    WHERE chatbot_id = ?
                ",
        id
    )
    .fetch_all(&data.db) // -> Vec<{ country: String, count: i64 }>
    .await
    .map_err(|err: sqlx::Error| err.to_string());

    HttpResponse::Ok().finish()
}


#[utoipa::path(
    operation_id = "delete_chat_history",
    post,
    path = "/api/chat_history/{id}",
    params(
        ("id" = String, Path, description = "id of chat history")
    ),
    responses(
        (status = 204, description = "Chat History Created Successfully"),
    )
)]
#[delete("/chat_history/{id}")] 
async fn delete_chat_history(
    id: web::Path<String>, 
    data: web::Data<AppState>
) -> impl Responder {

    let id = id.into_inner();

    let _ = sqlx::query!(
        r#"
        DELETE FROM chat_history
        WHERE id = ?
        "#,
        id
    )
    .execute(&data.db)
    .await
    .map_err(|err: sqlx::Error| err.to_string());

    HttpResponse::NoContent().finish()
}

pub fn config(conf: &mut web::ServiceConfig) {
    let scope = web::scope("/api")
        .service(health_checker_handler)
        .service(create_chat_history)
        .service(get_chat_history)
        .service(delete_chat_history);

    conf.service(scope);
}
use crate::{AppState, models::chatbot_setting_model::ChatbotSetting, schemas::chatbot_settings_schema::CreateChatbotSetting};

use actix_web::{get, post, web, HttpResponse, Responder};
use serde_json::json;

#[utoipa::path(
    get,
    path = "/healthchecker",
    tag = "Health Checker Endpoint",
    responses(
        (status = 200, description = "Authenticated User", body = Response),
    )
)]
#[get("/healthchecker")]
async fn health_checker_handler() -> impl Responder {
    const MESSAGE: &str = "Build Simple CRUD API with Rust, SQLX, MySQL, and Actix Web";

    HttpResponse::Ok().json(json!({"status": "success","message": MESSAGE}))
}

#[utoipa::path(
    operation_id = "create_chatbot_setting",
    post,
    path = "/chatbot_setting",
    request_body(content = CreateChatbotSetting, content_type = "application/json"),
    responses(
        (status = 200, description = "Chatbot Setting Created Successfully", body = ()),
        (status = 400, description = "Chatbot Setting with that title already exists", body = ()),
        (status = 500, description = "Internal Server Error", body = ()),
    )
)]
#[post("/chatbot_setting")]
pub async fn create_chatbot_setting_handler(
    body: web::Json<CreateChatbotSetting>,
    data: web::Data<AppState>,
) -> HttpResponse {
    let query_result =
    sqlx::query(r#"INSERT INTO chatbot_settings (id,chatbot_id,name,value) VALUES (?, ?, ?, ?)"#)
        .bind(body.id.to_owned())
        .bind(body.chatbot_id.to_owned())
        .bind(body.name.to_owned())
        .bind(body.value.to_owned())
        .execute(&data.db)
        .await
        .map_err(|err: sqlx::Error| err.to_string());

    if let Err(err) = query_result {
            if err.contains("Duplicate entry") {
                return HttpResponse::BadRequest().json(
                serde_json::json!({"status": "fail","message": "chatbot with that title already exists"}),
            );
        }

        return HttpResponse::InternalServerError()
            .json(serde_json::json!({"status": "error","message": format!("{:?}", err)}));
    }

    HttpResponse::Ok().finish()
}

#[utoipa::path(
    operation_id = "get_chatbot_setting",
    get,
    path = "/chatbot_setting/{id}",
    params(
        ("id" = String, Path, description = "id of chatbot setting")
    ),
    responses(
        (status = 200, description = "Chatbot Setting Found Successfully", body = CreateChatbotSetting),
        (status = 404, description = "Chatbot Setting Not Found", body = ()),
    )
)]
#[get("/chatbot_setting/{id}")]
async fn get_chatbot_setting_handler(
    path: web::Path<String>,
    data: web::Data<AppState>,
) -> HttpResponse {
    let chatbot_id = path.into_inner().to_string();
    let query_result = sqlx::query_as!(ChatbotSetting, r#"SELECT * FROM chatbot_settings WHERE id = ?"#, chatbot_id)
        .fetch_one(&data.db)
        .await;

    match query_result {
        Ok(chatbot_setting) => HttpResponse::Ok().json(chatbot_setting),
        Err(sqlx::Error::RowNotFound) => HttpResponse::NotFound().finish(),
        Err(err) => HttpResponse::InternalServerError().json(err.to_string()),
    }
}



pub fn config(conf: &mut web::ServiceConfig) {
    let scope = web::scope("/api")
        .service(health_checker_handler)
        .service(create_chatbot_setting_handler)
        .service(get_chatbot_setting_handler);
    conf.service(scope);
}

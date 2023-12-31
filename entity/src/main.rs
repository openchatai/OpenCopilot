pub mod models;
pub mod controllers;
pub mod schemas;

use actix_web::middleware::Logger;
use actix_web::{ web, App, HttpServer};
use dotenv::dotenv;
use sqlx::MySqlPool;
use sqlx::mysql::MySqlPoolOptions;
use utoipa_swagger_ui::SwaggerUi;
use chrono::NaiveDateTime;

use crate::controllers::chat_history_controller::{__path_health_checker_handler, __path_create_chat_history, __path_delete_chat_history, __path_get_chat_history};

use crate::controllers::chatbot_controller::{__path_create_chatbot_handler, __path_delete_chatbot_handler, __path_get_chatbot_handler, __path_list_chatbot_handler};

use crate::controllers::chatbot_setting_controller::{__path_create_chatbot_setting_handler, __path_get_chatbot_setting_handler};

use crate::schemas::chat_history_schema::{ChatHistoryDto, CreateChatHistoryDto};
use crate::schemas::chatbot_schema::{ChatbotCreateRequest, ChatbotDeleteRequest, ChatbotUpdateRequest};
use crate::schemas::chatbot_settings_schema::CreateChatbotSetting;
use utoipa::OpenApi;

#[derive(OpenApi)]
#[openapi(
    paths(health_checker_handler, create_chat_history, delete_chat_history, get_chat_history, create_chatbot_handler, delete_chatbot_handler, get_chatbot_handler, list_chatbot_handler, create_chatbot_setting_handler, get_chatbot_setting_handler),
    components(
        schemas(
            ChatHistoryDto,
            CreateChatHistoryDto,
            ChatbotCreateRequest, 
            ChatbotDeleteRequest, 
            ChatbotUpdateRequest,
            CreateChatbotSetting
        )
    ),
    tags((name = "Opencopilot Entities", description = "CRUD operation on all endpoints")),
    modifiers()
)]
struct ApiDoc;


pub struct AppState {
    db: MySqlPool,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    if std::env::var_os("RUST_LOG").is_none() {
        std::env::set_var("RUST_LOG", "actix_web=info");
    }
    dotenv().ok();

    let database_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = match MySqlPoolOptions::new()
        .max_connections(10)
        .connect(&database_url)
        .await
    {
        Ok(pool) => {
            println!("✅Connection to the database is successful!");
            pool
        }
        Err(err) => {
            println!("🔥 Failed to connect to the database: {:?}", err);
            std::process::exit(1);
        }
    };

    println!("🚀 Server started successfully");
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(AppState { db: pool.clone() }))
            .service(
                SwaggerUi::new("/swagger-ui/{_:.*}")
                    .url("/api-docs/openapi.json", ApiDoc::openapi()),
            )
            .configure(controllers::chatbot_controller::config)
            .configure(controllers::chatbot_setting_controller::config)
            .configure(controllers::chatbot_setting_controller::config)
            .wrap(Logger::default())
    })
    .bind(("127.0.0.1", 8000))?
    .run()
    .await
}
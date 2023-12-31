pub struct FailedJob {
    pub id: String,
    pub uuid: String,
    pub connection: String,
    pub queue: String,
    pub payload: String,
    pub exception: String,
    pub failed_at: chrono::NaiveDateTime,
}

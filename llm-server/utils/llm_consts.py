import os
from functools import lru_cache
from typing import TypedDict

from qdrant_client import QdrantClient

EXPERIMENTAL_FEATURES_ENABLED = os.getenv("EXPERIMENTAL_FEATURES_ENABLED", "NO")
SYSTEM_MESSAGE_PROMPT = "system_message_prompt"
SUMMARIZATION_PROMPT = "summarization_prompt"
X_App_Name = "X-App-Name"


class VsThresholds(TypedDict):
    actions_score_threshold: float
    flows_score_threshold: float
    kb_score_threshold: float


vs_thresholds: VsThresholds = {
    "actions_score_threshold": float(os.getenv("ACTIONS_SCORE_THRESHOLD", "0.25")),
    "flows_score_threshold": float(os.getenv("FLOWS_SCORE_THRESHOLD", "0.75")),
    "kb_score_threshold": float(os.getenv("KB_SCORE_THRESHOLD", "0.55")),
}

model_env_var = "CHAT_MODEL"


class VectorCollections:
    flows = "flows"
    chat_history = "chat_history"
    actions = "actions"
    knowledgebase = "knowledgebase"


class ChatStrategy:
    chain = "chain"
    function = "function"
    tool = "tool"


class UserMessageResponseType:
    actionable = "actionable"  # The user message should be answered with an action (flow or api action)
    informative = (
        "informative"  # The user message should be answered a normal text response
    )


@lru_cache(maxsize=5)  # Cache all calls
def initialize_qdrant_client() -> QdrantClient:
    # Get the API key and URL from environment variables if not provided
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")

    client = QdrantClient(url=qdrant_url)
    return client


def get_mysql_uri():
    mysql_uri = os.getenv("MYSQL_URI", "mysql://dbuser:dbpass@mysql:3306/opencopilot")
    if not mysql_uri:
        raise ValueError("MYSQL_URI environment variable is not set")

    # Assuming the MYSQL_URI is in the format: mysql://username:password@host:port/database
    # You may need to adjust the parsing based on the actual format of your MYSQL_URI
    components = mysql_uri.split("://")[1].split("@")
    user_pass, host_port_db = components[0], components[1]
    username, password = user_pass.split(":")

    # Adjusting the parsing based on the expected format
    host_port, database = host_port_db.split("/")
    host, port = host_port.split(":")

    # Creating pymysql format string
    pymysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

    return pymysql_uri


chat_strategy = os.getenv("CHAT_STRATEGY", ChatStrategy.chain)

import structlog
import logging
import sentry_sdk
import os
from sentry_sdk.integrations.logging import LoggingIntegration

# capture all logs info and above
logging_level = logging.INFO
sentry_logging = LoggingIntegration(
    level=logging_level,        # Set the desired logging level
    event_level=logging_level    # Set the desired event level (optional)
)


sentry_sdk.init(
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[sentry_logging],
)

dsn = os.getenv("SENTRY_DSN")
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class CustomLogger:
    def __init__(self, module_name: str = __name__, level: int = logging.INFO):
        self.logger = structlog.get_logger(module_name)
        logging.basicConfig(level=level, format="%(message)s")

    def log(self, level, event, **kwargs):
        self.logger.log(
            level,
            event=event,
            **kwargs
        )
        
        # only enable this for prod environment
        sentry_sdk.capture_message(event, level=logging.getLevelName(level), scope=None) if dsn is not None else None

    def info(self, event, **kwargs):
        self.log(logging.INFO, event, **kwargs)

    def warn(self, event, **kwargs):
        self.log(logging.WARNING, event, **kwargs)

    def error(self, event, **kwargs):
        self.log(logging.ERROR, event, exc_info=True, **kwargs)

    def debug(self, event, **kwargs):
        self.log(logging.DEBUG, event, **kwargs)
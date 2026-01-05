# Eksport singletonów aplikacji
from app.config import ConfigManager, get_config
from app.database import Database, get_database
from app.logger import AppLogger, get_logger

__all__ = [
    "Database",
    "get_database",
    "ConfigManager", 
    "get_config",
    "AppLogger",
    "get_logger",
]

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config
from app.database import get_database
from app.logger import get_logger
from app.middleware import TelemetryMiddleware
from app.routers import survey_router
from app.telemetry import get_telemetry


# Zainicjowanie wszystkich singletonów przy starcie aplikacji
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicjalizacja singletonów
    db = get_database()
    logger = get_logger()
    config = get_config()
    telemetry = get_telemetry()
    
    logger.info("Application starting...", module="startup")
    logger.info(f"Database initialized: {db.get_stats()}", module="startup")
    logger.info(f"Config loaded: {config.get_stats()}", module="startup")
    logger.info(f"Logger initialized: {logger.get_stats()}", module="startup")
    logger.info(f"Telemetry initialized: {telemetry.get_stats()}", module="startup")
    
    yield
    
    logger.info("Application shutting down...", module="shutdown")


# Uruchomienie serwera
def create_app() -> FastAPI:
    config = get_config()
    
    app = FastAPI(
        title=config.get("api", "title", "Polly - Survey API"),
        description=(
            "API for creating and managing surveys. "
            "Similar to Microsoft Forms, allows creating surveys, "
            "collecting responses, and viewing statistics."
        ),
        version=config.get("api", "version", "1.0.0"),
        lifespan=lifespan,
        docs_url=config.get("api", "docs_url", "/docs"),
        redoc_url=config.get("api", "redoc_url", "/redoc"),
    )

    # Pobranie ustawień CORS z konfiguracji
    cors_config = config.get_section("cors")
    
    # Dodanie CORS aby każdy mógł wysłać żądanie
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get("allow_origins", ["*"]),
        allow_credentials=cors_config.get("allow_credentials", True),
        allow_methods=cors_config.get("allow_methods", ["*"]),
        allow_headers=cors_config.get("allow_headers", ["*"]),
    )

    # Dodanie middleware telemetrii (Application Insights)
    app.add_middleware(TelemetryMiddleware)

    # Dodanie endpointów ankiet
    app.include_router(survey_router)
    
    @app.get("/", tags=["health"])
    async def root():
        return {
            "name": "Polly Survey API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    # Endpoint /health aby sprawdzić czy baza danych działą
    @app.get("/health", tags=["health"])
    async def health_check():
        db = get_database()
        logger = get_logger()
        config = get_config()
        telemetry = get_telemetry()

        db_stats = db.get_stats()
        
        return {
            "status": "healthy",
            # Backward/Frontend-compatible shortcut fields
            "database": {
                "surveys": db_stats.get("total_surveys", 0),
                "responses": db_stats.get("total_responses", 0),
            },
            "singletons": {
                "database": db_stats,
                "logger": logger.get_stats(),
                "config": config.get_stats(),
                "telemetry": telemetry.get_stats(),
            },
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

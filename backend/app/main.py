from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_database
from app.routers import survey_router


# Zainicjowane bazy danych
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    print(f"Database initialized: {db.get_stats()}")
    yield
    print("Application shutting down...")


# Uruchomienie serwera
def create_app() -> FastAPI:
    app = FastAPI(
        title="Polly - Survey API",
        description=(
            "API for creating and managing surveys. "
            "Similar to Microsoft Forms, allows creating surveys, "
            "collecting responses, and viewing statistics."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Dodanie CORS aby każdy mógł wysłać żądanie
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
        return {
            "status": "healthy",
            "database": db.get_stats(),
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

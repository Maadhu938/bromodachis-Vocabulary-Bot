from fastapi import FastAPI
from app.api.routes import router
from app.scheduler.tasks import setup_scheduler
from app.database.connection import engine, Base
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)
    
    # Start scheduler
    scheduler = setup_scheduler()
    
    yield
    
    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Scheduler stopped.")

app = FastAPI(
    title="Bromodachis Vocabulary Bot",
    description="Daily Japanese Vocabulary Sender",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Bromodachis Vocabulary Bot API!"}

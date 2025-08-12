import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent.parent))

from server.routes.user_routes import router as user_router
from server.routes.calculation_routes import router as calculation_router
from server.routes.rate_routes import router as rate_router
from server.routes.calculation_history_routes import router as history_router
from server.routes.chatbot_routes import router as chatbot_router

from server.database import client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.0.106:3000",
        "https://fifa-coins.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/user")
app.include_router(calculation_router, prefix="/api")
app.include_router(rate_router, prefix="/api")
app.include_router(history_router, prefix="/api/history")
app.include_router(chatbot_router, prefix="/api")

@app.on_event("startup")
async def startup_db_client():
    print("Connecting to MongoDB...")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("MongoDB connection closed")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI with MongoDB and Chatbot is running 🚀"}


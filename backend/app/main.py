from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, chat, data, learning, documents

app = FastAPI(
    title="WanderWise AI API",
    swagger_ui_parameters={"withCredentials": True},
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(learning.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to WanderWise AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

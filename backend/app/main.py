from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, data, learning

app = FastAPI(title="WanderWise AI API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(learning.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to WanderWise AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

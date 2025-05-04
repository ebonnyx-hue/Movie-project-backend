import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import app

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=5050, reload=True) 
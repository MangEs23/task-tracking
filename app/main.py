from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routers import auth, projects

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API")

# Middleware CORS (dari teman Anda)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Endpoint (Auth & Projects)
app.include_router(auth.router)
app.include_router(projects.router)

@app.get("/")
def root():
    return {"message": "API is running"}
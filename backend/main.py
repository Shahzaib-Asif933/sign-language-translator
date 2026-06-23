from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.predict import router

app = FastAPI(title="AI Sign Language Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Sign Language Translator API is running!"}
# from fastapi import FastAPI
# from app.api.routes import router
# import uvicorn

# app = FastAPI(title="Document Processing API")

# app.include_router(router)

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Document Processing API"} 

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.routes import router
import uvicorn

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

app = FastAPI(title="Document Processing API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes with a prefix
app.include_router(router, prefix="/api")

# Mount static files BEFORE defining root route
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Note: We're removing the root endpoint as it will be handled by the static file server

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

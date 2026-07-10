from fastapi import FastAPI
from backend.app.api import projects, sync, knowledge

app = FastAPI(
    title="Akashic MVP - Backend and Knowledge Engine API",
    description="Thin API adapter layer orchestrating documentation sync jobs and exposing the compiled knowledge base.",
    version="0.1.0"
)

# Register endpoint routers
app.include_router(projects.router)
app.include_router(sync.router)
app.include_router(knowledge.router)

@app.get("/")
def read_root():
    return {
        "app": "Akashic MVP",
        "status": "healthy",
        "docs_url": "/docs"
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

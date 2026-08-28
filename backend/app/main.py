from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.actions import router as actions_router


app = FastAPI(title="Cluely Execute API")

# Vite serves the frontend on this local address during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(actions_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Smallest possible endpoint: confirms the API is running."""
    return {"status": "ok", "service": "cluely-execute-api"}

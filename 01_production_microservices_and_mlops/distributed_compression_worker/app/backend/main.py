import uvicorn as uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from auth.refresh_token import router as refresh_token_router
from auth.signup import router as signup_router
from auth.login import router as login_router
from routers.tasks import router as task_router


app = FastAPI()
router = APIRouter()


app.include_router(router)
app.include_router(signup_router)
app.include_router(login_router)
app.include_router(task_router)
app.include_router(refresh_token_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="192.168.0.163",
        port=8082,
        log_level="info",
        reload=True
    )


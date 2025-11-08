from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from routers.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="User removal API", version="1.0.0")

# ---- Глобальний хендлер для HTTPException (уніфіковані JSON-помилки)
@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    # detail вже містить наш машинозчитуваний код або текст
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Додатковий root, щоб / не давав 404
class RootOk(BaseModel):
    ok: bool = True

@app.get("/", include_in_schema=False, response_model=RootOk)
def root():
    return RootOk()

# Підключаємо роутер користувачів
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
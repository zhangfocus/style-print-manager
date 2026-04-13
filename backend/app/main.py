from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import styles, prints, positions, restrictions, excel_io

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="款式印花管理系统",
    description="管理款式、印花、位置及限定关系的后台系统",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(styles.router)
app.include_router(prints.router)
app.include_router(positions.router)
app.include_router(restrictions.router)
app.include_router(excel_io.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

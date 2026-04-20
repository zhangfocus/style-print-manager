from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import styles, prints, positions, excel_io
from .routers.restrictions import router as restrictions_router, bans_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="款式印花管理系统",
    description="管理款式、印花、位置及限定关系的后台系统",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(styles.router)
app.include_router(prints.router)
app.include_router(positions.router)
app.include_router(restrictions_router)
app.include_router(bans_router)
app.include_router(excel_io.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# 托管前端构建产物（放在所有 API 路由之后）
_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _DIST.exists():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def serve_root():
        return FileResponse(_DIST / "index.html")

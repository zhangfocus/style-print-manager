from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base, SessionLocal
from .routers import styles, prints, positions, excel_io
from .routers.restrictions import router as restrictions_router, bans_router
from .cache import name_cache

Base.metadata.create_all(bind=engine)

# 定时任务调度器
scheduler = BackgroundScheduler()


def refresh_cache_job():
    """定时刷新缓存任务"""
    db = SessionLocal()
    try:
        name_cache.refresh_cache(db)
    except Exception as e:
        print(f"[Cache] 缓存刷新失败: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化缓存
    db = SessionLocal()
    try:
        name_cache.init_cache(db)
    except Exception as e:
        print(f"[Cache] 初始化缓存失败: {e}")
    finally:
        db.close()

    # 启动定时任务（每小时刷新一次）
    scheduler.add_job(refresh_cache_job, 'interval', hours=1, id='refresh_cache')
    scheduler.start()
    print("[Scheduler] 定时任务已启动")

    yield

    # 关闭时停止定时任务
    scheduler.shutdown()
    print("[Scheduler] 定时任务已停止")

app = FastAPI(
    title="款式印花管理系统",
    description="管理款式、印花、位置及限定关系的后台系统",
    version="2.0.0",
    lifespan=lifespan,
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

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import styles, prints, positions, restrictions, excel_io
import os

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="款式印花管理系统",
    description="管理款式、印花、位置及限定关系的后台系统",
    version="1.0.0",
)

# Register routers
app.include_router(styles.router)
app.include_router(prints.router)
app.include_router(positions.router)
app.include_router(restrictions.router)
app.include_router(excel_io.router)

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

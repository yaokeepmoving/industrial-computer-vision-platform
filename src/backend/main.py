from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from .routers.annotation import router as annotation_router
from .routers.cv_operation import router as cv_operation_router
from .routers.pipeline import router as cv_pipeline_router


# 创建FastAPI应用实例
app = FastAPI(
    title="工业铸字识别系统API",
    description="工业铸字识别系统的后端API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件路由
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 根路由
@app.get("/")
async def root():
    return {"message": "工业铸字识别系统API服务正在运行"}

# 注册标注路由
app.include_router(annotation_router)
app.include_router(cv_operation_router)
app.include_router(cv_pipeline_router)

# 启动服务器
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
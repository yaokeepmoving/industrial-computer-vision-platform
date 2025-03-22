from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..routers.base import CamelModel
from ..services.pipeline import PipelineService
from ..dependencies import get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/api/pipeline", tags=["pipelines"])

# 响应模型
class PipelineResponse(CamelModel):
    id: int
    name: str
    description: str | None
    operations: list
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 请求模型
class CreatePipelineRequest(BaseModel):
    name: str
    description: str | None = None
    operations: list | None = None

class UpdatePipelineRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    operations: list | None = None

@router.get("/pipelines", response_model=List[PipelineResponse])
async def get_pipelines(db: Session = Depends(get_db)):
    """获取所有管道"""
    service = PipelineService(db)
    return service.get_pipelines()

@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """获取指定管道"""
    service = PipelineService(db)
    pipeline = service.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@router.post("/pipelines", response_model=PipelineResponse)
async def create_pipeline(request: CreatePipelineRequest, db: Session = Depends(get_db)):
    """创建新的管道"""
    service = PipelineService(db)
    try:
        return service.create_pipeline(
            name=request.name,
            description=request.description,
            operations=request.operations
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    request: UpdatePipelineRequest,
    db: Session = Depends(get_db)
):
    """更新管道"""
    service = PipelineService(db)
    try:
        return service.update_pipeline(
            pipeline_id=pipeline_id,
            name=request.name,
            description=request.description,
            operations=request.operations
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """删除管道"""
    service = PipelineService(db)
    try:
        service.delete_pipeline(pipeline_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply_pipeline")
async def apply_pipeline(
    image_file: UploadFile = File(...),
    pipeline_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """应用管道处理图像"""
    service = PipelineService(db)
    try:
        contents = await image_file.read()
        result = service.apply_pipeline(contents, pipeline_id)
        
        # 返回处理结果
        if isinstance(result.get('data'), bytes):
            return Response(
                content=result['data'],
                media_type="image/png",
                headers={
                    'X-Pipeline-Results': json.dumps(result['results'])
                }
            )
        else:
            return result
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
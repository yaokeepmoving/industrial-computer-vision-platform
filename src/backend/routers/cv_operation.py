from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from ..routers.base import CamelModel
from ..services.cv_operation import CVOperationService
from ..dependencies import get_db
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..models import ParamConfig

router = APIRouter(prefix="/api/cv", tags=["cv_operations"])

# --- 响应模型继承 CamelModel ---
class CVOperationResponse(CamelModel):
    id: int
    name: str
    description: str | None
    code: str
    input_params: List[ParamConfig]
    output_params: List[ParamConfig]
    created_at: datetime
    updated_at: datetime

# --- 请求模型 ---
class CreateOperationRequest(BaseModel):
    name: str
    code: str
    description: str | None = None
    input_params: List[ParamConfig] | None = None
    output_params: List[ParamConfig] | None = None

class UpdateOperationRequest(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    input_params: List[ParamConfig] | None = None
    output_params: List[ParamConfig] | None = None


@router.get("/operations", response_model=List[CVOperationResponse])
async def get_operations(db: Session = Depends(get_db)):
    """获取所有CV操作"""
    service = CVOperationService(db)
    return service.get_operations()

@router.get("/operations/{operation_id}", response_model=CVOperationResponse)
async def get_operation(operation_id: int, db: Session = Depends(get_db)):
    """获取指定CV操作"""
    service = CVOperationService(db)
    operation = service.get_operation(operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return operation

@router.post("/operations", response_model=CVOperationResponse)
async def create_operation(request: CreateOperationRequest, db: Session = Depends(get_db)):
    """创建新的CV操作"""
    service = CVOperationService(db)
    try:
        return service.create_operation(
            name=request.name,
            code=request.code,
            description=request.description,
            input_params=request.input_params,
            output_params=request.output_params
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/operations/{operation_id}", response_model=CVOperationResponse)
async def update_operation(
    operation_id: int,
    request: UpdateOperationRequest,
    db: Session = Depends(get_db)
):
    """更新CV操作"""
    service = CVOperationService(db)
    try:
        return service.update_operation(
            operation_id=operation_id,
            name=request.name,
            code=request.code,
            description=request.description,
            input_params=request.input_params,
            output_params=request.output_params
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/operations/{operation_id}")
async def delete_operation(operation_id: int, db: Session = Depends(get_db)):
    """删除CV操作"""
    service = CVOperationService(db)
    try:
        service.delete_operation(operation_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply_operation")
async def apply_operation(
    operation_id: int = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """应用CV操作并返回处理结果"""
    service = CVOperationService(db)
    try:
        form_data = await request.form()
        result = service.apply_operation(operation_id, form_data)
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
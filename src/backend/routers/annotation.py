from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from sqlalchemy.orm import Session
from ..services.annotation import AnnotationService
from ..models import DatasetType
from ..dependencies import get_db
from typing import List
from datetime import datetime
import os
from pydantic import BaseModel

router = APIRouter(prefix="/api/annotation", tags=["annotation"])

# 响应模型
class DatasetResponse(BaseModel):
    id: int
    name: str
    type: DatasetType
    imageCount: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class ImageResponse(BaseModel):
    id: int
    filename: str
    url: str
    datasetId: int
    createdAt: datetime
    isAnnotated: bool = False

    class Config:
        from_attributes = True

# 请求模型
class CreateDatasetRequest(BaseModel):
    name: str
    type: DatasetType = DatasetType.TEXT_REGION

class UpdateDatasetRequest(BaseModel):
    name: str

# 数据集管理接口
@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(db: Session = Depends(get_db)):
    """获取所有数据集"""
    service = AnnotationService(db)
    datasets = service.get_datasets()
    
    # 转换为响应格式
    return [
        {
            "id": dataset.id,
            "name": dataset.name,
            "type": dataset.type,
            "imageCount": len(dataset.images),
            "createdAt": dataset.created_at,
            "updatedAt": dataset.updated_at
        }
        for dataset in datasets
    ]

@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    request: CreateDatasetRequest,
    db: Session = Depends(get_db)
):
    """创建新数据集"""
    service = AnnotationService(db)
    try:
        dataset = service.create_dataset(request.name, request.type)
        return {
            "id": dataset.id,
            "name": dataset.name,
            "type": dataset.type,
            "imageCount": len(dataset.images),
            "createdAt": dataset.created_at,
            "updatedAt": dataset.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create dataset: {str(e)}"
        )

@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
async def rename_dataset(
    dataset_id: int,
    request: UpdateDatasetRequest,
    db: Session = Depends(get_db)
):
    """重命名数据集"""
    service = AnnotationService(db)
    try:
        dataset = service.rename_dataset(dataset_id, request.name)
        return {
            "id": dataset.id,
            "name": dataset.name,
            "type": dataset.type,
            "imageCount": len(dataset.images),
            "createdAt": dataset.created_at,
            "updatedAt": dataset.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to rename dataset: {str(e)}"
        )

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    service = AnnotationService(db)
    service.delete_dataset(dataset_id)
    return {"status": "success"}

# 图片管理接口
@router.get("/datasets/{dataset_id}/images", response_model=List[ImageResponse])
async def get_dataset_images(dataset_id: int, db: Session = Depends(get_db)):
    """获取数据集下的所有图片"""
    service = AnnotationService(db)
    try:
        images = service.get_dataset_images(dataset_id)
        return [
            {
                "id": image.id,
                "filename": image.filename,
                "url": f"/uploads/{dataset_id}/{image.filename}",  # 根据实际的URL规则调整
                "isAnnotated": image.is_annotated,
                "datasetId": image.dataset_id,
                "createdAt": image.created_at
            }
            for image in images
        ]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get images: {str(e)}"
        )

@router.post("/datasets/{dataset_id}/images", response_model=List[ImageResponse])
async def upload_images(
    dataset_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """上传图片到数据集"""
    service = AnnotationService(db)
    uploaded_images = []
    
    try:
        # 确保上传目录存在
        upload_dir = os.path.join("uploads", str(dataset_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            # 生成安全的文件名
            filename = file.filename
            file_path = os.path.join(upload_dir, filename)
            
            # 保存文件
            try:
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to save file {filename}: {str(e)}"
                )
            
            # 保存到数据库
            try:
                url = f"/uploads/{dataset_id}/{filename}"
                image = service.create_image(
                    dataset_id=dataset_id,
                    filename=filename,
                    url=url
                )
                uploaded_images.append({
                    "id": image.id,
                    "filename": image.filename,
                    "url": url,
                    "datasetId": image.dataset_id,
                    "createdAt": image.created_at,
                    "isAnnotated": image.is_annotated
                })
            except Exception as e:
                # 如果数据库保存失败，删除已上传的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        return uploaded_images
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload images: {str(e)}"
        )

@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    service = AnnotationService(db)
    service.delete_image(image_id)
    return {"status": "success"}

# 标注管理接口
@router.get("/images/{image_id}/annotation")
async def get_image_annotation(image_id: int, db: Session = Depends(get_db)):
    """获取图片的标注数据"""
    service = AnnotationService(db)
    try:
        annotation = service.get_image_annotation(image_id)
        if annotation:
            return {
                "annotations": annotation.get("labels", []),
                "status": annotation.get("status", "pending")
            }
        return {
            "annotations": [],
            "status": "pending"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get annotation: {str(e)}"
        )

@router.post("/images/{image_id}/annotation")
async def create_annotation(
    image_id: int,
    annotation_data: dict,
    db: Session = Depends(get_db)
):
    service = AnnotationService(db)
    try:
        annotation = service.create_annotation(image_id, annotation_data)
        return {"status": "success", "annotation": annotation}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create annotation: {str(e)}"
        )

@router.put("/images/{image_id}/annotations/{annotation_id}")
async def update_annotation(
    image_id: int,
    annotation_id: int,
    annotation_data: dict,
    db: Session = Depends(get_db)
):
    service = AnnotationService(db)
    try:
        annotation = service.update_annotation(annotation_id, annotation_data)
        return {"status": "success", "annotation": annotation}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update annotation: {str(e)}"
        )


@router.delete("/images/{image_id}/annotations/{annotation_id}")
async def delete_annotation(
    image_id: int, 
    annotation_id: str, 
    db: Session = Depends(get_db)
):
    service = AnnotationService(db)
    try:
        service.delete_annotation(image_id, annotation_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete annotation: {str(e)}"
        )
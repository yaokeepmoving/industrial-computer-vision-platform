from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import Base, engine
from typing import Any
from typing_extensions import TypedDict

class DatasetType(PyEnum):
    TEXT_REGION = 'text_region'  # 文本区域数据集
    OCR = 'ocr'                  # OCR数据集

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[DatasetType] = mapped_column(Enum(DatasetType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_annotated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dataset = relationship("Dataset", back_populates="images")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")

class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)  # 存储标注数据的JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    image = relationship("Image", back_populates="annotations")

class ParamType(PyEnum):
    IMAGE = 'image'           # 图像类型
    NUMBER = 'number'         # 数值类型(int/float)
    TEXT = 'text'            # 文本类型
    BOOLEAN = 'boolean'      # 布尔类型
    ARRAY = 'array'          # 数组类型
    OBJECT = 'object'        # 对象类型

class ParamConfig(TypedDict):
    name: str                # 参数名称
    type: ParamType         # 参数类型
    description: str        # 参数描述
    default: Any           # 默认值
    required: bool         # 是否必需

class CVOperation(Base):
    __tablename__ = "cv_operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    code: Mapped[str] = mapped_column(String(10000), nullable=False)
    input_params: Mapped[list[ParamConfig]] = mapped_column(JSON, nullable=False, default=list)  # 输入参数配置
    output_params: Mapped[list[ParamConfig]] = mapped_column(JSON, nullable=False, default=list)  # 输入参数配置
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    operations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # 存储操作ID和参数的列表
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)
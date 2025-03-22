import base64
import json
import cv2
from fastapi.datastructures import FormData
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from ..models import CVOperation, ParamType, ParamConfig
from datetime import datetime
from typing import List, Optional, Dict, Any

class CVOperationService:
    def __init__(self, db: Session):
        self.db = db
        # 初始化代码执行上下文
        self.context = {
            'cv2': cv2,
            'np': np
        }

    def get_operations(self) -> List[CVOperation]:
        """获取所有CV操作"""
        return self.db.query(CVOperation).all()

    def get_operation(self, operation_id: int) -> Optional[CVOperation]:
        """获取指定CV操作"""
        return self.db.query(CVOperation).filter(CVOperation.id == operation_id).first()

    def create_operation(self, name: str, code: str, 
                        input_params: List[ParamConfig] = None,
                        output_params: List[ParamConfig] = None,
                        description: str = None) -> CVOperation:
        """创建新的CV操作"""
        try:
            operation = CVOperation(
                name=name,
                description=description,
                code=code,
                input_params=input_params or [],
                output_params=output_params or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(operation)
            self.db.commit()
            self.db.refresh(operation)
            return operation
        except Exception as e:
            self.db.rollback()
            raise e

    def update_operation(self, operation_id: int, name: str = None, 
                        code: str = None, description: str = None,
                        input_params: List[ParamConfig] = None,
                        output_params: List[ParamConfig] = None) -> CVOperation:
        """更新CV操作"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")

        if name is not None:
            operation.name = name
        if code is not None:
            operation.code = code
        if description is not None:
            operation.description = description
        if input_params is not None:
            operation.input_params = input_params
        if output_params is not None:
            operation.output_params = output_params
            
        operation.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(operation)
            return operation
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_operation(self, operation_id: int) -> None:
        """删除CV操作"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
            
        try:
            self.db.delete(operation)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e 
        
    def apply_operation(self, operation_id: int, params: FormData) -> dict:
        """应用CV操作并返回处理结果"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")

        try:
            # 根据operation的input_params处理参数
            processed_params = {}
            if params:
                for param_config in operation.input_params:
                    param_value = params.get(param_config.name)
                    if param_value is None:
                        if param_config.get('required', False):  # 检查必需参数
                            raise HTTPException(
                                status_code=400,
                                detail=f"Missing required parameter: {param_config.name}"
                            )
                        continue

                    try:
                        if param_config.type == ParamType.IMAGE:
                            # 处理图片类型
                            if isinstance(param_value, UploadFile):
                                image_bytes = param_value.file.read()
                                nparr = np.frombuffer(image_bytes, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                if img is None:
                                    raise ValueError("Invalid image data")
                                processed_params[param_config.name] = img
                            else:
                                raise ValueError("Expected UploadFile for image parameter")
                                
                        elif param_config.type == ParamType.NUMBER:
                            # 处理数值类型
                            processed_params[param_config.name] = float(param_value)
                            
                        elif param_config.type == ParamType.TEXT:
                            # 处理文本类型
                            processed_params[param_config.name] = str(param_value)
                            
                        elif param_config.type == ParamType.BOOLEAN:
                            # 处理布尔类型
                            if isinstance(param_value, str):
                                processed_params[param_config.name] = param_value.lower() == 'true'
                            else:
                                processed_params[param_config.name] = bool(param_value)
                                
                        elif param_config.type in (ParamType.ARRAY, ParamType.OBJECT):
                            # 处理数组和对象类型
                            if isinstance(param_value, str):
                                try:
                                    processed_params[param_config.name] = json.loads(param_value)
                                except json.JSONDecodeError:
                                    raise ValueError(f"Invalid JSON for parameter {param_config.name}")
                            else:
                                processed_params[param_config.name] = param_value
                        else:
                            # 未知类型保持不变
                            processed_params[param_config.name] = param_value
                            
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Error processing parameter {param_config.name}: {str(e)}"
                        )

            # 准备执行环境
            exec_context = {
                **self.context,
                **processed_params
            }

            # 执行代码
            namespace = {}
            try:
                exec(operation.code, exec_context, namespace)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error executing operation code: {str(e)}"
                )

            if 'process' not in namespace:
                raise HTTPException(
                    status_code=400,
                    detail="No 'process' function defined in operation code"
                )

            # 验证处理函数
            process_func = namespace['process']
            if not callable(process_func):
                raise HTTPException(
                    status_code=400,
                    detail="'process' must be a callable function"
                )

            # 执行处理函数
            try:
                result = process_func(**processed_params) if processed_params else process_func()
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error executing process function: {str(e)}"
                )

            # 验证输出类型
            if not operation.output_params:
                raise HTTPException(
                    status_code=400,
                    detail="No output type configured"
                )
            output_params = operation.output_params
            output_data = {}

            # 根据输出类型处理结果
            try:
                for param_config in output_params:
                    param_name = param_config['name']
                    param_type = param_config['type']
                    
                    if param_name not in result:
                        raise ValueError(f"Missing output parameter: {param_name}")
                        
                    value = result[param_name]
                    
                    if param_type == ParamType.IMAGE:
                        if not isinstance(value, np.ndarray):
                            raise ValueError(f"Expected image output for {param_name} but got different type")
                        success, encoded_img = cv2.imencode('.png', value)
                        if not success:
                            raise ValueError(f"Failed to encode processed image for {param_name}")
                        output_data[param_name] = {
                            'type': ParamType.IMAGE.value,
                            'data': base64.b64encode(encoded_img.tobytes()).decode('utf-8')
                        }
                    else:
                        output_data[param_name] = {
                            'type': param_type.value,
                            'data': value
                        }
                        
                return output_data
                
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error processing operation result: {str(e)}"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
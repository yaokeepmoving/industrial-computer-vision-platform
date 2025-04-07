from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Settings, Device
from datetime import datetime
from typing import List, Optional, Dict, Any

class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    # --- General Settings Methods ---
    
    def get_settings(self, category: Optional[str] = None) -> List[Settings]:
        """获取指定类别或所有设置"""
        query = self.db.query(Settings)
        if category:
            query = query.filter(Settings.category == category)
        return query.all()

    def get_setting(self, category: str, key: str) -> Optional[Settings]:
        """获取单个设置"""
        return self.db.query(Settings).filter(
            Settings.category == category,
            Settings.key == key
        ).first()

    def upsert_setting(self, category: str, key: str, value: str, description: Optional[str] = None) -> Settings:
        """创建或更新设置"""
        setting = self.get_setting(category, key)
        
        try:
            if setting:
                # Update existing setting
                setting.value = value
                if description:
                    setting.description = description
                setting.updated_at = datetime.utcnow()
            else:
                # Create new setting
                setting = Settings(
                    category=category,
                    key=key,
                    value=value,
                    description=description or "",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(setting)
                
            self.db.commit()
            self.db.refresh(setting)
            return setting
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_setting(self, category: str, key: str) -> bool:
        """删除设置"""
        setting = self.get_setting(category, key)
        if not setting:
            return False
            
        try:
            self.db.delete(setting)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    # --- System Settings Methods ---
    
    def get_system_settings(self) -> Dict[str, Any]:
        """获取所有系统设置"""
        settings = self.get_settings("system")
        result = {}
        
        for setting in settings:
            # Convert numeric values
            if setting.key in ["auto_save_interval", "alarm_threshold"]:
                result[setting.key] = int(setting.value)
            else:
                result[setting.key] = setting.value
                
        return result
        
    def update_system_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新系统设置"""
        for key, value in settings_data.items():
            self.upsert_setting("system", key, str(value))
            
        return self.get_system_settings()
    
    # --- MES Integration Settings Methods ---
    
    def get_mes_settings(self) -> Dict[str, str]:
        """获取MES集成设置"""
        settings = self.get_settings("mes")
        result = {}
        
        for setting in settings:
            result[setting.key] = setting.value
                
        return result
        
    def update_mes_settings(self, settings_data: Dict[str, str]) -> Dict[str, str]:
        """更新MES集成设置"""
        for key, value in settings_data.items():
            self.upsert_setting("mes", key, value)
            
        return self.get_mes_settings()

    # --- Device Methods ---
    
    def get_devices(self, type: Optional[str] = None) -> List[Device]:
        """获取设备列表，可选择按类型过滤"""
        query = self.db.query(Device)
        if type:
            query = query.filter(Device.type == type)
        return query.all()

    def get_device(self, device_id: int) -> Optional[Device]:
        """获取单个设备"""
        return self.db.query(Device).filter(Device.id == device_id).first()

    def get_device_by_name(self, name: str) -> Optional[Device]:
        """通过名称获取设备"""
        return self.db.query(Device).filter(Device.name == name).first()

    def create_device(self, name: str, type: str, model: Optional[str] = None, 
                      config: Dict[str, Any] = None, status: str = "offline") -> Device:
        """创建新设备"""
        if config is None:
            config = {}
        
        try:
            device = Device(
                name=name,
                type=type,
                model=model,
                config=config,
                status=status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            return device
        except Exception as e:
            self.db.rollback()
            raise e

    def update_device(self, device_id: int, data: Dict[str, Any]) -> Device:
        """更新设备"""
        device = self.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
            
        # If name is being updated, check for duplicates
        if 'name' in data and data['name'] != device.name:
            existing_device = self.get_device_by_name(data['name'])
            if existing_device:
                raise HTTPException(status_code=400, detail=f"Device with name '{data['name']}' already exists")
        
        try:
            # Update fields
            for key, value in data.items():
                if key in ['name', 'type', 'model', 'status']:
                    setattr(device, key, value)
                    
            # Handle config specially to merge rather than replace
            if 'config' in data:
                if device.config is None:
                    device.config = data['config']
                else:
                    device.config.update(data['config'])
                    
            device.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(device)
            return device
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_device(self, device_id: int) -> bool:
        """删除设备"""
        device = self.get_device(device_id)
        if not device:
            return False
            
        try:
            self.db.delete(device)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def update_device_status(self, device_id: int, status: str) -> Device:
        """更新设备状态"""
        device = self.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
            
        if status not in ["online", "offline", "error"]:
            raise HTTPException(status_code=400, detail="Invalid status")
            
        try:
            device.status = status
            device.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(device)
            return device
        except Exception as e:
            self.db.rollback()
            raise e 
// 相机设备接口类型定义
export interface CameraDevice {
  deviceId: string;
  label: string;
  capabilities: {
    formats: string[];
    resolutions: Array<{
      width: number;
      height: number;
    }>;
  };
}

// 相机设置接口类型定义
export interface CameraSettings {
  deviceId: string;
  resolution: {
    width: number;
    height: number;
  };
  format: string;
  exposure: number;
  gain: number;
  autoFocus: boolean;
  autoExposure: boolean;
}

// 数据集接口类型定义
export interface Dataset {
  data: Dataset | PromiseLike<Dataset>;
  id: number;
  name: string;
  imageCount: number;
}

// 图像数据接口类型定义
export interface ImageData {
  id: number;
  url: string;
  filename: string;
}

// OCR模型接口类型定义
export interface OcrModel {
  id: string;
  name: string;
  version: string;
  type: 'detection' | 'recognition' | 'end2end';
  supportedFormats: string[];
  accuracy: number;
  speed: number;
}

// OCR结果接口类型定义
export interface OcrResult {
  imageId: string;
  timestamp: string;
  boxes: Array<{
    id: string;
    text: string;
    confidence: number;
    bbox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
}

// 设备状态接口类型定义
export interface DeviceStatus {
  id: string;
  type: 'camera' | 'light' | 'trigger';
  status: 'online' | 'offline' | 'error';
  message?: string;
  lastUpdate: string;
}

// 标注数据接口类型定义
export interface AnnotationData {
  imageId: number;
  timestamp: string;
  labels: Array<{
    id: string;
    text: string;
    parent_id?: string;
    type: 'text_region' | 'character';
    bbox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    attributes?: Record<string, any>;
  }>;
}

// 标注标签接口类型定义
export interface AnnotationLabel {
  id: string;
  text: string;
  parent_id?: string;
  type: 'text_region' | 'character';
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  attributes?: Record<string, any>;
}
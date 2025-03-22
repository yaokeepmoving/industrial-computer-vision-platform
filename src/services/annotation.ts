import { apiService } from './api'

// 数据集类型枚举
export enum DatasetType {
  TEXT_REGION = 'text_region',
  OCR = 'ocr'
}

// 标注框
export interface BBox {
  x: number
  y: number
  width: number
  height: number
  rotation?: number
}

// 数据集
export interface Dataset {
  id: number
  name: string
  type: DatasetType
  imageCount: number
  createdAt: string
  updatedAt: string
}

// 图片
export interface Image {
  id: number
  filename: string
  url: string
  isAnnotated: boolean
  datasetId: number
  createdAt: string
}

// 标注数据
export interface AnnotationLabel {
  id: string
  type: 'text_region' | 'character'
  bbox: BBox
  label?: string
  confidence?: number
}
// 保存标注请求
export interface SaveAnnotationRequest {
  labels: AnnotationLabel[]
}

// 标注状态
export type AnnotationStatus = 'pending' | 'in_progress' | 'completed'

// 获取标注响应
export interface GetAnnotationResponse {
  annotations: AnnotationLabel[]
  status: AnnotationStatus
}

// 创建数据集请求
export interface CreateDatasetRequest {
  name: string
  type: DatasetType
}

// 更新数据集请求
export interface UpdateDatasetRequest {
  name: string
}

// 实现服务类
export class AnnotationService {
  // 数据集管理
  async getDatasets(): Promise<Dataset[]> {
    try {
      const response = await apiService.get<Dataset[]>('/annotation/datasets')
      return response
    } catch (error) {
      throw error
    }
  }

  async createDataset(data: CreateDatasetRequest): Promise<Dataset> {
    const response = await apiService.post<Dataset>(
      '/annotation/datasets',
      data
    )
    return response
  }

  async renameDataset(datasetId: number, name: string): Promise<Dataset> {
    try {
      const response = await apiService.put<Dataset>(
        `/annotation/datasets/${datasetId}`,
        { name }
      )
      return response
    } catch (error) {
      console.error('重命名数据集失败:', error)
      throw error
    }
  }

  async deleteDataset(datasetId: number): Promise<void> {
    await apiService.delete<void>(`/annotation/datasets/${datasetId}`)
  }

  // 图片管理
  async getDatasetImages(datasetId: number): Promise<Image[]> {
    const response = await apiService.get<Image[]>(
      `/annotation/datasets/${datasetId}/images`
    )
    return response
  }

  async uploadImages(datasetId: number, files: File[]): Promise<Image[]> {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await apiService.post<Image[]>(
      `/annotation/datasets/${datasetId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      } as any
    )
    return response
  }

  async deleteImage(imageId: number): Promise<void> {
    await apiService.delete(`/annotation/images/${imageId}`)
  }

  // 标注管理
  async getImageAnnotation(imageId: number): Promise<GetAnnotationResponse> {
    try {
      return await apiService.get<GetAnnotationResponse>(
        `/annotation/images/${imageId}/annotation`
      )
    } catch (error) {
      console.error('Failed to get annotations:', error)
      throw error
    }
  }

  async saveAnnotation(imageId: number, data: SaveAnnotationRequest): Promise<void> {
    try {
      console.log('Saving annotations:', data)
      await apiService.post(
        `/annotation/images/${imageId}/annotation`,
        data
      )
    } catch (error) {
      console.error('Failed to save annotations:', error)
      throw error
    }
  }

  async deleteAnnotation(imageId: number, annotationId: string): Promise<void> {
    try {
      console.log('Deleting annotation:', { imageId, annotationId })
      await apiService.delete(
        `/annotation/images/${imageId}/annotations/${annotationId}`
      )
    } catch (error) {
      console.error('Failed to delete annotation:', error)
      throw error
    }
  }
}
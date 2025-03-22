import { OcrModel, OcrResult, ImageData } from './types';
import { apiService } from './api';

export interface ModelService {
  getModels(): Promise<OcrModel[]>;
  getModel(id: string): Promise<OcrModel>;
  predict(modelId: string, image: ImageData): Promise<OcrResult>;
  train(modelId: string, data: Array<{ image: ImageData; labels: string[] }>): Promise<void>;
  evaluate(modelId: string, testData: Array<{ image: ImageData; labels: string[] }>): Promise<{
    accuracy: number;
    speed: number;
    confusionMatrix: Record<string, Record<string, number>>;
  }>;
}

export class ModelServiceImpl implements ModelService {
  async getModels(): Promise<OcrModel[]> {
    return apiService.get<OcrModel[]>('/models');
  }

  async getModel(id: string): Promise<OcrModel> {
    return apiService.get<OcrModel>(`/models/${id}`);
  }

  async predict(modelId: string, image: ImageData): Promise<OcrResult> {
    return apiService.post<OcrResult>(`/models/${modelId}/predict`, { image });
  }

  async train(modelId: string, data: Array<{ image: ImageData; labels: string[] }>): Promise<void> {
    await apiService.post(`/models/${modelId}/train`, { data });
  }

  async evaluate(modelId: string, testData: Array<{ image: ImageData; labels: string[] }>): Promise<{
    accuracy: number;
    speed: number;
    confusionMatrix: Record<string, Record<string, number>>;
  }> {
    return apiService.post(`/models/${modelId}/evaluate`, { testData });
  }
}
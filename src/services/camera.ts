import { CameraDevice, CameraSettings, ImageData } from './types';
import { apiService } from './api';

export interface CameraService {
  getDevices(): Promise<CameraDevice[]>;
  getSettings(): Promise<CameraSettings>;
  updateSettings(settings: Partial<CameraSettings>): Promise<void>;
  startStream(): Promise<void>;
  stopStream(): Promise<void>;
  captureImage(): Promise<ImageData>;
}

export class CameraServiceImpl implements CameraService {
  async getDevices(): Promise<CameraDevice[]> {
    return apiService.get<CameraDevice[]>('/cameras/devices');
  }

  async getSettings(): Promise<CameraSettings> {
    return apiService.get<CameraSettings>('/cameras/settings');
  }

  async updateSettings(settings: Partial<CameraSettings>): Promise<void> {
    await apiService.put('/cameras/settings', settings);
  }

  async startStream(): Promise<void> {
    await apiService.post('/cameras/stream/start');
  }

  async stopStream(): Promise<void> {
    await apiService.post('/cameras/stream/stop');
  }

  async captureImage(): Promise<ImageData> {
    return apiService.post<ImageData>('/cameras/capture');
  }
}
import { ref } from 'vue';
import { apiService } from './api';

// 系统状态类型
export interface SystemStatus {
  status: 'normal' | 'warning' | 'error';
  uptime: number;
  message?: string;
}

// 统计数据类型
export interface Statistics {
  total: number;
  change: number;
}

// 准确率数据类型
export interface Accuracy {
  value: number;
  change: number;
}

// 告警信息类型
export interface Alert {
  id: string;
  type: string;
  message: string;
  timestamp: number;
}

// Dashboard服务
export const useDashboard = () => {
  const systemStatus = ref<SystemStatus>({ status: 'normal', uptime: 0 });
  const detectionStats = ref<Statistics>({ total: 0, change: 0 });
  const defectStats = ref<Statistics>({ total: 0, change: 0 });
  const accuracy = ref<Accuracy>({ value: 0, change: 0 });
  const alerts = ref<Alert[]>([]);

  // 获取系统状态
  const getSystemStatus = async () => {
    const data = await apiService.get<SystemStatus>('/dashboard/system-status');
    systemStatus.value = data;
    return systemStatus.value;
  };

  // 获取今日检测统计
  const getDetectionStats = async () => {
    const data = await apiService.get<Statistics>('/dashboard/detection-stats');
    detectionStats.value = data;
    return detectionStats.value;
  };

  // 获取缺陷统计
  const getDefectStats = async () => {
    const data = await apiService.get<Statistics>('/dashboard/defect-stats');
    defectStats.value = data;
    return defectStats.value;
  };

  // 获取准确率
  const getAccuracy = async () => {
    const data = await apiService.get<Accuracy>('/dashboard/accuracy');
    accuracy.value = data;
    return accuracy.value;
  };

  // 获取最近告警
  const getRecentAlerts = async () => {
    const data = await apiService.get<Alert[]>('/dashboard/alerts');
    alerts.value = data;
    return alerts.value;
  };

  return {
    systemStatus,
    detectionStats,
    defectStats,
    accuracy,
    alerts,
    getSystemStatus,
    getDetectionStats,
    getDefectStats,
    getAccuracy,
    getRecentAlerts
  };
};
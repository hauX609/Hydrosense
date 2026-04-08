// API Types
export interface PredictionRequest {
  lat: number;
  lon: number;
  date: number;
  elevation: number;
  slope: number;
  landcover: number;
  precip_1d: number;
  precip_3d: number;
  precip_7d: number;
  precip_14d: number;
  dis_last: number;
  dis_trend_3: number;
  dayofyear: number;
}

export interface PredictionResponse {
  flood_probability: number;
  risk_level: 'Low' | 'Medium' | 'High';
  is_flood_predicted: boolean;
  confidence: number;
}

export interface ModelInfo {
  model_name: string;
  model_type: string;
  feature_names: string[];
  feature_count: number;
  version: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  timestamp: string;
}

// New Types for Enhanced Features

export interface Alert {
  id: string;
  timestamp: string;
  location: string;
  lat: number;
  lon: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  probability: number;
  message: string;
  isRead: boolean;
}

export interface SavedLocation {
  id: string;
  nickname: string;
  lat: number;
  lon: number;
  addedAt: string;
}

export interface PredictionHistoryEntry {
  id: string;
  timestamp: string;
  location: string;
  lat: number;
  lon: number;
  request: PredictionRequest;
  response: PredictionResponse;
}

export interface StatisticsData {
  totalPredictions: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  averageRisk: number;
  recentPredictions: PredictionHistoryEntry[];
}

export interface ComparisonLocation {
  id: string;
  nickname: string;
  lat: number;
  lon: number;
  precip_1d?: number;
  precip_3d?: number;
  precip_7d?: number;
  precip_14d?: number;
  prediction?: PredictionResponse;
}

export type Theme = 'light' | 'dark';

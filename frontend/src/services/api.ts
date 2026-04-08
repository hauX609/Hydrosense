import type { PredictionRequest, PredictionResponse, ModelInfo, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new ApiError(response.status, error.message || `HTTP ${response.status}`);
    }
    return response.json();
}

export async function predictFlood(data: PredictionRequest): Promise<PredictionResponse> {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    return handleResponse<PredictionResponse>(response);
}

export async function getModelInfo(): Promise<ModelInfo> {
    const response = await fetch(`${API_BASE_URL}/model/info`);
    return handleResponse<ModelInfo>(response);
}

export async function checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<HealthResponse>(response);
}

export { ApiError };

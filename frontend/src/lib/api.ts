import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ThreatEntity {
  name: string;
  count: number;
}

export interface AnalysisResponse {
  success: boolean;
  data: {
    _id: string;
    aiDetectionScore: number;
    threatEntities: ThreatEntity[];
    [key: string]: any;
  };
}

export interface BlockchainResponse {
  success: boolean;
  data: {
    transactionHash: string;
  };
}

export const analysisAPI = {
  analyzeText: async (text: string): Promise<AnalysisResponse> => {
    const response = await api.post('/analysis/text', { text });
    return response.data;
  },

  analyzeFile: async (file: File): Promise<AnalysisResponse> => {
    const formData = new FormData();
    formData.append('analysisFile', file);
    
    const response = await api.post('/analysis/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getAnalysisById: async (id: string): Promise<AnalysisResponse> => {
    const response = await api.get(`/analysis/${id}`);
    return response.data;
  },
};

export const blockchainAPI = {
  shareToBlockchain: async (id: string): Promise<BlockchainResponse> => {
    const response = await api.post(`/blockchain/share/${id}`);
    return response.data;
  },
};
